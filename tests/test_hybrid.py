"""
Tests for Phase 20: Hybrid Memory Architecture.

Covers: MemoryRouter, SyncEngine, SyncWorker, conflict resolution,
        memory versioning, SDK integration, REST endpoints.
"""

import os
import sys
import time
import json
import unittest
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from openmemo.storage.sqlite_store import SQLiteStore
from openmemo.sync.memory_router import MemoryRouter
from openmemo.sync.sync_engine import SyncEngine, SyncConfig
from openmemo.sync.sync_worker import SyncWorker
from openmemo.config import OpenMemoConfig, HybridConfig
from openmemo.api.sdk import Memory


class TestMemoryRouter(unittest.TestCase):
    def setUp(self):
        self.tmp_local = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.tmp_cloud = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.local_store = SQLiteStore(self.tmp_local.name)
        self.cloud_store = SQLiteStore(self.tmp_cloud.name)

    def tearDown(self):
        self.local_store.close()
        self.cloud_store.close()
        os.unlink(self.tmp_local.name)
        os.unlink(self.tmp_cloud.name)

    def test_local_mode(self):
        router = MemoryRouter(mode="local", local_store=self.local_store)
        self.assertEqual(router.get_mode(), "local")
        self.assertEqual(router.read_store, self.local_store)
        self.assertEqual(router.write_store, self.local_store)

    def test_cloud_mode(self):
        router = MemoryRouter(mode="cloud", local_store=self.local_store,
                               cloud_store=self.cloud_store)
        self.assertEqual(router.get_mode(), "cloud")
        self.assertEqual(router.read_store, self.cloud_store)
        self.assertEqual(router.write_store, self.cloud_store)

    def test_hybrid_mode(self):
        router = MemoryRouter(mode="hybrid", local_store=self.local_store,
                               cloud_store=self.cloud_store)
        self.assertEqual(router.get_mode(), "hybrid")
        self.assertEqual(router.read_store, self.local_store)
        self.assertEqual(router.write_store, self.local_store)

    def test_invalid_mode(self):
        with self.assertRaises(ValueError):
            MemoryRouter(mode="invalid", local_store=self.local_store)

    def test_cloud_mode_requires_cloud_store(self):
        with self.assertRaises(ValueError):
            MemoryRouter(mode="cloud", local_store=self.local_store)

    def test_local_write_and_read(self):
        router = MemoryRouter(mode="local", local_store=self.local_store)
        router.put_cell({
            "id": "c1", "note_id": "c1", "content": "test memory",
            "cell_type": "fact", "created_at": time.time(),
        })
        cell = router.get_cell("c1")
        self.assertIsNotNone(cell)
        self.assertEqual(cell["content"], "test memory")

    def test_hybrid_fallback_to_cloud(self):
        router = MemoryRouter(mode="hybrid", local_store=self.local_store,
                               cloud_store=self.cloud_store)
        self.cloud_store.put_cell({
            "id": "cloud1", "note_id": "cloud1", "content": "cloud memory",
            "cell_type": "fact", "created_at": time.time(),
        })
        cell = router.get_cell("cloud1")
        self.assertIsNotNone(cell)
        self.assertEqual(cell["content"], "cloud memory")

    def test_hybrid_write_goes_to_local(self):
        sync_engine = SyncEngine(local_store=self.local_store,
                                  cloud_store=self.cloud_store)
        router = MemoryRouter(mode="hybrid", local_store=self.local_store,
                               cloud_store=self.cloud_store,
                               sync_engine=sync_engine)
        router.put_cell({
            "id": "h1", "note_id": "h1", "content": "hybrid write",
            "cell_type": "fact", "created_at": time.time(),
        })
        local_cell = self.local_store.get_cell("h1")
        self.assertIsNotNone(local_cell)

        cloud_cell = self.cloud_store.get_cell("h1")
        self.assertIsNone(cloud_cell)

    def test_router_status(self):
        router = MemoryRouter(mode="local", local_store=self.local_store)
        status = router.get_status()
        self.assertEqual(status["mode"], "local")
        self.assertTrue(status["local_available"])
        self.assertFalse(status["cloud_available"])

    def test_router_note_operations(self):
        router = MemoryRouter(mode="local", local_store=self.local_store)
        router.put_note({"id": "n1", "content": "test note", "timestamp": time.time()})
        note = router.get_note("n1")
        self.assertIsNotNone(note)
        notes = router.list_notes()
        self.assertGreaterEqual(len(notes), 1)
        router.delete_note("n1")
        self.assertIsNone(router.get_note("n1"))

    def test_router_scene_operations(self):
        router = MemoryRouter(mode="local", local_store=self.local_store)
        router.put_scene({"id": "s1", "title": "test scene", "created_at": time.time()})
        scene = router.get_scene("s1")
        self.assertIsNotNone(scene)
        scenes = router.list_scenes()
        self.assertGreaterEqual(len(scenes), 1)

    def test_router_edge_operations(self):
        router = MemoryRouter(mode="local", local_store=self.local_store)
        router.put_edge({
            "edge_id": "e1", "memory_a": "c1", "memory_b": "c2",
            "relation_type": "related", "confidence": 0.8, "created_at": time.time(),
        })
        edges = router.get_edges("c1")
        self.assertGreaterEqual(len(edges), 1)


class TestSyncEngine(unittest.TestCase):
    def setUp(self):
        self.tmp_local = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.tmp_cloud = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.local_store = SQLiteStore(self.tmp_local.name)
        self.cloud_store = SQLiteStore(self.tmp_cloud.name)
        self.engine = SyncEngine(
            local_store=self.local_store, cloud_store=self.cloud_store,
            db_path=self.tmp_local.name,
        )

    def tearDown(self):
        self.engine.close()
        self.local_store.close()
        self.cloud_store.close()
        os.unlink(self.tmp_local.name)
        os.unlink(self.tmp_cloud.name)
        sync_path = self.tmp_local.name.replace(".db", "_sync.db")
        if os.path.exists(sync_path):
            os.unlink(sync_path)

    def test_queue_sync(self):
        self.engine.queue_sync("put_cell", {"id": "c1", "content": "test"})
        self.assertEqual(self.engine.get_queue_size(), 1)

    def test_push_sync(self):
        self.local_store.put_cell({
            "id": "c1", "note_id": "c1", "content": "local memory",
            "cell_type": "fact", "created_at": time.time(),
        })
        self.engine.queue_sync("put_cell", {
            "id": "c1", "note_id": "c1", "content": "local memory",
            "cell_type": "fact", "created_at": time.time(),
        })

        result = self.engine.push_sync()
        self.assertEqual(result["pushed"], 1)
        self.assertEqual(result["failed"], 0)

        cloud_cell = self.cloud_store.get_cell("c1")
        self.assertIsNotNone(cloud_cell)
        self.assertEqual(cloud_cell["content"], "local memory")

    def test_pull_sync(self):
        self.cloud_store.put_cell({
            "id": "cloud1", "note_id": "cloud1", "content": "cloud memory",
            "cell_type": "fact", "created_at": time.time(),
        })

        result = self.engine.pull_sync()
        self.assertGreaterEqual(result["pulled"], 1)

        local_cell = self.local_store.get_cell("cloud1")
        self.assertIsNotNone(local_cell)

    def test_full_sync(self):
        self.engine.queue_sync("put_cell", {
            "id": "c1", "note_id": "c1", "content": "to sync",
            "cell_type": "fact", "created_at": time.time(),
        })
        result = self.engine.full_sync()
        self.assertIn("push", result)
        self.assertIn("pull", result)
        self.assertIn("timestamp", result)

    def test_conflict_resolution_last_write_wins(self):
        self.local_store.put_cell({
            "id": "conflict1", "note_id": "conflict1",
            "content": "local version",
            "cell_type": "fact", "created_at": time.time() - 100,
            "last_accessed": time.time() - 100,
        })
        self.cloud_store.put_cell({
            "id": "conflict1", "note_id": "conflict1",
            "content": "cloud version (newer)",
            "cell_type": "fact", "created_at": time.time(),
            "last_accessed": time.time(),
        })

        result = self.engine.pull_sync()
        self.assertGreaterEqual(result["conflicts"], 1)

        local_cell = self.local_store.get_cell("conflict1")
        self.assertEqual(local_cell["content"], "cloud version (newer)")

    def test_conflict_resolution_confidence(self):
        engine = SyncEngine(
            local_store=self.local_store, cloud_store=self.cloud_store,
            config=SyncConfig(conflict_strategy="confidence"),
        )

        local = {
            "id": "c1", "content": "local", "created_at": time.time(),
            "metadata": json.dumps({"confidence": 0.9}),
        }
        cloud = {
            "id": "c1", "content": "cloud", "created_at": time.time(),
            "metadata": json.dumps({"confidence": 0.6}),
        }
        resolved = engine._resolve_conflict(local, cloud)
        self.assertEqual(resolved["content"], "local")

    def test_no_cloud_store_push(self):
        engine = SyncEngine(local_store=self.local_store)
        result = engine.push_sync()
        self.assertIn("error", result)

    def test_sync_status(self):
        status = self.engine.get_status()
        self.assertIn("last_sync", status)
        self.assertIn("sync_count", status)
        self.assertIn("queue_size", status)
        self.assertIn("conflict_strategy", status)

    def test_memory_versioning(self):
        self.engine.update_version("c1")
        self.assertEqual(self.engine.get_version("c1"), 1)
        self.engine.update_version("c1")
        self.assertEqual(self.engine.get_version("c1"), 2)

    def test_push_delete_operations(self):
        self.cloud_store.put_cell({
            "id": "del1", "note_id": "del1", "content": "to delete",
            "cell_type": "fact", "created_at": time.time(),
        })
        self.engine.queue_sync("delete_cell", {"id": "del1"})
        result = self.engine.push_sync()
        self.assertEqual(result["pushed"], 1)


class TestSyncWorker(unittest.TestCase):
    def setUp(self):
        self.tmp_local = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.tmp_cloud = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.local_store = SQLiteStore(self.tmp_local.name)
        self.cloud_store = SQLiteStore(self.tmp_cloud.name)
        self.engine = SyncEngine(
            local_store=self.local_store, cloud_store=self.cloud_store,
        )
        self.worker = SyncWorker(self.engine, interval=1)

    def tearDown(self):
        self.worker.stop()
        self.local_store.close()
        self.cloud_store.close()
        os.unlink(self.tmp_local.name)
        os.unlink(self.tmp_cloud.name)

    def test_run_once(self):
        result = self.worker.run_once()
        self.assertIn("push", result)
        self.assertIn("pull", result)

    def test_worker_status(self):
        status = self.worker.get_status()
        self.assertFalse(status["running"])
        self.assertEqual(status["interval"], 1)

    def test_start_stop(self):
        self.worker.start()
        self.assertTrue(self.worker.is_running)
        time.sleep(0.1)
        self.worker.stop()
        self.assertFalse(self.worker.is_running)


class TestSDKHybridMode(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.memo = Memory(db_path=self.tmp.name)

    def tearDown(self):
        self.memo.close()
        os.unlink(self.tmp.name)

    def test_default_local_mode(self):
        self.assertEqual(self.memo.get_memory_mode(), "local")
        self.assertIsNone(self.memo.sync_engine)
        self.assertIsNone(self.memo.router)

    def test_sync_status_local(self):
        status = self.memo.get_sync_status()
        self.assertEqual(status["mode"], "local")
        self.assertTrue(status["local_available"])
        self.assertFalse(status["cloud_available"])
        self.assertFalse(status["sync_enabled"])

    def test_push_sync_no_cloud(self):
        result = self.memo.push_sync()
        self.assertIn("error", result)

    def test_pull_sync_no_cloud(self):
        result = self.memo.pull_sync()
        self.assertIn("error", result)

    def test_full_sync_no_cloud(self):
        result = self.memo.full_sync()
        self.assertIn("error", result)

    def test_normal_operations_still_work(self):
        mid = self.memo.write_memory("test hybrid memory", scene="test")
        self.assertIsNotNone(mid)
        result = self.memo.recall_context("hybrid", scene="test")
        self.assertIn("context", result)
        stats = self.memo.stats()
        self.assertIn("cells", stats)


class TestSDKHybridWithCloud(unittest.TestCase):
    def setUp(self):
        self.tmp_local = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.tmp_cloud = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.cloud_store = SQLiteStore(self.tmp_cloud.name)

        config = OpenMemoConfig()
        config.hybrid.memory_mode = "hybrid"
        self.memo = Memory(
            db_path=self.tmp_local.name,
            config=config,
            cloud_store=self.cloud_store,
        )

    def tearDown(self):
        if self.memo.sync_worker:
            self.memo.sync_worker.stop()
        self.memo.close()
        self.cloud_store.close()
        os.unlink(self.tmp_local.name)
        os.unlink(self.tmp_cloud.name)
        sync_path = self.tmp_local.name.replace(".db", "_sync.db")
        if os.path.exists(sync_path):
            os.unlink(sync_path)

    def test_hybrid_mode_active(self):
        self.assertEqual(self.memo.get_memory_mode(), "hybrid")
        self.assertIsNotNone(self.memo.sync_engine)
        self.assertIsNotNone(self.memo.router)

    def test_write_goes_to_local(self):
        mid = self.memo.write_memory("hybrid test memory", scene="test")
        self.assertIsNotNone(mid)

        local_cells = self.memo._local_store.list_cells(limit=10)
        self.assertGreater(len(local_cells), 0)

    def test_push_sync_to_cloud(self):
        self.memo.write_memory("memory to sync", scene="sync")
        result = self.memo.push_sync()
        self.assertIn("pushed", result)

    def test_pull_from_cloud(self):
        self.cloud_store.put_cell({
            "id": "cloud_cell1", "note_id": "cloud_cell1",
            "content": "cloud imported memory",
            "cell_type": "fact", "created_at": time.time(),
        })
        result = self.memo.pull_sync()
        self.assertIn("pulled", result)

    def test_sync_status_hybrid(self):
        status = self.memo.get_sync_status()
        self.assertEqual(status["mode"], "hybrid")
        self.assertTrue(status["local_available"])
        self.assertTrue(status["cloud_available"])
        self.assertTrue(status["sync_enabled"])

    def test_full_sync(self):
        self.memo.write_memory("test full sync", scene="test")
        result = self.memo.full_sync()
        self.assertIn("push", result)
        self.assertIn("pull", result)


class TestRESTSync(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        from openmemo.api.rest_server import create_app
        self.app = create_app(db_path=self.tmp.name)
        self.client = self.app.test_client()

    def tearDown(self):
        os.unlink(self.tmp.name)

    def test_sync_push_endpoint(self):
        resp = self.client.post("/sync/push")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertIn("error", data)

    def test_sync_pull_endpoint(self):
        resp = self.client.get("/sync/pull")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertIn("error", data)

    def test_sync_status_endpoint(self):
        resp = self.client.get("/sync/status")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["mode"], "local")
        self.assertFalse(data["sync_enabled"])

    def test_existing_endpoints_still_work(self):
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertIn("sync_push", data.get("endpoints", {}))
        self.assertIn("sync_pull", data.get("endpoints", {}))
        self.assertIn("sync_status", data.get("endpoints", {}))


class TestRESTHybridSync(unittest.TestCase):
    def setUp(self):
        self.tmp_local = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.tmp_cloud = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.cloud_store = SQLiteStore(self.tmp_cloud.name)

        config = OpenMemoConfig()
        config.hybrid.memory_mode = "hybrid"

        from openmemo.api.rest_server import create_app
        self.app = create_app(
            db_path=self.tmp_local.name, config=config,
            cloud_store=self.cloud_store,
        )
        self.client = self.app.test_client()

    def tearDown(self):
        self.cloud_store.close()
        os.unlink(self.tmp_local.name)
        os.unlink(self.tmp_cloud.name)
        sync_path = self.tmp_local.name.replace(".db", "_sync.db")
        if os.path.exists(sync_path):
            os.unlink(sync_path)

    def test_hybrid_sync_status(self):
        resp = self.client.get("/sync/status")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["mode"], "hybrid")
        self.assertTrue(data["sync_enabled"])

    def test_hybrid_write_and_push(self):
        self.client.post("/memory/write", json={
            "content": "hybrid REST test memory", "scene": "test",
        })
        resp = self.client.post("/sync/push")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertIn("pushed", data)

    def test_hybrid_pull(self):
        self.cloud_store.put_cell({
            "id": "rest_cloud1", "note_id": "rest_cloud1",
            "content": "REST cloud memory",
            "cell_type": "fact", "created_at": time.time(),
        })
        resp = self.client.get("/sync/pull")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertIn("pulled", data)


class TestAutoSync(unittest.TestCase):
    def setUp(self):
        self.tmp_local = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.tmp_cloud = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.cloud_store = SQLiteStore(self.tmp_cloud.name, check_same_thread=False)

    def tearDown(self):
        self.cloud_store.close()
        os.unlink(self.tmp_local.name)
        os.unlink(self.tmp_cloud.name)
        sync_path = self.tmp_local.name.replace(".db", "_sync.db")
        if os.path.exists(sync_path):
            os.unlink(sync_path)

    def test_auto_sync_worker_thread_safe(self):
        config = OpenMemoConfig()
        config.hybrid.memory_mode = "hybrid"
        config.hybrid.auto_sync = False

        memo = Memory(
            db_path=self.tmp_local.name, config=config,
            cloud_store=self.cloud_store,
        )
        memo._auto_graph = False

        memo.write_memory("thread safe sync test", scene="test")

        result = memo.sync_worker.run_once()
        self.assertIn("push", result)
        self.assertIn("pull", result)

        memo.sync_worker.stop()
        memo.close()

    def test_fallback_warning_no_cloud(self):
        config = OpenMemoConfig()
        config.hybrid.memory_mode = "hybrid"

        memo = Memory(db_path=self.tmp_local.name, config=config)
        self.assertEqual(memo.get_memory_mode(), "local")
        memo.close()


if __name__ == "__main__":
    unittest.main()

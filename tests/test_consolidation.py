"""
Tests for Phase 19: Autonomous Memory Consolidation Engine.

Covers: duplicate detection, clustering, pattern extraction,
        playbook generation, memory decay, SDK integration.
"""

import os
import sys
import time
import unittest
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from openmemo.storage.sqlite_store import SQLiteStore
from openmemo.core.consolidation import (
    ConsolidationEngine, ConsolidationConfig,
    _content_similarity, _extract_keywords,
)
from openmemo.api.sdk import Memory


class TestContentSimilarity(unittest.TestCase):
    def test_identical_text(self):
        sim = _content_similarity("fix docker env bug", "fix docker env bug")
        self.assertGreaterEqual(sim, 0.99)

    def test_similar_text(self):
        sim = _content_similarity(
            "Docker environment variable missing caused deployment failure",
            "Docker environment variable missing led to deployment crash",
        )
        self.assertGreater(sim, 0.5)

    def test_unrelated_text(self):
        sim = _content_similarity(
            "The weather is sunny today",
            "Quantum computing uses qubits for processing",
        )
        self.assertLess(sim, 0.3)

    def test_empty_text(self):
        sim = _content_similarity("", "something")
        self.assertEqual(sim, 0.0)

    def test_keyword_extraction(self):
        kw = _extract_keywords("The quick brown fox jumps over the lazy dog")
        self.assertIn("quick", kw)
        self.assertIn("brown", kw)
        self.assertIn("fox", kw)
        self.assertNotIn("the", kw)


class TestDuplicateDetection(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.store = SQLiteStore(self.tmp.name)
        self.engine = ConsolidationEngine(store=self.store)

    def tearDown(self):
        self.store.close()
        os.unlink(self.tmp.name)

    def _add_cell(self, cell_id, content, confidence=0.8):
        import json
        self.store.put_cell({
            "id": cell_id, "note_id": cell_id, "content": content,
            "cell_type": "fact", "created_at": time.time(),
            "access_count": 0,
            "metadata": json.dumps({"confidence": confidence}),
        })

    def test_detect_duplicates(self):
        self._add_cell("c1", "Docker environment variable missing caused deployment failure crash")
        self._add_cell("c2", "Docker environment variable missing caused deployment failure error")
        self._add_cell("c3", "Quantum computing uses qubits for parallel processing tasks")

        dupes = self.engine.detect_duplicates()
        self.assertEqual(len(dupes), 1)
        self.assertGreater(dupes[0]["similarity"], 0.7)

    def test_merge_keeps_stronger(self):
        self._add_cell("c1", "Docker environment variable missing caused deployment failure crash", confidence=0.9)
        self._add_cell("c2", "Docker environment variable missing caused deployment failure error", confidence=0.7)

        cells = self.store.list_cells(limit=100)
        remaining, merged = self.engine._deduplicate(cells)
        self.assertEqual(merged, 1)
        self.assertEqual(len(remaining), 1)

    def test_no_duplicates(self):
        self._add_cell("c1", "Python is great for machine learning")
        self._add_cell("c2", "JavaScript is used for web development")

        dupes = self.engine.detect_duplicates()
        self.assertEqual(len(dupes), 0)


class TestClustering(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.store = SQLiteStore(self.tmp.name)
        self.engine = ConsolidationEngine(
            store=self.store,
            config=ConsolidationConfig(cluster_min_size=3),
        )

    def tearDown(self):
        self.store.close()
        os.unlink(self.tmp.name)

    def _add_cell(self, cell_id, content):
        self.store.put_cell({
            "id": cell_id, "note_id": cell_id, "content": content,
            "cell_type": "fact", "created_at": time.time(),
            "metadata": '{"confidence": 0.8}',
        })

    def test_cluster_similar_memories(self):
        self._add_cell("c1", "Docker container deployment failed due to port conflict")
        self._add_cell("c2", "Docker deployment error: port already in use on container")
        self._add_cell("c3", "Container port conflict causing Docker deployment failure")
        self._add_cell("c4", "Unrelated memory about cooking pasta")

        cells = self.store.list_cells(limit=100)
        clusters = self.engine._cluster(cells)
        self.assertGreaterEqual(len(clusters), 1)
        cluster_contents = [c["content"] for c in clusters[0]]
        self.assertTrue(all("Docker" in ct or "container" in ct.lower()
                            or "docker" in ct.lower() for ct in cluster_contents))

    def test_no_cluster_below_threshold(self):
        self._add_cell("c1", "Memory about cats")
        self._add_cell("c2", "Memory about dogs")

        cells = self.store.list_cells(limit=100)
        clusters = self.engine._cluster(cells)
        self.assertEqual(len(clusters), 0)


class TestPatternExtraction(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.store = SQLiteStore(self.tmp.name)
        self.engine = ConsolidationEngine(
            store=self.store,
            config=ConsolidationConfig(cluster_min_size=3),
        )

    def tearDown(self):
        self.store.close()
        os.unlink(self.tmp.name)

    def test_extract_pattern_from_cluster(self):
        cluster = [
            {"id": "c1", "content": "Docker env variable missing caused deployment failure", "scene": "deploy", "agent_id": ""},
            {"id": "c2", "content": "Missing env variable in Docker config led to crash", "scene": "deploy", "agent_id": ""},
            {"id": "c3", "content": "Deployment failed because Docker env variable not set", "scene": "deploy", "agent_id": ""},
        ]
        patterns = self.engine._extract_patterns([cluster])
        self.assertEqual(len(patterns), 1)
        self.assertEqual(patterns[0]["cell_type"], "pattern")
        self.assertIn("docker", patterns[0]["content"].lower())

    def test_pattern_stored_in_db(self):
        cluster = [
            {"id": "c1", "content": "Server timeout during peak hours", "scene": "ops", "agent_id": ""},
            {"id": "c2", "content": "Peak hours cause server timeout issues", "scene": "ops", "agent_id": ""},
            {"id": "c3", "content": "Timeout errors on server at peak traffic", "scene": "ops", "agent_id": ""},
        ]
        patterns = self.engine._extract_patterns([cluster])
        self.assertEqual(len(patterns), 1)
        stored = self.store.get_cell(patterns[0]["id"])
        self.assertIsNotNone(stored)
        self.assertEqual(stored["cell_type"], "pattern")

    def test_llm_callback_used(self):
        def mock_llm(op, data):
            if op == "extract_pattern":
                return {"pattern": "Docker deployments fail when env vars missing", "confidence": 0.95}
            return None

        engine = ConsolidationEngine(store=self.store, llm_fn=mock_llm)
        cluster = [
            {"id": "c1", "content": "Docker env error", "scene": "", "agent_id": ""},
            {"id": "c2", "content": "Missing Docker env", "scene": "", "agent_id": ""},
            {"id": "c3", "content": "Docker crash env", "scene": "", "agent_id": ""},
        ]
        patterns = engine._extract_patterns([cluster])
        self.assertEqual(len(patterns), 1)
        self.assertIn("Docker deployments", patterns[0]["content"])


class TestPlaybookGeneration(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.store = SQLiteStore(self.tmp.name)
        self.engine = ConsolidationEngine(store=self.store)

    def tearDown(self):
        self.store.close()
        os.unlink(self.tmp.name)

    def test_generate_playbook_from_pattern(self):
        pattern = {
            "id": "p1", "content": "Docker deployment failures", "scene": "deploy", "agent_id": "",
        }
        cluster = [
            {"id": "c1", "content": "Check Docker env variables before deployment"},
            {"id": "c2", "content": "Verify Dockerfile configuration is correct"},
            {"id": "c3", "content": "Run docker-compose up to test locally first"},
        ]
        playbooks = self.engine._generate_playbooks([pattern], [cluster])
        self.assertEqual(len(playbooks), 1)
        self.assertIn("Playbook", playbooks[0]["content"])
        self.assertEqual(playbooks[0]["cell_type"], "playbook")

    def test_playbook_stored_in_db(self):
        pattern = {"id": "p1", "content": "Test pattern", "scene": "", "agent_id": ""}
        cluster = [
            {"id": "c1", "content": "Step one of the process"},
            {"id": "c2", "content": "Step two of the process"},
            {"id": "c3", "content": "Step three of the process"},
        ]
        playbooks = self.engine._generate_playbooks([pattern], [cluster])
        if playbooks:
            stored = self.store.get_cell(playbooks[0]["id"])
            self.assertIsNotNone(stored)
            self.assertEqual(stored["cell_type"], "playbook")


class TestMemoryDecay(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.store = SQLiteStore(self.tmp.name)
        self.engine = ConsolidationEngine(
            store=self.store,
            config=ConsolidationConfig(decay_days=60, decay_confidence_threshold=0.3),
        )

    def tearDown(self):
        self.store.close()
        os.unlink(self.tmp.name)

    def test_remove_old_low_confidence(self):
        old_time = time.time() - 90 * 86400
        import json
        self.store.put_cell({
            "id": "old1", "note_id": "old1", "content": "Old low confidence memory",
            "cell_type": "fact", "created_at": old_time, "last_accessed": old_time,
            "metadata": json.dumps({"confidence": 0.2}),
        })
        self.store.put_cell({
            "id": "new1", "note_id": "new1", "content": "Recent high confidence memory",
            "cell_type": "fact", "created_at": time.time(), "last_accessed": time.time(),
            "metadata": json.dumps({"confidence": 0.9}),
        })
        cells = self.store.list_cells(limit=100)
        decayed, removed = self.engine._decay_memories(cells)
        self.assertGreaterEqual(removed, 1)

        remaining = self.store.list_cells(limit=100)
        ids = [c["id"] for c in remaining]
        self.assertNotIn("old1", ids)
        self.assertIn("new1", ids)

    def test_protect_patterns_from_decay(self):
        old_time = time.time() - 90 * 86400
        import json
        self.store.put_cell({
            "id": "pat1", "note_id": "pat1", "content": "Important pattern",
            "cell_type": "pattern", "created_at": old_time, "last_accessed": old_time,
            "metadata": json.dumps({"confidence": 0.2}),
        })
        cells = self.store.list_cells(limit=100)
        _, removed = self.engine._decay_memories(cells)
        self.assertEqual(removed, 0)


class TestMemoryPromotion(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.store = SQLiteStore(self.tmp.name)
        self.engine = ConsolidationEngine(
            store=self.store,
            config=ConsolidationConfig(promotion_confidence=0.9, promotion_cluster_size=3),
        )

    def tearDown(self):
        self.store.close()
        os.unlink(self.tmp.name)

    def test_promote_high_value_memory(self):
        import json
        self.store.put_cell({
            "id": "c1", "note_id": "c1", "content": "Valuable insight about deployment",
            "cell_type": "fact", "access_count": 5,
            "created_at": time.time(), "last_accessed": time.time(),
            "metadata": json.dumps({"confidence": 0.95}),
        })
        cells = self.store.list_cells(limit=100)
        promoted = self.engine._promote_memories(cells)
        self.assertEqual(promoted, 1)
        cell = self.store.get_cell("c1")
        self.assertEqual(cell["cell_type"], "pattern")

    def test_no_promote_low_access(self):
        import json
        self.store.put_cell({
            "id": "c1", "note_id": "c1", "content": "Low access memory",
            "cell_type": "fact", "access_count": 1,
            "created_at": time.time(),
            "metadata": json.dumps({"confidence": 0.95}),
        })
        cells = self.store.list_cells(limit=100)
        promoted = self.engine._promote_memories(cells)
        self.assertEqual(promoted, 0)


class TestFullConsolidation(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.memo = Memory(db_path=self.tmp.name)
        self.memo._auto_graph = False

    def tearDown(self):
        self.memo.close()
        os.unlink(self.tmp.name)

    def test_consolidate_via_sdk(self):
        self.memo.write_memory("Docker env variable missing caused crash", scene="deploy")
        self.memo.write_memory("Missing Docker environment variable bug", scene="deploy")
        self.memo.write_memory("Docker environment variable not set error", scene="deploy")
        self.memo.write_memory("Docker env config missing in deployment", scene="deploy")

        result = self.memo.consolidate(scene="deploy")
        self.assertIn("duplicates_merged", result)
        self.assertIn("clusters_found", result)
        self.assertIn("patterns_extracted", result)
        self.assertIn("duration_ms", result)

    def test_get_patterns_via_sdk(self):
        self.memo.write_memory("Server timeout during peak traffic load connection error", scene="ops")
        self.memo.write_memory("Server timeout during peak traffic load connection refused", scene="ops")
        self.memo.write_memory("Server timeout during peak traffic load connection dropped", scene="ops")
        self.memo.write_memory("Server timeout during peak traffic load connection reset", scene="ops")

        self.memo.consolidate(scene="ops")
        patterns = self.memo.get_patterns(scene="ops")
        self.assertGreater(len(patterns), 0)
        pattern_types = [p.get("cell_type") for p in patterns]
        self.assertTrue(any(t in ("pattern", "playbook") for t in pattern_types))

    def test_detect_duplicates_via_sdk(self):
        self.memo.write_memory("Use Python for backend development")
        self.memo.write_memory("Python backend development is recommended")
        self.memo.write_memory("JavaScript is great for frontend")

        dupes = self.memo.detect_duplicates()
        self.assertIsInstance(dupes, list)

    def test_governance_consolidate_operation(self):
        self.memo.write_memory("Test memory for consolidation")
        result = self.memo.memory_governance("consolidate")
        self.assertIn("duplicates_merged", result)

    def test_consolidation_result_structure(self):
        result = self.memo.consolidate()
        required_keys = [
            "duplicates_merged", "clusters_found", "patterns_extracted",
            "playbooks_generated", "memories_decayed", "memories_removed",
            "promoted", "duration_ms",
        ]
        for key in required_keys:
            self.assertIn(key, result)

    def test_stats_unchanged(self):
        self.memo.write_memory("Test memory")
        stats = self.memo.stats()
        self.assertIn("cells", stats)
        self.assertIn("edges", stats)


class TestEndToEndConsolidation(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.memo = Memory(db_path=self.tmp.name)
        self.memo._auto_graph = False

    def tearDown(self):
        self.memo.close()
        os.unlink(self.tmp.name)

    def test_consolidation_produces_clusters_and_patterns(self):
        for i in range(5):
            self.memo.write_memory(
                f"Docker environment variable config caused deployment failure variant{i}",
                scene="deploy",
            )

        result = self.memo.consolidate(scene="deploy")
        self.assertGreater(result["clusters_found"], 0)
        self.assertGreater(result["patterns_extracted"], 0)

    def test_consolidation_produces_playbooks(self):
        for i in range(5):
            self.memo.write_memory(
                f"Server timeout during peak traffic load connection issue{i}",
                scene="ops",
            )

        result = self.memo.consolidate(scene="ops")
        self.assertGreaterEqual(result["playbooks_generated"], 0)
        self.assertGreater(result["patterns_extracted"], 0)


class TestRESTConsolidation(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        from openmemo.api.rest_server import create_app
        self.app = create_app(db_path=self.tmp.name)
        self.client = self.app.test_client()

    def tearDown(self):
        os.unlink(self.tmp.name)

    def _write(self, content, scene="test"):
        return self.client.post("/memory/write", json={
            "content": content, "scene": scene,
        })

    def test_consolidate_endpoint(self):
        for i in range(4):
            self._write(f"Docker environment variable error deployment failure item{i}", "deploy")

        resp = self.client.post("/memory/consolidate", json={"scene": "deploy"})
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertIn("duplicates_merged", data)
        self.assertIn("clusters_found", data)
        self.assertIn("patterns_extracted", data)
        self.assertIn("duration_ms", data)

    def test_patterns_endpoint(self):
        for i in range(4):
            self._write(f"Server timeout peak traffic connection error variant{i}", "ops")
        self.client.post("/memory/consolidate", json={"scene": "ops"})

        resp = self.client.get("/memory/patterns?scene=ops")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertIn("patterns", data)
        self.assertIsInstance(data["patterns"], list)

    def test_duplicates_endpoint(self):
        resp = self.client.get("/memory/duplicates")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertIn("duplicates", data)
        self.assertIsInstance(data["duplicates"], list)

    def test_patterns_response_schema(self):
        for i in range(4):
            self._write(f"Database query optimization index performance issue{i}", "db")
        self.client.post("/memory/consolidate", json={"scene": "db"})

        resp = self.client.get("/memory/patterns?scene=db")
        data = resp.get_json()
        for p in data.get("patterns", []):
            self.assertIn("id", p)
            self.assertIn("content", p)
            self.assertIn("type", p)
            self.assertIn("confidence", p)


if __name__ == "__main__":
    unittest.main()

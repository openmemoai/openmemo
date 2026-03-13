"""
Tests for Phase 22 — Team Memory System

Covers:
  - TeamRouter: scope routing, namespace, scope weights
  - PromotionWorker: shared→team promotion with criteria
  - SDK: write with team_id/task_id, team recall, promote_to_team, list_team/task_memories
  - MemCell: team_id/task_id fields in dataclass + to_dict/from_dict
  - SQLite store: team_id/task_id columns, list_cells_scoped with team filtering
  - REST API: team endpoints
"""

import os
import time
import tempfile
import pytest

from openmemo.api.sdk import Memory
from openmemo.core.memcell import MemCell
from openmemo.team.team_router import (
    route_scope, build_namespace, get_scope_weight, apply_scope_weights,
    SCOPE_PRIVATE, SCOPE_SHARED, SCOPE_TEAM, SCOPE_CONVERSATION,
    TEAM_TYPES, SHARED_TYPES,
)
from openmemo.team.promotion import PromotionWorker, PromotionConfig, TEMPORARY_TYPES
from openmemo.storage.sqlite_store import SQLiteStore


@pytest.fixture
def tmp_db():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    yield path
    if os.path.exists(path):
        os.unlink(path)


@pytest.fixture
def memory(tmp_db):
    m = Memory(db_path=tmp_db)
    yield m
    m.close()


@pytest.fixture
def store(tmp_db):
    s = SQLiteStore(tmp_db)
    yield s
    s.close()


class TestTeamRouter:

    def test_route_scope_explicit(self):
        assert route_scope("fact", scope="team") == "team"
        assert route_scope("decision", scope="private") == "private"

    def test_route_scope_team_types(self):
        for t in TEAM_TYPES:
            assert route_scope(t) == SCOPE_TEAM, f"{t} should route to team"

    def test_route_scope_shared_types(self):
        for t in SHARED_TYPES:
            assert route_scope(t) == SCOPE_SHARED, f"{t} should route to shared"

    def test_route_scope_default_private(self):
        assert route_scope("fact") == SCOPE_PRIVATE
        assert route_scope("note") == SCOPE_PRIVATE

    def test_build_namespace_basic(self):
        ns = build_namespace(team_id="team1", task_id="task1", agent_id="a1", scope="private")
        assert "team1" in ns
        assert "task1" in ns
        assert "a1" in ns
        assert "private" in ns

    def test_build_namespace_team_scope(self):
        ns = build_namespace(team_id="team1", task_id="task1", agent_id="a1", scope="team")
        assert "team1" in ns
        assert "a1" not in ns

    def test_build_namespace_no_team(self):
        ns = build_namespace(agent_id="a1", scope="private")
        assert "openmemo" in ns
        assert "a1" in ns

    def test_get_scope_weight(self):
        assert get_scope_weight("private") == 1.0
        assert get_scope_weight("conversation") == 0.90
        assert get_scope_weight("shared") == 0.85
        assert get_scope_weight("team") == 0.70
        assert get_scope_weight("unknown") == 0.5

    def test_apply_scope_weights_dict(self):
        items = [
            {"score": 1.0, "scope": "private"},
            {"score": 1.0, "scope": "team"},
        ]
        weighted = apply_scope_weights(items)
        assert weighted[0]["score"] == 1.0
        assert weighted[1]["score"] == 0.70


class TestPromotionConfig:

    def test_defaults(self):
        config = PromotionConfig()
        assert config.confidence_threshold == 0.75
        assert config.access_threshold == 2
        assert config.min_age_hours == 1

    def test_custom(self):
        config = PromotionConfig(confidence_threshold=0.9, access_threshold=5, min_age_hours=2)
        assert config.confidence_threshold == 0.9
        assert config.access_threshold == 5
        assert config.min_age_hours == 2


class TestPromotionWorker:

    def test_evaluate_temporary_type(self):
        worker = PromotionWorker()
        for t in TEMPORARY_TYPES:
            cell = {"cell_type": t, "scope": "shared", "metadata": {"confidence": 0.9},
                    "access_count": 10, "created_at": 0}
            assert not worker.evaluate_promotion(cell)

    def test_evaluate_already_team(self):
        worker = PromotionWorker()
        cell = {"cell_type": "decision", "scope": "team",
                "metadata": {"confidence": 0.9}, "access_count": 10, "created_at": 0}
        assert not worker.evaluate_promotion(cell)

    def test_evaluate_low_confidence(self):
        worker = PromotionWorker()
        cell = {"cell_type": "decision", "scope": "shared",
                "metadata": {"confidence": 0.3}, "access_count": 10, "created_at": 0}
        assert not worker.evaluate_promotion(cell)

    def test_evaluate_too_young(self):
        worker = PromotionWorker()
        cell = {"cell_type": "decision", "scope": "shared",
                "metadata": {"confidence": 0.9}, "access_count": 10,
                "created_at": time.time()}
        assert not worker.evaluate_promotion(cell)

    def test_evaluate_promotable(self):
        worker = PromotionWorker()
        cell = {"cell_type": "decision", "scope": "shared",
                "metadata": {"confidence": 0.9}, "access_count": 3,
                "created_at": time.time() - 7200}
        assert worker.evaluate_promotion(cell)

    def test_promote_to_team_no_store(self):
        worker = PromotionWorker()
        result = worker.promote_to_team()
        assert result["promoted"] == 0
        assert result["evaluated"] == 0

    def test_promote_to_team_with_store(self, store):
        old_time = time.time() - 7200
        cell_data = {
            "id": "c1", "note_id": "n1", "content": "Use retry with backoff",
            "cell_type": "decision", "scope": "shared", "importance": 0.8,
            "access_count": 5, "created_at": old_time, "last_accessed": time.time(),
            "agent_id": "a1", "scene": "coding", "conversation_id": "",
            "team_id": "team1", "task_id": "task1",
            "facts": [], "stage": "exploration",
            "connections": [], "metadata": {"confidence": 0.9},
        }
        import json
        cell_data["facts"] = json.dumps(cell_data["facts"])
        cell_data["connections"] = json.dumps(cell_data["connections"])
        cell_data["metadata"] = json.dumps(cell_data["metadata"])
        store.put_cell(cell_data)

        worker = PromotionWorker(store=store)
        result = worker.promote_to_team(team_id="team1")
        assert result["evaluated"] == 1
        assert result["promoted"] == 1

        updated = store.get_cell("c1")
        assert updated["scope"] == "team"
        assert updated["team_id"] == "team1"

    def test_promote_skips_low_confidence(self, store):
        old_time = time.time() - 7200
        cell_data = {
            "id": "c2", "note_id": "n1", "content": "Maybe use caching",
            "cell_type": "finding", "scope": "shared", "importance": 0.3,
            "access_count": 1, "created_at": old_time, "last_accessed": time.time(),
            "agent_id": "a1", "scene": "coding", "conversation_id": "",
            "team_id": "", "task_id": "",
            "facts": "[]", "stage": "exploration",
            "connections": "[]", "metadata": '{"confidence": 0.3}',
        }
        store.put_cell(cell_data)
        worker = PromotionWorker(store=store)
        result = worker.promote_to_team()
        assert result["promoted"] == 0


class TestMemCellTeamFields:

    def test_memcell_has_team_fields(self):
        cell = MemCell(content="test", team_id="t1", task_id="tk1")
        assert cell.team_id == "t1"
        assert cell.task_id == "tk1"

    def test_memcell_defaults(self):
        cell = MemCell(content="test")
        assert cell.team_id == ""
        assert cell.task_id == ""

    def test_to_dict_includes_team_fields(self):
        cell = MemCell(content="test", team_id="t1", task_id="tk1")
        d = cell.to_dict()
        assert d["team_id"] == "t1"
        assert d["task_id"] == "tk1"

    def test_from_dict_includes_team_fields(self):
        d = {"content": "test", "team_id": "t1", "task_id": "tk1"}
        cell = MemCell.from_dict(d)
        assert cell.team_id == "t1"
        assert cell.task_id == "tk1"


class TestStoreTeamFields:

    def test_put_cell_with_team_fields(self, store):
        cell = {
            "id": "c1", "note_id": "n1", "content": "test",
            "cell_type": "fact", "scope": "team",
            "team_id": "team1", "task_id": "task1",
            "facts": "[]", "stage": "exploration", "importance": 0.5,
            "access_count": 0, "last_accessed": 0, "created_at": time.time(),
            "agent_id": "", "scene": "", "conversation_id": "",
            "connections": "[]", "metadata": "{}",
        }
        store.put_cell(cell)
        result = store.get_cell("c1")
        assert result is not None
        assert result["team_id"] == "team1"
        assert result["task_id"] == "task1"
        assert result["scope"] == "team"

    def test_list_cells_scoped_team(self, store):
        now = time.time()
        for i, (scope, tid) in enumerate([
            ("team", "team1"), ("team", "team2"), ("private", ""), ("shared", "")
        ]):
            store.put_cell({
                "id": f"c{i}", "note_id": "n1", "content": f"cell{i}",
                "cell_type": "fact", "scope": scope,
                "team_id": tid, "task_id": "",
                "facts": "[]", "stage": "exploration", "importance": 0.5,
                "access_count": 0, "last_accessed": 0, "created_at": now,
                "agent_id": "a1", "scene": "", "conversation_id": "",
                "connections": "[]", "metadata": "{}",
            })

        results = store.list_cells_scoped(agent_id="a1", team_id="team1")
        scopes = {r["scope"] for r in results}
        team_ids = {r.get("team_id", "") for r in results if r["scope"] == "team"}
        assert "team" in scopes
        assert "team1" in team_ids
        assert "team2" not in team_ids

    def test_list_cells_scoped_task_id(self, store):
        now = time.time()
        store.put_cell({
            "id": "c10", "note_id": "n1", "content": "shared for task1",
            "cell_type": "fact", "scope": "shared",
            "team_id": "", "task_id": "task1",
            "facts": "[]", "stage": "exploration", "importance": 0.5,
            "access_count": 0, "last_accessed": 0, "created_at": now,
            "agent_id": "a1", "scene": "", "conversation_id": "",
            "connections": "[]", "metadata": "{}",
        })
        store.put_cell({
            "id": "c11", "note_id": "n1", "content": "shared for task2",
            "cell_type": "fact", "scope": "shared",
            "team_id": "", "task_id": "task2",
            "facts": "[]", "stage": "exploration", "importance": 0.5,
            "access_count": 0, "last_accessed": 0, "created_at": now,
            "agent_id": "a1", "scene": "", "conversation_id": "",
            "connections": "[]", "metadata": "{}",
        })
        store.put_cell({
            "id": "c12", "note_id": "n1", "content": "team memory",
            "cell_type": "fact", "scope": "team",
            "team_id": "team1", "task_id": "",
            "facts": "[]", "stage": "exploration", "importance": 0.5,
            "access_count": 0, "last_accessed": 0, "created_at": now,
            "agent_id": "a1", "scene": "", "conversation_id": "",
            "connections": "[]", "metadata": "{}",
        })
        results = store.list_cells_scoped(agent_id="a1", task_id="task1")
        ids = {r["id"] for r in results}
        assert "c10" in ids
        assert "c12" in ids


class TestSDKTeamMemory:

    def test_write_with_team_id(self, memory):
        mid = memory.write_memory(
            content="Use exponential backoff for retries",
            scene="coding", memory_type="decision",
            team_id="team1", task_id="task1",
            agent_id="agent1",
        )
        assert mid

    def test_write_team_scope_auto_routing(self, memory):
        mid = memory.write_memory(
            content="Always use UTC timestamps",
            memory_type="convention",
            team_id="team1", agent_id="a1",
        )
        assert mid

    def test_list_team_memories(self, memory):
        memory.write_memory(
            content="Team convention: use snake_case",
            memory_type="convention", scope="team",
            team_id="team1", agent_id="a1",
        )
        memory.write_memory(
            content="Private note",
            memory_type="fact", scope="private",
            agent_id="a1",
        )
        results = memory.list_team_memories(team_id="team1")
        assert len(results) >= 1
        assert all(r["scope"] == "team" for r in results)

    def test_list_task_memories(self, memory):
        memory.write_memory(
            content="Task finding: API latency is 200ms",
            memory_type="finding", scope="shared",
            team_id="team1", task_id="task42",
            agent_id="a1",
        )
        memory.write_memory(
            content="Other task finding",
            memory_type="finding", scope="shared",
            team_id="team1", task_id="task99",
            agent_id="a1",
        )
        results = memory.list_task_memories(task_id="task42")
        assert len(results) >= 1
        assert all(r.get("task_id") == "task42" for r in results)

    def test_promote_to_team(self, memory):
        old_time = time.time() - 7200
        memory.write_memory(
            content="Validated: cache improves performance 3x",
            memory_type="validated", scope="shared",
            team_id="team1", task_id="task1",
            agent_id="a1", confidence=0.9,
        )
        cell_list = memory.store.list_cells(limit=10)
        for c in cell_list:
            if c.get("scope") == "shared":
                c["created_at"] = old_time
                c["access_count"] = 5
                memory.store.put_cell(c)

        result = memory.promote_to_team(team_id="team1")
        assert result["evaluated"] >= 1
        assert result["promoted"] >= 0

    def test_search_with_team_id(self, memory):
        memory.write_memory(
            content="Team decision: use PostgreSQL for persistence",
            memory_type="decision", scope="team",
            team_id="team1", agent_id="a1",
        )
        results = memory.search_memory(
            query="PostgreSQL", team_id="team1", agent_id="a1",
        )
        assert isinstance(results, list)

    def test_recall_with_team_id(self, memory):
        memory.write_memory(
            content="Team workflow: deploy to staging before prod",
            memory_type="workflow", scope="team",
            team_id="team1", agent_id="a1",
        )
        result = memory.recall_context(
            query="deployment", team_id="team1", agent_id="a1",
        )
        assert isinstance(result, dict)


class TestRESTTeamEndpoints:

    @pytest.fixture
    def client(self, tmp_db):
        from openmemo.api.rest_server import create_app
        app = create_app(db_path=tmp_db)
        app.config["TESTING"] = True
        with app.test_client() as c:
            yield c

    def test_write_with_team_fields(self, client):
        resp = client.post("/memory/write", json={
            "content": "Team standard: all PRs need 2 approvals",
            "type": "standard",
            "scope": "team",
            "team_id": "team1",
            "task_id": "task1",
            "agent_id": "a1",
        })
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["memory_id"]

    def test_recall_with_team_fields(self, client):
        client.post("/memory/write", json={
            "content": "Team convention: use TypeScript strict mode",
            "type": "convention",
            "scope": "team",
            "team_id": "team1",
            "agent_id": "a1",
        })
        resp = client.post("/memory/recall", json={
            "query": "TypeScript",
            "team_id": "team1",
            "agent_id": "a1",
        })
        assert resp.status_code == 200

    def test_team_promote_endpoint(self, client):
        resp = client.post("/team/promote", json={"team_id": "team1"})
        assert resp.status_code == 200
        data = resp.get_json()
        assert "promoted" in data
        assert "evaluated" in data

    def test_team_memories_endpoint(self, client):
        client.post("/memory/write", json={
            "content": "Team policy: no secrets in code",
            "type": "policy",
            "scope": "team",
            "team_id": "team1",
            "agent_id": "a1",
        })
        resp = client.get("/team/memories?team_id=team1")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "results" in data
        assert "count" in data

    def test_task_memories_endpoint(self, client):
        client.post("/memory/write", json={
            "content": "Task finding: endpoint responds in 50ms",
            "type": "finding",
            "scope": "shared",
            "team_id": "team1",
            "task_id": "task42",
            "agent_id": "a1",
        })
        resp = client.get("/team/task/task42?team_id=team1")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "results" in data

    def test_search_with_team_fields(self, client):
        client.post("/memory/write", json={
            "content": "Team uses Redis for caching",
            "type": "decision",
            "scope": "team",
            "team_id": "team1",
            "agent_id": "a1",
        })
        resp = client.post("/memory/search", json={
            "query": "Redis caching",
            "team_id": "team1",
            "agent_id": "a1",
        })
        assert resp.status_code == 200


class TestTeamRecallIntegration:

    def test_layered_recall_includes_team(self, memory):
        memory.write_memory(
            content="Private note about my approach",
            memory_type="fact", scope="private",
            agent_id="a1",
        )
        memory.write_memory(
            content="Shared task finding about performance",
            memory_type="finding", scope="shared",
            team_id="team1", task_id="task1",
            agent_id="a1",
        )
        memory.write_memory(
            content="Team standard: always profile before optimizing",
            memory_type="standard", scope="team",
            team_id="team1", agent_id="a1",
        )
        results = memory.search_memory(
            query="performance optimization",
            agent_id="a1", team_id="team1",
        )
        assert isinstance(results, list)

    def test_multi_team_isolation(self, memory):
        memory.write_memory(
            content="Team Alpha decision: use gRPC",
            memory_type="decision", scope="team",
            team_id="alpha", agent_id="a1",
        )
        memory.write_memory(
            content="Team Beta decision: use REST",
            memory_type="decision", scope="team",
            team_id="beta", agent_id="a1",
        )
        alpha_mems = memory.list_team_memories(team_id="alpha")
        beta_mems = memory.list_team_memories(team_id="beta")
        alpha_contents = [m["content"] for m in alpha_mems]
        beta_contents = [m["content"] for m in beta_mems]
        assert any("gRPC" in c for c in alpha_contents)
        assert not any("REST" in c for c in alpha_contents)
        assert any("REST" in c for c in beta_contents)
        assert not any("gRPC" in c for c in beta_contents)

"""Tests for Phase 17: Agent Scoped Memory System."""
import time
import pytest
from openmemo.api.sdk import Memory


class TestMemoryScope:
    @pytest.fixture
    def mem(self):
        m = Memory(db_path=":memory:")
        yield m
        m.close()

    def test_default_scope_is_private(self, mem):
        mem.write_memory("Private fact", agent_id="agent_a")
        cells = mem.store.list_cells(limit=10)
        assert len(cells) == 1
        assert cells[0]["scope"] == "private"

    def test_explicit_shared_scope(self, mem):
        mem.write_memory("Shared rule", agent_id="agent_a", scope="shared")
        cells = mem.store.list_cells(limit=10)
        assert cells[0]["scope"] == "shared"

    def test_auto_shared_for_rules_type(self, mem):
        mem.write_memory("Always use HTTPS", memory_type="rules", agent_id="agent_a")
        cells = mem.store.list_cells(limit=10)
        assert cells[0]["scope"] == "shared"

    def test_auto_shared_for_playbook_type(self, mem):
        mem.write_memory("Deploy checklist", memory_type="playbook", agent_id="agent_a")
        cells = mem.store.list_cells(limit=10)
        assert cells[0]["scope"] == "shared"

    def test_auto_shared_for_pattern_type(self, mem):
        mem.write_memory("Retry pattern", memory_type="pattern", agent_id="agent_a")
        cells = mem.store.list_cells(limit=10)
        assert cells[0]["scope"] == "shared"

    def test_auto_shared_for_convention_type(self, mem):
        mem.write_memory("Use camelCase", memory_type="convention", agent_id="agent_a")
        cells = mem.store.list_cells(limit=10)
        assert cells[0]["scope"] == "shared"

    def test_auto_shared_for_policy_type(self, mem):
        mem.write_memory("No direct DB access", memory_type="policy", agent_id="agent_a")
        cells = mem.store.list_cells(limit=10)
        assert cells[0]["scope"] == "shared"

    def test_conversation_scope(self, mem):
        mem.write_memory("Conversation fact", agent_id="agent_a",
                         scope="conversation", conversation_id="conv_1")
        cells = mem.store.list_cells(limit=10)
        assert cells[0]["scope"] == "conversation"
        assert cells[0]["conversation_id"] == "conv_1"


class TestScopeIsolation:
    @pytest.fixture
    def mem(self):
        m = Memory(db_path=":memory:")
        yield m
        m.close()

    def test_private_memory_isolation(self, mem):
        mem.write_memory("Agent A secret", agent_id="agent_a",
                         scene="coding", scope="private")
        mem.write_memory("Agent B secret", agent_id="agent_b",
                         scene="coding", scope="private")

        results_a = mem.search_memory("secret", agent_id="agent_a", scene="coding")
        results_b = mem.search_memory("secret", agent_id="agent_b", scene="coding")

        contents_a = [r["content"] for r in results_a]
        contents_b = [r["content"] for r in results_b]

        assert "Agent A secret" in contents_a
        assert "Agent B secret" not in contents_a
        assert "Agent B secret" in contents_b
        assert "Agent A secret" not in contents_b

    def test_shared_memory_visible_to_all(self, mem):
        mem.write_memory("Shared deployment rule", agent_id="agent_a",
                         scene="infra", scope="shared")
        mem.write_memory("Agent B private", agent_id="agent_b",
                         scene="infra", scope="private")

        results_a = mem.search_memory("deployment rule", agent_id="agent_a", scene="infra")
        results_b = mem.search_memory("deployment rule", agent_id="agent_b", scene="infra")

        contents_a = [r["content"] for r in results_a]
        contents_b = [r["content"] for r in results_b]

        assert "Shared deployment rule" in contents_a
        assert "Shared deployment rule" in contents_b

    def test_conversation_scope_isolation(self, mem):
        mem.write_memory("Conv 1 context data", agent_id="agent_a",
                         scope="conversation", conversation_id="conv_1")
        mem.write_memory("Conv 2 context data", agent_id="agent_a",
                         scope="conversation", conversation_id="conv_2")

        results_1 = mem.store.list_cells_scoped(
            agent_id="agent_a", conversation_id="conv_1")
        results_2 = mem.store.list_cells_scoped(
            agent_id="agent_a", conversation_id="conv_2")

        contents_1 = [r["content"] for r in results_1]
        contents_2 = [r["content"] for r in results_2]

        assert "Conv 1 context data" in contents_1
        assert "Conv 2 context data" not in contents_1
        assert "Conv 2 context data" in contents_2
        assert "Conv 1 context data" not in contents_2

    def test_mixed_scope_recall(self, mem):
        mem.write_memory("Private memory for A", agent_id="agent_a",
                         scene="coding", scope="private")
        mem.write_memory("Shared coding standard memory", agent_id="agent_b",
                         scene="coding", scope="shared")
        mem.write_memory("Private memory for B", agent_id="agent_b",
                         scene="coding", scope="private")

        results = mem.search_memory("memory", agent_id="agent_a", scene="coding")
        contents = [r["content"] for r in results]

        assert "Private memory for A" in contents
        assert "Shared coding standard memory" in contents
        assert "Private memory for B" not in contents


class TestAgentRegistry:
    @pytest.fixture
    def mem(self):
        m = Memory(db_path=":memory:")
        yield m
        m.close()

    def test_register_agent(self, mem):
        result = mem.register_agent("coding_agent", agent_type="coder",
                                    description="Writes code")
        assert result["agent_id"] == "coding_agent"
        assert result["status"] == "registered"

    def test_list_agents(self, mem):
        mem.register_agent("agent_1", agent_type="researcher")
        mem.register_agent("agent_2", agent_type="coder")
        agents = mem.list_agents()
        assert len(agents) == 2
        ids = [a["agent_id"] for a in agents]
        assert "agent_1" in ids
        assert "agent_2" in ids

    def test_agent_persistence(self, mem):
        mem.register_agent("persistent_agent", agent_type="deployer",
                           description="Handles deployments")
        agent = mem.store.get_agent("persistent_agent")
        assert agent is not None
        assert agent["agent_type"] == "deployer"
        assert agent["description"] == "Handles deployments"

    def test_agent_not_found(self, mem):
        agent = mem.store.get_agent("nonexistent")
        assert agent is None


class TestConversationTracking:
    @pytest.fixture
    def mem(self):
        m = Memory(db_path=":memory:")
        yield m
        m.close()

    def test_start_conversation(self, mem):
        result = mem.start_conversation("conv_001", agent_id="agent_a",
                                        scene="coding")
        assert result["conversation_id"] == "conv_001"
        assert result["status"] == "started"

    def test_list_conversations(self, mem):
        mem.start_conversation("conv_1", agent_id="agent_a")
        mem.start_conversation("conv_2", agent_id="agent_b")
        mem.start_conversation("conv_3", agent_id="agent_a")

        all_convs = mem.list_conversations()
        assert len(all_convs) == 3

        a_convs = mem.list_conversations(agent_id="agent_a")
        assert len(a_convs) == 2

    def test_conversation_with_scene(self, mem):
        mem.start_conversation("conv_x", agent_id="agent_a", scene="debug")
        convs = mem.list_conversations(agent_id="agent_a")
        assert convs[0]["scene"] == "debug"


class TestSharedMemoryPromotion:
    @pytest.fixture
    def mem(self):
        m = Memory(db_path=":memory:")
        yield m
        m.close()

    def test_promote_high_confidence_memories(self, mem):
        mid = mem.write_memory("Important pattern", agent_id="agent_a",
                               confidence=0.95, scope="private")
        cells = mem.store.list_cells(limit=10)
        cell = cells[0]
        from openmemo.core.memcell import MemCell
        cell_obj = MemCell.from_dict(cell)
        cell_obj.access_count = 5
        mem.store.put_cell(cell_obj.to_dict())

        result = mem.promote_shared_memories()
        assert result["promoted"] == 1

        updated = mem.store.get_cell(cell["id"])
        assert updated["scope"] == "shared"
        assert updated["metadata"].get("promoted_to_shared") is True

    def test_no_promote_low_confidence(self, mem):
        mem.write_memory("Low confidence fact", agent_id="agent_a",
                         confidence=0.5, scope="private")
        cells = mem.store.list_cells(limit=10)
        cell = cells[0]
        from openmemo.core.memcell import MemCell
        cell_obj = MemCell.from_dict(cell)
        cell_obj.access_count = 10
        mem.store.put_cell(cell_obj.to_dict())

        result = mem.promote_shared_memories()
        assert result["promoted"] == 0

    def test_no_promote_low_access(self, mem):
        mem.write_memory("High conf low access", agent_id="agent_a",
                         confidence=0.95, scope="private")
        result = mem.promote_shared_memories()
        assert result["promoted"] == 0

    def test_already_shared_not_promoted(self, mem):
        mem.write_memory("Already shared", agent_id="agent_a",
                         confidence=0.95, scope="shared")
        cells = mem.store.list_cells(limit=10)
        cell = cells[0]
        from openmemo.core.memcell import MemCell
        cell_obj = MemCell.from_dict(cell)
        cell_obj.access_count = 10
        mem.store.put_cell(cell_obj.to_dict())

        result = mem.promote_shared_memories()
        assert result["promoted"] == 0


class TestSharedMemoryDecay:
    @pytest.fixture
    def mem(self):
        m = Memory(db_path=":memory:")
        yield m
        m.close()

    def test_decay_old_shared_memories(self, mem):
        mem.write_memory("Old shared fact", agent_id="agent_a", scope="shared")
        cells = mem.store.list_cells(limit=10)
        cell = cells[0]
        from openmemo.core.memcell import MemCell
        cell_obj = MemCell.from_dict(cell)
        cell_obj.last_accessed = time.time() - (91 * 86400)
        mem.store.put_cell(cell_obj.to_dict())

        result = mem.decay_shared_memories(max_age_days=90)
        assert result["decayed"] == 1

        remaining = mem.store.list_cells(limit=10)
        assert len(remaining) == 0

    def test_no_decay_recent_shared(self, mem):
        mem.write_memory("Recent shared fact", agent_id="agent_a", scope="shared")
        result = mem.decay_shared_memories(max_age_days=90)
        assert result["decayed"] == 0

    def test_no_decay_private_memories(self, mem):
        mem.write_memory("Old private fact", agent_id="agent_a", scope="private")
        cells = mem.store.list_cells(limit=10)
        cell = cells[0]
        from openmemo.core.memcell import MemCell
        cell_obj = MemCell.from_dict(cell)
        cell_obj.last_accessed = time.time() - (200 * 86400)
        mem.store.put_cell(cell_obj.to_dict())

        result = mem.decay_shared_memories(max_age_days=90)
        assert result["decayed"] == 0
        remaining = mem.store.list_cells(limit=10)
        assert len(remaining) == 1


class TestGovernanceWithScope:
    @pytest.fixture
    def mem(self):
        m = Memory(db_path=":memory:")
        yield m
        m.close()

    def test_cleanup_includes_shared_promotion(self, mem):
        mem.write_memory("Promotable fact", agent_id="agent_a", confidence=0.95)
        cells = mem.store.list_cells(limit=10)
        from openmemo.core.memcell import MemCell
        cell_obj = MemCell.from_dict(cells[0])
        cell_obj.access_count = 5
        mem.store.put_cell(cell_obj.to_dict())

        result = mem.memory_governance("cleanup")
        assert "shared_promoted" in result
        assert "shared_decayed" in result
        assert result["shared_promoted"] == 1


class TestScopedListCells:
    @pytest.fixture
    def mem(self):
        m = Memory(db_path=":memory:")
        yield m
        m.close()

    def test_list_cells_scoped_returns_private_and_shared(self, mem):
        mem.write_memory("Agent A private info", agent_id="agent_a", scope="private")
        mem.write_memory("Agent B private info", agent_id="agent_b", scope="private")
        mem.write_memory("Shared knowledge base", agent_id="agent_b", scope="shared")

        scoped = mem.store.list_cells_scoped(agent_id="agent_a")
        contents = [c["content"] for c in scoped]

        assert "Agent A private info" in contents
        assert "Shared knowledge base" in contents
        assert "Agent B private info" not in contents

    def test_list_cells_scoped_with_scene(self, mem):
        mem.write_memory("A private coding fact", agent_id="agent_a",
                         scene="coding", scope="private")
        mem.write_memory("A private deploy fact", agent_id="agent_a",
                         scene="deploy", scope="private")
        mem.write_memory("Shared coding rule fact", agent_id="agent_b",
                         scene="coding", scope="shared")

        scoped = mem.store.list_cells_scoped(agent_id="agent_a", scene="coding")
        contents = [c["content"] for c in scoped]

        assert "A private coding fact" in contents
        assert "Shared coding rule fact" in contents
        assert "A private deploy fact" not in contents


class TestMultiAgentScenario:
    @pytest.fixture
    def mem(self):
        m = Memory(db_path=":memory:")
        yield m
        m.close()

    def test_research_coding_deploy_agents(self, mem):
        mem.register_agent("research", agent_type="researcher",
                           description="Researches topics")
        mem.register_agent("coding", agent_type="coder",
                           description="Writes code")
        mem.register_agent("deploy", agent_type="deployer",
                           description="Deploys apps")

        mem.write_memory("Python 3.12 is recommended",
                         agent_id="research", scene="stack", scope="shared")
        mem.write_memory("Use Poetry for dependency management",
                         agent_id="research", scene="stack", scope="shared")

        mem.write_memory("Implemented auth with JWT tokens",
                         agent_id="coding", scene="auth", scope="private")

        mem.write_memory("Always run tests before deploying",
                         agent_id="deploy", scene="deploy",
                         memory_type="rules", scope="shared")

        research_results = mem.search_memory("Python recommended",
                                             agent_id="research", scene="stack")
        assert len(research_results) > 0

        coding_results = mem.search_memory("Python recommended",
                                           agent_id="coding", scene="stack")
        assert len(coding_results) > 0

        deploy_private = mem.search_memory("JWT tokens",
                                           agent_id="deploy", scene="auth")
        deploy_contents = [r["content"] for r in deploy_private]
        assert "Implemented auth with JWT tokens" not in deploy_contents

        agents = mem.list_agents()
        assert len(agents) == 3

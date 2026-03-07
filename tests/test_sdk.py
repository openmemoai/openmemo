import pytest
import os
import tempfile
from openmemo import Memory, MemoryClient


@pytest.fixture
def memory():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    m = Memory(db_path=path)
    yield m
    m.close()
    os.remove(path)


class TestMemorySDK:
    def test_add_returns_id(self, memory):
        note_id = memory.add("test content")
        assert note_id is not None
        assert len(note_id) > 0

    def test_write_alias(self, memory):
        note_id = memory.write("test content via write")
        assert note_id is not None

    def test_memory_client_alias(self):
        assert MemoryClient is Memory

    def test_recall_kv_mode(self, memory):
        memory.write("User prefers dark mode")
        memory.write("Project uses Python 3.11")
        result = memory.recall("dark mode", mode="kv")
        assert "memories" in result
        assert isinstance(result["memories"], list)
        assert any("dark mode" in m for m in result["memories"])

    def test_recall_narrative_mode(self, memory):
        memory.write("Python is great")
        memory.write("JavaScript is popular")
        result = memory.recall("programming languages", mode="narrative")
        assert "memory_story" in result
        assert "sources" in result
        assert "confidence" in result
        assert isinstance(result["memory_story"], str)

    def test_recall_default_is_kv(self, memory):
        memory.write("test content")
        result = memory.recall("test")
        assert "memories" in result

    def test_recall_with_limit(self, memory):
        for i in range(5):
            memory.write(f"Memory item {i} about coding")
        result = memory.recall("coding", limit=2)
        assert len(result["memories"]) <= 2

    def test_recall_raw(self, memory):
        memory.write("test content")
        results = memory.recall_raw("test")
        assert isinstance(results, list)
        if results:
            r = results[0]
            assert "content" in r
            assert "score" in r
            assert "source" in r
            assert "cell_id" in r

    def test_context(self, memory):
        memory.write("User prefers dark mode", agent_id="a1", scene="prefs")
        memory.write("Deploy on AWS", agent_id="a1", scene="infra")
        context = memory.context("user preference", agent_id="a1", limit=3)
        assert isinstance(context, list)
        assert all(isinstance(c, str) for c in context)

    def test_reconstruct(self, memory):
        memory.write("Python is great")
        memory.write("JavaScript is popular")
        result = memory.reconstruct("programming languages")
        assert "query" in result
        assert "narrative" in result
        assert "sources" in result
        assert "confidence" in result

    def test_maintain(self, memory):
        for i in range(10):
            memory.write(f"Memory entry {i}")
        result = memory.maintain()
        assert "pyramid" in result
        assert "total_cells" in result
        assert result["total_cells"] == 10

    def test_stats(self, memory):
        memory.write("one")
        memory.write("two")
        stats = memory.stats()
        assert stats["notes"] == 2
        assert stats["cells"] == 2
        assert "stages" in stats

    def test_context_manager(self):
        fd, path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        with Memory(db_path=path) as m:
            m.write("context manager test")
            stats = m.stats()
            assert stats["notes"] == 1
        os.remove(path)

    def test_conflict_detection(self, memory):
        memory.write("User prefers dark mode")
        memory.write("User dislikes dark mode")
        stats = memory.stats()
        assert stats["unresolved_conflicts"] >= 1

    def test_with_vector_store(self):
        fd, path = tempfile.mkstemp(suffix=".db")
        os.close(fd)

        def simple_embed(text):
            words = text.lower().split()
            return [1.0 if "python" in words else 0.0,
                    1.0 if "java" in words else 0.0,
                    1.0 if "rust" in words else 0.0]

        m = Memory(db_path=path, embed_fn=simple_embed)
        m.write("Python is great")
        m.write("Java is popular")
        result = m.recall("Python programming")
        assert len(result["memories"]) > 0
        m.close()
        os.remove(path)

    def test_add_with_agent_id(self, memory):
        memory.write("fact for agent A", agent_id="agent_a")
        memory.write("fact for agent B", agent_id="agent_b")
        result = memory.recall("fact", agent_id="agent_a")
        assert len(result["memories"]) >= 1

    def test_add_with_scene(self, memory):
        memory.write("coding preference", agent_id="a1", scene="coding")
        memory.write("food preference", agent_id="a1", scene="personal")
        result = memory.recall("preference", agent_id="a1", scene="coding")
        assert len(result["memories"]) >= 1

    def test_add_with_cell_type(self, memory):
        memory.write("user prefers Python", cell_type="preference")
        memory.write("must use HTTPS", cell_type="constraint")
        memory.write("chose Flask over Django", cell_type="decision")
        stats = memory.stats()
        assert stats["cells"] == 3

    def test_scenes_returns_names(self, memory):
        memory.write("item 1", agent_id="a1", scene="work")
        memory.write("item 2", agent_id="a1", scene="personal")
        scenes = memory.scenes(agent_id="a1")
        assert isinstance(scenes, list)
        assert len(scenes) == 2
        assert "work" in scenes
        assert "personal" in scenes

    def test_scenes_detail(self, memory):
        memory.write("item 1", agent_id="a1", scene="work")
        scenes = memory.scenes_detail(agent_id="a1")
        assert isinstance(scenes, list)
        assert len(scenes) == 1
        assert "title" in scenes[0]
        assert "cell_ids" in scenes[0]

    def test_delete(self, memory):
        memory.write("to be deleted")
        cells = memory.store.list_cells()
        cell_id = cells[0]["id"]
        deleted = memory.delete(cell_id)
        assert deleted is True

    def test_search(self, memory):
        memory.write("Python is great for ML")
        memory.write("JavaScript for web")
        results = memory.search("Python")
        assert isinstance(results, list)
        if results:
            assert "content" in results[0]
            assert "score" in results[0]
            assert "cell_id" in results[0]

    def test_search_with_limit(self, memory):
        for i in range(5):
            memory.write(f"Item {i} about testing")
        results = memory.search("testing", limit=2)
        assert len(results) <= 2

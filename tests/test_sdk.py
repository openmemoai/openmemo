import pytest
import os
import tempfile
from openmemo import Memory


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

    def test_add_and_recall(self, memory):
        memory.add("User prefers dark mode")
        memory.add("Project uses Python 3.11")
        results = memory.recall("dark mode")
        assert len(results) > 0
        assert any("dark mode" in r["content"] for r in results)

    def test_recall_returns_dicts(self, memory):
        memory.add("test content")
        results = memory.recall("test")
        assert isinstance(results, list)
        if results:
            r = results[0]
            assert "content" in r
            assert "score" in r
            assert "source" in r
            assert "cell_id" in r

    def test_reconstruct(self, memory):
        memory.add("Python is great")
        memory.add("JavaScript is popular")
        result = memory.reconstruct("programming languages")
        assert "query" in result
        assert "narrative" in result
        assert "sources" in result
        assert "confidence" in result

    def test_maintain(self, memory):
        for i in range(10):
            memory.add(f"Memory entry {i}")
        result = memory.maintain()
        assert "pyramid" in result
        assert "total_cells" in result
        assert result["total_cells"] == 10

    def test_stats(self, memory):
        memory.add("one")
        memory.add("two")
        stats = memory.stats()
        assert stats["notes"] == 2
        assert stats["cells"] == 2
        assert "stages" in stats

    def test_context_manager(self):
        fd, path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        with Memory(db_path=path) as m:
            m.add("context manager test")
            stats = m.stats()
            assert stats["notes"] == 1
        os.remove(path)

    def test_conflict_detection(self, memory):
        memory.add("User prefers dark mode")
        memory.add("User dislikes dark mode")
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
        m.add("Python is great")
        m.add("Java is popular")
        results = m.recall("Python programming")
        assert len(results) > 0
        m.close()
        os.remove(path)

import pytest
import os
import tempfile
from openmemo.storage.sqlite_store import SQLiteStore


@pytest.fixture
def store():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    s = SQLiteStore(db_path=path)
    yield s
    s.close()
    os.remove(path)


class TestSQLiteStore:
    def test_put_and_get_note(self, store):
        store.put_note({"id": "n1", "content": "hello", "source": "test", "timestamp": 1.0, "metadata": {}})
        note = store.get_note("n1")
        assert note is not None
        assert note["content"] == "hello"

    def test_list_notes(self, store):
        store.put_note({"id": "n1", "content": "a", "source": "test", "timestamp": 1.0, "metadata": {}})
        store.put_note({"id": "n2", "content": "b", "source": "test", "timestamp": 2.0, "metadata": {}})
        notes = store.list_notes()
        assert len(notes) == 2

    def test_delete_note(self, store):
        store.put_note({"id": "n1", "content": "del", "source": "test", "timestamp": 1.0, "metadata": {}})
        assert store.delete_note("n1") is True
        assert store.get_note("n1") is None
        assert store.delete_note("nonexistent") is False

    def test_put_and_get_cell(self, store):
        store.put_cell({
            "id": "c1", "note_id": "n1", "content": "cell content",
            "facts": [], "stage": "exploration", "importance": 0.5,
            "access_count": 0, "last_accessed": 1.0, "created_at": 1.0,
            "connections": [], "metadata": {}
        })
        cell = store.get_cell("c1")
        assert cell is not None
        assert cell["content"] == "cell content"

    def test_list_cells(self, store):
        for i in range(5):
            store.put_cell({
                "id": f"c{i}", "note_id": "", "content": f"cell {i}",
                "facts": [], "stage": "exploration", "importance": 0.5,
                "access_count": 0, "last_accessed": 1.0, "created_at": float(i),
                "connections": [], "metadata": {}
            })
        cells = store.list_cells(limit=3)
        assert len(cells) == 3

    def test_put_and_get_scene(self, store):
        store.put_scene({
            "id": "s1", "title": "Scene 1", "summary": "",
            "cell_ids": ["c1", "c2"], "theme": "test",
            "created_at": 1.0, "updated_at": 1.0, "metadata": {}
        })
        scene = store.get_scene("s1")
        assert scene is not None
        assert scene["title"] == "Scene 1"
        assert len(scene["cell_ids"]) == 2

    def test_put_and_list_skills(self, store):
        store.put_skill({
            "id": "sk1", "name": "test skill", "description": "desc",
            "pattern": "test", "usage_count": 5, "success_rate": 0.8,
            "created_at": 1.0, "metadata": {}
        })
        skills = store.list_skills()
        assert len(skills) == 1
        assert skills[0]["name"] == "test skill"

    def test_upsert_note(self, store):
        store.put_note({"id": "n1", "content": "v1", "source": "test", "timestamp": 1.0, "metadata": {}})
        store.put_note({"id": "n1", "content": "v2", "source": "test", "timestamp": 2.0, "metadata": {}})
        note = store.get_note("n1")
        assert note["content"] == "v2"

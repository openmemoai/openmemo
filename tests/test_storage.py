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
            "cell_type": "fact",
            "facts": [], "stage": "exploration", "importance": 0.5,
            "access_count": 0, "last_accessed": 1.0, "created_at": 1.0,
            "agent_id": "", "scene": "",
            "connections": [], "metadata": {}
        })
        cell = store.get_cell("c1")
        assert cell is not None
        assert cell["content"] == "cell content"
        assert cell["cell_type"] == "fact"

    def test_list_cells(self, store):
        for i in range(5):
            store.put_cell({
                "id": f"c{i}", "note_id": "", "content": f"cell {i}",
                "cell_type": "fact",
                "facts": [], "stage": "exploration", "importance": 0.5,
                "access_count": 0, "last_accessed": 1.0, "created_at": float(i),
                "agent_id": "", "scene": "",
                "connections": [], "metadata": {}
            })
        cells = store.list_cells(limit=3)
        assert len(cells) == 3

    def test_list_cells_by_agent_id(self, store):
        store.put_cell({
            "id": "c1", "note_id": "", "content": "agent A cell",
            "cell_type": "fact", "facts": [], "stage": "exploration",
            "importance": 0.5, "access_count": 0, "last_accessed": 1.0,
            "created_at": 1.0, "agent_id": "agent_a", "scene": "",
            "connections": [], "metadata": {}
        })
        store.put_cell({
            "id": "c2", "note_id": "", "content": "agent B cell",
            "cell_type": "fact", "facts": [], "stage": "exploration",
            "importance": 0.5, "access_count": 0, "last_accessed": 1.0,
            "created_at": 1.0, "agent_id": "agent_b", "scene": "",
            "connections": [], "metadata": {}
        })
        cells_a = store.list_cells(agent_id="agent_a")
        assert len(cells_a) == 1
        assert cells_a[0]["content"] == "agent A cell"

    def test_list_cells_by_scene(self, store):
        store.put_cell({
            "id": "c1", "note_id": "", "content": "coding cell",
            "cell_type": "fact", "facts": [], "stage": "exploration",
            "importance": 0.5, "access_count": 0, "last_accessed": 1.0,
            "created_at": 1.0, "agent_id": "", "scene": "coding",
            "connections": [], "metadata": {}
        })
        store.put_cell({
            "id": "c2", "note_id": "", "content": "personal cell",
            "cell_type": "fact", "facts": [], "stage": "exploration",
            "importance": 0.5, "access_count": 0, "last_accessed": 1.0,
            "created_at": 1.0, "agent_id": "", "scene": "personal",
            "connections": [], "metadata": {}
        })
        cells = store.list_cells(scene="coding")
        assert len(cells) == 1
        assert cells[0]["content"] == "coding cell"

    def test_delete_cell(self, store):
        store.put_cell({
            "id": "c1", "note_id": "", "content": "to delete",
            "cell_type": "fact", "facts": [], "stage": "exploration",
            "importance": 0.5, "access_count": 0, "last_accessed": 1.0,
            "created_at": 1.0, "agent_id": "", "scene": "",
            "connections": [], "metadata": {}
        })
        assert store.delete_cell("c1") is True
        assert store.get_cell("c1") is None
        assert store.delete_cell("nonexistent") is False

    def test_put_and_get_scene(self, store):
        store.put_scene({
            "id": "s1", "title": "Scene 1", "summary": "",
            "cell_ids": ["c1", "c2"], "theme": "test",
            "agent_id": "", "created_at": 1.0, "updated_at": 1.0, "metadata": {}
        })
        scene = store.get_scene("s1")
        assert scene is not None
        assert scene["title"] == "Scene 1"
        assert len(scene["cell_ids"]) == 2

    def test_list_scenes_by_agent_id(self, store):
        store.put_scene({
            "id": "s1", "title": "Agent A Scene", "summary": "",
            "cell_ids": [], "theme": "", "agent_id": "agent_a",
            "created_at": 1.0, "updated_at": 1.0, "metadata": {}
        })
        store.put_scene({
            "id": "s2", "title": "Agent B Scene", "summary": "",
            "cell_ids": [], "theme": "", "agent_id": "agent_b",
            "created_at": 1.0, "updated_at": 1.0, "metadata": {}
        })
        scenes = store.list_scenes(agent_id="agent_a")
        assert len(scenes) == 1
        assert scenes[0]["title"] == "Agent A Scene"

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

    def test_note_with_agent_id(self, store):
        store.put_note({
            "id": "n1", "content": "hello", "source": "test",
            "agent_id": "a1", "scene": "s1",
            "timestamp": 1.0, "metadata": {}
        })
        note = store.get_note("n1")
        assert note["agent_id"] == "a1"
        assert note["scene"] == "s1"

    def test_list_notes_by_agent_id(self, store):
        store.put_note({"id": "n1", "content": "a", "source": "test",
                        "agent_id": "a1", "timestamp": 1.0, "metadata": {}})
        store.put_note({"id": "n2", "content": "b", "source": "test",
                        "agent_id": "a2", "timestamp": 2.0, "metadata": {}})
        notes = store.list_notes(agent_id="a1")
        assert len(notes) == 1

    def test_cell_type_stored(self, store):
        store.put_cell({
            "id": "c1", "note_id": "", "content": "preference",
            "cell_type": "preference",
            "facts": [], "stage": "exploration", "importance": 0.5,
            "access_count": 0, "last_accessed": 1.0, "created_at": 1.0,
            "agent_id": "", "scene": "",
            "connections": [], "metadata": {}
        })
        cell = store.get_cell("c1")
        assert cell["cell_type"] == "preference"

import pytest
import time
from openmemo.core.memory import Note, AtomicFact
from openmemo.core.memcell import MemCell, LifecycleStage
from openmemo.core.scene import MemScene


class TestNote:
    def test_create_note(self):
        note = Note(content="test content")
        assert note.content == "test content"
        assert note.source == "manual"
        assert note.id != ""

    def test_to_dict(self):
        note = Note(content="hello", source="api")
        d = note.to_dict()
        assert d["content"] == "hello"
        assert d["source"] == "api"

    def test_from_dict(self):
        d = {"content": "world", "source": "test", "id": "abc"}
        note = Note.from_dict(d)
        assert note.content == "world"
        assert note.id == "abc"


class TestAtomicFact:
    def test_create(self):
        fact = AtomicFact(content="User likes Python", fact_type="preference")
        assert fact.content == "User likes Python"
        assert fact.fact_type == "preference"
        assert fact.confidence == 1.0

    def test_to_dict(self):
        fact = AtomicFact(content="test", note_id="n1")
        d = fact.to_dict()
        assert d["note_id"] == "n1"


class TestMemCell:
    def test_create(self):
        cell = MemCell(content="test memory")
        assert cell.stage == LifecycleStage.EXPLORATION
        assert cell.importance == 0.5
        assert cell.access_count == 0

    def test_access_updates_count(self):
        cell = MemCell(content="test")
        cell.access()
        assert cell.access_count == 1

    def test_lifecycle_transitions(self):
        cell = MemCell(content="test", importance=0.8)
        for _ in range(3):
            cell.access()
        assert cell.stage == LifecycleStage.CONSOLIDATION

        for _ in range(7):
            cell.access()
        assert cell.stage == LifecycleStage.MASTERY

    def test_to_dict_and_from_dict(self):
        cell = MemCell(content="roundtrip", importance=0.9)
        cell.access()
        d = cell.to_dict()
        restored = MemCell.from_dict(d)
        assert restored.content == "roundtrip"
        assert restored.access_count == 1
        assert restored.importance == 0.9


class TestMemScene:
    def test_create(self):
        scene = MemScene(title="Test Scene")
        assert scene.title == "Test Scene"
        assert scene.cell_ids == []

    def test_add_cell(self):
        scene = MemScene()
        scene.add_cell("cell1")
        scene.add_cell("cell2")
        assert len(scene.cell_ids) == 2
        scene.add_cell("cell1")
        assert len(scene.cell_ids) == 2

    def test_remove_cell(self):
        scene = MemScene()
        scene.add_cell("cell1")
        scene.remove_cell("cell1")
        assert len(scene.cell_ids) == 0

    def test_to_dict_and_from_dict(self):
        scene = MemScene(title="RT", theme="test")
        scene.add_cell("c1")
        d = scene.to_dict()
        restored = MemScene.from_dict(d)
        assert restored.title == "RT"
        assert "c1" in restored.cell_ids

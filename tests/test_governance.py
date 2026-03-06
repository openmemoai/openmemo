import pytest
from openmemo.governance.conflict_detector import ConflictDetector
from openmemo.governance.version_manager import VersionManager


class TestConflictDetector:
    def test_detect_contradiction(self):
        detector = ConflictDetector()
        new_cell = {"id": "c1", "content": "User dislikes dark mode"}
        existing = [{"id": "c2", "content": "User likes dark mode"}]
        conflicts = detector.detect(new_cell, existing)
        assert len(conflicts) >= 1

    def test_no_conflict(self):
        detector = ConflictDetector()
        new_cell = {"id": "c1", "content": "Python is great for data science"}
        existing = [{"id": "c2", "content": "JavaScript is popular for web"}]
        conflicts = detector.detect(new_cell, existing)
        assert len(conflicts) == 0

    def test_resolve_conflict(self):
        detector = ConflictDetector()
        new_cell = {"id": "c1", "content": "User dislikes dark mode"}
        existing = [{"id": "c2", "content": "User likes dark mode"}]
        conflicts = detector.detect(new_cell, existing)
        assert len(conflicts) > 0

        detector.resolve(conflicts[0].id, "User changed preference")
        unresolved = detector.get_unresolved()
        assert len(unresolved) == 0


class TestVersionManager:
    def test_snapshot(self):
        vm = VersionManager()
        cell = {"id": "c1", "content": "v1", "stage": "exploration", "importance": 0.5}
        version = vm.snapshot(cell)
        assert version.cell_id == "c1"
        assert version.version_id == "c1_v1"

    def test_get_history(self):
        vm = VersionManager()
        cell = {"id": "c1", "content": "v1", "stage": "exploration", "importance": 0.5}
        vm.snapshot(cell, change_type="create")
        cell["content"] = "v2"
        vm.snapshot(cell, change_type="update")

        history = vm.get_history("c1")
        assert len(history) == 2
        assert history[0].change_type == "create"
        assert history[1].change_type == "update"

    def test_rollback(self):
        vm = VersionManager()
        cell = {"id": "c1", "content": "original", "stage": "exploration", "importance": 0.5}
        vm.snapshot(cell)
        cell["content"] = "modified"
        vm.snapshot(cell)

        rolled_back = vm.rollback("c1", "c1_v1")
        assert rolled_back is not None
        assert rolled_back["content"] == "original"

    def test_rollback_wrong_cell(self):
        vm = VersionManager()
        cell = {"id": "c1", "content": "test", "stage": "exploration", "importance": 0.5}
        vm.snapshot(cell)

        result = vm.rollback("c2", "c1_v1")
        assert result is None

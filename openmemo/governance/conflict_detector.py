"""
Conflict Detector - Identifies contradictory facts in memory.

Supports pluggable conflict detection strategies.
Detection rules are configurable via GovernanceConfig.
"""

import time
from abc import ABC, abstractmethod
from typing import List, Optional
from dataclasses import dataclass, field


@dataclass
class Conflict:
    id: str = ""
    cell_id_a: str = ""
    cell_id_b: str = ""
    content_a: str = ""
    content_b: str = ""
    conflict_type: str = "contradiction"
    resolved: bool = False
    resolution: str = ""
    detected_at: float = field(default_factory=time.time)


class ConflictStrategy(ABC):
    @abstractmethod
    def is_conflicting(self, text_a: str, text_b: str) -> bool:
        pass


class DefaultConflictStrategy(ConflictStrategy):
    def __init__(self, config=None):
        from openmemo.config import GovernanceConfig
        self._config = config or GovernanceConfig()

    def is_conflicting(self, text_a: str, text_b: str) -> bool:
        words_a = set(text_a.lower().split())
        words_b = set(text_b.lower().split())

        for pos, neg in self._config.conflict_pairs:
            if pos in words_a and neg in words_b:
                shared = (words_a - {pos}) & (words_b - {neg})
                if len(shared) >= self._config.conflict_min_shared_words:
                    return True
            if neg in words_a and pos in words_b:
                shared = (words_a - {neg}) & (words_b - {pos})
                if len(shared) >= self._config.conflict_min_shared_words:
                    return True

        return False


class ConflictDetector:
    def __init__(self, strategy: ConflictStrategy = None, config=None):
        self._strategy = strategy or DefaultConflictStrategy(config=config)
        self._conflicts = []

    def detect(self, new_cell: dict, existing_cells: List[dict]) -> List[Conflict]:
        new_content = new_cell.get("content", "")
        conflicts = []

        for cell in existing_cells:
            existing_content = cell.get("content", "")
            if self._strategy.is_conflicting(new_content, existing_content):
                conflict = Conflict(
                    id=f"conflict_{len(self._conflicts)}",
                    cell_id_a=new_cell.get("id", ""),
                    cell_id_b=cell.get("id", ""),
                    content_a=new_content,
                    content_b=existing_content,
                )
                conflicts.append(conflict)
                self._conflicts.append(conflict)

        return conflicts

    def get_unresolved(self) -> List[Conflict]:
        return [c for c in self._conflicts if not c.resolved]

    def resolve(self, conflict_id: str, resolution: str):
        for c in self._conflicts:
            if c.id == conflict_id:
                c.resolved = True
                c.resolution = resolution
                break

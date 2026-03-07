"""
OpenMemo Configuration - Centralized configuration management.

All tunable parameters are managed through OpenMemoConfig.
This allows the engine behavior to be customized without
modifying source code.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional


@dataclass
class RecallConfig:
    fast_brain_enabled: bool = True
    middle_brain_enabled: bool = True
    merge_boost: float = 1.2
    bm25_k1: float = 1.5
    bm25_b: float = 0.75
    bm25_avg_doc_len: int = 100
    default_top_k: int = 10
    default_budget: int = 2000


@dataclass
class GovernanceConfig:
    conflict_detection_enabled: bool = True
    conflict_min_shared_words: int = 2
    conflict_pairs: list = field(default_factory=lambda: [
        ("prefers", "dislikes"), ("likes", "hates"), ("likes", "dislikes"),
        ("uses", "avoids"), ("always", "never"), ("true", "false"),
        ("yes", "no"), ("enabled", "disabled"), ("on", "off"),
        ("active", "inactive"), ("supports", "opposes"),
    ])


@dataclass
class PyramidConfig:
    short_term_max: int = 50
    mid_term_max: int = 20
    long_term_max: int = 10
    short_term_hours: int = 24
    batch_size: int = 5


@dataclass
class SkillConfig:
    pattern_threshold: int = 3
    auto_extract: bool = True


@dataclass
class OpenMemoConfig:
    recall: RecallConfig = field(default_factory=RecallConfig)
    governance: GovernanceConfig = field(default_factory=GovernanceConfig)
    pyramid: PyramidConfig = field(default_factory=PyramidConfig)
    skill: SkillConfig = field(default_factory=SkillConfig)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OpenMemoConfig":
        config = cls()
        if "recall" in data:
            for k, v in data["recall"].items():
                if hasattr(config.recall, k):
                    setattr(config.recall, k, v)
        if "governance" in data:
            for k, v in data["governance"].items():
                if hasattr(config.governance, k):
                    setattr(config.governance, k, v)
        if "pyramid" in data:
            for k, v in data["pyramid"].items():
                if hasattr(config.pyramid, k):
                    setattr(config.pyramid, k, v)
        if "skill" in data:
            for k, v in data["skill"].items():
                if hasattr(config.skill, k):
                    setattr(config.skill, k, v)
        return config

"""
OpenMemo Protocol - Standard schemas for memory operations.

These schemas define the data contract for OpenMemo's memory interface.
All implementations must conform to these schemas.
"""

import uuid
import time
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field


@dataclass
class MemCellSchema:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    note_id: str = ""
    content: str = ""
    cell_type: str = "fact"
    stage: str = "exploration"
    confidence: float = 1.0
    access_count: int = 0
    agent_id: str = ""
    scene: str = ""
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SceneSchema:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    cell_ids: List[str] = field(default_factory=list)
    agent_id: str = ""
    created_at: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WriteRequest:
    content: str = ""
    source: str = "api"
    agent_id: str = ""
    scene: str = ""
    cell_type: str = "fact"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RecallRequest:
    query: str = ""
    agent_id: str = ""
    scene: str = ""
    top_k: int = 10
    budget: int = 2000


@dataclass
class RecallResultItem:
    cell_id: str = ""
    content: str = ""
    score: float = 0.0
    source: str = "fast"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RecallResponse:
    results: List[RecallResultItem] = field(default_factory=list)


@dataclass
class SearchRequest:
    query: str = ""
    agent_id: str = ""
    top_k: int = 10


@dataclass
class ReconstructRequest:
    query: str = ""
    agent_id: str = ""
    max_sources: int = 10


@dataclass
class ReconstructResponse:
    query: str = ""
    narrative: str = ""
    sources: List[str] = field(default_factory=list)
    confidence: float = 0.0
    conflicts: List[Dict[str, Any]] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)

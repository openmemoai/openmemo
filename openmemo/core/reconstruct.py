"""
Reconstructive Recall - Narrative generation from memory.

Supports pluggable reconstruction strategies.
The default implementation provides basic timeline-based narrative.
"""

import time
from abc import ABC, abstractmethod
from typing import List, Optional
from dataclasses import dataclass, field


@dataclass
class Reconstruction:
    query: str = ""
    narrative: str = ""
    sources: list = field(default_factory=list)
    confidence: float = 0.0
    timestamp: float = field(default_factory=time.time)


class ReconstructStrategy(ABC):
    @abstractmethod
    def build_narrative(self, query: str, segments: List[str], scores: List[float]) -> Reconstruction:
        pass


class DefaultReconstructStrategy(ReconstructStrategy):
    def build_narrative(self, query: str, segments: List[str], scores: List[float]) -> Reconstruction:
        if not segments:
            return Reconstruction(query=query, narrative="No relevant memories found.")

        if len(segments) == 1:
            narrative = segments[0]
        else:
            narrative = "\n\n".join(f"- {s}" for s in segments)

        avg_score = sum(scores) / len(scores) if scores else 0

        return Reconstruction(
            query=query,
            narrative=narrative,
            confidence=min(avg_score, 1.0),
        )


class ReconstructiveRecall:
    def __init__(self, recall_engine=None, store=None, strategy: ReconstructStrategy = None):
        self.recall_engine = recall_engine
        self.store = store
        self._strategy = strategy or DefaultReconstructStrategy()

    def reconstruct(self, query: str, max_sources: int = 10) -> Reconstruction:
        if not self.recall_engine:
            return Reconstruction(query=query, narrative="No recall engine available.")

        results = self.recall_engine.recall(query, top_k=max_sources)

        if not results:
            return Reconstruction(query=query, narrative="No relevant memories found.")

        sorted_results = sorted(
            results,
            key=lambda r: r.metadata.get("timestamp", 0) if r.metadata else 0
        )

        segments = [r.content for r in sorted_results]
        scores = [r.score for r in sorted_results]

        reconstruction = self._strategy.build_narrative(query, segments, scores)
        reconstruction.sources = [r.cell_id for r in sorted_results]

        return reconstruction

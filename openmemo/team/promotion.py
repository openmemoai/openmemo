"""
Team Memory Promotion Worker - Promotes shared task memories to team scope.

Promotion criteria:
  - validated success (confidence > threshold)
  - cross-task reusable (not temporary detail)
  - high confidence
  - not a temporary/intermediate result

Pipeline: shared memory → evaluation → team memory
"""

import time
import logging
from typing import List, Optional, Callable

logger = logging.getLogger("openmemo")

TEMPORARY_TYPES = {"intermediate", "debug_log", "retry", "error_trace"}
PROMOTABLE_TYPES = {"decision", "workflow", "standard", "convention", "policy",
                    "pattern", "playbook", "finding", "validated"}

DEFAULT_CONFIDENCE_THRESHOLD = 0.75
DEFAULT_ACCESS_THRESHOLD = 2
DEFAULT_MIN_AGE_HOURS = 1


class PromotionConfig:
    def __init__(self, confidence_threshold: float = DEFAULT_CONFIDENCE_THRESHOLD,
                 access_threshold: int = DEFAULT_ACCESS_THRESHOLD,
                 min_age_hours: float = DEFAULT_MIN_AGE_HOURS,
                 auto_promote_types: set = None):
        self.confidence_threshold = confidence_threshold
        self.access_threshold = access_threshold
        self.min_age_hours = min_age_hours
        self.auto_promote_types = auto_promote_types or PROMOTABLE_TYPES


class PromotionWorker:
    def __init__(self, store=None, config: PromotionConfig = None,
                 llm_fn: Optional[Callable] = None):
        self.store = store
        self.config = config or PromotionConfig()
        self._llm_fn = llm_fn

    def evaluate_promotion(self, cell: dict) -> bool:
        cell_type = cell.get("cell_type", "")
        if cell_type in TEMPORARY_TYPES:
            return False

        scope = cell.get("scope", "private")
        if scope == "team":
            return False

        confidence = self._get_confidence(cell)
        if confidence < self.config.confidence_threshold:
            return False

        access_count = cell.get("access_count", 0)
        if access_count < self.config.access_threshold:
            if cell_type not in self.config.auto_promote_types:
                return False

        created_at = cell.get("created_at", 0)
        if created_at:
            age_hours = (time.time() - created_at) / 3600
            if age_hours < self.config.min_age_hours:
                return False

        return True

    def promote_to_team(self, team_id: str = "") -> dict:
        if not self.store:
            return {"promoted": 0, "evaluated": 0}

        cells = self.store.list_cells(limit=1000)
        shared_cells = [c for c in cells if c.get("scope") == "shared"]
        if team_id:
            shared_cells = [c for c in shared_cells
                           if not c.get("team_id") or c.get("team_id") == team_id]

        promoted = 0
        evaluated = len(shared_cells)

        for cell in shared_cells:
            if self.evaluate_promotion(cell):
                cell["scope"] = "team"
                if team_id:
                    cell["team_id"] = team_id
                cell["metadata"] = cell.get("metadata", {})
                if isinstance(cell["metadata"], str):
                    import json
                    try:
                        cell["metadata"] = json.loads(cell["metadata"])
                    except Exception:
                        cell["metadata"] = {}
                cell["metadata"]["promoted_at"] = time.time()
                cell["metadata"]["promoted_from"] = "shared"
                self.store.put_cell(cell)
                promoted += 1

        logger.info("[openmemo:team] promotion: evaluated=%d promoted=%d",
                     evaluated, promoted)
        return {"promoted": promoted, "evaluated": evaluated}

    def _get_confidence(self, cell: dict) -> float:
        meta = cell.get("metadata", {})
        if isinstance(meta, str):
            import json
            try:
                meta = json.loads(meta)
            except Exception:
                meta = {}
        return float(meta.get("confidence", cell.get("importance", 0.5)))

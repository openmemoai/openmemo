"""
Team Memory Router - Intelligent scope routing for team memory operations.

Routes memory writes to the correct scope (private/shared/team) based on
content type and context. Handles layered recall with scope weights.
"""

import logging
from typing import List, Optional

logger = logging.getLogger("openmemo")

SCOPE_PRIVATE = "private"
SCOPE_SHARED = "shared"
SCOPE_TEAM = "team"
SCOPE_CONVERSATION = "conversation"

TEAM_TYPES = {"decision", "workflow", "standard", "convention", "policy"}
SHARED_TYPES = {"task_progress", "finding", "blocker", "validated", "rules",
                "playbook", "pattern"}

SCOPE_WEIGHTS = {
    SCOPE_PRIVATE: 1.0,
    SCOPE_CONVERSATION: 0.90,
    SCOPE_SHARED: 0.85,
    SCOPE_TEAM: 0.70,
}


def route_scope(memory_type: str, scope: str = "",
                team_id: str = "", task_id: str = "") -> str:
    if scope:
        return scope

    if memory_type in TEAM_TYPES:
        return SCOPE_TEAM
    if memory_type in SHARED_TYPES:
        return SCOPE_SHARED
    return SCOPE_PRIVATE


def build_namespace(team_id: str = "", task_id: str = "",
                    agent_id: str = "", scope: str = "private") -> str:
    parts = ["openmemo"]
    if team_id:
        parts.append(team_id)
    if task_id:
        parts.append(task_id)
    if agent_id and scope == SCOPE_PRIVATE:
        parts.append(agent_id)
    parts.append(scope)
    return "/".join(parts)


def get_scope_weight(scope: str) -> float:
    return SCOPE_WEIGHTS.get(scope, 0.5)


def apply_scope_weights(results: list, store=None) -> list:
    weighted = []
    for r in results:
        cell = None
        if store and hasattr(r, "cell_id"):
            cell = store.get_cell(r.cell_id)
        elif isinstance(r, dict):
            cell = r

        scope = "private"
        if cell:
            scope = cell.get("scope", "private")

        weight = get_scope_weight(scope)

        if hasattr(r, "score"):
            r.score = r.score * weight
        elif isinstance(r, dict) and "score" in r:
            r["score"] = r["score"] * weight

        weighted.append(r)

    return weighted

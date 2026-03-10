"""
CrewAI Adapter for OpenMemo.

Provides memory backend for CrewAI agent crews.
Supports per-agent memory isolation and shared crew memory via crew_id tagging.

Usage:
    from openmemo.adapters.crewai_adapter import CrewAIMemory
    memory = CrewAIMemory(agent_id="researcher", crew_id="dev_team",
                           default_scene="research")

    memory.write_memory("User prefers academic papers", memory_type="preference")
    context = memory.inject_context("What sources should I use?")
"""

from typing import List, Dict
from openmemo.adapters.base_adapter import BaseMemoryAdapter


class CrewAIMemory(BaseMemoryAdapter):
    adapter_name = "crewai"

    def __init__(self, crew_id: str = "", **kwargs):
        super().__init__(**kwargs)
        self.crew_id = crew_id

    def _crew_metadata(self, extra: dict = None) -> dict:
        metadata = {}
        if self.crew_id:
            metadata["crew_id"] = self.crew_id
        if extra:
            metadata.update(extra)
        return metadata

    def on_task_start(self, task_description: str, scene: str = ""):
        self.write_memory(
            content=f"Task started: {task_description}",
            scene=scene,
            memory_type="observation",
            metadata=self._crew_metadata(),
        )

    def on_task_complete(self, task_description: str, result: str,
                         scene: str = ""):
        content = f"Task completed: {task_description}"
        if result:
            content += f" | Result: {result}"
        self.write_memory(
            content=content,
            scene=scene,
            memory_type="decision",
            confidence=0.9,
            metadata=self._crew_metadata(),
        )

    def on_agent_action(self, agent_role: str, action: str, scene: str = ""):
        self.write_memory(
            content=f"[{agent_role}] {action}",
            scene=scene,
            memory_type="observation",
            metadata=self._crew_metadata({"agent_role": agent_role}),
        )

    def get_crew_context(self, query: str, scene: str = None,
                         limit: int = 5) -> List[str]:
        return self.get_context(query, scene=scene, limit=limit)

    def get_task_memory(self, task_description: str, limit: int = 3) -> List[Dict]:
        return self.recall_memory(query=task_description, limit=limit)

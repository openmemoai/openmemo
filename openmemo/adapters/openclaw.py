"""
OpenClaw Adapter for OpenMemo.

Provides a memory backend for OpenClaw agent sessions.

Usage:
    from openmemo.adapters.openclaw import OpenClawMemoryBackend

    backend = OpenClawMemoryBackend(agent_id="claw_agent")
    backend.write("User prefers Python")
    context = backend.recall("programming language")
"""

from typing import List, Dict
from openmemo.api.sdk import Memory


class OpenClawMemoryBackend:
    """
    OpenClaw memory_backend=openmemo integration.

    Automatically writes session data and recalls
    relevant memory for each interaction.
    """

    def __init__(self, db_path: str = "openmemo.db", agent_id: str = "",
                 memory: Memory = None):
        self._memory = memory or Memory(db_path=db_path)
        self.agent_id = agent_id

    def write(self, content: str, scene: str = "", cell_type: str = "fact") -> str:
        return self._memory.add(
            content=content,
            agent_id=self.agent_id,
            scene=scene,
            cell_type=cell_type,
            source="openclaw",
        )

    def recall(self, query: str, scene: str = "", top_k: int = 10) -> List[Dict]:
        return self._memory.recall(
            query=query,
            agent_id=self.agent_id,
            scene=scene,
            top_k=top_k,
        )

    def search(self, query: str, top_k: int = 10) -> List[Dict]:
        return self._memory.search(
            query=query,
            agent_id=self.agent_id,
            top_k=top_k,
        )

    def get_context(self, query: str, max_tokens: int = 2000) -> str:
        results = self._memory.recall(
            query=query,
            agent_id=self.agent_id,
            budget=max_tokens,
        )
        return "\n".join(r["content"] for r in results)

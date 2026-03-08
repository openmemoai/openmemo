"""
OpenClaw Adapter for OpenMemo.

Provides a memory backend for OpenClaw agent sessions.
Supports both local SDK and remote API modes.

Usage (local):
    from openmemo.adapters.openclaw import OpenClawMemoryBackend
    backend = OpenClawMemoryBackend(agent_id="claw_agent")

Usage (remote):
    from openmemo.adapters.openclaw import OpenClawMemoryBackend
    backend = OpenClawMemoryBackend(
        agent_id="claw_agent",
        base_url="https://api.openmemo.ai",
    )
"""

from typing import List, Dict


class OpenClawMemoryBackend:
    def __init__(self, db_path: str = "openmemo.db", agent_id: str = "",
                 memory=None, base_url: str = None, api_key: str = None):
        self.agent_id = agent_id

        if memory:
            self._memory = memory
        elif base_url:
            from openmemo.api.remote import RemoteMemory
            self._memory = RemoteMemory(base_url=base_url, api_key=api_key)
        else:
            from openmemo.api.sdk import Memory
            self._memory = Memory(db_path=db_path)

    def write_memory(self, content: str, scene: str = "",
                     memory_type: str = "fact", confidence: float = 0.8) -> str:
        return self._memory.write_memory(
            content=content,
            scene=scene,
            memory_type=memory_type,
            confidence=confidence,
            agent_id=self.agent_id,
        )

    def recall_context(self, query: str, scene: str = "",
                       mode: str = "kv", limit: int = 5) -> dict:
        return self._memory.recall_context(
            query=query,
            scene=scene,
            agent_id=self.agent_id,
            mode=mode,
            limit=limit,
        )

    def search_memory(self, query: str, scene: str = "",
                      limit: int = 10) -> List[Dict]:
        return self._memory.search_memory(
            query=query,
            scene=scene,
            agent_id=self.agent_id,
            limit=limit,
        )

    def list_scenes(self) -> List[str]:
        return self._memory.list_scenes(agent_id=self.agent_id)

    def memory_governance(self, operation: str = "cleanup") -> dict:
        return self._memory.memory_governance(operation=operation)

    def write(self, content: str, scene: str = "", cell_type: str = "fact") -> str:
        return self.write_memory(content=content, scene=scene, memory_type=cell_type)

    def recall(self, query: str, scene: str = "", mode: str = "kv",
               limit: int = 10) -> dict:
        return self.recall_context(query=query, scene=scene, mode=mode, limit=limit)

    def search(self, query: str, limit: int = 10) -> List[Dict]:
        return self.search_memory(query=query, limit=limit)

    def get_context(self, query: str, scene: str = "", limit: int = 3) -> List[str]:
        result = self.recall_context(query=query, scene=scene, limit=limit)
        return result.get("context", [])

    def close(self):
        if hasattr(self._memory, 'close'):
            self._memory.close()

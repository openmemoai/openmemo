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
    """
    OpenClaw memory_backend=openmemo integration.

    Supports two modes:
    - Local: Uses embedded SQLite via Memory SDK (default)
    - Remote: Calls OpenMemo REST API via RemoteMemory

    Args:
        db_path: Local database path (local mode only). Default: "openmemo.db"
        agent_id: Agent identifier for memory isolation.
        memory: Pre-configured Memory or RemoteMemory instance.
        base_url: Remote API URL. If provided, uses remote mode.
        api_key: API key for remote authentication (future use).
    """

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

    def write(self, content: str, scene: str = "", cell_type: str = "fact") -> str:
        return self._memory.write(
            content=content,
            agent_id=self.agent_id,
            scene=scene,
            cell_type=cell_type,
            source="openclaw",
        )

    def recall(self, query: str, scene: str = "", mode: str = "kv",
               limit: int = 10) -> dict:
        return self._memory.recall(
            query=query,
            agent_id=self.agent_id,
            scene=scene,
            mode=mode,
            limit=limit,
        )

    def search(self, query: str, limit: int = 10) -> List[Dict]:
        return self._memory.search(
            query=query,
            agent_id=self.agent_id,
            limit=limit,
        )

    def get_context(self, query: str, scene: str = "", limit: int = 3) -> List[str]:
        return self._memory.context(
            query=query,
            agent_id=self.agent_id,
            scene=scene,
            limit=limit,
        )

    def close(self):
        if hasattr(self._memory, 'close'):
            self._memory.close()

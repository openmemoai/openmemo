"""
LangChain Adapter for OpenMemo.

Provides OpenMemoMemory() that works as a LangChain
BaseMemory compatible memory backend.

Supports both local SDK and remote API modes.

Usage (local):
    from openmemo.adapters.langchain import OpenMemoMemory
    memory = OpenMemoMemory(agent_id="my_agent")

Usage (remote):
    from openmemo.adapters.langchain import OpenMemoMemory
    memory = OpenMemoMemory(
        agent_id="my_agent",
        base_url="https://api.openmemo.ai",
    )
"""

from typing import Any, Dict, List


class OpenMemoMemory:
    """
    LangChain-compatible memory backend powered by OpenMemo.

    Args:
        db_path: Local database path (local mode only). Default: "openmemo.db"
        agent_id: Agent identifier for memory isolation.
        memory: Pre-configured Memory or RemoteMemory instance.
        memory_key: Key used in LangChain memory variables. Default: "history"
        base_url: Remote API URL. If provided, uses remote mode.
        api_key: API key for remote authentication (future use).
    """

    memory_key: str = "history"

    def __init__(self, db_path: str = "openmemo.db", agent_id: str = "",
                 memory=None, memory_key: str = "history",
                 base_url: str = None, api_key: str = None):
        self.agent_id = agent_id
        self.memory_key = memory_key

        if memory:
            self._memory = memory
        elif base_url:
            from openmemo.api.remote import RemoteMemory
            self._memory = RemoteMemory(base_url=base_url, api_key=api_key)
        else:
            from openmemo.api.sdk import Memory
            self._memory = Memory(db_path=db_path)

    @property
    def memory_variables(self) -> List[str]:
        return [self.memory_key]

    def load_memory_variables(self, inputs: Dict[str, Any]) -> Dict[str, str]:
        query = inputs.get("input", "")
        if not query:
            return {self.memory_key: ""}

        context = self._memory.context(
            query=query,
            agent_id=self.agent_id,
            limit=5,
        )

        if not context:
            return {self.memory_key: ""}

        return {self.memory_key: "\n".join(context)}

    def save_context(self, inputs: Dict[str, Any], outputs: Dict[str, str]) -> None:
        user_input = inputs.get("input", "")
        ai_output = outputs.get("output", "")

        if user_input:
            self._memory.write(
                content=f"User: {user_input}",
                agent_id=self.agent_id,
                scene="conversation",
                cell_type="observation",
            )

        if ai_output:
            self._memory.write(
                content=f"Assistant: {ai_output}",
                agent_id=self.agent_id,
                scene="conversation",
                cell_type="observation",
            )

    def clear(self) -> None:
        pass

    def close(self):
        if hasattr(self._memory, 'close'):
            self._memory.close()

"""
LangChain Adapter for OpenMemo.

Provides OpenMemoMemory() that works as a LangChain
BaseMemory compatible memory backend.

Usage:
    from openmemo.adapters.langchain import OpenMemoMemory

    memory = OpenMemoMemory(agent_id="my_agent")
    memory.save_context({"input": "hello"}, {"output": "hi"})
    history = memory.load_memory_variables({"input": "greeting"})
"""

from typing import Any, Dict, List
from openmemo.api.sdk import Memory


class OpenMemoMemory:
    """
    LangChain-compatible memory backend powered by OpenMemo.

    Stores conversation context as memories and retrieves
    relevant context on each interaction.
    """

    memory_key: str = "history"

    def __init__(self, db_path: str = "openmemo.db", agent_id: str = "",
                 memory: Memory = None, memory_key: str = "history"):
        self._memory = memory or Memory(db_path=db_path)
        self.agent_id = agent_id
        self.memory_key = memory_key

    @property
    def memory_variables(self) -> List[str]:
        return [self.memory_key]

    def load_memory_variables(self, inputs: Dict[str, Any]) -> Dict[str, str]:
        query = inputs.get("input", "")
        if not query:
            return {self.memory_key: ""}

        results = self._memory.recall(
            query=query,
            agent_id=self.agent_id,
            top_k=5,
        )

        if not results:
            return {self.memory_key: ""}

        context = "\n".join(r["content"] for r in results)
        return {self.memory_key: context}

    def save_context(self, inputs: Dict[str, Any], outputs: Dict[str, str]) -> None:
        user_input = inputs.get("input", "")
        ai_output = outputs.get("output", "")

        if user_input:
            self._memory.add(
                content=f"User: {user_input}",
                agent_id=self.agent_id,
                scene="conversation",
                cell_type="observation",
            )

        if ai_output:
            self._memory.add(
                content=f"Assistant: {ai_output}",
                agent_id=self.agent_id,
                scene="conversation",
                cell_type="observation",
            )

    def clear(self) -> None:
        pass

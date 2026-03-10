"""
AutoGen Adapter for OpenMemo.

Provides memory backend for Microsoft AutoGen multi-agent conversations.
Supports per-agent memory and shared group-chat memory.

Usage:
    from openmemo.adapters.autogen_adapter import AutoGenMemory
    memory = AutoGenMemory(agent_id="assistant", default_scene="coding")

    memory.on_message("user_proxy", "Please write a sort function")
    memory.on_reply("assistant", "Here is a quicksort implementation...")
    context = memory.inject_context("How should I optimize the sort?")
"""

from typing import List, Dict
from openmemo.adapters.base_adapter import BaseMemoryAdapter


class AutoGenMemory(BaseMemoryAdapter):
    adapter_name = "autogen"

    def __init__(self, group_id: str = "", **kwargs):
        super().__init__(**kwargs)
        self.group_id = group_id

    def on_message(self, sender: str, content: str, scene: str = None):
        metadata = {"sender": sender}
        if self.group_id:
            metadata["group_id"] = self.group_id
        self.write_memory(
            content=f"[{sender}] {content}",
            scene=scene,
            memory_type="observation",
            metadata=metadata,
        )

    def on_reply(self, agent_name: str, content: str, scene: str = None):
        metadata = {"sender": agent_name, "role": "assistant"}
        if self.group_id:
            metadata["group_id"] = self.group_id
        self.write_memory(
            content=f"[{agent_name}] {content}",
            scene=scene,
            memory_type="observation",
            metadata=metadata,
        )

    def on_tool_call(self, agent_name: str, tool_name: str,
                     result: str, scene: str = None):
        metadata = {"sender": agent_name, "tool": tool_name}
        if self.group_id:
            metadata["group_id"] = self.group_id
        self.write_memory(
            content=f"[{agent_name}] tool:{tool_name} → {result}",
            scene=scene,
            memory_type="decision",
            confidence=0.9,
            metadata=metadata,
        )

    def on_task_complete(self, task: str, result: str, scene: str = None):
        metadata = {}
        if self.group_id:
            metadata["group_id"] = self.group_id
        content = f"Task completed: {task}"
        if result:
            content += f" | Result: {result}"
        self.write_memory(
            content=content,
            scene=scene,
            memory_type="decision",
            confidence=0.9,
            metadata=metadata,
        )

    def get_conversation_context(self, query: str, scene: str = None,
                                  limit: int = 5) -> List[str]:
        return self.get_context(query, scene=scene, limit=limit)

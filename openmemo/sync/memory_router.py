"""
Hybrid Memory Router — decides where memory operations go.

Supports three modes:
  - local:  All operations use local store only
  - cloud:  All operations use cloud store only
  - hybrid: Read local first, write local + async sync to cloud
"""

import logging
from typing import List, Optional

logger = logging.getLogger("openmemo")

MEMORY_MODES = ("local", "cloud", "hybrid")


class MemoryRouter:
    def __init__(self, mode: str = "local", local_store=None,
                 cloud_store=None, sync_engine=None):
        if mode not in MEMORY_MODES:
            raise ValueError(f"Invalid memory mode: {mode}. Must be one of {MEMORY_MODES}")

        self.mode = mode
        self.local_store = local_store
        self.cloud_store = cloud_store
        self.sync_engine = sync_engine

        if mode == "cloud" and not cloud_store:
            raise ValueError("Cloud mode requires a cloud_store")
        if mode == "hybrid" and (not local_store or not cloud_store):
            raise ValueError("Hybrid mode requires both local_store and cloud_store")
        if mode == "local" and not local_store:
            raise ValueError("Local mode requires a local_store")

    @property
    def read_store(self):
        if self.mode == "cloud":
            return self.cloud_store
        return self.local_store

    @property
    def write_store(self):
        if self.mode == "cloud":
            return self.cloud_store
        return self.local_store

    def put_note(self, note: dict) -> str:
        result = self.write_store.put_note(note)
        self._queue_sync("put_note", note)
        return result

    def get_note(self, note_id: str) -> Optional[dict]:
        result = self.read_store.get_note(note_id)
        if result is None and self.mode == "hybrid":
            result = self.cloud_store.get_note(note_id)
        return result

    def list_notes(self, limit: int = 100, offset: int = 0,
                   agent_id: str = None) -> List[dict]:
        return self.read_store.list_notes(limit=limit, offset=offset,
                                          agent_id=agent_id)

    def delete_note(self, note_id: str) -> bool:
        result = self.write_store.delete_note(note_id)
        self._queue_sync("delete_note", {"id": note_id})
        return result

    def put_cell(self, cell: dict) -> str:
        result = self.write_store.put_cell(cell)
        self._queue_sync("put_cell", cell)
        return result

    def get_cell(self, cell_id: str) -> Optional[dict]:
        result = self.read_store.get_cell(cell_id)
        if result is None and self.mode == "hybrid":
            result = self.cloud_store.get_cell(cell_id)
        return result

    def list_cells(self, limit: int = 100, offset: int = 0,
                   agent_id: str = None, scene: str = None) -> List[dict]:
        return self.read_store.list_cells(limit=limit, offset=offset,
                                          agent_id=agent_id, scene=scene)

    def list_cells_scoped(self, agent_id: str = None, conversation_id: str = None,
                          scene: str = None, limit: int = 100) -> List[dict]:
        return self.read_store.list_cells_scoped(
            agent_id=agent_id, conversation_id=conversation_id,
            scene=scene, limit=limit,
        )

    def delete_cell(self, cell_id: str) -> bool:
        result = self.write_store.delete_cell(cell_id)
        self._queue_sync("delete_cell", {"id": cell_id})
        return result

    def put_scene(self, scene: dict) -> str:
        result = self.write_store.put_scene(scene)
        self._queue_sync("put_scene", scene)
        return result

    def get_scene(self, scene_id: str) -> Optional[dict]:
        return self.read_store.get_scene(scene_id)

    def list_scenes(self, limit: int = 100, offset: int = 0,
                    agent_id: str = None) -> List[dict]:
        return self.read_store.list_scenes(limit=limit, offset=offset,
                                           agent_id=agent_id)

    def put_skill(self, skill: dict) -> str:
        result = self.write_store.put_skill(skill)
        self._queue_sync("put_skill", skill)
        return result

    def get_skill(self, skill_id: str) -> Optional[dict]:
        return self.read_store.get_skill(skill_id)

    def list_skills(self, scene: str = "", status: str = "") -> List[dict]:
        return self.read_store.list_skills(scene=scene, status=status)

    def delete_skill(self, skill_id: str) -> bool:
        result = self.write_store.delete_skill(skill_id)
        self._queue_sync("delete_skill", {"id": skill_id})
        return result

    def put_skill_feedback(self, feedback: dict) -> str:
        return self.write_store.put_skill_feedback(feedback)

    def list_skill_feedback(self, skill_id: str = "") -> List[dict]:
        return self.read_store.list_skill_feedback(skill_id)

    def put_agent(self, agent: dict) -> str:
        result = self.write_store.put_agent(agent)
        self._queue_sync("put_agent", agent)
        return result

    def get_agent(self, agent_id: str) -> Optional[dict]:
        return self.read_store.get_agent(agent_id)

    def list_agents(self) -> List[dict]:
        return self.read_store.list_agents()

    def delete_agent(self, agent_id: str) -> bool:
        result = self.write_store.delete_agent(agent_id)
        self._queue_sync("delete_agent", {"agent_id": agent_id})
        return result

    def put_conversation(self, conversation: dict) -> str:
        result = self.write_store.put_conversation(conversation)
        return result

    def list_conversations(self, agent_id: str = None) -> List[dict]:
        return self.read_store.list_conversations(agent_id=agent_id)

    def put_edge(self, edge: dict) -> str:
        result = self.write_store.put_edge(edge)
        self._queue_sync("put_edge", edge)
        return result

    def get_edges(self, memory_id: str) -> List[dict]:
        return self.read_store.get_edges(memory_id)

    def delete_edge(self, edge_id: str) -> bool:
        result = self.write_store.delete_edge(edge_id)
        self._queue_sync("delete_edge", {"edge_id": edge_id})
        return result

    def list_edges(self, limit: int = 100) -> List[dict]:
        return self.read_store.list_edges(limit=limit)

    def close(self):
        if self.local_store:
            self.local_store.close()
        if self.cloud_store and self.cloud_store != self.local_store:
            self.cloud_store.close()

    def _queue_sync(self, operation: str, data: dict):
        if self.mode == "hybrid" and self.sync_engine:
            try:
                self.sync_engine.queue_sync(operation, data)
            except Exception as e:
                logger.warning("[openmemo:router] sync queue failed: %s", e)

    def get_mode(self) -> str:
        return self.mode

    def get_status(self) -> dict:
        status = {
            "mode": self.mode,
            "local_available": self.local_store is not None,
            "cloud_available": self.cloud_store is not None,
            "sync_enabled": self.sync_engine is not None,
        }
        if self.sync_engine:
            status["sync_status"] = self.sync_engine.get_status()
        return status

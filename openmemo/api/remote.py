"""
OpenMemo Remote Client — HTTP-based Memory Core API v1.0

Connects to a remote OpenMemo server (e.g., api.openmemo.ai)
instead of using a local database.

Usage:
    from openmemo import RemoteMemory

    mem = RemoteMemory(base_url="https://api.openmemo.ai")
    mem.write_memory("User prefers Python", scene="coding", memory_type="preference")
    result = mem.recall_context("language preference", scene="coding")
    print(result)  # {"context": ["User prefers Python"]}

Install with:
    pip install openmemo[remote]
"""

from typing import List

try:
    import requests
except ImportError:
    requests = None

DEFAULT_BASE_URL = "https://api.openmemo.ai"


class RemoteMemory:
    """
    HTTP client for OpenMemo REST API.

    Provides the same 5 core APIs as the local SDK but
    calls a remote server over HTTP.

    Args:
        base_url: Server URL. Default: https://api.openmemo.ai
        api_key: Optional API key for authentication (future use).
        timeout: Request timeout in seconds. Default: 30.
    """

    def __init__(self, base_url: str = None, api_key: str = None,
                 timeout: int = 30):
        if requests is None:
            raise ImportError(
                "Install remote dependencies: pip install openmemo[remote]"
            )
        self.base_url = (base_url or DEFAULT_BASE_URL).rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self._session = requests.Session()
        self._session.headers["Content-Type"] = "application/json"
        if api_key:
            self._session.headers["Authorization"] = f"Bearer {api_key}"

    def _post(self, path: str, data: dict) -> dict:
        url = f"{self.base_url}{path}"
        resp = self._session.post(url, json=data, timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()

    def _get(self, path: str, params: dict = None) -> dict:
        url = f"{self.base_url}{path}"
        resp = self._session.get(url, params=params, timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()

    def _delete(self, path: str) -> dict:
        url = f"{self.base_url}{path}"
        resp = self._session.delete(url, timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()

    # ─── Core API 1: write_memory ───

    def write_memory(self, content: str, scene: str = "",
                     memory_type: str = "fact", confidence: float = 0.8,
                     agent_id: str = "", metadata: dict = None) -> str:
        data = {
            "content": content,
            "scene": scene,
            "type": memory_type,
            "confidence": confidence,
            "agent_id": agent_id,
        }
        if metadata:
            data["metadata"] = metadata
        result = self._post("/memory/write", data)
        return result.get("memory_id", "")

    # ─── Core API 2: search_memory ───

    def search_memory(self, query: str, scene: str = "",
                      agent_id: str = "", limit: int = 10) -> List[dict]:
        data = {
            "query": query,
            "limit": limit,
            "agent_id": agent_id,
        }
        if scene:
            data["scene"] = scene
        result = self._post("/memory/search", data)
        return result.get("results", [])

    # ─── Core API 3: recall_context ───

    def recall_context(self, query: str, scene: str = "",
                       agent_id: str = "", limit: int = 5,
                       mode: str = "kv") -> dict:
        data = {
            "query": query,
            "limit": limit,
            "mode": mode,
            "agent_id": agent_id,
        }
        if scene:
            data["scene"] = scene
        return self._post("/memory/recall", data)

    # ─── Core API 4: list_scenes ───

    def list_scenes(self, agent_id: str = "") -> List[str]:
        params = {}
        if agent_id:
            params["agent_id"] = agent_id
        result = self._get("/memory/scenes", params=params)
        return result.get("scenes", [])

    # ─── Core API 5: memory_governance ───

    def memory_governance(self, operation: str = "cleanup") -> dict:
        return self._post("/memory/governance", {"operation": operation})

    # ─── Backward-compatible aliases ───

    def write(self, content: str, agent_id: str = "", scene: str = "",
              cell_type: str = "fact", source: str = "api",
              metadata: dict = None) -> str:
        return self.write_memory(
            content=content, scene=scene, memory_type=cell_type,
            agent_id=agent_id, metadata=metadata,
        )

    def add(self, content: str, source: str = "api", agent_id: str = "",
            scene: str = "", cell_type: str = "fact",
            metadata: dict = None) -> str:
        return self.write_memory(
            content=content, scene=scene, memory_type=cell_type,
            agent_id=agent_id, metadata=metadata,
        )

    def recall(self, query: str, agent_id: str = "", scene: str = "",
               mode: str = "kv", top_k: int = None, limit: int = None,
               budget: int = 2000) -> dict:
        effective_limit = limit or top_k or 5
        return self.recall_context(
            query=query, scene=scene, agent_id=agent_id,
            limit=effective_limit, mode=mode,
        )

    def context(self, query: str, agent_id: str = "", scene: str = "",
                limit: int = 3) -> List[str]:
        result = self.recall_context(
            query=query, scene=scene, agent_id=agent_id,
            limit=limit, mode="kv",
        )
        return result.get("context", [])

    def search(self, query: str, agent_id: str = "",
               top_k: int = None, limit: int = None) -> List[dict]:
        effective_limit = limit or top_k or 10
        return self.search_memory(
            query=query, agent_id=agent_id, limit=effective_limit,
        )

    def scenes(self, agent_id: str = "") -> List[str]:
        return self.list_scenes(agent_id=agent_id)

    def delete(self, memory_id: str) -> bool:
        try:
            self._delete(f"/memory/{memory_id}")
            return True
        except Exception:
            return False

    def reconstruct(self, query: str, agent_id: str = "",
                    max_sources: int = 10) -> dict:
        data = {
            "query": query,
            "agent_id": agent_id,
            "max_sources": max_sources,
        }
        return self._post("/memory/reconstruct", data)

    def health(self) -> dict:
        return self._get("/health")

    def stats(self) -> dict:
        return self._get("/api/stats")

    def close(self):
        self._session.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

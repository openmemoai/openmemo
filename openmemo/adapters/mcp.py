"""
MCP (Model Context Protocol) Adapter for OpenMemo.

Allows OpenMemo to serve as a memory backend for
Claude and other MCP-compatible AI assistants.

Supports both local SDK and remote API modes.

Usage (local):
    from openmemo.adapters.mcp import OpenMemoMCPServer
    server = OpenMemoMCPServer()

Usage (remote):
    from openmemo.adapters.mcp import OpenMemoMCPServer
    server = OpenMemoMCPServer(base_url="https://api.openmemo.ai")
"""


class OpenMemoMCPServer:
    def __init__(self, db_path: str = "openmemo.db", memory=None,
                 base_url: str = None, api_key: str = None):
        if memory:
            self.memory = memory
        elif base_url:
            from openmemo.api.remote import RemoteMemory
            self.memory = RemoteMemory(base_url=base_url, api_key=api_key)
        else:
            from openmemo.api.sdk import Memory
            self.memory = Memory(db_path=db_path)

    def get_tools(self):
        return [
            {
                "name": "write_memory",
                "description": "Store a memory. Use this to remember facts, decisions, preferences, or observations.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "content": {"type": "string", "description": "The memory content to store"},
                        "scene": {"type": "string", "description": "Context scene (e.g., 'coding', 'deployment')"},
                        "memory_type": {"type": "string", "enum": ["fact", "decision", "preference", "constraint", "observation"]},
                        "confidence": {"type": "number", "description": "Confidence level 0-1", "default": 0.8},
                        "agent_id": {"type": "string", "description": "Agent identifier"},
                    },
                    "required": ["content"],
                },
            },
            {
                "name": "recall_context",
                "description": "Recall relevant memories for agent reasoning. Returns contextually relevant past memories.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "What to recall"},
                        "scene": {"type": "string", "description": "Filter by scene"},
                        "mode": {"type": "string", "enum": ["kv", "narrative", "raw"], "description": "Recall mode"},
                        "limit": {"type": "integer", "description": "Max results", "default": 5},
                        "agent_id": {"type": "string", "description": "Agent identifier"},
                    },
                    "required": ["query"],
                },
            },
            {
                "name": "search_memory",
                "description": "Search memories by query. Returns scored results.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"},
                        "scene": {"type": "string", "description": "Filter by scene"},
                        "limit": {"type": "integer", "description": "Max results", "default": 10},
                        "agent_id": {"type": "string", "description": "Agent identifier"},
                    },
                    "required": ["query"],
                },
            },
            {
                "name": "list_scenes",
                "description": "List all memory scenes.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "agent_id": {"type": "string", "description": "Agent identifier"},
                    },
                },
            },
        ]

    def handle_tool(self, tool_name: str, arguments: dict) -> dict:
        if tool_name == "write_memory":
            memory_id = self.memory.write_memory(
                content=arguments["content"],
                scene=arguments.get("scene", ""),
                memory_type=arguments.get("memory_type", "fact"),
                confidence=arguments.get("confidence", 0.8),
                agent_id=arguments.get("agent_id", ""),
            )
            return {"memory_id": memory_id, "status": "stored"}

        elif tool_name == "recall_context":
            return self.memory.recall_context(
                query=arguments["query"],
                scene=arguments.get("scene", ""),
                agent_id=arguments.get("agent_id", ""),
                mode=arguments.get("mode", "kv"),
                limit=arguments.get("limit", 5),
            )

        elif tool_name == "search_memory":
            results = self.memory.search_memory(
                query=arguments["query"],
                scene=arguments.get("scene", ""),
                agent_id=arguments.get("agent_id", ""),
                limit=arguments.get("limit", 10),
            )
            return {"results": results}

        elif tool_name == "list_scenes":
            scenes = self.memory.list_scenes(
                agent_id=arguments.get("agent_id", ""),
            )
            return {"scenes": scenes}

        return {"error": f"Unknown tool: {tool_name}"}

    def close(self):
        if hasattr(self.memory, 'close'):
            self.memory.close()

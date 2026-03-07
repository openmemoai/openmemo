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
    """
    MCP tool server backed by OpenMemo.

    Args:
        db_path: Local database path (local mode only). Default: "openmemo.db"
        memory: Pre-configured Memory or RemoteMemory instance.
        base_url: Remote API URL. If provided, uses remote mode.
        api_key: API key for remote authentication (future use).
    """

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
                "name": "memory_write",
                "description": "Store a memory for later recall. Use this to remember facts, decisions, preferences, or observations.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "content": {"type": "string", "description": "The memory content to store"},
                        "agent_id": {"type": "string", "description": "Agent identifier"},
                        "scene": {"type": "string", "description": "Context scene (e.g., 'coding', 'planning')"},
                        "cell_type": {"type": "string", "enum": ["fact", "decision", "preference", "constraint", "observation"]},
                    },
                    "required": ["content"],
                },
            },
            {
                "name": "memory_recall",
                "description": "Recall relevant memories based on a query. Returns contextually relevant past memories.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "What to recall"},
                        "agent_id": {"type": "string", "description": "Agent identifier"},
                        "scene": {"type": "string", "description": "Filter by scene"},
                        "mode": {"type": "string", "enum": ["kv", "narrative"], "description": "Recall mode: kv for key-value pairs, narrative for story"},
                        "limit": {"type": "integer", "description": "Max results", "default": 5},
                    },
                    "required": ["query"],
                },
            },
            {
                "name": "memory_context",
                "description": "Get memory context for prompt injection. Returns a list of relevant memories as strings.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Context query"},
                        "agent_id": {"type": "string", "description": "Agent identifier"},
                        "scene": {"type": "string", "description": "Filter by scene"},
                        "limit": {"type": "integer", "description": "Max context items", "default": 3},
                    },
                    "required": ["query"],
                },
            },
        ]

    def handle_tool(self, tool_name: str, arguments: dict) -> dict:
        if tool_name == "memory_write":
            memory_id = self.memory.write(
                content=arguments["content"],
                agent_id=arguments.get("agent_id", ""),
                scene=arguments.get("scene", ""),
                cell_type=arguments.get("cell_type", "fact"),
            )
            return {"memory_id": memory_id, "status": "stored"}

        elif tool_name == "memory_recall":
            result = self.memory.recall(
                query=arguments["query"],
                agent_id=arguments.get("agent_id", ""),
                scene=arguments.get("scene", ""),
                mode=arguments.get("mode", "kv"),
                limit=arguments.get("limit", 5),
            )
            return result

        elif tool_name == "memory_context":
            context = self.memory.context(
                query=arguments["query"],
                agent_id=arguments.get("agent_id", ""),
                scene=arguments.get("scene", ""),
                limit=arguments.get("limit", 3),
            )
            return {"memory_context": context}

        return {"error": f"Unknown tool: {tool_name}"}

    def close(self):
        if hasattr(self.memory, 'close'):
            self.memory.close()

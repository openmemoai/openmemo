"""
MCP (Model Context Protocol) Adapter for OpenMemo.

Allows OpenMemo to serve as a memory backend for
Claude and other MCP-compatible AI assistants.

Usage:
    from openmemo.adapters.mcp import OpenMemoMCPServer
    server = OpenMemoMCPServer()
    server.run()
"""

from openmemo.api.sdk import Memory


class OpenMemoMCPServer:
    def __init__(self, db_path: str = "openmemo.db", memory: Memory = None):
        self.memory = memory or Memory(db_path=db_path)

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
                        "top_k": {"type": "integer", "description": "Max results", "default": 10},
                    },
                    "required": ["query"],
                },
            },
            {
                "name": "memory_search",
                "description": "Search stored memories. Returns raw matches for debugging.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"},
                        "agent_id": {"type": "string", "description": "Agent identifier"},
                    },
                    "required": ["query"],
                },
            },
        ]

    def handle_tool(self, tool_name: str, arguments: dict) -> dict:
        if tool_name == "memory_write":
            memory_id = self.memory.add(
                content=arguments["content"],
                agent_id=arguments.get("agent_id", ""),
                scene=arguments.get("scene", ""),
                cell_type=arguments.get("cell_type", "fact"),
            )
            return {"memory_id": memory_id}

        elif tool_name == "memory_recall":
            results = self.memory.recall(
                query=arguments["query"],
                agent_id=arguments.get("agent_id", ""),
                top_k=arguments.get("top_k", 10),
            )
            return {"results": results}

        elif tool_name == "memory_search":
            results = self.memory.search(
                query=arguments["query"],
                agent_id=arguments.get("agent_id", ""),
            )
            return {"results": results}

        return {"error": f"Unknown tool: {tool_name}"}

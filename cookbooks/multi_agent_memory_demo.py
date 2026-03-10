"""
Multi-Agent Memory Demo — Phase 17

Demonstrates how multiple agents can:
1. Register themselves in the agent registry
2. Write private, shared, and conversation-scoped memories
3. Recall memories with proper isolation
4. Promote high-value memories to shared scope

Usage:
    python cookbooks/multi_agent_memory_demo.py
"""

from openmemo import Memory


def main():
    memory = Memory(db_path=":memory:")

    print("=" * 60)
    print("  OpenMemo Multi-Agent Memory Demo")
    print("=" * 60)

    print("\n1. Registering agents...")
    memory.register_agent("research", agent_type="researcher",
                          description="Researches topics and gathers information")
    memory.register_agent("coding", agent_type="coder",
                          description="Writes and reviews code")
    memory.register_agent("deploy", agent_type="deployer",
                          description="Handles deployment and infrastructure")

    agents = memory.list_agents()
    for a in agents:
        print(f"   ✓ {a['agent_id']} ({a['agent_type']}): {a['description']}")

    print("\n2. Writing shared memories (visible to all agents)...")
    memory.write_memory("Project uses Python 3.12 with FastAPI",
                        agent_id="research", scene="stack", scope="shared")
    memory.write_memory("PostgreSQL is the primary database",
                        agent_id="research", scene="stack", scope="shared")
    memory.write_memory("Always run linting before commit",
                        agent_id="coding", memory_type="rules")
    print("   ✓ 3 shared memories written")

    print("\n3. Writing private memories (agent-specific)...")
    memory.write_memory("Found paper on RAG optimization techniques",
                        agent_id="research", scene="research", scope="private")
    memory.write_memory("Implemented JWT auth in auth_service.py",
                        agent_id="coding", scene="auth", scope="private")
    memory.write_memory("Production server IP is 10.0.1.42",
                        agent_id="deploy", scene="infra", scope="private")
    print("   ✓ 3 private memories written")

    print("\n4. Writing conversation-scoped memories...")
    memory.start_conversation("debug-session-001", agent_id="coding",
                              scene="debugging")
    memory.write_memory("Error traced to race condition in queue handler",
                        agent_id="coding", scope="conversation",
                        conversation_id="debug-session-001")
    print("   ✓ 1 conversation memory written")

    print("\n5. Testing memory isolation...")

    print("\n   [Research agent] searching 'Python stack':")
    results = memory.search_memory("Python stack", agent_id="research",
                                   scene="stack")
    for r in results:
        print(f"      → {r['content']} (score: {r['score']:.3f})")

    print("\n   [Coding agent] searching 'Python stack':")
    results = memory.search_memory("Python stack", agent_id="coding",
                                   scene="stack")
    for r in results:
        print(f"      → {r['content']} (score: {r['score']:.3f})")

    print("\n   [Deploy agent] searching 'JWT auth':")
    results = memory.search_memory("JWT auth", agent_id="deploy",
                                   scene="auth")
    if not results:
        print("      → (empty — correctly isolated, JWT is coding agent's private memory)")
    for r in results:
        print(f"      → {r['content']}")

    print("\n   [Coding agent] searching 'JWT auth':")
    results = memory.search_memory("JWT auth", agent_id="coding",
                                   scene="auth")
    for r in results:
        print(f"      → {r['content']} (score: {r['score']:.3f})")

    print("\n6. Context injection for agent prompt...")
    from openmemo.adapters.base_adapter import BaseMemoryAdapter
    adapter = BaseMemoryAdapter(memory=memory, agent_id="coding",
                                default_scene="stack")
    prompt = "What technology should I use for the new microservice?"
    injected = adapter.inject_context(prompt)
    print(f"   Original prompt: {prompt}")
    print(f"   Injected prompt:\n{injected}")

    print("\n7. Shared memory promotion...")
    memory.write_memory("Always validate input before processing",
                        agent_id="coding", scope="private", confidence=0.95)
    cells = memory.store.list_cells(limit=100)
    from openmemo.core.memcell import MemCell
    for c in cells:
        if "validate input" in c["content"]:
            cell_obj = MemCell.from_dict(c)
            cell_obj.access_count = 5
            memory.store.put_cell(cell_obj.to_dict())

    result = memory.promote_shared_memories()
    print(f"   ✓ Promoted {result['promoted']} memories to shared scope")

    print("\n8. Listing conversations...")
    convs = memory.list_conversations()
    for c in convs:
        print(f"   ✓ {c['conversation_id']} (agent: {c['agent_id']}, scene: {c['scene']})")

    print("\n" + "=" * 60)
    stats = memory.stats()
    print(f"  Total: {stats['cells']} memories, {stats['scenes']} scenes")
    print("  Demo complete!")
    print("=" * 60)

    memory.close()


if __name__ == "__main__":
    main()

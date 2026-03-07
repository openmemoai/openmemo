"""
Cookbook: Coding Assistant with Memory

A coding assistant that remembers user preferences,
project context, and past decisions.

Usage:
    pip install openmemo
    python cookbooks/coding_assistant.py
"""

from openmemo import MemoryClient

mem = MemoryClient(db_path="coding_assistant.db")

mem.write(
    "User prefers Python 3.11 with type hints",
    agent_id="coding_agent",
    scene="preferences",
    cell_type="preference",
)

mem.write(
    "Project uses Flask for backend API",
    agent_id="coding_agent",
    scene="project_setup",
    cell_type="fact",
)

mem.write(
    "Use PostgreSQL in production, SQLite in development",
    agent_id="coding_agent",
    scene="project_setup",
    cell_type="decision",
)

mem.write(
    "Always run tests before committing",
    agent_id="coding_agent",
    scene="workflow",
    cell_type="constraint",
)

mem.write(
    "User struggled with async code yesterday",
    agent_id="coding_agent",
    scene="observations",
    cell_type="observation",
)

result = mem.recall(
    "What database should I use?",
    agent_id="coding_agent",
    mode="kv",
)
print("=== Recall (KV mode): database preference ===")
for m in result["memories"]:
    print(f"  - {m}")

result = mem.recall(
    "What are the project constraints?",
    agent_id="coding_agent",
    scene="workflow",
    mode="narrative",
)
print("\n=== Recall (Narrative mode): workflow constraints ===")
print(f"  {result['memory_story']}")

context = mem.context(
    "deploy application",
    agent_id="coding_agent",
    limit=3,
)
print(f"\n=== Agent Context (for prompt injection) ===")
for c in context:
    print(f"  - {c}")

scenes = mem.scenes(agent_id="coding_agent")
print(f"\n=== Scenes ({len(scenes)}) ===")
for s in scenes:
    print(f"  - {s}")

stats = mem.stats()
print(f"\n=== Stats ===")
print(f"  Notes: {stats['notes']}, Cells: {stats['cells']}, Scenes: {stats['scenes']}")

mem.close()
print("\nDone!")

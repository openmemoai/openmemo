"""
Cookbook: Coding Assistant with Memory

A coding assistant that remembers user preferences,
project context, and past decisions.

Usage:
    pip install openmemo
    python cookbooks/coding_assistant.py
"""

from openmemo import Memory

memory = Memory(db_path="coding_assistant.db")

memory.add(
    "User prefers Python 3.11 with type hints",
    agent_id="coding_agent",
    scene="preferences",
    cell_type="preference",
)

memory.add(
    "Project uses Flask for backend API",
    agent_id="coding_agent",
    scene="project_setup",
    cell_type="fact",
)

memory.add(
    "Use PostgreSQL in production, SQLite in development",
    agent_id="coding_agent",
    scene="project_setup",
    cell_type="decision",
)

memory.add(
    "Always run tests before committing",
    agent_id="coding_agent",
    scene="workflow",
    cell_type="constraint",
)

memory.add(
    "User struggled with async code yesterday",
    agent_id="coding_agent",
    scene="observations",
    cell_type="observation",
)

results = memory.recall(
    "What database should I use?",
    agent_id="coding_agent",
)
print("=== Recall: database preference ===")
for r in results:
    print(f"  [{r['score']:.2f}] {r['content']}")

results = memory.recall(
    "What are the project constraints?",
    agent_id="coding_agent",
    scene="workflow",
)
print("\n=== Recall: workflow constraints ===")
for r in results:
    print(f"  [{r['score']:.2f}] {r['content']}")

scenes = memory.scenes(agent_id="coding_agent")
print(f"\n=== Scenes ({len(scenes)}) ===")
for s in scenes:
    print(f"  - {s['title']} ({len(s.get('cell_ids', []))} memories)")

stats = memory.stats()
print(f"\n=== Stats ===")
print(f"  Notes: {stats['notes']}, Cells: {stats['cells']}, Scenes: {stats['scenes']}")

memory.close()
print("\nDone!")

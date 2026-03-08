"""
Cookbook: Coding Assistant with Memory

A coding assistant that remembers user preferences,
project context, and past decisions.

Usage:
    pip install openmemo
    python cookbooks/coding_assistant.py
"""

from openmemo import OpenMemo

memo = OpenMemo(db_path="coding_assistant.db")

memo.write_memory(
    "User prefers Python 3.11 with type hints",
    scene="preferences",
    memory_type="preference",
)

memo.write_memory(
    "Project uses Flask for backend API",
    scene="project_setup",
    memory_type="fact",
)

memo.write_memory(
    "Use PostgreSQL in production, SQLite in development",
    scene="project_setup",
    memory_type="decision",
    confidence=0.95,
)

memo.write_memory(
    "Always run tests before committing",
    scene="workflow",
    memory_type="constraint",
)

memo.write_memory(
    "User struggled with async code yesterday",
    scene="observations",
    memory_type="observation",
    confidence=0.7,
)

result = memo.recall_context(
    "What database should I use?",
    mode="kv",
)
print("=== recall_context (KV mode): database ===")
for c in result["context"]:
    print(f"  - {c}")

result = memo.recall_context(
    "What are the project constraints?",
    scene="workflow",
    mode="narrative",
)
print("\n=== recall_context (Narrative mode): workflow ===")
print(f"  {result['memory_story']}")

results = memo.search_memory("deploy application")
print(f"\n=== search_memory: deploy ===")
for r in results:
    print(f"  - [{r['score']:.2f}] {r['content']}")

scenes = memo.list_scenes()
print(f"\n=== list_scenes ({len(scenes)}) ===")
for s in scenes:
    print(f"  - {s}")

stats = memo.stats()
print(f"\n=== Stats ===")
print(f"  Notes: {stats['notes']}, Cells: {stats['cells']}, Scenes: {stats['scenes']}")

memo.close()
print("\nDone!")

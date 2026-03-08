"""
Cookbook: Personal Memory Assistant

A personal assistant that builds up knowledge about
the user over time — preferences, goals, and observations.

Usage:
    pip install openmemo
    python cookbooks/personal_memory.py
"""

from openmemo import OpenMemo

memo = OpenMemo(db_path="personal_memory.db")

AGENT_ID = "personal_assistant"

memo.write_memory("User's name is Alex", scene="identity", memory_type="fact", agent_id=AGENT_ID)
memo.write_memory("Alex prefers dark mode in all applications", scene="preferences", memory_type="preference", agent_id=AGENT_ID)
memo.write_memory("Alex is learning Rust programming language", scene="goals", memory_type="observation", agent_id=AGENT_ID)
memo.write_memory("Alex decided to wake up at 6am every day", scene="goals", memory_type="decision", agent_id=AGENT_ID)
memo.write_memory("Alex doesn't like receiving notifications after 10pm", scene="preferences", memory_type="constraint", agent_id=AGENT_ID)

print("=== recall_context (KV): Alex's preferences ===")
result = memo.recall_context("Alex preferences", agent_id=AGENT_ID, mode="kv")
for c in result["context"]:
    print(f"  - {c}")

print("\n=== recall_context (Narrative): Alex's goals ===")
result = memo.recall_context("What are Alex's goals?", agent_id=AGENT_ID, mode="narrative")
print(f"  {result['memory_story']}")
print(f"  Confidence: {result['confidence']:.2f}")

print("\n=== list_scenes ===")
scenes = memo.list_scenes(agent_id=AGENT_ID)
for s in scenes:
    print(f"  - {s}")

print("\n=== memory_governance: cleanup ===")
result = memo.memory_governance("cleanup")
print(f"  {result}")

stats = memo.stats()
print(f"\n=== Stats: {stats['cells']} memories across {stats['scenes']} scenes ===")

memo.close()
print("\nDone!")

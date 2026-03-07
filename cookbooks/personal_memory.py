"""
Cookbook: Personal Memory Assistant

A personal assistant that builds up knowledge about
the user over time — preferences, goals, and observations.

Usage:
    pip install openmemo
    python cookbooks/personal_memory.py
"""

from openmemo import MemoryClient

mem = MemoryClient(db_path="personal_memory.db")

AGENT_ID = "personal_assistant"

mem.write("User's name is Alex", agent_id=AGENT_ID, scene="identity", cell_type="fact")
mem.write("Alex prefers dark mode in all applications", agent_id=AGENT_ID, scene="preferences", cell_type="preference")
mem.write("Alex is learning Rust programming language", agent_id=AGENT_ID, scene="goals", cell_type="observation")
mem.write("Alex decided to wake up at 6am every day", agent_id=AGENT_ID, scene="goals", cell_type="decision")
mem.write("Alex doesn't like receiving notifications after 10pm", agent_id=AGENT_ID, scene="preferences", cell_type="constraint")
mem.write("Alex mentioned being interested in machine learning", agent_id=AGENT_ID, scene="interests", cell_type="observation")

print("=== KV Recall: Alex's preferences ===")
result = mem.recall("Alex preferences", agent_id=AGENT_ID, mode="kv")
for m in result["memories"]:
    print(f"  - {m}")

print("\n=== Narrative Recall: Alex's goals ===")
result = mem.recall("What are Alex's goals?", agent_id=AGENT_ID, mode="narrative")
print(f"  {result['memory_story']}")
print(f"  Confidence: {result['confidence']:.2f}")

print("\n=== Agent Context: for prompt injection ===")
context = mem.context("What does Alex like?", agent_id=AGENT_ID, limit=3)
for c in context:
    print(f"  - {c}")

print("\n=== Scenes ===")
scenes = mem.scenes(agent_id=AGENT_ID)
for s in scenes:
    print(f"  - {s}")

stats = mem.stats()
print(f"\n=== Stats: {stats['cells']} memories across {stats['scenes']} scenes ===")

mem.close()
print("\nDone!")

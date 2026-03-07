"""
Cookbook: Personal Memory Assistant

A personal assistant that builds up knowledge about
the user over time — preferences, goals, and observations.

Usage:
    pip install openmemo
    python cookbooks/personal_memory.py
"""

from openmemo import Memory

memory = Memory(db_path="personal_memory.db")

AGENT_ID = "personal_assistant"

memory.add(
    "User's name is Alex",
    agent_id=AGENT_ID,
    scene="identity",
    cell_type="fact",
)

memory.add(
    "Alex prefers dark mode in all applications",
    agent_id=AGENT_ID,
    scene="preferences",
    cell_type="preference",
)

memory.add(
    "Alex is learning Rust programming language",
    agent_id=AGENT_ID,
    scene="goals",
    cell_type="observation",
)

memory.add(
    "Alex decided to wake up at 6am every day",
    agent_id=AGENT_ID,
    scene="goals",
    cell_type="decision",
)

memory.add(
    "Alex doesn't like receiving notifications after 10pm",
    agent_id=AGENT_ID,
    scene="preferences",
    cell_type="constraint",
)

memory.add(
    "Alex mentioned being interested in machine learning",
    agent_id=AGENT_ID,
    scene="interests",
    cell_type="observation",
)

print("=== What do we know about Alex's preferences? ===")
results = memory.recall("Alex preferences", agent_id=AGENT_ID)
for r in results:
    print(f"  [{r['score']:.2f}] {r['content']}")

print("\n=== Reconstruct: Alex's goals ===")
reconstruction = memory.reconstruct("What are Alex's goals?", agent_id=AGENT_ID)
print(f"  Narrative:\n{reconstruction['narrative']}")
print(f"  Confidence: {reconstruction['confidence']:.2f}")
print(f"  Sources: {len(reconstruction['sources'])}")

print("\n=== Memory scenes ===")
scenes = memory.scenes(agent_id=AGENT_ID)
for s in scenes:
    print(f"  - {s['title']}")

stats = memory.stats()
print(f"\n=== Stats: {stats['cells']} memories across {stats['scenes']} scenes ===")

memory.close()
print("\nDone!")

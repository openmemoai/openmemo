"""
Cookbook: Customer Support Agent with Memory

A support agent that remembers customer interactions,
preferences, and issue history across sessions.

Usage:
    pip install openmemo
    python cookbooks/customer_support.py
"""

from openmemo import OpenMemo

memo = OpenMemo(db_path="support_agent.db")

AGENT_ID = "support_agent"

memo.write_memory(
    "Customer John (ID: C-1001) prefers email communication",
    scene="customer_c1001",
    memory_type="preference",
    agent_id=AGENT_ID,
)

memo.write_memory(
    "John reported login issues on 2024-01-15, resolved by resetting password",
    scene="customer_c1001",
    memory_type="fact",
    agent_id=AGENT_ID,
)

memo.write_memory(
    "Do not offer more than $100 credit without manager approval",
    scene="policies",
    memory_type="constraint",
    confidence=1.0,
    agent_id=AGENT_ID,
)

print("=== recall_context: John's history ===")
result = memo.recall_context(
    "What issues has John had?",
    scene="customer_c1001",
    agent_id=AGENT_ID,
)
for c in result["context"]:
    print(f"  - {c}")

print("\n=== search_memory: credit policies ===")
results = memo.search_memory("credit limit policy", agent_id=AGENT_ID)
for r in results:
    print(f"  - {r['content']}")

print("\n=== list_scenes ===")
scenes = memo.list_scenes(agent_id=AGENT_ID)
for s in scenes:
    print(f"  - {s}")

memo.close()
print("\nDone!")

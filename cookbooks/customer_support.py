"""
Cookbook: Customer Support Agent with Memory

A support agent that remembers customer interactions,
preferences, and issue history across sessions.

Usage:
    pip install openmemo
    python cookbooks/customer_support.py
"""

from openmemo import Memory

memory = Memory(db_path="support_agent.db")

AGENT_ID = "support_agent"

memory.add(
    "Customer John (ID: C-1001) prefers email communication",
    agent_id=AGENT_ID,
    scene="customer_c1001",
    cell_type="preference",
)

memory.add(
    "John reported login issues on 2024-01-15, resolved by resetting password",
    agent_id=AGENT_ID,
    scene="customer_c1001",
    cell_type="fact",
)

memory.add(
    "John is on the Pro plan, renewed last month",
    agent_id=AGENT_ID,
    scene="customer_c1001",
    cell_type="fact",
)

memory.add(
    "Customer Sarah (ID: C-1002) prefers phone support",
    agent_id=AGENT_ID,
    scene="customer_c1002",
    cell_type="preference",
)

memory.add(
    "Sarah had billing dispute in December, issued $50 credit",
    agent_id=AGENT_ID,
    scene="customer_c1002",
    cell_type="decision",
)

memory.add(
    "Do not offer more than $100 credit without manager approval",
    agent_id=AGENT_ID,
    scene="policies",
    cell_type="constraint",
)

print("=== Looking up John's history ===")
results = memory.recall(
    "What issues has John had?",
    agent_id=AGENT_ID,
    scene="customer_c1001",
)
for r in results:
    print(f"  [{r['score']:.2f}] {r['content']}")

print("\n=== Checking credit policies ===")
results = memory.recall(
    "credit limit policy",
    agent_id=AGENT_ID,
    scene="policies",
)
for r in results:
    print(f"  [{r['score']:.2f}] {r['content']}")

print("\n=== All customer scenes ===")
scenes = memory.scenes(agent_id=AGENT_ID)
for s in scenes:
    print(f"  - {s['title']} ({len(s.get('cell_ids', []))} items)")

memory.close()
print("\nDone!")

"""
Cookbook: Customer Support Agent with Memory

A support agent that remembers customer interactions,
preferences, and issue history across sessions.

Usage:
    pip install openmemo
    python cookbooks/customer_support.py
"""

from openmemo import MemoryClient

mem = MemoryClient(db_path="support_agent.db")

AGENT_ID = "support_agent"

mem.write(
    "Customer John (ID: C-1001) prefers email communication",
    agent_id=AGENT_ID,
    scene="customer_c1001",
    cell_type="preference",
)

mem.write(
    "John reported login issues on 2024-01-15, resolved by resetting password",
    agent_id=AGENT_ID,
    scene="customer_c1001",
    cell_type="fact",
)

mem.write(
    "John is on the Pro plan, renewed last month",
    agent_id=AGENT_ID,
    scene="customer_c1001",
    cell_type="fact",
)

mem.write(
    "Customer Sarah (ID: C-1002) prefers phone support",
    agent_id=AGENT_ID,
    scene="customer_c1002",
    cell_type="preference",
)

mem.write(
    "Sarah had billing dispute in December, issued $50 credit",
    agent_id=AGENT_ID,
    scene="customer_c1002",
    cell_type="decision",
)

mem.write(
    "Do not offer more than $100 credit without manager approval",
    agent_id=AGENT_ID,
    scene="policies",
    cell_type="constraint",
)

print("=== Looking up John's history (KV mode) ===")
result = mem.recall(
    "What issues has John had?",
    agent_id=AGENT_ID,
    scene="customer_c1001",
    mode="kv",
)
for m in result["memories"]:
    print(f"  - {m}")

print("\n=== Checking credit policies ===")
context = mem.context(
    "credit limit policy",
    agent_id=AGENT_ID,
    limit=3,
)
for c in context:
    print(f"  - {c}")

print("\n=== All scenes ===")
scenes = mem.scenes(agent_id=AGENT_ID)
for s in scenes:
    print(f"  - {s}")

mem.close()
print("\nDone!")

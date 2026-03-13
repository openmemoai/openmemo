#!/usr/bin/env python3
"""
Team Memory Demo — Phase 22

Demonstrates team memory features:
  1. Write memories with team_id/task_id
  2. Scope routing (private/shared/team)
  3. Layered recall with scope weights
  4. Promotion from shared → team
  5. Team/task memory listing
  6. Multi-team isolation
"""

import time
from openmemo import Memory, route_scope, PromotionWorker

def main():
    print("=" * 60)
    print("  OpenMemo Team Memory Demo (Phase 22)")
    print("=" * 60)

    mem = Memory(db_path=":memory:")

    print("\n--- 1. Scope Routing ---")
    for mtype in ["decision", "finding", "fact", "workflow", "playbook"]:
        scope = route_scope(mtype)
        print(f"  {mtype:15s} → {scope}")

    print("\n--- 2. Write memories with team_id / task_id ---")
    m1 = mem.write_memory(
        content="Team decision: use PostgreSQL for all persistent data",
        memory_type="decision", scope="team",
        team_id="team-alpha", agent_id="agent-1",
    )
    print(f"  Team decision stored: {m1}")

    m2 = mem.write_memory(
        content="Task finding: API response time is 150ms p99",
        memory_type="finding", scope="shared",
        team_id="team-alpha", task_id="perf-audit",
        agent_id="agent-2",
    )
    print(f"  Shared finding stored: {m2}")

    m3 = mem.write_memory(
        content="My personal debugging notes",
        memory_type="fact", scope="private",
        agent_id="agent-1",
    )
    print(f"  Private note stored: {m3}")

    print("\n--- 3. List team memories ---")
    team_mems = mem.list_team_memories(team_id="team-alpha")
    print(f"  Team Alpha has {len(team_mems)} team-scope memories:")
    for m in team_mems:
        print(f"    - [{m.get('cell_type')}] {m.get('content', '')[:60]}")

    print("\n--- 4. List task memories ---")
    task_mems = mem.list_task_memories(task_id="perf-audit")
    print(f"  Task 'perf-audit' has {len(task_mems)} shared/team memories:")
    for m in task_mems:
        print(f"    - [{m.get('scope')}] {m.get('content', '')[:60]}")

    print("\n--- 5. Recall with team context ---")
    results = mem.search_memory(
        query="PostgreSQL database",
        agent_id="agent-1", team_id="team-alpha",
    )
    print(f"  Found {len(results)} results for 'PostgreSQL database':")
    for r in results:
        print(f"    - score={r['score']:.3f} | {r['content'][:60]}")

    print("\n--- 6. Promotion: shared → team ---")
    mem.write_memory(
        content="Validated pattern: retry with exponential backoff reduces errors by 80%",
        memory_type="validated", scope="shared",
        team_id="team-alpha", task_id="reliability",
        agent_id="agent-2", confidence=0.95,
    )
    cells = mem.store.list_cells(limit=100)
    for c in cells:
        if c.get("scope") == "shared":
            c["created_at"] = time.time() - 7200
            c["access_count"] = 5
            mem.store.put_cell(c)

    result = mem.promote_to_team(team_id="team-alpha")
    print(f"  Evaluated: {result['evaluated']}, Promoted: {result['promoted']}")

    team_mems_after = mem.list_team_memories(team_id="team-alpha")
    print(f"  Team Alpha now has {len(team_mems_after)} team-scope memories")

    print("\n--- 7. Multi-team isolation ---")
    mem.write_memory(
        content="Beta team: use MongoDB for document storage",
        memory_type="decision", scope="team",
        team_id="team-beta", agent_id="agent-3",
    )
    alpha = mem.list_team_memories(team_id="team-alpha")
    beta = mem.list_team_memories(team_id="team-beta")
    print(f"  Alpha team memories: {len(alpha)}")
    print(f"  Beta team memories: {len(beta)}")

    mem.close()
    print("\n" + "=" * 60)
    print("  Demo complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()

"""
Phase 21 Demo: Memory Skill Engine
===================================
Demonstrates the complete skill lifecycle:
  experience → memory → pattern → playbook → skill → execution → feedback → evolution

Run:
  cd oss-openmemo
  PYTHONPATH=. python cookbooks/skill_engine_demo.py
"""

import time
import tempfile
import os
from openmemo import OpenMemo, OpenMemoConfig

def main():
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    memo = OpenMemo(db_path=tmp.name)
    memo._auto_graph = False

    print("=" * 60)
    print("Phase 21: Memory Skill Engine Demo")
    print("=" * 60)

    print("\n--- Step 1: Write debug experiences ---")
    experiences = [
        ("Docker container crashed, checked env variables and fixed .env file", "deployment"),
        ("Docker container failed to start, verified .env and restarted", "deployment"),
        ("Docker compose error, inspected logs and fixed environment config", "deployment"),
        ("Python import error, added missing package to requirements.txt", "coding"),
        ("Python ModuleNotFoundError, checked sys.path and installed package", "coding"),
        ("API timeout, increased connection pool and added retry logic", "backend"),
    ]

    for content, scene in experiences:
        memo.write_memory(content, scene=scene)
        print(f"  Written: [{scene}] {content[:60]}...")

    print(f"\n  Total memories: {memo.stats()['notes']}")

    print("\n--- Step 2: Create patterns (simulating consolidation) ---")
    memo.store.put_cell({
        "id": "pattern_docker", "note_id": "pattern_docker",
        "content": "When docker containers fail, check environment variables, verify .env file, and restart",
        "cell_type": "pattern", "scene": "deployment",
        "confidence": 0.85, "created_at": time.time(),
    })
    memo.store.put_cell({
        "id": "pattern_python", "note_id": "pattern_python",
        "content": "Python import errors are resolved by checking sys.path and installing missing packages",
        "cell_type": "pattern", "scene": "coding",
        "confidence": 0.75, "created_at": time.time(),
    })
    memo.store.put_cell({
        "id": "playbook_docker", "note_id": "playbook_docker",
        "content": "Docker debugging playbook: systematic container troubleshooting",
        "cell_type": "playbook", "scene": "deployment",
        "confidence": 0.9, "created_at": time.time(),
        "metadata": '{"steps": ["docker logs <container>", "docker inspect <container>", "check .env file", "docker-compose restart"]}',
    })
    print("  Created 2 patterns + 1 playbook")

    print("\n--- Step 3: Extract skills from memory ---")
    skills = memo.extract_skills_from_memory()
    print(f"  Extracted {len(skills)} skills:")
    for s in skills:
        print(f"    - {s['name']} (scene={s['scene']}, confidence={s['confidence']:.2f})")
        if s.get("steps"):
            for step in s["steps"][:3]:
                print(f"        step: {step[:60]}")

    print("\n--- Step 4: Recall skills for a new task ---")
    query = "docker container crashed and won't start"
    recalled = memo.recall_skills(query, scene="deployment")
    print(f"  Query: '{query}'")
    print(f"  Found {len(recalled)} relevant skills:")
    for r in recalled:
        print(f"    - {r['name']} (confidence={r.get('confidence', 0):.2f})")

    print("\n--- Step 5: Execute skill (suggest mode) ---")
    if skills:
        skill_id = skills[0]["id"]
        result = memo.execute_skill(skill_id, mode="suggest")
        print(f"  Skill: {result.get('skill_name')}")
        print(f"  Mode: {result['mode']}")
        print(f"  Suggested steps:")
        for step in result.get("suggested_steps", []):
            print(f"    → {step}")

        print("\n--- Step 6: Execute skill (auto mode) ---")
        auto_result = memo.execute_skill(skill_id, mode="auto")
        print(f"  Auto-executed {auto_result['steps_executed']} steps:")
        for r in auto_result.get("results", []):
            print(f"    Step {r['step']}: {r['action']} [{r['status']}]")

        print("\n--- Step 7: Record feedback ---")
        for i in range(6):
            success = i < 5
            memo.record_skill_feedback(skill_id, success=success,
                                       result=f"attempt {i+1}: {'success' if success else 'failed'}")
        skill_data = memo.get_skill(skill_id)
        print(f"  Skill: {skill_data['name']}")
        print(f"  Usage count: {skill_data['usage_count']}")
        print(f"  Success rate: {skill_data['success_rate']:.2f}")

    print("\n--- Step 8: Skill evolution ---")
    memo.store.put_skill({
        "id": "weak1", "name": "bad_approach",
        "description": "A poor approach", "pattern": "bad",
        "scene": "misc", "trigger": "error",
        "steps": '["try random fix"]', "tools": "[]",
        "confidence": 0.1, "usage_count": 10, "success_rate": 0.05,
        "skill_version": 1, "status": "active",
        "created_at": time.time(), "updated_at": time.time(),
        "metadata": {},
    })

    evolution = memo.evolve_skills()
    print(f"  Merged: {evolution['merged']}")
    print(f"  Deprecated: {evolution['deprecated']}")
    print(f"  Promoted: {evolution['promoted']}")

    print("\n--- Step 9: Final skill registry ---")
    all_skills = memo.list_skills()
    print(f"  Total skills: {len(all_skills)}")
    for s in all_skills:
        print(f"    [{s['status']:>10}] {s['name']} "
              f"(v{s.get('skill_version', 1)}, "
              f"usage={s.get('usage_count', 0)}, "
              f"success={s.get('success_rate', 0):.0%})")

    print("\n--- Step 10: Filter by scene ---")
    deployment_skills = memo.list_skills(scene="deployment")
    print(f"  Deployment skills: {len(deployment_skills)}")
    coding_skills = memo.list_skills(scene="coding")
    print(f"  Coding skills: {len(coding_skills)}")

    print("\n" + "=" * 60)
    print("Phase 21 Demo Complete!")
    print("experience → memory → pattern → playbook → skill → evolution")
    print("=" * 60)

    memo.close()
    os.unlink(tmp.name)


if __name__ == "__main__":
    main()

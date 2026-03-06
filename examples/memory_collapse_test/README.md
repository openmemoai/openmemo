# The AI Memory Collapse Test

**What happens when an AI system runs for hours instead of minutes?**

Most AI systems work fine for short tasks. But when a system runs for 50+ steps, problems appear:

- Context windows explode
- Important facts get overwritten
- Past decisions are lost
- Experience cannot be reused

This demo simulates a long-running AI agent and tests whether critical facts can still be recalled after 50 steps of activity.

## Run

```bash
python run_demo.py
```

## What It Tests

The agent performs 50 steps of work:
- Creates project files and configurations
- Fixes bugs and installs dependencies
- Runs tests and optimizes code
- Records critical facts along the way

Then we ask questions about early facts (e.g., "Where was the API key stored?") and compare three memory approaches:

| Method | Result |
|---|---|
| Chat History | Context lost after window slides |
| Vector Retrieval | Fuzzy, unreliable matches |
| **OpenMemo** | **Exact recall with structured memory** |

## Why OpenMemo Wins

OpenMemo stores memories as structured MemCells, not raw text. This means:

- Facts are preserved regardless of how many steps pass
- Conflicts are detected automatically
- Recall uses structured matching, not just similarity

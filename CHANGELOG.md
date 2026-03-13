# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/).

This project is licensed under AGPLv3.

## [0.12.0] - 2026-03-13

### Added — Phase 22: Team Memory System
- **Scope Model**: 4-level scope (`private`, `conversation`, `shared`, `team`) with intelligent auto-routing
- **TeamRouter** (`openmemo/team/team_router.py`): Routes writes by type — `decision/workflow/standard/convention/policy` → team; `task_progress/finding/blocker/validated/playbook/pattern` → shared
- **Scope Weights**: Applied during recall — private=1.0, conversation=0.90, shared=0.85, team=0.70
- **MemCell team fields**: Added `team_id` and `task_id` to MemCell dataclass, `to_dict/from_dict`, and SQLite schema
- **PromotionWorker** (`openmemo/team/promotion.py`): Promotes shared→team memories based on confidence (>0.75), access count (≥2), age (>1h), and type
- **Layered Recall**: BM25/Vector strategies accept `team_id`/`task_id` for cross-agent knowledge access
- **SDK API**: `promote_to_team()`, `list_team_memories()`, `list_task_memories()`. All write/search/recall accept `team_id`/`task_id`
- **REST API**: `POST /team/promote`, `GET /team/memories`, `GET /team/task/{task_id}`
- **Demo**: `cookbooks/team_memory_demo.py`

### Added — Phase 20: Hybrid Memory Architecture
- **MemoryRouter** (`openmemo/sync/memory_router.py`): Routes operations based on mode (local/cloud/hybrid). Read local first, write local, async sync to cloud
- **SyncEngine** (`openmemo/sync/sync_engine.py`): Push/pull sync with persistent sync queue, conflict resolution (last-write-wins or confidence-based), memory versioning
- **SyncWorker** (`openmemo/sync/sync_worker.py`): Periodic background sync thread with configurable interval
- **Three modes**: `local` (default, fast, private), `cloud` (team/enterprise), `hybrid` (local read + cloud sync)
- **SDK API**: `push_sync()`, `pull_sync()`, `full_sync()`, `get_sync_status()`, `get_memory_mode()`
- **REST API**: `POST /sync/push`, `GET /sync/pull`, `GET /sync/status`
- **Config**: `HybridConfig` (memory_mode, cloud_endpoint, sync_interval, conflict_strategy, auto_sync)

### Added — Phase 19: Autonomous Memory Consolidation Engine
- **ConsolidationEngine** (`openmemo/core/consolidation.py`): Transforms raw memories into evolved knowledge
- **Duplicate Detection**: Keyword Jaccard similarity (default threshold=0.75), merges weaker into stronger cell
- **Memory Clustering**: Groups semantically similar memories (threshold=0.25) into clusters
- **Pattern Extraction**: Extracts common themes from clusters as `pattern` type cells. LLM callback supported
- **Playbook Generation**: Converts patterns into operational `playbook` type cells. LLM callback supported
- **Memory Decay**: Removes old low-confidence memories, decays mid-age memories
- **Memory Promotion**: Promotes high-confidence, frequently accessed memories to `pattern` type
- **SDK API**: `consolidate()`, `get_patterns()`, `detect_duplicates()`, governance operation `"consolidate"`
- **REST API**: `POST /memory/consolidate`, `GET /memory/patterns`, `GET /memory/duplicates`

### Added — NormalizedMergeStrategy (Recall)
- `NormalizedMergeStrategy` in `openmemo/core/recall.py`: Normalizes BM25 (weight=0.4) and vector (weight=0.6) scores before additive merge to prevent BM25 raw score inflation

## [0.11.1] - 2026-03-13

### Fixed
- **Critical crash fix**: `SQLiteStore` now uses thread-local connections (`threading.local()`)
  instead of a shared `self.conn`. This eliminates `EXC_BAD_ACCESS (SIGSEGV)` crashes that
  occurred when Inspector panel polling, Sync Worker background threads, and agent write
  operations accessed the same SQLite connection concurrently.
- Enabled WAL (Write-Ahead Logging) mode on all connections for better concurrent read/write
  performance without blocking.
- Verified fix with concurrent 6-thread stress test (2 writers + 3 readers + 1 inspector poller).

## [0.1.0] - 2026-03-06

### Added
- MemCell engine for structured memory units
- MemScene engine for scene-based containers
- Recall engine with tri-brain architecture (fast/mid/slow)
- Reconstructive recall for narrative generation
- Memory Pyramid with short/mid/long term tiers
- Skill engine (simplified) for experience-to-skill extraction
- Governance: conflict detection and version management
- Storage adapters: SQLite (default), base interface
- Python SDK with simple `Memory` API
- REST server for HTTP access
- 3 example demos: memory stress test, coding agent, research agent
- Docker support

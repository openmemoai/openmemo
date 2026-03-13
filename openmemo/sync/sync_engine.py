"""
Sync Engine — handles Local ↔ Cloud memory synchronization.

Features:
  - Sync queue for async replication
  - Push sync (local → cloud)
  - Pull sync (cloud → local)
  - Conflict resolution (last-write-wins / confidence-based)
  - Memory versioning
"""

import json
import time
import uuid
import logging
import sqlite3
import threading
from typing import List, Optional, Dict
from dataclasses import dataclass, field

logger = logging.getLogger("openmemo")


@dataclass
class SyncConfig:
    sync_interval: int = 30
    batch_size: int = 100
    conflict_strategy: str = "last_write_wins"
    max_retries: int = 3
    encryption_enabled: bool = False


SYNC_STATUS_PENDING = "pending"
SYNC_STATUS_SYNCED = "synced"
SYNC_STATUS_FAILED = "failed"
SYNC_STATUS_CONFLICT = "conflict"


class SyncEngine:
    def __init__(self, local_store=None, cloud_store=None,
                 config: SyncConfig = None, db_path: str = None):
        self.local_store = local_store
        self.cloud_store = cloud_store
        self.config = config or SyncConfig()
        self._queue: List[dict] = []
        self._last_sync = 0.0
        self._sync_count = 0
        self._conflict_count = 0
        self._error_count = 0
        self._lock = threading.Lock()

        self._sync_db = None
        self._sync_db_path = None
        if db_path:
            self._sync_db_path = db_path.replace(".db", "_sync.db") if db_path.endswith(".db") else db_path + "_sync"
            self._init_sync_db(self._sync_db_path)

    def _init_sync_db(self, db_path: str):
        self._sync_db = sqlite3.connect(db_path, check_same_thread=False)
        self._sync_db.row_factory = sqlite3.Row
        self._sync_db.executescript("""
            CREATE TABLE IF NOT EXISTS sync_queue (
                sync_id TEXT PRIMARY KEY,
                memory_id TEXT,
                operation TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                data TEXT DEFAULT '{}',
                retries INTEGER DEFAULT 0,
                created_at REAL,
                synced_at REAL
            );

            CREATE TABLE IF NOT EXISTS sync_versions (
                memory_id TEXT PRIMARY KEY,
                version INTEGER DEFAULT 1,
                local_hash TEXT DEFAULT '',
                cloud_hash TEXT DEFAULT '',
                updated_at REAL
            );

            CREATE TABLE IF NOT EXISTS sync_state (
                key TEXT PRIMARY KEY,
                value TEXT
            );
        """)
        self._sync_db.commit()

    def queue_sync(self, operation: str, data: dict):
        entry = {
            "sync_id": str(uuid.uuid4())[:12],
            "memory_id": data.get("id", data.get("edge_id", "")),
            "operation": operation,
            "status": SYNC_STATUS_PENDING,
            "data": data,
            "retries": 0,
            "created_at": time.time(),
        }

        with self._lock:
            self._queue.append(entry)

        if self._sync_db:
            try:
                with self._lock:
                    self._sync_db.execute(
                        "INSERT OR REPLACE INTO sync_queue (sync_id, memory_id, operation, status, data, retries, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                        (entry["sync_id"], entry["memory_id"], operation,
                         SYNC_STATUS_PENDING, json.dumps(data), 0, entry["created_at"]),
                    )
                    self._sync_db.commit()
            except Exception as e:
                logger.warning("[openmemo:sync] queue persist failed: %s", e)

    def push_sync(self) -> dict:
        if not self.cloud_store:
            return {"pushed": 0, "failed": 0, "error": "no cloud store"}

        pushed = 0
        failed = 0
        pending = self._get_pending()

        for entry in pending[:self.config.batch_size]:
            try:
                self._execute_sync(entry)
                entry["status"] = SYNC_STATUS_SYNCED
                pushed += 1
            except Exception as e:
                entry["retries"] = entry.get("retries", 0) + 1
                if entry["retries"] >= self.config.max_retries:
                    entry["status"] = SYNC_STATUS_FAILED
                    failed += 1
                    self._error_count += 1
                logger.warning("[openmemo:sync] push failed: %s", e)

            self._update_queue_entry(entry)

        self._sync_count += pushed
        self._last_sync = time.time()

        return {
            "pushed": pushed,
            "failed": failed,
            "remaining": max(0, len(pending) - self.config.batch_size),
        }

    def pull_sync(self, since: float = 0) -> dict:
        if not self.cloud_store or not self.local_store:
            return {"pulled": 0, "conflicts": 0, "error": "stores not configured"}

        pulled = 0
        conflicts = 0

        cloud_cells = self.cloud_store.list_cells(limit=self.config.batch_size)

        for cell in cloud_cells:
            created_at = cell.get("created_at", 0)
            if created_at <= since:
                continue

            local_cell = self.local_store.get_cell(cell.get("id", ""))

            if local_cell is None:
                self.local_store.put_cell(cell)
                pulled += 1
            else:
                resolved = self._resolve_conflict(local_cell, cell)
                if resolved != local_cell:
                    self.local_store.put_cell(resolved)
                    pulled += 1
                    conflicts += 1
                    self._conflict_count += 1

        self._last_sync = time.time()

        return {
            "pulled": pulled,
            "conflicts": conflicts,
        }

    def full_sync(self) -> dict:
        push_result = self.push_sync()
        pull_result = self.pull_sync()

        return {
            "push": push_result,
            "pull": pull_result,
            "timestamp": time.time(),
        }

    def _execute_sync(self, entry: dict):
        op = entry["operation"]
        data = entry.get("data", {})

        if op == "put_cell":
            self.cloud_store.put_cell(data)
        elif op == "put_note":
            self.cloud_store.put_note(data)
        elif op == "delete_cell":
            self.cloud_store.delete_cell(data.get("id", ""))
        elif op == "delete_note":
            self.cloud_store.delete_note(data.get("id", ""))
        elif op == "put_scene":
            self.cloud_store.put_scene(data)
        elif op == "put_edge":
            self.cloud_store.put_edge(data)
        elif op == "delete_edge":
            self.cloud_store.delete_edge(data.get("edge_id", ""))
        elif op == "put_skill":
            self.cloud_store.put_skill(data)
        elif op == "put_agent":
            self.cloud_store.put_agent(data)
        elif op == "delete_agent":
            self.cloud_store.delete_agent(data.get("agent_id", ""))
        else:
            logger.warning("[openmemo:sync] unknown operation: %s", op)

    def _resolve_conflict(self, local: dict, cloud: dict) -> dict:
        if self.config.conflict_strategy == "confidence":
            local_meta = local.get("metadata", {})
            cloud_meta = cloud.get("metadata", {})
            if isinstance(local_meta, str):
                try:
                    local_meta = json.loads(local_meta)
                except:
                    local_meta = {}
            if isinstance(cloud_meta, str):
                try:
                    cloud_meta = json.loads(cloud_meta)
                except:
                    cloud_meta = {}

            local_conf = local_meta.get("confidence", 0.5)
            cloud_conf = cloud_meta.get("confidence", 0.5)
            return cloud if cloud_conf > local_conf else local

        local_ts = local.get("last_accessed", local.get("created_at", 0))
        cloud_ts = cloud.get("last_accessed", cloud.get("created_at", 0))
        return cloud if cloud_ts > local_ts else local

    def _get_pending(self) -> List[dict]:
        if self._sync_db:
            try:
                with self._lock:
                    cursor = self._sync_db.execute(
                        "SELECT * FROM sync_queue WHERE status = ? ORDER BY created_at LIMIT ?",
                        (SYNC_STATUS_PENDING, self.config.batch_size),
                    )
                    rows = cursor.fetchall()
                entries = []
                for row in rows:
                    entry = dict(row)
                    entry["data"] = json.loads(entry.get("data", "{}"))
                    entries.append(entry)
                return entries
            except Exception:
                pass

        with self._lock:
            return [e for e in self._queue if e.get("status") == SYNC_STATUS_PENDING]

    def _update_queue_entry(self, entry: dict):
        if self._sync_db:
            try:
                with self._lock:
                    self._sync_db.execute(
                        "UPDATE sync_queue SET status = ?, retries = ?, synced_at = ? WHERE sync_id = ?",
                        (entry["status"], entry.get("retries", 0),
                         time.time() if entry["status"] == SYNC_STATUS_SYNCED else None,
                         entry["sync_id"]),
                    )
                    self._sync_db.commit()
            except Exception:
                pass

        with self._lock:
            for i, e in enumerate(self._queue):
                if e.get("sync_id") == entry.get("sync_id"):
                    self._queue[i] = entry
                    break

    def get_queue_size(self) -> int:
        if self._sync_db:
            try:
                with self._lock:
                    cursor = self._sync_db.execute(
                        "SELECT COUNT(*) FROM sync_queue WHERE status = ?",
                        (SYNC_STATUS_PENDING,),
                    )
                    return cursor.fetchone()[0]
            except Exception:
                pass
        with self._lock:
            return len([e for e in self._queue if e.get("status") == SYNC_STATUS_PENDING])

    def get_status(self) -> dict:
        return {
            "last_sync": self._last_sync,
            "sync_count": self._sync_count,
            "conflict_count": self._conflict_count,
            "error_count": self._error_count,
            "queue_size": self.get_queue_size(),
            "conflict_strategy": self.config.conflict_strategy,
        }

    def update_version(self, memory_id: str, version: int = None):
        if not self._sync_db:
            return

        try:
            cursor = self._sync_db.execute(
                "SELECT version FROM sync_versions WHERE memory_id = ?",
                (memory_id,),
            )
            row = cursor.fetchone()
            new_version = version or (row["version"] + 1 if row else 1)

            self._sync_db.execute(
                "INSERT OR REPLACE INTO sync_versions (memory_id, version, updated_at) VALUES (?, ?, ?)",
                (memory_id, new_version, time.time()),
            )
            self._sync_db.commit()
        except Exception as e:
            logger.warning("[openmemo:sync] version update failed: %s", e)

    def get_version(self, memory_id: str) -> int:
        if not self._sync_db:
            return 0
        try:
            cursor = self._sync_db.execute(
                "SELECT version FROM sync_versions WHERE memory_id = ?",
                (memory_id,),
            )
            row = cursor.fetchone()
            return row["version"] if row else 0
        except Exception:
            return 0

    def close(self):
        if self._sync_db:
            self._sync_db.close()

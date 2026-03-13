"""
Sync Worker — periodic background sync between local and cloud.

Runs at configurable intervals to push pending changes and pull updates.
"""

import time
import threading
import logging

logger = logging.getLogger("openmemo")


class SyncWorker:
    def __init__(self, sync_engine, interval: int = 30):
        self.sync_engine = sync_engine
        self.interval = interval
        self._running = False
        self._thread = None
        self._last_result = None

    def start(self):
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        logger.info("[openmemo:sync_worker] started (interval=%ds)", self.interval)

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
        logger.info("[openmemo:sync_worker] stopped")

    def _run_loop(self):
        while self._running:
            try:
                self._last_result = self.sync_engine.full_sync()
                logger.debug("[openmemo:sync_worker] sync result: %s", self._last_result)
            except Exception as e:
                logger.warning("[openmemo:sync_worker] sync error: %s", e)
            time.sleep(self.interval)

    def run_once(self) -> dict:
        try:
            self._last_result = self.sync_engine.full_sync()
            return self._last_result
        except Exception as e:
            logger.warning("[openmemo:sync_worker] sync error: %s", e)
            return {"error": str(e)}

    @property
    def is_running(self) -> bool:
        return self._running

    def get_status(self) -> dict:
        return {
            "running": self._running,
            "interval": self.interval,
            "last_result": self._last_result,
        }

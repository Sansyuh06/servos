"""
Servos – File System Watcher.
Detects modifications in configured directories.
"""

import time
import threading
from pathlib import Path
from typing import Callable, List, Dict


class FileWatcher:
    def __init__(self, paths: List[str], callback: Callable[[Dict], None], poll_interval: float = 2.0):
        self.paths = paths
        self.callback = callback
        self.poll_interval = poll_interval
        self._snapshot: Dict[str, float] = {}
        self._running = False
        self._thread: threading.Thread | None = None

    def start(self):
        if self._running:
            return
        self._running = True
        self._snapshot = self._take_snapshot()
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)

    def _take_snapshot(self) -> Dict[str, float]:
        snap = {}
        for base in self.paths:
            for p in Path(base).rglob('*'):
                try:
                    snap[str(p)] = p.stat().st_mtime
                except Exception:
                    pass
        return snap

    def _loop(self):
        while self._running:
            time.sleep(self.poll_interval)
            new_snap = self._take_snapshot()
            changed = [p for p, m in new_snap.items() if p not in self._snapshot or self._snapshot.get(p) != m]
            if changed:
                try:
                    self.callback({'modified': changed})
                except Exception:
                    pass
            self._snapshot = new_snap

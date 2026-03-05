"""
Servos – Network Monitor.
Tracks network interface changes and reports alerts.
"""

import time
import threading
from typing import Callable, List, Dict

import psutil


class NetworkMonitor:
    def __init__(self, callback: Callable[[Dict], None], poll_interval: float = 2.0):
        self.callback = callback
        self.poll_interval = poll_interval
        self._known: List[str] = []
        self._running = False
        self._thread: threading.Thread | None = None

    def start(self):
        if self._running:
            return
        self._running = True
        self._known = self._current_interfaces()
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)

    def _current_interfaces(self) -> List[str]:
        return list(psutil.net_if_addrs().keys())

    def _loop(self):
        while self._running:
            time.sleep(self.poll_interval)
            current = self._current_interfaces()
            added = set(current) - set(self._known)
            removed = set(self._known) - set(current)
            if added or removed:
                event = {"added": list(added), "removed": list(removed)}
                try:
                    self.callback(event)
                except Exception:
                    pass
            self._known = current

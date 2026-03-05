"""
Servos – Process Monitor.
Watches for new or suspicious processes.
"""

import time
import threading
from typing import Callable, Set, Dict

import psutil


class ProcessMonitor:
    def __init__(self, callback: Callable[[Dict], None], poll_interval: float = 2.0):
        self.callback = callback
        self.poll_interval = poll_interval
        self._known_pids: Set[int] = set()
        self._running = False
        self._thread: threading.Thread | None = None

    def start(self):
        if self._running:
            return
        self._running = True
        self._known_pids = {p.pid for p in psutil.process_iter(['pid'])}
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)

    def _loop(self):
        while self._running:
            time.sleep(self.poll_interval)
            current = {p.pid for p in psutil.process_iter(['pid'])}
            new = current - self._known_pids
            if new:
                procs = []
                for pid in new:
                    try:
                        p = psutil.Process(pid)
                        procs.append({'pid': pid, 'name': p.name()})
                    except Exception:
                        pass
                if procs:
                    try:
                        self.callback({'new_processes': procs})
                    except Exception:
                        pass
            self._known_pids = current

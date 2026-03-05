"""
Coordinator that launches multiple forensic scans concurrently and handles results.
"""

import threading
from typing import Dict, Any, List, Callable


class MultiScanCoordinator:
    def __init__(self, scan_funcs: List[Callable[..., Dict[str, Any]]], callback: Callable[[Dict[str, Any]], None]):
        self.scan_funcs = scan_funcs
        self.callback = callback

    def run_all(self):
        threads = []
        for func in self.scan_funcs:
            t = threading.Thread(target=self._run_and_callback, args=(func,))
            t.daemon = True
            t.start()
            threads.append(t)
        # optionally join if synchronous
        for t in threads:
            t.join()

    def _run_and_callback(self, func: Callable[..., Dict[str, Any]]):
        try:
            result = func()
            self.callback(result)
        except Exception as e:
            self.callback({'error': str(e)})

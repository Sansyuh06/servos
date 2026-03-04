"""
Servos – Log Analyzer Module.
Parses various log formats and produces structured events.
"""

import os
from typing import List, Dict, Any


class LogAnalyzer:
    def analyze_file(self, path: str) -> List[Dict[str, Any]]:
        events: List[Dict[str, Any]] = []
        if path.lower().endswith(".evtx"):
            # requires evtx package
            try:
                import Evtx
                with Evtx.Evtx(path) as log:
                    for record in log.records():
                        events.append({"timestamp": record.timestamp(), "xml": record.xml()})
            except ImportError:
                pass
        else:
            # simple text parser, split lines
            try:
                with open(path, encoding="utf-8", errors="ignore") as f:
                    for line in f:
                        events.append({"line": line.strip()})
            except Exception:
                pass
        return events

    def analyze_directory(self, root: str) -> Dict[str, List[Dict[str, Any]]]:
        results: Dict[str, List[Dict[str, Any]]] = {}
        for dirpath, dirnames, filenames in os.walk(root):
            for fn in filenames:
                full = os.path.join(dirpath, fn)
                results[full] = self.analyze_file(full)
        return results

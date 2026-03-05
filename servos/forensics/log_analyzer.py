"""
Servos – Log Analyzer Module.
Parses various log formats and produces structured events.  Also contains a
pattern matcher that can flag common attack vectors such as failed logins,
encoded PowerShell, lateral movement, etc.  Results from ``analyze_patterns``
are intended for inclusion in case reports and risk dashboards.
"""

import os
import re
from dataclasses import dataclass
from typing import List, Dict, Any, Optional


@dataclass
class LogThreat:
    """Represents a suspicious log entry matched by a known pattern."""
    pattern_name: str
    severity: str     # low, medium, high
    matched_line: str
    timestamp: str
    file_path: str


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

    # ------------------------------------------------------------------
    # Pattern matcher
    # ------------------------------------------------------------------
    def analyze_patterns(self, path: str) -> List[LogThreat]:
        """Scan a single log file for known malicious patterns.

        Returns a list of :class:`LogThreat` objects sorted by severity.
        Duplicate line matches are collapsed.
        """
        pattern_defs = {
            "FAILED_LOGIN": re.compile(r"(failed|failure|invalid).{0,30}(login|password|auth)", re.I),
            "ENCODED_POWERSHELL": re.compile(r"powershell.{0,50}(-enc|-encodedcommand)", re.I),
            "PRIVILEGE_ESCALATION": re.compile(r"(sudo|runas|privilege|UAC).{0,30}(granted|escalat|bypass)", re.I),
            "LATERAL_MOVEMENT": re.compile(r"(net use|psexec|wmic|at\.exe|schtasks)", re.I),
            "DATA_EXFIL": re.compile(r"(curl|wget|ftp|upload|POST).{0,50}(http|ftp|sftp)", re.I),
            "RANSOMWARE_INDICATOR": re.compile(r"\.(locked|encrypted|crypt|ransom)", re.I),
            "CLEARED_LOGS": re.compile(r"(eventlog|auditlog|clearev|wevtutil).{0,20}(clear|delete|wipe)", re.I),
        }

        # read file lines first
        try:
            with open(path, encoding="utf-8", errors="ignore") as f:
                lines = [l.rstrip("\n") for l in f]
        except Exception:
            return []

        matches: Dict[str, List[str]] = {name: [] for name in pattern_defs}
        for line in lines:
            for name, regex in pattern_defs.items():
                if regex.search(line):
                    matches[name].append(line)

        # build LogThreat objects
        threats: List[LogThreat] = []
        seen: set = set()

        # timestamp extractor (common iso/datetime at beginning)
        ts_re = re.compile(r"(\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2})")

        for name, lines_matched in matches.items():
            if not lines_matched:
                continue
            severity = "high"
            if name == "FAILED_LOGIN":
                # promote to medium only if many occurrences
                severity = "medium" if len(lines_matched) >= 5 else "low"
            elif name in ("CLEARED_LOGS",):
                severity = "medium"

            for ln in lines_matched:
                key = (name, ln)
                if key in seen:
                    continue
                seen.add(key)
                ts_match = ts_re.search(ln)
                ts = ts_match.group(1) if ts_match else ""
                threats.append(LogThreat(
                    pattern_name=name,
                    severity=severity,
                    matched_line=ln,
                    timestamp=ts,
                    file_path=path,
                ))

        # sort by severity (high > medium > low)
        order = {"high": 0, "medium": 1, "low": 2}
        threats.sort(key=lambda t: order.get(t.severity, 3))
        return threats


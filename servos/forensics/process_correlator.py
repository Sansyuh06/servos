"""
Link processes to files discovered during analysis.

Used to identify cases where a running or recently executed process
corresponds to a file found on the device, particularly when the file
appears in a suspicious location or has a high threat score.
"""

import os
from dataclasses import dataclass
from typing import List, Dict, Any

from servos.models.schema import FileMetadata


@dataclass
class Correlation:
    process_name: str
    process_pid: int
    matched_file_path: str
    match_type: str      # NAME_MATCH, PATH_MATCH, SUSPICIOUS_LOCATION, MASQUERADE
    severity: str        # low, medium, high, critical


class ProcessCorrelator:
    """Analyze relationships between process snapshots and file listings."""

    SYSTEM_PROCESS_NAMES = {"svchost", "explorer", "lsass", "services"}
    SUSPICIOUS_DIRS = ["\\temp\\", "\\appdata\\", "/temp/", "/appdata/", "downloads"]

    def correlate(self, processes: List[Dict[str, Any]],
                  files: List[FileMetadata]) -> List[Correlation]:
        """Return a list of correlations between the given *processes* and *files*.

        ``processes`` is a list of dictionaries coming from ProcessMonitor or
        similar snapshot; it may contain keys ``name``, ``pid`` and optionally
        ``exe`` (full path to executable).  ``files`` is the list produced by
        FileAnalyzer (``FileMetadata`` objects).
        """
        corrs: List[Correlation] = []

        # build quick lookup from path to FileMetadata
        file_map = {f.full_path.lower(): f for f in files}

        for proc in processes:
            pname = proc.get("name", "").lower()
            pid = proc.get("pid", 0)
            ppath = proc.get("exe", "") or proc.get("path", "")
            ppath = ppath.lower()

            # 1. NAME_MATCH: process name equals filename without extension
            for f in files:
                fname_noext = os.path.splitext(os.path.basename(f.full_path))[0].lower()
                if pname == fname_noext and f.full_path:
                    severity = "medium"
                    if f.suspicious or f.entropy > 7.0:
                        severity = "high"
                    corrs.append(Correlation(
                        process_name=pname,
                        process_pid=pid,
                        matched_file_path=f.full_path,
                        match_type="NAME_MATCH",
                        severity=severity,
                    ))

            # 2. PATH_MATCH: executable path appears in file listing
            if ppath and ppath in file_map:
                f = file_map[ppath]
                severity = "medium"
                if f.suspicious or f.entropy > 7.0:
                    severity = "high"
                corrs.append(Correlation(
                    process_name=pname,
                    process_pid=pid,
                    matched_file_path=f.full_path,
                    match_type="PATH_MATCH",
                    severity=severity,
                ))

            # 3. SUSPICIOUS_LOCATION: process running from strange directory and
            #    a matching file exists there
            if ppath and any(dirfrag in ppath for dirfrag in self.SUSPICIOUS_DIRS):
                if ppath in file_map:
                    corrs.append(Correlation(
                        process_name=pname,
                        process_pid=pid,
                        matched_file_path=ppath,
                        match_type="SUSPICIOUS_LOCATION",
                        severity="high",
                    ))

            # 4. MASQUERADE: process has a system-like name but not located in
            #    system32
            if pname in self.SYSTEM_PROCESS_NAMES:
                if ppath and "system32" not in ppath:
                    severity = "high"
                    corrs.append(Correlation(
                        process_name=pname,
                        process_pid=pid,
                        matched_file_path=ppath,
                        match_type="MASQUERADE",
                        severity=severity,
                    ))

        return corrs

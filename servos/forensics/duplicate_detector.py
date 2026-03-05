"""
Duplicate file detection utilities.

The goal is to identify files that share the same SHA-256 hash and flag
suspicious groups, particularly executable masquerading or cross-directory
duplication between system and user data.
"""

import os
from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass
class DuplicateAlert:
    sha256: str
    files: List[str]
    reason: str
    severity: str  # 'low','medium','high','critical'


class DuplicateDetector:
    """Identify duplicate files based on integrity hashes."""

    def find_duplicates(self, integrity_hashes: Dict[str, str]) -> Dict[str, List[str]]:
        """Invert a map of filepath->sha256 into sha256->[filepaths] grouping.

        Only groups containing two or more entries are returned.
        """
        dupes: Dict[str, List[str]] = {}
        for fp, h in integrity_hashes.items():
            if not h:
                continue
            dupes.setdefault(h, []).append(fp)
        # remove singletons
        return {h: fps for h, fps in dupes.items() if len(fps) > 1}

    def find_suspicious_duplicates(self, dupes: Dict[str, List[str]]) -> List[DuplicateAlert]:
        """Flag groups of duplicates that look suspicious.

        * executables duplicated in temp/startup/system directories
        * duplicates crossing user and system paths
        * masquerading where same hash used for a document and an exe
        """
        alerts: List[DuplicateAlert] = []
        for h, fps in dupes.items():
            has_exe = any(fp.lower().endswith(('.exe', '.dll', '.sys', '.com', '.bat', '.cmd')) for fp in fps)
            user_paths = [fp for fp in fps if any(part.lower() in fp.lower() for part in ('users', 'documents', 'downloads', 'desktop'))]
            system_paths = [fp for fp in fps if any(part.lower() in fp.lower() for part in ('\\windows\\', '\\system32\\', '\\syswow64\\'))]

            # check masquerade
            exts = set(os.path.splitext(fp)[1].lower() for fp in fps)
            if has_exe and len(exts) > 1:
                alerts.append(DuplicateAlert(
                    sha256=h,
                    files=fps,
                    reason="Same hash used by executable and non-executable file",
                    severity="high",
                ))
                continue

            # check cross user/system duplication
            if user_paths and system_paths:
                alerts.append(DuplicateAlert(
                    sha256=h,
                    files=fps,
                    reason="File present in both user and system directories",
                    severity="medium",
                ))
                continue

            # executables in strange places
            temp_dir = os.getenv('TEMP', '').lower()
            if has_exe and any((temp_dir and fp.lower().startswith(temp_dir)) or '/temp/' in fp.lower() or '\\temp\\' in fp.lower() or '/startup' in fp.lower() for fp in fps):
                alerts.append(DuplicateAlert(
                    sha256=h,
                    files=fps,
                    reason="Executable duplicated in temp/startup location",
                    severity="high",
                ))
                continue

        return alerts

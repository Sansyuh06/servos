"""
Recycle Bin parser for Windows $Recycle.Bin artifacts.

Parses metadata files ($I*) to recover original paths, sizes and deletion
timestamps, and pairs them with the corresponding $R* content files.  This is
useful for identifying recently deleted executables and files of interest.
"""

import os
import struct
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Optional


@dataclass
class DeletedFileRecord:
    original_path: str
    deleted_at: str          # ISO8601
    file_size: int
    bin_path: str            # path to $I file
    severity: str            # 'low','medium','high'


class RecycleBinParser:
    """Locate and parse Recycle Bin stubs on a given device path."""

    def parse(self, device_path: str,
              window_start: Optional[datetime] = None,
              window_end: Optional[datetime] = None) -> List[DeletedFileRecord]:
        """Scan *device_path* for $Recycle.Bin entries.

        *window_start* and *window_end* may be provided to help flag records
        deleted within the investigation time window.  If omitted, the last
        30 days are treated as the window.
        """
        records: List[DeletedFileRecord] = []

        if window_end is None:
            window_end = datetime.utcnow()
        if window_start is None:
            window_start = window_end - timedelta(days=30)

        # walk the recycle bin directory structure
        for root, dirs, files in os.walk(device_path):
            for fname in files:
                if not fname.startswith("$I"):
                    continue
                i_path = os.path.join(root, fname)
                try:
                    with open(i_path, "rb") as f:
                        data = f.read()
                except (OSError, PermissionError):
                    continue

                # parse metadata structure
                if len(data) < 16:
                    continue
                file_size = struct.unpack_from("<Q", data, 0)[0]
                ft_raw = struct.unpack_from("<Q", data, 8)[0]
                # convert FILETIME (100-ns since 1601) to datetime
                deleted_dt = datetime.utcfromtimestamp((ft_raw - 116444736000000000) / 1e7)
                # rest is UTF-16LE path
                try:
                    path_bytes = data[16:]
                    orig_path = path_bytes.decode("utf-16le", errors="ignore").rstrip("\x00")
                except Exception:
                    orig_path = ""

                # severity heuristics
                sev = "low"
                if orig_path.lower().endswith(('.exe', '.dll', '.com', '.bat', '.cmd', '.scr')):
                    sev = "high"
                elif window_start <= deleted_dt <= window_end:
                    sev = "medium"

                records.append(DeletedFileRecord(
                    original_path=orig_path,
                    deleted_at=deleted_dt.isoformat(),
                    file_size=file_size,
                    bin_path=i_path,
                    severity=sev,
                ))
        return records

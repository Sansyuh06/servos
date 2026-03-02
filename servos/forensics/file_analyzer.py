"""
Servos – File System Analyzer.
Recursively enumerate files, capture metadata, detect anomalies.
"""

import os
import math
import stat
from datetime import datetime
from typing import List, Dict
from collections import Counter

from servos.models.schema import FileMetadata, FileSystemAnalysis


# Common suspicious extensions
SUSPICIOUS_EXTENSIONS = {
    ".exe", ".bat", ".cmd", ".com", ".scr", ".pif", ".vbs", ".vbe",
    ".js", ".jse", ".wsf", ".wsh", ".ps1", ".msi", ".dll", ".sys",
}

# Extensions that should NOT contain high entropy (possible encryption / packing)
LOW_ENTROPY_EXPECTED = {
    ".txt", ".csv", ".html", ".htm", ".xml", ".json", ".md", ".log",
}


class FileAnalyzer:
    """Analyze file system structure and content."""

    def __init__(self, scan_hidden: bool = True, max_file_size_mb: int = 500):
        self.scan_hidden = scan_hidden
        self.max_file_bytes = max_file_size_mb * 1024 * 1024

    def analyze(self, root_path: str) -> FileSystemAnalysis:
        """Perform full file system analysis on the given path."""
        result = FileSystemAnalysis()
        type_counter: Counter = Counter()

        for dirpath, dirnames, filenames in os.walk(root_path):
            result.total_dirs += 1
            for fname in filenames:
                fpath = os.path.join(dirpath, fname)
                meta = self._get_metadata(fpath)
                if meta is None:
                    continue

                result.total_files += 1
                result.total_size_bytes += meta.file_size
                result.files.append(meta)

                ext = meta.extension.lower() if meta.extension else "(no ext)"
                type_counter[ext] += 1

                if meta.is_hidden:
                    result.hidden_files += 1

                if meta.suspicious:
                    result.suspicious_files.append(meta)

        result.file_type_counts = dict(type_counter.most_common())
        return result

    def _get_metadata(self, filepath: str) -> FileMetadata | None:
        """Extract metadata for a single file."""
        try:
            st = os.stat(filepath)
        except (PermissionError, OSError):
            return None

        fname = os.path.basename(filepath)
        ext = os.path.splitext(fname)[1]
        is_hidden = fname.startswith(".") or bool(st.st_file_attributes & stat.FILE_ATTRIBUTE_HIDDEN) if hasattr(st, "st_file_attributes") else fname.startswith(".")

        meta = FileMetadata(
            filename=fname,
            full_path=filepath,
            file_size=st.st_size,
            created=datetime.fromtimestamp(st.st_ctime).isoformat(),
            modified=datetime.fromtimestamp(st.st_mtime).isoformat(),
            accessed=datetime.fromtimestamp(st.st_atime).isoformat(),
            is_hidden=is_hidden,
            extension=ext,
        )

        # Check for suspicious indicators
        suspicious_reasons = []

        # 1) Executable on a USB
        if ext.lower() in SUSPICIOUS_EXTENSIONS:
            suspicious_reasons.append(f"Executable extension: {ext}")

        # 2) Extension mismatch (very basic: .exe with wrong header)
        if ext.lower() in {".pdf", ".docx", ".xlsx", ".jpg", ".png"}:
            if st.st_size > 0 and st.st_size < 100:
                suspicious_reasons.append("File too small for declared type")

        # 3) Entropy analysis (only for small-ish files)
        if st.st_size > 0 and st.st_size <= self.max_file_bytes:
            try:
                ent = self._calculate_entropy(filepath)
                meta.entropy = round(ent, 2)
                if ent > 7.0 and ext.lower() in LOW_ENTROPY_EXPECTED:
                    suspicious_reasons.append(f"High entropy ({ent:.1f}) for {ext} file")
            except Exception:
                pass

        if suspicious_reasons:
            meta.suspicious = True
            meta.suspicious_reason = "; ".join(suspicious_reasons)

        return meta

    @staticmethod
    def _calculate_entropy(filepath: str, block_size: int = 65536) -> float:
        """Calculate Shannon entropy of a file (0-8 for byte data)."""
        byte_counts = [0] * 256
        total = 0
        try:
            with open(filepath, "rb") as f:
                while True:
                    data = f.read(block_size)
                    if not data:
                        break
                    for b in data:
                        byte_counts[b] += 1
                    total += len(data)
        except (PermissionError, OSError):
            return 0.0

        if total == 0:
            return 0.0

        entropy = 0.0
        for count in byte_counts:
            if count == 0:
                continue
            p = count / total
            entropy -= p * math.log2(p)
        return entropy

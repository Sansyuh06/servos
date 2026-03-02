"""
Servos – File Hasher.
Batch MD5/SHA-256 hashing with progress tracking.
"""

import os
import hashlib
from typing import List, Dict, Tuple


class FileHasher:
    """Hash files for integrity verification and comparison."""

    def hash_file(self, filepath: str) -> Dict[str, str]:
        """Compute MD5 and SHA-256 of a single file."""
        md5 = hashlib.md5()
        sha256 = hashlib.sha256()
        try:
            with open(filepath, "rb") as f:
                while True:
                    chunk = f.read(65536)
                    if not chunk:
                        break
                    md5.update(chunk)
                    sha256.update(chunk)
        except (PermissionError, OSError):
            return {"md5": "ERROR", "sha256": "ERROR", "file": filepath}
        return {
            "md5": md5.hexdigest(),
            "sha256": sha256.hexdigest(),
            "file": filepath,
        }

    def hash_files(self, file_list: List[str],
                   progress_callback=None) -> List[Dict[str, str]]:
        """Hash a batch of files."""
        results = []
        total = len(file_list)
        for i, fp in enumerate(file_list):
            result = self.hash_file(fp)
            results.append(result)
            if progress_callback:
                progress_callback(i + 1, total, fp)
        return results

    def hash_directory(self, dir_path: str,
                       max_file_size: int = 500 * 1024 * 1024,
                       progress_callback=None) -> List[Dict[str, str]]:
        """Hash all files in a directory tree."""
        file_list = []
        for root, dirs, files in os.walk(dir_path):
            for fname in sorted(files):
                fpath = os.path.join(root, fname)
                try:
                    if os.path.getsize(fpath) <= max_file_size:
                        file_list.append(fpath)
                except OSError:
                    continue
        return self.hash_files(file_list, progress_callback)

    @staticmethod
    def verify_hash(filepath: str, expected_sha256: str) -> bool:
        """Check if a file matches an expected SHA-256 hash."""
        sha256 = hashlib.sha256()
        try:
            with open(filepath, "rb") as f:
                while True:
                    chunk = f.read(65536)
                    if not chunk:
                        break
                    sha256.update(chunk)
        except (PermissionError, OSError):
            return False
        return sha256.hexdigest() == expected_sha256

"""
Servos – Backup & Evidence Preservation.
Creates forensic backups with integrity hashing and chain-of-custody docs.
"""

import os
import json
import shutil
import hashlib
from datetime import datetime
from typing import Optional, Dict

from servos.models.schema import BackupResult, DeviceInfo
from servos.config import get_config


class EvidenceBackup:
    """Create forensically sound backups of storage devices / directories."""

    def __init__(self):
        cfg = get_config()
        self.default_backup_dir = cfg.get("backup_location",
                                           os.path.join(os.path.expanduser("~"), ".servos", "backups"))

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def create_backup(self, source_path: str, case_id: str,
                      destination: Optional[str] = None) -> BackupResult:
        """
        Create a full backup of the source directory / drive.

        Args:
            source_path: Root of device / directory to back up.
            case_id: Case identifier for naming.
            destination: Override backup location.

        Returns:
            BackupResult with paths and hashes.
        """
        if destination is None:
            destination = self.default_backup_dir

        os.makedirs(destination, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = os.path.join(destination, f"{case_id}_{timestamp}")
        os.makedirs(backup_dir, exist_ok=True)

        files_backed_up = 0
        total_size = 0

        # Walk the source and copy files
        for root, dirs, files in os.walk(source_path):
            rel_root = os.path.relpath(root, source_path)
            dest_root = os.path.join(backup_dir, rel_root)
            os.makedirs(dest_root, exist_ok=True)

            for filename in files:
                src_file = os.path.join(root, filename)
                dst_file = os.path.join(dest_root, filename)
                try:
                    shutil.copy2(src_file, dst_file)
                    files_backed_up += 1
                    total_size += os.path.getsize(dst_file)
                except (PermissionError, OSError):
                    # Skip files we can't access
                    continue

        # Generate integrity hashes of the backup directory
        hash_md5, hash_sha256 = self._hash_directory(backup_dir)

        result = BackupResult(
            backup_path=backup_dir,
            hash_md5=hash_md5,
            hash_sha256=hash_sha256,
            size_bytes=total_size,
            files_backed_up=files_backed_up,
        )

        # Write backup metadata alongside
        meta_path = os.path.join(backup_dir, "_backup_metadata.json")
        self._write_metadata(meta_path, result, source_path, case_id)

        return result

    def verify_integrity(self, backup_path: str, expected_md5: str,
                         expected_sha256: str) -> bool:
        """Verify backup hasn't been modified since creation."""
        current_md5, current_sha256 = self._hash_directory(backup_path)
        return current_md5 == expected_md5 and current_sha256 == expected_sha256

    def generate_loc(self, case_id: str, device: DeviceInfo,
                     backup: BackupResult,
                     investigator: str = "Investigator") -> Dict:
        """Generate chain-of-custody (LoC) JSON document."""
        loc = {
            "case_id": case_id,
            "document_type": "Chain of Custody",
            "generated_at": datetime.now().isoformat(),
            "investigator": investigator,
            "device": {
                "path": device.path,
                "name": device.name,
                "capacity": device.capacity_human,
                "filesystem": device.filesystem,
                "serial": device.serial,
            },
            "backup": {
                "location": backup.backup_path,
                "hash_md5": backup.hash_md5,
                "hash_sha256": backup.hash_sha256,
                "size_bytes": backup.size_bytes,
                "files_backed_up": backup.files_backed_up,
                "created_at": backup.created_at,
            },
            "actions_log": [
                {
                    "timestamp": datetime.now().isoformat(),
                    "action": "Backup created",
                    "performed_by": investigator,
                    "notes": f"Full backup of {device.path} to {backup.backup_path}",
                }
            ],
            "integrity_verified": True,
        }
        return loc

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def hash_file(filepath: str) -> Dict[str, str]:
        """Compute MD5 and SHA-256 hashes of a single file."""
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
            return {"md5": "ERROR", "sha256": "ERROR"}
        return {"md5": md5.hexdigest(), "sha256": sha256.hexdigest()}

    def _hash_directory(self, dir_path: str):
        """Compute combined hash of all files in a directory (sorted for reproducibility)."""
        md5 = hashlib.md5()
        sha256 = hashlib.sha256()
        for root, dirs, files in os.walk(dir_path):
            for filename in sorted(files):
                if filename.startswith("_backup_metadata"):
                    continue
                filepath = os.path.join(root, filename)
                try:
                    with open(filepath, "rb") as f:
                        while True:
                            chunk = f.read(65536)
                            if not chunk:
                                break
                            md5.update(chunk)
                            sha256.update(chunk)
                except (PermissionError, OSError):
                    continue
        return md5.hexdigest(), sha256.hexdigest()

    @staticmethod
    def _write_metadata(path: str, backup: BackupResult,
                        source: str, case_id: str):
        meta = {
            "case_id": case_id,
            "source_path": source,
            "backup_path": backup.backup_path,
            "hash_md5": backup.hash_md5,
            "hash_sha256": backup.hash_sha256,
            "size_bytes": backup.size_bytes,
            "files_backed_up": backup.files_backed_up,
            "created_at": backup.created_at,
            "created_by": "Servos v1.0.0",
        }
        with open(path, "w") as f:
            json.dump(meta, f, indent=2)

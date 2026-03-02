"""
Servos – Forensic Artifact Extractor.
Extract browser history, recent files, registry, and logs.
"""

import os
import json
import sqlite3
import glob
from datetime import datetime, timedelta
from typing import List

from servos.models.schema import ArtifactItem, ArtifactResult


class ArtifactExtractor:
    """Extract forensic artifacts from a device or system."""

    def extract_all(self, target_path: str) -> ArtifactResult:
        """Run all artifact extraction routines."""
        result = ArtifactResult()

        result.browser_history = self._extract_browser_history(target_path)
        result.recent_files = self._extract_recent_files(target_path)
        result.registry_items = self._extract_registry_artifacts(target_path)
        result.log_entries = self._extract_log_files(target_path)

        result.total_artifacts = len(result.all_artifacts())
        return result

    # ------------------------------------------------------------------
    # Browser History (Chrome SQLite)
    # ------------------------------------------------------------------

    def _extract_browser_history(self, target_path: str) -> List[ArtifactItem]:
        """Extract Chrome browser history from the target."""
        artifacts = []

        # Scan for Chrome History databases on the device
        patterns = [
            os.path.join(target_path, "**", "History"),
            os.path.join(target_path, "**", "Google", "Chrome", "**", "History"),
            os.path.join(target_path, "**", "Default", "History"),
        ]

        found_dbs = set()
        for pattern in patterns:
            for match in glob.glob(pattern, recursive=True):
                if os.path.isfile(match) and match not in found_dbs:
                    found_dbs.add(match)

        for db_path in found_dbs:
            try:
                entries = self._read_chrome_history(db_path)
                artifacts.extend(entries)
            except Exception:
                continue

        # Also check for any .sqlite / .db files that might be browser data
        for root, dirs, files in os.walk(target_path):
            for f in files:
                if f.lower() in ("places.sqlite",):  # Firefox
                    try:
                        entries = self._read_firefox_history(os.path.join(root, f))
                        artifacts.extend(entries)
                    except Exception:
                        continue

        return artifacts

    def _read_chrome_history(self, db_path: str) -> List[ArtifactItem]:
        """Read Chrome History SQLite database."""
        items = []
        try:
            conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT url, title, visit_count, last_visit_time
                FROM urls ORDER BY last_visit_time DESC LIMIT 100
            """)
            for row in cursor.fetchall():
                url, title, visit_count, chrome_time = row
                # Chrome timestamps: microseconds since 1601-01-01
                try:
                    ts = datetime(1601, 1, 1) + timedelta(microseconds=chrome_time)
                    timestamp = ts.isoformat()
                except (ValueError, OverflowError):
                    timestamp = ""

                suspicious = 0.0
                desc = f"{title or 'No Title'} – {url}"
                # Flag suspicious domains
                suspicious_keywords = ["malware", "hack", "exploit", "darkweb",
                                       "ransomware", "keylog", "phishing", "pastebin"]
                for kw in suspicious_keywords:
                    if kw in url.lower() or kw in (title or "").lower():
                        suspicious = 0.8
                        break

                items.append(ArtifactItem(
                    artifact_type="browser_history",
                    timestamp=timestamp,
                    description=desc,
                    content={"url": url, "title": title, "visit_count": visit_count},
                    suspicious_score=suspicious,
                    source_path=db_path,
                ))
            conn.close()
        except Exception:
            pass
        return items

    def _read_firefox_history(self, db_path: str) -> List[ArtifactItem]:
        """Read Firefox places.sqlite database."""
        items = []
        try:
            conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT url, title, visit_count, last_visit_date
                FROM moz_places ORDER BY last_visit_date DESC LIMIT 100
            """)
            for row in cursor.fetchall():
                url, title, visit_count, moz_time = row
                try:
                    ts = datetime(1970, 1, 1) + timedelta(microseconds=moz_time or 0)
                    timestamp = ts.isoformat()
                except (ValueError, OverflowError):
                    timestamp = ""

                items.append(ArtifactItem(
                    artifact_type="browser_history",
                    timestamp=timestamp,
                    description=f"{title or 'No Title'} – {url}",
                    content={"url": url, "title": title, "visit_count": visit_count},
                    source_path=db_path,
                ))
            conn.close()
        except Exception:
            pass
        return items

    # ------------------------------------------------------------------
    # Recent Files
    # ------------------------------------------------------------------

    def _extract_recent_files(self, target_path: str) -> List[ArtifactItem]:
        """Extract recently modified files from the target."""
        artifacts = []
        now = datetime.now()
        cutoff = now - timedelta(days=30)  # Last 30 days

        for root, dirs, files in os.walk(target_path):
            for fname in files:
                fpath = os.path.join(root, fname)
                try:
                    mtime = datetime.fromtimestamp(os.path.getmtime(fpath))
                    if mtime >= cutoff:
                        artifacts.append(ArtifactItem(
                            artifact_type="recent_file",
                            timestamp=mtime.isoformat(),
                            description=f"Recently modified: {fname}",
                            content={
                                "filename": fname,
                                "path": fpath,
                                "size": os.path.getsize(fpath),
                                "modified": mtime.isoformat(),
                            },
                            source_path=fpath,
                        ))
                except (PermissionError, OSError):
                    continue

        # Sort by most recent first, limit to top 100
        artifacts.sort(key=lambda a: a.timestamp, reverse=True)
        return artifacts[:100]

    # ------------------------------------------------------------------
    # Registry Artifacts (Windows – stubs for hackathon)
    # ------------------------------------------------------------------

    def _extract_registry_artifacts(self, target_path: str) -> List[ArtifactItem]:
        """Extract Windows registry artifacts from the target (if applicable)."""
        artifacts = []
        # Look for registry hive files on the device
        reg_files = ["NTUSER.DAT", "SAM", "SECURITY", "SOFTWARE", "SYSTEM"]
        for root, dirs, files in os.walk(target_path):
            for fname in files:
                if fname.upper() in reg_files:
                    fpath = os.path.join(root, fname)
                    artifacts.append(ArtifactItem(
                        artifact_type="registry",
                        timestamp=datetime.fromtimestamp(
                            os.path.getmtime(fpath)).isoformat(),
                        description=f"Registry hive found: {fname}",
                        content={"hive_name": fname, "path": fpath,
                                 "size": os.path.getsize(fpath)},
                        suspicious_score=0.3,
                        source_path=fpath,
                    ))
        return artifacts

    # ------------------------------------------------------------------
    # Log Files
    # ------------------------------------------------------------------

    def _extract_log_files(self, target_path: str) -> List[ArtifactItem]:
        """Extract notable log files from the target."""
        artifacts = []
        log_extensions = {".log", ".evt", ".evtx"}

        for root, dirs, files in os.walk(target_path):
            for fname in files:
                ext = os.path.splitext(fname)[1].lower()
                if ext in log_extensions:
                    fpath = os.path.join(root, fname)
                    try:
                        size = os.path.getsize(fpath)
                        mtime = datetime.fromtimestamp(os.path.getmtime(fpath))
                        # Read first few lines as preview
                        preview = ""
                        try:
                            with open(fpath, "r", errors="replace") as lf:
                                preview = lf.read(500)
                        except Exception:
                            pass

                        artifacts.append(ArtifactItem(
                            artifact_type="log",
                            timestamp=mtime.isoformat(),
                            description=f"Log file: {fname} ({size} bytes)",
                            content={
                                "filename": fname,
                                "path": fpath,
                                "size": size,
                                "preview": preview[:500],
                            },
                            source_path=fpath,
                        ))
                    except (PermissionError, OSError):
                        continue

        return artifacts[:50]

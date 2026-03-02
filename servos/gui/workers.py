"""
Servos – Background Worker Threads.
Non-blocking investigation, scan, and device detection workers.
"""

import os
import json
import traceback

from PyQt6.QtCore import QThread, pyqtSignal

from servos.config import get_config
from servos.models.schema import (
    DeviceInfo, Case, ForensicFindings, LLMInterpretation,
    get_session, CaseRecord,
)
from servos.preservation.backup import EvidenceBackup
from servos.forensics.file_analyzer import FileAnalyzer
from servos.forensics.hasher import FileHasher
from servos.forensics.artifact_extractor import ArtifactExtractor
from servos.forensics.malware_detector import MalwareDetector
from servos.forensics.timeline import TimelineBuilder
from servos.llm.investigator import LLMInvestigator
from servos.reports.generator import ReportGenerator


class InvestigationWorker(QThread):
    """Full investigation pipeline running in background."""
    progress = pyqtSignal(int, str)   # percent, description
    finished = pyqtSignal(object)     # Case
    error = pyqtSignal(str)

    def __init__(self, device: DeviceInfo, mode: str, investigator: str):
        super().__init__()
        self.device = device
        self.mode = mode
        self.investigator = investigator

    def run(self):
        try:
            cfg = get_config()
            case = Case(device_info=self.device, mode=self.mode,
                        investigator=self.investigator)

            # 1. Backup
            self.progress.emit(5, "Creating forensic backup…")
            backup_svc = EvidenceBackup()
            case.backup = backup_svc.create_backup(
                self.device.mount_point, case.id)
            self.progress.emit(15,
                f"✓ Backup complete — {case.backup.files_backed_up} files copied")

            # 2. File System
            self.progress.emit(20, "Enumerating file system…")
            findings = ForensicFindings()
            findings.file_system = FileAnalyzer().analyze(self.device.mount_point)
            self.progress.emit(35,
                f"✓ {findings.file_system.total_files} files in "
                f"{findings.file_system.total_dirs} directories")

            # 3. Hashing
            self.progress.emit(38, "Computing SHA-256 hashes…")
            hasher = FileHasher()
            paths = [f.full_path for f in findings.file_system.files[:500]]
            hashes = hasher.hash_files(paths)
            findings.integrity_hashes = {
                r["file"]: r["sha256"] for r in hashes if r["sha256"] != "ERROR"
            }
            self.progress.emit(50,
                f"✓ Hashed {len(findings.integrity_hashes)} files")

            # 4. Artifacts
            self.progress.emit(53, "Extracting forensic artifacts…")
            findings.artifacts = ArtifactExtractor().extract_all(
                self.device.mount_point)
            self.progress.emit(62,
                f"✓ {findings.artifacts.total_artifacts} artifacts extracted")

            # 5. Malware
            self.progress.emit(65, "Running malware detection…")
            findings.malware = MalwareDetector().scan(self.device.mount_point)
            self.progress.emit(75,
                f"✓ Malware scan done — Risk: {findings.malware.risk_level}")

            # 6. Timeline
            self.progress.emit(78, "Reconstructing activity timeline…")
            findings.timeline = TimelineBuilder().build(
                findings.file_system, findings.artifacts)
            self.progress.emit(82,
                f"✓ Timeline: {len(findings.timeline.events)} events")

            case.findings = findings

            # 7. LLM
            self.progress.emit(85, "Running AI analysis…")
            llm = LLMInvestigator()
            interp = LLMInterpretation()
            fd = self._findings_summary(findings)
            interp.recommendations = llm.suggest_next_steps(fd)
            interp.summary = llm.generate_summary({
                "id": case.id,
                "device_info": self.device.to_dict(),
                "findings": fd,
            })
            interp.risk_assessment = (
                findings.malware.risk_level if findings.malware else "UNKNOWN")
            case.interpretation = interp
            self.progress.emit(90, "✓ AI analysis complete")

            # 8. Reports
            self.progress.emit(92, "Generating reports…")
            rd = cfg.get("reports_dir",
                         os.path.join(os.path.expanduser("~"),
                                      ".servos", "reports"))
            os.makedirs(rd, exist_ok=True)
            gen = ReportGenerator()
            gen.generate_txt(case, os.path.join(rd, f"{case.id}_report.txt"))
            gen.generate_json(case, os.path.join(rd, f"{case.id}_report.json"))
            gen.generate_csv(case, os.path.join(rd, f"{case.id}_artifacts.csv"))
            try:
                pdf = os.path.join(rd, f"{case.id}_report.pdf")
                gen.generate_pdf(case, pdf)
                case.report_path = pdf
            except Exception:
                case.report_path = os.path.join(rd, f"{case.id}_report.txt")

            case.status = "completed"
            self.progress.emit(100, "✓ Investigation complete!")
            self._save_db(case)
            self.finished.emit(case)

        except Exception as e:
            self.error.emit(f"{e}\n\n{traceback.format_exc()}")

    @staticmethod
    def _findings_summary(f):
        d = {}
        if f.file_system:
            d["file_system"] = {
                "total_files": f.file_system.total_files,
                "suspicious": len(f.file_system.suspicious_files),
            }
        if f.malware:
            d["malware"] = {
                "risk_level": f.malware.risk_level,
                "indicators": len(f.malware.indicators),
            }
        if f.artifacts:
            d["artifacts"] = {
                "browser": len(f.artifacts.browser_history),
                "recent": len(f.artifacts.recent_files),
            }
        return d

    @staticmethod
    def _save_db(case):
        try:
            s = get_session()
            s.merge(CaseRecord(
                id=case.id, created_at=case.created_at,
                investigator=case.investigator, mode=case.mode,
                status=case.status, report_path=case.report_path or "",
                device_info_json=json.dumps(
                    case.device_info.to_dict() if case.device_info else {}),
                backup_json=json.dumps(
                    case.backup.to_dict() if case.backup else {}),
            ))
            s.commit()
            s.close()
        except Exception:
            pass


class ScanWorker(QThread):
    """Quick scan worker."""
    progress = pyqtSignal(str)
    finished = pyqtSignal(object, object)  # FileSystemAnalysis, MalwareResult
    error = pyqtSignal(str)

    def __init__(self, path: str):
        super().__init__()
        self.path = path

    def run(self):
        try:
            self.progress.emit("Analyzing file system…")
            analysis = FileAnalyzer().analyze(self.path)
            self.progress.emit(
                f"✓ {analysis.total_files} files found, scanning for malware…")
            malware = MalwareDetector().scan(self.path)
            self.progress.emit("✓ Scan complete")
            self.finished.emit(analysis, malware)
        except Exception as e:
            self.error.emit(str(e))


class DeviceRefreshWorker(QThread):
    """Refresh connected devices in background."""
    finished = pyqtSignal(list)

    def run(self):
        from servos.detection.usb_monitor import USBDetectionService
        svc = USBDetectionService()
        self.finished.emit(svc.detect_devices())

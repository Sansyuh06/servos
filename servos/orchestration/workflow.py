"""
Servos – Investigation Workflow Orchestration.
State-machine-based pipeline: INIT → BACKUP → ANALYZE → INTERPRET → REPORT → COMPLETE.
"""

import os
import json
from datetime import datetime
from typing import Optional

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.panel import Panel
from rich.prompt import Confirm

from servos.models.schema import (
    Case, DeviceInfo, ForensicFindings, BackupResult, LLMInterpretation
)
from servos.preservation.backup import EvidenceBackup
from servos.forensics.file_analyzer import FileAnalyzer
from servos.forensics.hasher import FileHasher
from servos.forensics.artifact_extractor import ArtifactExtractor
from servos.forensics.malware_detector import MalwareDetector
from servos.forensics.timeline import TimelineBuilder
from servos.llm.investigator import LLMInvestigator
from servos.reports.generator import ReportGenerator
from servos.config import get_config

console = Console()


class InvestigationWorkflow:
    """Orchestrate a complete forensic investigation."""

    def __init__(self, mode: str = "full_auto"):
        self.mode = mode
        self.llm = LLMInvestigator()
        self.case: Optional[Case] = None

    # ------------------------------------------------------------------
    # Full Automation
    # ------------------------------------------------------------------

    def run_full_automation(self, device: DeviceInfo,
                            backup_dest: Optional[str] = None) -> Case:
        """Execute the full automated investigation pipeline."""
        cfg = get_config()

        # 1. Create case
        self.case = Case(device_info=device, mode="full_auto")
        console.print(Panel(
            f"[bold green]Case Created:[/] {self.case.id}\n"
            f"Device: {device.name}\n"
            f"Mode: Full Automation",
            title="🔍 Servos Investigation",
        ))

        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console,
        ) as progress:
            main_task = progress.add_task("Running investigation...", total=6)

            # Step 1: Backup
            progress.update(main_task, description="[Step 1/6] Creating forensic backup...")
            self.case.backup = self._do_backup(device, backup_dest)
            progress.advance(main_task)

            # Step 2: File System Analysis
            progress.update(main_task, description="[Step 2/6] Analyzing file system...")
            findings = ForensicFindings()
            findings.file_system = FileAnalyzer().analyze(device.mount_point)
            progress.advance(main_task)

            # Step 3: Hash Files
            progress.update(main_task, description="[Step 3/6] Hashing files...")
            hasher = FileHasher()
            file_paths = [f.full_path for f in findings.file_system.files[:500]]
            hash_results = hasher.hash_files(file_paths)
            findings.integrity_hashes = {
                r["file"]: r["sha256"] for r in hash_results if r["sha256"] != "ERROR"
            }
            progress.advance(main_task)

            # Step 4: Artifact Extraction + Malware Detection
            progress.update(main_task, description="[Step 4/6] Extracting artifacts & scanning for malware...")
            findings.artifacts = ArtifactExtractor().extract_all(device.mount_point)
            findings.malware = MalwareDetector().scan(device.mount_point)
            progress.advance(main_task)

            # Step 5: Timeline + LLM Interpretation
            progress.update(main_task, description="[Step 5/6] Building timeline & AI analysis...")
            findings.timeline = TimelineBuilder().build(findings.file_system, findings.artifacts)
            self.case.findings = findings

            # LLM interpretation
            interp = self._do_interpretation(findings)
            self.case.interpretation = interp
            progress.advance(main_task)

            # Step 6: Report Generation
            progress.update(main_task, description="[Step 6/6] Generating report...")
            self.case.report_path = self._do_report()
            self.case.status = "completed"
            progress.advance(main_task)

        # Print summary
        self._print_summary()
        return self.case

    # ------------------------------------------------------------------
    # Hybrid Mode
    # ------------------------------------------------------------------

    def run_hybrid(self, device: DeviceInfo,
                   backup_dest: Optional[str] = None) -> Case:
        """Execute hybrid investigation with user confirmations."""
        self.case = Case(device_info=device, mode="hybrid")
        console.print(Panel(
            f"[bold cyan]Case Created:[/] {self.case.id}\n"
            f"Device: {device.name}\n"
            f"Mode: Hybrid (step-by-step confirmation)",
            title="🔍 Servos Investigation",
        ))

        # Step 1: Backup (mandatory)
        console.print("\n[bold yellow]⚠  MANDATORY: Creating forensic backup first...[/]")
        self.case.backup = self._do_backup(device, backup_dest)
        console.print("[green]✓ Backup created successfully.[/]\n")

        # Step 2: File System Analysis
        if Confirm.ask("[cyan]Proceed with file system analysis?[/]", default=True):
            console.print("[blue]Analyzing file system...[/]")
            findings = ForensicFindings()
            findings.file_system = FileAnalyzer().analyze(device.mount_point)
            console.print(f"[green]✓ Found {findings.file_system.total_files} files, "
                          f"{len(findings.file_system.suspicious_files)} suspicious.[/]\n")
        else:
            findings = ForensicFindings()

        # Step 3: Hash Files
        if findings.file_system and Confirm.ask("[cyan]Hash all files for integrity verification?[/]", default=True):
            console.print("[blue]Hashing files...[/]")
            hasher = FileHasher()
            file_paths = [f.full_path for f in findings.file_system.files[:500]]
            hash_results = hasher.hash_files(file_paths)
            findings.integrity_hashes = {
                r["file"]: r["sha256"] for r in hash_results if r["sha256"] != "ERROR"
            }
            console.print(f"[green]✓ Hashed {len(findings.integrity_hashes)} files.[/]\n")

        # Step 4: Artifacts
        if Confirm.ask("[cyan]Extract forensic artifacts (browser history, logs, etc.)?[/]", default=True):
            console.print("[blue]Extracting artifacts...[/]")
            findings.artifacts = ArtifactExtractor().extract_all(device.mount_point)
            console.print(f"[green]✓ Extracted {findings.artifacts.total_artifacts} artifacts.[/]\n")

        # Step 5: Malware Scan
        if Confirm.ask("[cyan]Scan for malware indicators?[/]", default=True):
            console.print("[blue]Scanning for malware...[/]")
            findings.malware = MalwareDetector().scan(device.mount_point)
            console.print(f"[green]✓ Scan complete. Risk: {findings.malware.risk_level}[/]\n")

        # Step 6: Timeline
        if Confirm.ask("[cyan]Build activity timeline?[/]", default=True):
            console.print("[blue]Building timeline...[/]")
            findings.timeline = TimelineBuilder().build(findings.file_system, findings.artifacts)
            console.print(f"[green]✓ Timeline built with {len(findings.timeline.events)} events.[/]\n")

        self.case.findings = findings

        # Step 7: LLM Interpretation
        if Confirm.ask("[cyan]Get AI-powered analysis of findings?[/]", default=True):
            interp = self._do_interpretation(findings)
            self.case.interpretation = interp

        # Step 8: Report
        if Confirm.ask("[cyan]Generate investigation report?[/]", default=True):
            self.case.report_path = self._do_report()

        self.case.status = "completed"
        self._print_summary()
        return self.case

    # ------------------------------------------------------------------
    # Manual Mode
    # ------------------------------------------------------------------

    def run_manual(self, device: DeviceInfo,
                   backup_dest: Optional[str] = None) -> Case:
        """Provide manual mode guidance – checklists and instructions."""
        self.case = Case(device_info=device, mode="manual")
        console.print(Panel(
            f"[bold magenta]Case Created:[/] {self.case.id}\n"
            f"Device: {device.name}\n"
            f"Mode: Manual (guidance only)",
            title="🔍 Servos Investigation",
        ))

        # Mandatory backup
        console.print("\n[bold yellow]⚠  MANDATORY: Creating forensic backup first...[/]")
        self.case.backup = self._do_backup(device, backup_dest)
        console.print("[green]✓ Backup created successfully.[/]\n")

        checklist = """
[bold]FORENSIC INVESTIGATION CHECKLIST[/]
══════════════════════════════════════════

[yellow]Step 1: Backup (DONE ✓)[/yellow]
  Backup created at: {backup_path}
  Hash MD5: {hash_md5}
  Hash SHA-256: {hash_sha256}

[cyan]Step 2: File System Analysis[/cyan]
  Run: servos scan --target "{mount}" --analysis filesystem
  What to look for:
  • Executable files on removable media
  • Hidden files or folders
  • Files with high entropy (possible encryption)
  • Extension mismatches

[cyan]Step 3: File Hashing[/cyan]
  Run: servos scan --target "{mount}" --analysis hash
  What to do:
  • Hash all files for integrity baseline
  • Compare against NSRL known-good database
  • Flag unknown executables

[cyan]Step 4: Artifact Extraction[/cyan]
  Run: servos scan --target "{mount}" --analysis artifacts
  What to look for:
  • Browser history (suspicious domains)
  • Recently modified files
  • Registry hive files
  • Log files

[cyan]Step 5: Malware Screening[/cyan]
  Run: servos scan --target "{mount}" --analysis malware
  What to check:
  • YARA-like signature matches
  • Files with entropy > 7.0
  • Suspicious filename patterns

[cyan]Step 6: Timeline Reconstruction[/cyan]
  Combine all timestamps to identify activity windows.

[cyan]Step 7: Report Generation[/cyan]
  Run: servos report --case {case_id}
""".format(
            backup_path=self.case.backup.backup_path,
            hash_md5=self.case.backup.hash_md5,
            hash_sha256=self.case.backup.hash_sha256,
            mount=device.mount_point,
            case_id=self.case.id,
        )
        console.print(checklist)

        self.case.status = "active"
        return self.case

    # ------------------------------------------------------------------
    # Shared Helpers
    # ------------------------------------------------------------------

    def _do_backup(self, device: DeviceInfo,
                   dest: Optional[str] = None) -> BackupResult:
        backup_svc = EvidenceBackup()
        return backup_svc.create_backup(
            source_path=device.mount_point,
            case_id=self.case.id,
            destination=dest,
        )

    def _do_interpretation(self, findings: ForensicFindings) -> LLMInterpretation:
        interp = LLMInterpretation()

        findings_dict = {}
        if findings.file_system:
            findings_dict["file_system"] = {
                "total_files": findings.file_system.total_files,
                "suspicious_files": len(findings.file_system.suspicious_files),
                "file_types": dict(list(findings.file_system.file_type_counts.items())[:10]),
            }
        if findings.malware:
            findings_dict["malware"] = {
                "risk_level": findings.malware.risk_level,
                "indicators": len(findings.malware.indicators),
                "files_scanned": findings.malware.files_scanned,
            }
        if findings.artifacts:
            findings_dict["artifacts"] = {
                "browser_history": len(findings.artifacts.browser_history),
                "recent_files": len(findings.artifacts.recent_files),
                "registry_items": len(findings.artifacts.registry_items),
                "log_entries": len(findings.artifacts.log_entries),
            }

        interp.recommendations = self.llm.suggest_next_steps(findings_dict)
        interp.summary = self.llm.generate_summary({
            "id": self.case.id,
            "device_info": self.case.device_info.to_dict() if self.case.device_info else {},
            "findings": findings_dict,
            "status": self.case.status,
        })

        if findings.malware:
            interp.risk_assessment = findings.malware.risk_level
        else:
            interp.risk_assessment = "UNKNOWN"

        return interp

    def _do_report(self) -> str:
        gen = ReportGenerator()
        cfg = get_config()
        reports_dir = cfg.get("reports_dir",
                              os.path.join(os.path.expanduser("~"), ".servos", "reports"))
        os.makedirs(reports_dir, exist_ok=True)

        # Generate TXT report (always works, no binary deps)
        txt_path = os.path.join(reports_dir, f"{self.case.id}_report.txt")
        gen.generate_txt(self.case, txt_path)

        # Try PDF
        try:
            pdf_path = os.path.join(reports_dir, f"{self.case.id}_report.pdf")
            gen.generate_pdf(self.case, pdf_path)
            console.print(f"[green]✓ PDF Report: {pdf_path}[/]")
        except Exception:
            pass

        # JSON export
        json_path = os.path.join(reports_dir, f"{self.case.id}_report.json")
        gen.generate_json(self.case, json_path)

        return txt_path

    def _print_summary(self):
        if not self.case:
            return

        findings = self.case.findings
        risk = "UNKNOWN"
        total_files = 0
        suspicious = 0
        malware_indicators = 0

        if findings:
            if findings.file_system:
                total_files = findings.file_system.total_files
                suspicious = len(findings.file_system.suspicious_files)
            if findings.malware:
                risk = findings.malware.risk_level
                malware_indicators = len(findings.malware.indicators)

        interp_text = ""
        if self.case.interpretation:
            interp_text = self.case.interpretation.summary

        console.print("\n")
        console.print(Panel(f"""
[bold]INVESTIGATION COMPLETE[/]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Case ID:              {self.case.id}
Device:               {self.case.device_info.name if self.case.device_info else 'N/A'}
Status:               [green]{self.case.status}[/]
Files Analyzed:       {total_files}
Suspicious Files:     {suspicious}
Malware Indicators:   {malware_indicators}
Risk Assessment:      [{'red' if risk in ('HIGH', 'CRITICAL') else 'yellow' if risk == 'MEDIUM' else 'green'}]{risk}[/]

[bold]AI Summary:[/]
{interp_text}

[bold]Report:[/] {self.case.report_path}
""", title="📋 Investigation Summary", border_style="green"))

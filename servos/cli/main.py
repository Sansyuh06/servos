"""
Servos – CLI Main Commands.
Click-based command group for the Servos forensic assistant.
"""

import os
import sys
import click
from rich.console import Console
from rich.prompt import Prompt, IntPrompt, Confirm

from servos.cli.ui import print_banner, print_device_table, print_mode_selection, print_success, print_warning, print_error
from servos.config import get_config, save_config, ensure_dirs
from servos.detection.usb_monitor import USBDetectionService
from servos.orchestration.workflow import InvestigationWorkflow
from servos.models.schema import init_db

console = Console()


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    """Servos – Offline AI Forensic Assistant."""
    ensure_dirs()
    init_db()
    if ctx.invoked_subcommand is None:
        interactive_menu()


@cli.command()
def new():
    """Start a new forensic investigation."""
    print_banner()
    _start_investigation()


@cli.command()
def scan():
    """Quick-scan a target directory."""
    print_banner()
    target = Prompt.ask("[cyan]Enter target path to scan[/]", default=".")

    if not os.path.exists(target):
        print_error(f"Path not found: {target}")
        return

    console.print(f"[blue]Scanning {target}...[/]\n")

    from servos.forensics.file_analyzer import FileAnalyzer
    from servos.forensics.malware_detector import MalwareDetector

    fa = FileAnalyzer()
    analysis = fa.analyze(target)
    console.print(f"  Files: {analysis.total_files}")
    console.print(f"  Directories: {analysis.total_dirs}")
    console.print(f"  Suspicious: {len(analysis.suspicious_files)}")

    if analysis.suspicious_files:
        console.print("\n[yellow]Suspicious files:[/]")
        for sf in analysis.suspicious_files[:15]:
            console.print(f"  [red]•[/] {sf.filename} – {sf.suspicious_reason}")

    console.print("\n[blue]Running malware scan...[/]")
    md = MalwareDetector()
    result = md.scan(target)
    console.print(f"  Risk Level: [{_risk_color(result.risk_level)}]{result.risk_level}[/]")
    console.print(f"  Indicators: {len(result.indicators)}")

    for ind in result.indicators[:10]:
        console.print(f"    [{ind.severity.upper()}] {ind.rule_name}: {ind.description}")

    print_success("Scan complete.")


@cli.command()
def devices():
    """List connected storage devices."""
    print_banner()
    svc = USBDetectionService()
    devs = svc.detect_devices()
    print_device_table(devs)


@cli.command()
def cases():
    """List investigation cases."""
    from servos.models.schema import get_session, CaseRecord

    session = get_session()
    records = session.query(CaseRecord).order_by(CaseRecord.created_at.desc()).limit(20).all()

    if not records:
        console.print("[dim]No cases found. Start one with:[/] [cyan]servos new[/]")
        return

    from rich.table import Table
    table = Table(title="Investigation Cases")
    table.add_column("Case ID", style="bold cyan")
    table.add_column("Date", style="green")
    table.add_column("Mode", style="yellow")
    table.add_column("Status", style="magenta")

    for r in records:
        table.add_row(r.id, (r.created_at or "")[:19], r.mode, r.status)

    console.print(table)
    session.close()


@cli.command()
def settings():
    """View/edit Servos settings."""
    cfg = get_config()
    from rich.table import Table
    table = Table(title="Servos Settings")
    table.add_column("Setting", style="bold cyan")
    table.add_column("Value", style="green")

    for key in ["llm_model", "llm_base_url", "backup_location", "reports_dir",
                 "usb_poll_interval", "entropy_threshold", "llm_enabled"]:
        table.add_row(key, str(cfg.get(key, "")))

    console.print(table)

    if Confirm.ask("\n[cyan]Edit settings?[/]", default=False):
        key = Prompt.ask("Setting name")
        if key in cfg:
            val = Prompt.ask(f"New value for {key}", default=str(cfg[key]))
            save_config({key: val})
            print_success(f"Updated {key} = {val}")
        else:
            print_error(f"Unknown setting: {key}")


@cli.command()
def monitor():
    """Monitor for new USB devices in real-time."""
    print_banner()
    console.print("[bold yellow]Monitoring for new devices... (Ctrl+C to stop)[/]\n")

    def on_device(dev):
        console.print(f"\n[bold green]🔌 NEW DEVICE DETECTED![/]")
        console.print(f"  Name:     {dev.name}")
        console.print(f"  Path:     {dev.path}")
        console.print(f"  Capacity: {dev.capacity_human}")
        console.print(f"  Mount:    {dev.mount_point}")

        if Confirm.ask("\n[cyan]Start investigation on this device?[/]", default=True):
            mode = _select_mode()
            workflow = InvestigationWorkflow(mode=mode)
            if mode == "full_auto":
                workflow.run_full_automation(dev)
            elif mode == "hybrid":
                workflow.run_hybrid(dev)
            else:
                workflow.run_manual(dev)

    svc = USBDetectionService(callback=on_device)
    svc.start_monitoring()

    try:
        import time
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        svc.stop_monitoring()
        console.print("\n[dim]Monitoring stopped.[/]")


@cli.command()
@click.option("--version", is_flag=True, help="Show version.")
def about(version):
    """About Servos."""
    console.print("""
[bold green]Servos – Offline AI Forensic Assistant[/]
Version: 1.0.0
Author:  MoMoSapiens (Akash Santhnu Sundar)
License: MIT
Tagline: "Forensics for the Rest of Us"

An offline, AI-powered digital forensics assistant that
detects devices, enforces backups, and guides investigations.
""")


# ------------------------------------------------------------------
# Interactive Menu
# ------------------------------------------------------------------

def interactive_menu():
    """Main interactive menu loop."""
    print_banner()

    while True:
        console.print("\n[bold]Main Menu:[/]\n")
        console.print("  [cyan]1.[/] New Investigation")
        console.print("  [cyan]2.[/] Quick Scan")
        console.print("  [cyan]3.[/] List Devices")
        console.print("  [cyan]4.[/] View Cases")
        console.print("  [cyan]5.[/] Monitor for USB")
        console.print("  [cyan]6.[/] Settings")
        console.print("  [cyan]7.[/] About")
        console.print("  [cyan]0.[/] Exit")

        choice = Prompt.ask("\n[bold]Select option[/]", default="0")

        if choice == "1":
            _start_investigation()
        elif choice == "2":
            ctx = click.Context(scan)
            scan.invoke(ctx)
        elif choice == "3":
            ctx = click.Context(devices)
            devices.invoke(ctx)
        elif choice == "4":
            ctx = click.Context(cases)
            cases.invoke(ctx)
        elif choice == "5":
            ctx = click.Context(monitor)
            monitor.invoke(ctx)
        elif choice == "6":
            ctx = click.Context(settings)
            settings.invoke(ctx)
        elif choice == "7":
            ctx = click.Context(about)
            about.invoke(ctx)
        elif choice == "0":
            console.print("[dim]Goodbye![/]")
            break


def _start_investigation():
    """Launch an investigation flow."""
    console.print("\n[bold]Starting New Investigation[/]\n")

    # Detect devices
    svc = USBDetectionService()
    devs = svc.detect_devices()

    if not devs:
        print_warning("No storage devices detected.")
        target = Prompt.ask("[cyan]Enter target path manually[/]")
        if not os.path.exists(target):
            print_error(f"Path not found: {target}")
            return
        from servos.models.schema import DeviceInfo
        dev = DeviceInfo(path=target, name=target, mount_point=target)
    else:
        print_device_table(devs)
        idx = IntPrompt.ask(f"\n[cyan]Select device (1-{len(devs)})[/]", default=1)
        if idx < 1 or idx > len(devs):
            print_error("Invalid selection.")
            return
        dev = devs[idx - 1]

    mode = _select_mode()

    cfg = get_config()
    backup_dest = Prompt.ask("[cyan]Backup destination[/]",
                             default=cfg.get("backup_location", ""))

    workflow = InvestigationWorkflow(mode=mode)

    if mode == "full_auto":
        workflow.run_full_automation(dev, backup_dest)
    elif mode == "hybrid":
        workflow.run_hybrid(dev, backup_dest)
    else:
        workflow.run_manual(dev, backup_dest)

    # Save case to database
    _save_case(workflow.case)


def _select_mode() -> str:
    print_mode_selection()
    choice = Prompt.ask("[cyan]Select mode (1/2/3)[/]", default="1")
    return {"1": "full_auto", "2": "hybrid", "3": "manual"}.get(choice, "full_auto")


def _save_case(case):
    """Persist case to SQLite database."""
    if not case:
        return
    try:
        from servos.models.schema import get_session, CaseRecord
        import json
        session = get_session()
        record = CaseRecord(
            id=case.id,
            created_at=case.created_at,
            investigator=case.investigator,
            mode=case.mode,
            status=case.status,
            device_info_json=json.dumps(case.device_info.to_dict() if case.device_info else {}),
            backup_json=json.dumps(case.backup.to_dict() if case.backup else {}),
            report_path=case.report_path or "",
        )
        session.merge(record)
        session.commit()
        session.close()
    except Exception:
        pass


def _risk_color(level: str) -> str:
    return {"CRITICAL": "bold red", "HIGH": "red", "MEDIUM": "yellow", "LOW": "green"}.get(level, "white")

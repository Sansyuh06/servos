"""
Servos – CLI UI Helpers.
Rich-based progress bars, tables, panels, and ASCII art.
"""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

console = Console()

BANNER = r"""
[bold green]
 ╔═══════════════════════════════════════════════════════════╗
 ║                                                           ║
 ║   ███████╗███████╗██████╗ ██╗   ██╗ ██████╗ ███████╗     ║
 ║   ██╔════╝██╔════╝██╔══██╗██║   ██║██╔═══██╗██╔════╝     ║
 ║   ███████╗█████╗  ██████╔╝██║   ██║██║   ██║███████╗     ║
 ║   ╚════██║██╔══╝  ██╔══██╗╚██╗ ██╔╝██║   ██║╚════██║     ║
 ║   ███████║███████╗██║  ██║ ╚████╔╝ ╚██████╔╝███████║     ║
 ║   ╚══════╝╚══════╝╚═╝  ╚═╝  ╚═══╝   ╚═════╝ ╚══════╝     ║
 ║                                                           ║
 ║      [cyan]Offline AI Forensic Assistant v1.0.0[/cyan]              ║
 ║      [dim]"Forensics for the Rest of Us"[/dim]                   ║
 ║                                                           ║
 ╚═══════════════════════════════════════════════════════════╝
[/bold green]"""


def print_banner():
    """Display the Servos ASCII banner."""
    console.print(BANNER)


def print_device_table(devices):
    """Display detected devices in a formatted table."""
    table = Table(title="Detected Storage Devices", show_lines=True)
    table.add_column("#", style="bold cyan", width=4)
    table.add_column("Device", style="bold")
    table.add_column("Mount", style="green")
    table.add_column("Capacity", style="yellow")
    table.add_column("FS", style="blue")
    table.add_column("Removable", style="magenta")

    for i, dev in enumerate(devices):
        table.add_row(
            str(i + 1),
            dev.name,
            dev.mount_point,
            dev.capacity_human,
            dev.filesystem,
            "✓" if dev.is_removable else "✗",
        )

    console.print(table)


def print_mode_selection():
    """Display investigation mode options."""
    console.print("\n[bold]Select Investigation Mode:[/]\n")

    modes = Table(show_header=False, show_lines=True, padding=(0, 2))
    modes.add_column("Key", style="bold cyan", width=5)
    modes.add_column("Mode", style="bold", width=20)
    modes.add_column("Description", width=60)

    modes.add_row("1", "Full Automation",
                  "Servos handles everything. You get a final report.\n[dim]Best for: Non-experts, time-sensitive situations[/]")
    modes.add_row("2", "Hybrid Mode",
                  "Servos suggests steps; you approve each one.\n[dim]Best for: Moderately experienced investigators[/]")
    modes.add_row("3", "Manual Mode",
                  "Servos provides guidance only. You execute.\n[dim]Best for: Expert investigators[/]")

    console.print(modes)


def print_status(msg: str, style: str = "bold blue"):
    console.print(f"[{style}]{msg}[/]")


def print_success(msg: str):
    console.print(f"[bold green]✓ {msg}[/]")


def print_warning(msg: str):
    console.print(f"[bold yellow]⚠ {msg}[/]")


def print_error(msg: str):
    console.print(f"[bold red]✗ {msg}[/]")

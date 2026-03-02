"""
Servos – Main Entry Point.
Bootstraps the application and launches the CLI.
"""

from servos.cli.main import cli
from servos.config import ensure_dirs
from servos.models.schema import init_db


def main():
    """Application entry point."""
    ensure_dirs()
    init_db()
    cli()


if __name__ == "__main__":
    main()

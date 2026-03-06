"""
Servos Desktop Application Launcher
====================================
Launches Servos as a standalone desktop application.
- Starts the FastAPI backend server
- Opens the app in a dedicated window (no address bar, minimal chrome)
- Closes cleanly on exit

Usage:
    python launch_app.py
    -- or --
    Double-click Servos.bat
"""

import sys
import os
import time
import threading
import socket
import subprocess
import webbrowser

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def find_free_port():
    """Return a fixed port to avoid multiple conflicting instances."""
    return 8000


def start_server(port: int):
    """Start the FastAPI server in a background thread."""
    import uvicorn
    from servos.server import app
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="warning")


def wait_for_server(port: int, timeout: float = 15.0):
    """Wait until the server is responding."""
    import urllib.request
    start = time.time()
    while time.time() - start < timeout:
        try:
            urllib.request.urlopen(f"http://127.0.0.1:{port}/api/settings", timeout=2)
            return True
        except Exception:
            time.sleep(0.3)
    return False


def open_as_app(url: str):
    """
    Try to open the app as a standalone window (PWA-like).
    Priority:
      1. Edge --app mode (native app window, no address bar)
      2. Chrome --app mode
      3. Fallback: default browser
    """
    edge_paths = [
        os.path.expandvars(r"%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe"),
        os.path.expandvars(r"%ProgramFiles%\Microsoft\Edge\Application\msedge.exe"),
        os.path.expandvars(r"%LocalAppData%\Microsoft\Edge\Application\msedge.exe"),
    ]
    chrome_paths = [
        os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%LocalAppData%\Google\Chrome\Application\chrome.exe"),
    ]

    # Try Edge in app mode (most Windows machines have it)
    for path in edge_paths:
        if os.path.isfile(path):
            subprocess.Popen([
                path,
                f"--app={url}",
                "--window-size=1400,900",
                "--disable-extensions",
                "--disable-sync",
                f"--user-data-dir={os.path.join(os.path.expanduser('~'), '.servos', 'browser_data')}",
            ])
            return "Edge App Mode"

    # Try Chrome in app mode
    for path in chrome_paths:
        if os.path.isfile(path):
            subprocess.Popen([
                path,
                f"--app={url}",
                "--window-size=1400,900",
                "--disable-extensions",
                f"--user-data-dir={os.path.join(os.path.expanduser('~'), '.servos', 'browser_data')}",
            ])
            return "Chrome App Mode"

    # Fallback: default browser
    webbrowser.open(url)
    return "Default Browser"


def main():
    port = find_free_port()

    print()
    print("  ╔═══════════════════════════════════════════╗")
    print("  ║   SERVOS — Offline AI Forensic Platform   ║")
    print("  ║   Forensics for the Rest of Us            ║")
    print("  ╚═══════════════════════════════════════════╝")
    print()
    print(f"  Starting backend on port {port}...")

    # Start FastAPI in background thread
    server_thread = threading.Thread(target=start_server, args=(port,), daemon=True)
    server_thread.start()

    # Wait for server to be ready
    if not wait_for_server(port):
        print("  ERROR: Backend failed to start!")
        sys.exit(1)

    url = f"http://127.0.0.1:{port}/"
    mode = open_as_app(url)
    print(f"  App launched via: {mode}")
    print(f"  URL: {url}")
    print()
    print("  Press Ctrl+C to shut down.")
    print()

    # Keep running until user closes
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n  Shutting down...")
        sys.exit(0)


if __name__ == "__main__":
    main()

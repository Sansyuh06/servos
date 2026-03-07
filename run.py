"""
Servos Launcher – Start the native React-based web application.
Run: python run.py
"""
import sys
import os
import time
import threading
import subprocess
import webbrowser

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def start_server():
    import uvicorn
    from servos.server import app
    print("\n  Starting backend on port 8000...")
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="warning")

def open_browser():
    # Wait for the server to spin up
    import urllib.request
    timeout = 15.0
    start = time.time()
    url = "http://127.0.0.1:8000"
    server_ready = False
    
    while time.time() - start < timeout:
        try:
            urllib.request.urlopen(f"{url}/api/settings", timeout=2)
            server_ready = True
            break
        except Exception:
            time.sleep(0.5)
            
    if not server_ready:
        print("\n  Warning: Backend took too long to start. Try opening http://127.0.0.1:8000 manually.")
        return

    print(f"\n  Backend ready! Launching App Window...\n")
    
    # Try Edge/Chrome App Mode
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

    for path in edge_paths + chrome_paths:
        if os.path.isfile(path):
            subprocess.Popen([
                path,
                f"--app={url}",
                "--window-size=1400,900",
                "--disable-extensions",
                f"--user-data-dir={os.path.join(os.path.expanduser('~'), '.servos', 'browser_data')}",
            ])
            return

    # Fallback to default browser
    webbrowser.open(url)

def main():
    print()
    print("  ╔═══════════════════════════════════════════╗")
    print("  ║   SERVOS — Offline AI Forensic Platform   ║")
    print("  ║   Forensics for the Rest of Us            ║")
    print("  ╚═══════════════════════════════════════════╝")
    
    # Start browser thread
    threading.Thread(target=open_browser, daemon=True).start()
    
    # Run uvicorn in main thread so Ctrl+C works cleanly
    try:
        start_server()
    except KeyboardInterrupt:
        print("\n  Shutting down...")
        sys.exit(0)

if __name__ == "__main__":
    main()

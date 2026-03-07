import sys
import os
import time
import threading
import uvicorn
import webview

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from servos.server import app

def start_server():
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="warning")

def main():
    # Start FastAPI in a daemon thread
    t = threading.Thread(target=start_server, daemon=True)
    t.start()
    
    # Wait for server
    import urllib.request
    server_ready = False
    start = time.time()
    while time.time() - start < 15:
        try:
            urllib.request.urlopen("http://127.0.0.1:8000/api/settings", timeout=2)
            server_ready = True
            break
        except Exception:
            time.sleep(0.5)
            
    if not server_ready:
        print("Backend failed to start")
        sys.exit(1)
    
    # Create native window
    webview.create_window(
        title="Servos — Offline AI Forensic Platform", 
        url="http://127.0.0.1:8000",
        width=1400,
        height=900,
        min_size=(1024, 768)
    )
    webview.start()

if __name__ == '__main__':
    main()

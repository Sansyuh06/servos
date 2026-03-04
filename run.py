"""
Servos Launcher – Start the native React-based web application.
Run: python run.py
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    import launch_app
    launch_app.main()


if __name__ == "__main__":
    main()

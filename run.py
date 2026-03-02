"""
Servos Launcher – Start the native desktop application.
Run: python run.py
"""


def main():
    from servos.app import main as app_main
    app_main()


if __name__ == "__main__":
    main()

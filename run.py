"""
Servos Launcher – Start the native desktop application.
Run: python run.py
"""


def main():
    from servos.gui.main_window import main as gui_main
    gui_main()


if __name__ == "__main__":
    main()

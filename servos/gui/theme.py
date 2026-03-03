"""
Servos — Premium Design System.
Inspired by Linear, Vercel, and Raycast: ultra-clean dark mode.
"""

# ── Color Tokens ─────────────────────────────────────────────
BG_PRIMARY   = "#09090b"   # Near-black zinc
BG_SURFACE   = "#0c0c0f"   # Sidebar
BG_CARD      = "#131316"   # Card backgrounds
BG_ELEVATED  = "#1a1a1f"   # Hover / elevated
BG_HOVER     = "#1f1f24"
BG_INPUT     = "#111114"

BORDER       = "#27272a"   # Zinc-800
BORDER_FOCUS = "#3b82f6"
BORDER_DIM   = "#1e1e22"

CYAN         = "#22d3ee"
BLUE         = "#3b82f6"
GREEN        = "#22c55e"
RED          = "#ef4444"
ORANGE       = "#f97316"
YELLOW       = "#eab308"
PURPLE       = "#a78bfa"
TEAL         = "#14b8a6"

TEXT         = "#e4e4e7"   # Zinc-200
TEXT_SEC     = "#a1a1aa"   # Zinc-400
TEXT_DIM     = "#71717a"   # Zinc-500
TEXT_BRIGHT  = "#fafafa"   # Zinc-50

# ── Main Stylesheet ──────────────────────────────────────────
STYLESHEET = f"""
/* ━━━ Global ━━━ */
QMainWindow, QWidget {{
    background-color: {BG_PRIMARY};
    color: {TEXT};
    font-family: 'Segoe UI', 'Inter', -apple-system, sans-serif;
    font-size: 13px;
}}

/* ━━━ Buttons ━━━ */
QPushButton {{
    background-color: {BG_CARD};
    color: {TEXT};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 8px 16px;
    font-weight: 500;
    font-size: 13px;
    min-height: 18px;
}}
QPushButton:hover {{
    background-color: {BG_HOVER};
    border-color: #3f3f46;
}}
QPushButton:pressed {{
    background-color: {BG_PRIMARY};
}}
QPushButton:disabled {{
    color: {TEXT_DIM};
    border-color: {BORDER_DIM};
}}
QPushButton[cssClass="primary"] {{
    background: {BLUE};
    border: 1px solid #60a5fa;
    color: #ffffff;
    font-weight: 600;
    border-radius: 8px;
}}
QPushButton[cssClass="primary"]:hover {{
    background: #2563eb;
    border-color: #93c5fd;
}}
QPushButton[cssClass="success"] {{
    background-color: rgba(34, 197, 94, 0.12);
    border: 1px solid rgba(34, 197, 94, 0.3);
    color: {GREEN};
}}
QPushButton[cssClass="danger"] {{
    background-color: rgba(239, 68, 68, 0.12);
    border: 1px solid rgba(239, 68, 68, 0.3);
    color: {RED};
}}
QPushButton[cssClass="nav"] {{
    text-align: left;
    padding: 10px 16px;
    border: none;
    border-radius: 6px;
    font-weight: 500;
    background: transparent;
    color: {TEXT_DIM};
    font-size: 13px;
}}
QPushButton[cssClass="nav"]:hover {{
    background-color: {BG_HOVER};
    color: {TEXT};
}}
QPushButton[cssClass="navActive"] {{
    text-align: left;
    padding: 10px 16px;
    border: none;
    border-left: 2px solid {BLUE};
    border-radius: 0px 6px 6px 0px;
    font-weight: 600;
    background-color: rgba(59, 130, 246, 0.08);
    color: {TEXT_BRIGHT};
}}

/* ━━━ Inputs ━━━ */
QLineEdit, QTextEdit, QPlainTextEdit {{
    background-color: {BG_INPUT};
    color: {TEXT};
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 13px;
    selection-background-color: {BLUE};
    selection-color: white;
}}
QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
    border-color: {BLUE};
}}
QComboBox {{
    background-color: {BG_INPUT};
    color: {TEXT};
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 13px;
    min-height: 18px;
}}
QComboBox:focus {{
    border-color: {BLUE};
}}
QComboBox::drop-down {{
    border: none;
    width: 28px;
}}
QComboBox QAbstractItemView {{
    background-color: {BG_CARD};
    border: 1px solid {BORDER};
    selection-background-color: {BG_HOVER};
    color: {TEXT};
}}

/* ━━━ Group Boxes ━━━ */
QGroupBox {{
    background-color: {BG_CARD};
    border: 1px solid {BORDER};
    border-radius: 10px;
    margin-top: 14px;
    padding: 20px;
    padding-top: 32px;
    font-weight: 500;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    left: 16px;
    padding: 2px 10px;
    color: {TEXT_SEC};
    font-size: 12px;
    font-weight: 600;
    background-color: {BG_CARD};
    border-radius: 4px;
    border: 1px solid {BORDER};
    letter-spacing: 0.5px;
}}

/* ━━━ Progress Bar ━━━ */
QProgressBar {{
    background-color: {BG_INPUT};
    border: 1px solid {BORDER};
    border-radius: 6px;
    text-align: center;
    color: {TEXT_BRIGHT};
    font-size: 11px;
    font-weight: 600;
    height: 20px;
}}
QProgressBar::chunk {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 {BLUE}, stop:1 #60a5fa);
    border-radius: 5px;
}}

/* ━━━ Tables ━━━ */
QTableWidget {{
    background-color: {BG_CARD};
    border: 1px solid {BORDER};
    border-radius: 10px;
    gridline-color: {BORDER_DIM};
    selection-background-color: rgba(59, 130, 246, 0.15);
    alternate-background-color: {BG_PRIMARY};
    font-size: 12px;
}}
QTableWidget::item {{
    padding: 8px;
    border-bottom: 1px solid {BORDER_DIM};
}}
QTableWidget::item:selected {{
    color: {TEXT_BRIGHT};
}}
QHeaderView::section {{
    background-color: {BG_PRIMARY};
    color: {TEXT_DIM};
    border: none;
    border-bottom: 1px solid {BORDER};
    padding: 10px 8px;
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}

/* ━━━ Tabs ━━━ */
QTabWidget::pane {{
    border: 1px solid {BORDER};
    border-radius: 0 10px 10px 10px;
    background-color: {BG_CARD};
    padding: 10px;
}}
QTabBar::tab {{
    background-color: transparent;
    color: {TEXT_DIM};
    border: none;
    padding: 10px 20px;
    margin-right: 2px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    font-weight: 500;
    font-size: 12px;
}}
QTabBar::tab:selected {{
    background-color: {BG_CARD};
    color: {TEXT_BRIGHT};
    border: 1px solid {BORDER};
    border-bottom: 1px solid {BG_CARD};
}}
QTabBar::tab:hover:!selected {{
    background-color: {BG_HOVER};
    color: {TEXT};
}}

/* ━━━ Scroll ━━━ */
QScrollArea {{
    border: none;
    background: transparent;
}}
QScrollBar:vertical {{
    background: transparent;
    width: 6px;
    margin: 0;
}}
QScrollBar::handle:vertical {{
    background: {BORDER};
    border-radius: 3px;
    min-height: 40px;
}}
QScrollBar::handle:vertical:hover {{
    background: {TEXT_DIM};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
    height: 0; background: none;
}}
QScrollBar:horizontal {{
    background: transparent;
    height: 6px;
}}
QScrollBar::handle:horizontal {{
    background: {BORDER};
    border-radius: 3px;
    min-width: 40px;
}}

/* ━━━ Lists ━━━ */
QListWidget {{
    background-color: {BG_CARD};
    border: 1px solid {BORDER};
    border-radius: 10px;
    outline: none;
}}
QListWidget::item {{
    padding: 12px;
    border-bottom: 1px solid {BORDER_DIM};
    color: {TEXT_SEC};
}}
QListWidget::item:hover {{
    background-color: {BG_HOVER};
    color: {TEXT};
}}
QListWidget::item:selected {{
    background-color: rgba(59, 130, 246, 0.1);
    color: {TEXT_BRIGHT};
    border-left: 3px solid {BLUE};
}}

/* ━━━ Labels ━━━ */
QLabel {{
    color: {TEXT};
    background: transparent;
}}
QLabel[cssClass="title"] {{
    font-size: 28px;
    font-weight: 700;
    color: {TEXT_BRIGHT};
    letter-spacing: -0.5px;
}}
QLabel[cssClass="subtitle"] {{
    font-size: 13px;
    color: {TEXT_DIM};
}}
QLabel[cssClass="sectionTitle"] {{
    font-size: 15px;
    font-weight: 600;
    color: {TEXT};
}}
QLabel[cssClass="metric"] {{
    font-size: 36px;
    font-weight: 700;
    color: {TEXT_BRIGHT};
}}
QLabel[cssClass="metricLabel"] {{
    font-size: 11px;
    font-weight: 600;
    color: {TEXT_DIM};
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}

/* ━━━ Splitter ━━━ */
QSplitter::handle {{
    background: {BORDER};
    width: 1px;
}}

/* ━━━ Tooltip ━━━ */
QToolTip {{
    background-color: {BG_CARD};
    color: {TEXT};
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 12px;
}}

/* ━━━ Frame separator ━━━ */
QFrame[cssClass="separator"] {{
    background-color: {BORDER};
    max-height: 1px;
    min-height: 1px;
}}
"""

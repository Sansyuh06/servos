"""
Servos – Ultra-Aesthetic Design System.
Inspired by 21st.dev (Magic UI / Aceternity): glassmorphism, glowing borders, deep backgrounds.
"""

# ── Color Tokens ─────────────────────────────────────────────
BG_PRIMARY   = "#030712"  # Extremely dark slate (near black)
BG_SURFACE   = "#0b0f19"  # Deep surface
BG_CARD      = "rgba(17, 24, 39, 0.7)"  # Glassmorphism base
BG_ELEVATED  = "#1f2937"
BG_HOVER     = "rgba(31, 41, 55, 0.8)"
BG_INPUT     = "rgba(3, 7, 18, 0.6)"

BORDER       = "rgba(55, 65, 81, 0.5)"
BORDER_FOCUS = "#38bdf8"
BORDER_DIM   = "rgba(31, 41, 55, 0.5)"

CYAN         = "#22d3ee"  # Bright cyan
BLUE         = "#3b82f6"  # Royal blue
GREEN        = "#10b981"
RED          = "#ef4444"
ORANGE       = "#f97316"
YELLOW       = "#eab308"
PURPLE       = "#8b5cf6"
TEAL         = "#14b8a6"

TEXT         = "#e2e8f0"
TEXT_SEC     = "#94a3b8"
TEXT_DIM     = "#64748b"
TEXT_BRIGHT  = "#ffffff"

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
    background-color: rgba(17, 24, 39, 0.8);
    color: {TEXT};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 10px 20px;
    font-weight: 600;
    font-size: 13px;
    min-height: 20px;
}}
QPushButton:hover {{
    background-color: {BG_HOVER};
    border: 1px solid {CYAN};
    color: {CYAN};
}}
QPushButton:pressed {{
    background-color: {BG_PRIMARY};
}}
QPushButton:disabled {{
    color: {TEXT_DIM};
    border-color: {BORDER_DIM};
}}
/* Shimmer / Glowing Button from 21st.dev */
QPushButton[cssClass="primary"] {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #1d4ed8, stop:1 #3b82f6);
    border: 1px solid #60a5fa;
    color: #ffffff;
    font-weight: bold;
    border-radius: 10px;
}}
QPushButton[cssClass="primary"]:hover {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #2563eb, stop:1 #60a5fa);
    border: 1px solid #93c5fd;
}}
QPushButton[cssClass="success"] {{
    background-color: rgba(6, 78, 59, 0.8);
    border: 1px solid {GREEN};
    color: {GREEN};
}}
QPushButton[cssClass="danger"] {{
    background-color: rgba(127, 29, 29, 0.8);
    border: 1px solid {RED};
    color: {RED};
}}
QPushButton[cssClass="nav"] {{
    text-align: left;
    padding: 14px 20px;
    border: none;
    border-radius: 8px;
    font-weight: 500;
    background: transparent;
    color: {TEXT_SEC};
}}
QPushButton[cssClass="nav"]:hover {{
    background-color: {BG_HOVER};
    color: {TEXT_BRIGHT};
}}
QPushButton[cssClass="navActive"] {{
    text-align: left;
    padding: 14px 20px;
    border: none;
    border-left: 3px solid {CYAN};
    border-radius: 0px 8px 8px 0px;
    font-weight: 600;
    background-color: rgba(34, 211, 238, 0.08);
    color: {CYAN};
}}

/* ━━━ Inputs ━━━ */
QLineEdit, QTextEdit, QPlainTextEdit {{
    background-color: {BG_INPUT};
    color: {TEXT};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 10px 14px;
    font-size: 13px;
    selection-background-color: {CYAN};
    selection-color: {BG_PRIMARY};
}}
QLineEdit:focus, QTextEdit:focus {{
    border-color: {CYAN};
}}
QComboBox {{
    background-color: {BG_INPUT};
    color: {TEXT};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 10px 14px;
    font-size: 13px;
    min-height: 20px;
}}
QComboBox:focus {{
    border-color: {CYAN};
}}
QComboBox::drop-down {{
    border: none;
    width: 30px;
}}
QComboBox QAbstractItemView {{
    background-color: {BG_SURFACE};
    border: 1px solid {BORDER};
    selection-background-color: {BG_HOVER};
    color: {TEXT};
}}

/* ━━━ Group Boxes / Cards (Bento Grid Style) ━━━ */
QGroupBox {{
    background-color: {BG_CARD};
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 16px;
    margin-top: 16px;
    padding: 24px;
    padding-top: 36px;
    font-weight: 600;
    font-size: 14px;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    left: 20px;
    padding: 2px 12px;
    color: {CYAN};
    font-size: 13px;
    background-color: {BG_PRIMARY};
    border-radius: 6px;
    border: 1px solid rgba(34, 211, 238, 0.2);
}}

/* ━━━ Progress Bar (Gradient Glow) ━━━ */
QProgressBar {{
    background-color: rgba(3, 7, 18, 0.8);
    border: 1px solid {BORDER};
    border-radius: 8px;
    text-align: center;
    color: {TEXT_BRIGHT};
    font-size: 11px;
    font-weight: 700;
    height: 24px;
}}
QProgressBar::chunk {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #3b82f6, stop:0.5 #22d3ee, stop:1 #8b5cf6);
    border-radius: 7px;
}}

/* ━━━ Tables (Modern SaaS style) ━━━ */
QTableWidget {{
    background-color: transparent;
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 12px;
    gridline-color: transparent;
    selection-background-color: rgba(34, 211, 238, 0.15);
    alternate-background-color: rgba(255, 255, 255, 0.02);
    font-size: 12px;
}}
QTableWidget::item {{
    padding: 8px;
    border-bottom: 1px solid {BORDER_DIM};
}}
QTableWidget::item:selected {{
    color: {CYAN};
}}
QHeaderView::section {{
    background-color: rgba(11, 15, 25, 0.8);
    color: {TEXT_SEC};
    border: none;
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    padding: 12px 8px;
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}

/* ━━━ Tabs ━━━ */
QTabWidget::pane {{
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 0 12px 12px 12px;
    background-color: {BG_CARD};
    padding: 12px;
}}
QTabBar::tab {{
    background-color: transparent;
    color: {TEXT_DIM};
    border: 1px solid transparent;
    border-bottom: none;
    padding: 12px 24px;
    margin-right: 4px;
    border-top-left-radius: 12px;
    border-top-right-radius: 12px;
    font-weight: 600;
    font-size: 12px;
}}
QTabBar::tab:selected {{
    background-color: {BG_CARD};
    color: {CYAN};
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-bottom: 2px solid {BG_CARD};
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
    background-color: {BG_INPUT};
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 12px;
    outline: none;
}}
QListWidget::item {{
    padding: 16px;
    border-bottom: 1px solid {BORDER_DIM};
    color: {TEXT_SEC};
}}
QListWidget::item:hover {{
    background-color: {BG_HOVER};
    color: {TEXT};
}}
QListWidget::item:selected {{
    background-color: rgba(34, 211, 238, 0.1);
    color: {CYAN};
    border-left: 4px solid {CYAN};
}}

/* ━━━ Labels (Neon Typography styling) ━━━ */
QLabel {{
    color: {TEXT};
    background: transparent;
}}
QLabel[cssClass="title"] {{
    font-size: 32px;
    font-weight: 800;
    color: {TEXT_BRIGHT};
    letter-spacing: -1px;
}}
QLabel[cssClass="subtitle"] {{
    font-size: 14px;
    color: {TEXT_SEC};
}}
QLabel[cssClass="sectionTitle"] {{
    font-size: 16px;
    font-weight: 700;
    color: {CYAN};
}}
QLabel[cssClass="metric"] {{
    font-size: 46px;
    font-weight: 800;
    color: {TEXT_BRIGHT};
}}
QLabel[cssClass="metricLabel"] {{
    font-size: 11px;
    font-weight: 700;
    color: {BLUE};
    text-transform: uppercase;
    letter-spacing: 1px;
}}
/* Aceternity glowing border styles for Risk cards */
QLabel[cssClass="riskLow"] {{
    font-size: 22px; font-weight: 800; color: #ffffff;
    padding: 16px; background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 rgba(16, 185, 129, 0.2), stop:1 rgba(16, 185, 129, 0.05));
    border: 1px solid rgba(16, 185, 129, 0.5); border-radius: 12px;
}}
QLabel[cssClass="riskMedium"] {{
    font-size: 22px; font-weight: 800; color: #ffffff;
    padding: 16px; background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 rgba(234, 179, 8, 0.2), stop:1 rgba(234, 179, 8, 0.05));
    border: 1px solid rgba(234, 179, 8, 0.5); border-radius: 12px;
}}
QLabel[cssClass="riskHigh"] {{
    font-size: 22px; font-weight: 800; color: #ffffff;
    padding: 16px; background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 rgba(249, 115, 22, 0.2), stop:1 rgba(249, 115, 22, 0.05));
    border: 1px solid rgba(249, 115, 22, 0.5); border-radius: 12px;
}}
QLabel[cssClass="riskCritical"] {{
    font-size: 22px; font-weight: 800; color: #ffffff;
    padding: 16px; background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 rgba(239, 68, 68, 0.3), stop:1 rgba(239, 68, 68, 0.05));
    border: 1px solid rgba(239, 68, 68, 0.6); border-radius: 12px;
}}

/* ━━━ Splitter ━━━ */
QSplitter::handle {{
    background: {BORDER};
    width: 1px;
}}

/* ━━━ Tooltip ━━━ */
QToolTip {{
    background-color: {BG_ELEVATED};
    color: {TEXT};
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 12px;
}}

/* ━━━ Frame separator ━━━ */
QFrame[cssClass="separator"] {{
    background-color: {BORDER};
    max-height: 1px;
    min-height: 1px;
}}
"""

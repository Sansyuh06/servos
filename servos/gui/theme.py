"""
Servos – Enterprise Design System.
Cybersecurity-grade dark theme with cyan/neon accents.
"""

# ── Color Tokens ─────────────────────────────────────────────
BG_PRIMARY   = "#0a0e1a"
BG_SURFACE   = "#0f1420"
BG_CARD      = "#141a2a"
BG_ELEVATED  = "#1a2236"
BG_HOVER     = "#1e293b"
BG_INPUT     = "#0c1018"

BORDER       = "#1e2d4a"
BORDER_FOCUS = "#00d9ff"
BORDER_DIM   = "#162038"

CYAN         = "#00d9ff"
BLUE         = "#0099ff"
GREEN        = "#00e676"
RED          = "#ff3b30"
ORANGE       = "#ff9500"
YELLOW       = "#ffb800"
PURPLE       = "#a78bfa"
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
    background-color: {BG_CARD};
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
    border-color: {CYAN};
    color: {CYAN};
}}
QPushButton:pressed {{
    background-color: {BG_PRIMARY};
}}
QPushButton:disabled {{
    color: {TEXT_DIM};
    border-color: {BORDER_DIM};
}}
QPushButton[cssClass="primary"] {{
    background-color: #0d3b66;
    border: 1px solid {CYAN};
    color: {CYAN};
}}
QPushButton[cssClass="primary"]:hover {{
    background-color: #10476b;
}}
QPushButton[cssClass="success"] {{
    background-color: #0a3d1f;
    border: 1px solid {GREEN};
    color: {GREEN};
}}
QPushButton[cssClass="danger"] {{
    background-color: #3d0a0a;
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
    color: {TEXT};
}}
QPushButton[cssClass="navActive"] {{
    text-align: left;
    padding: 14px 20px;
    border: none;
    border-left: 3px solid {CYAN};
    border-radius: 0px 8px 8px 0px;
    font-weight: 600;
    background-color: rgba(0, 217, 255, 0.08);
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
    background-color: {BG_CARD};
    border: 1px solid {BORDER};
    selection-background-color: {BG_HOVER};
    color: {TEXT};
}}

/* ━━━ Group Boxes / Cards ━━━ */
QGroupBox {{
    background-color: {BG_CARD};
    border: 1px solid {BORDER};
    border-radius: 10px;
    margin-top: 16px;
    padding: 20px;
    padding-top: 32px;
    font-weight: 600;
    font-size: 14px;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    left: 18px;
    padding: 2px 10px;
    color: {CYAN};
    font-size: 13px;
}}

/* ━━━ Progress Bar ━━━ */
QProgressBar {{
    background-color: {BG_INPUT};
    border: 1px solid {BORDER};
    border-radius: 6px;
    text-align: center;
    color: {TEXT};
    font-size: 11px;
    font-weight: 600;
    height: 24px;
}}
QProgressBar::chunk {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 {CYAN}, stop:0.5 {BLUE}, stop:1 {TEAL});
    border-radius: 5px;
}}

/* ━━━ Tables ━━━ */
QTableWidget {{
    background-color: {BG_CARD};
    border: 1px solid {BORDER};
    border-radius: 8px;
    gridline-color: {BORDER_DIM};
    selection-background-color: rgba(0, 217, 255, 0.1);
    alternate-background-color: {BG_SURFACE};
    font-size: 12px;
}}
QTableWidget::item {{
    padding: 8px;
    border-bottom: 1px solid {BORDER_DIM};
}}
QTableWidget::item:selected {{
    background-color: rgba(0, 217, 255, 0.12);
    color: {CYAN};
}}
QHeaderView::section {{
    background-color: {BG_SURFACE};
    color: {TEXT_DIM};
    border: none;
    border-bottom: 2px solid {BORDER};
    padding: 10px 8px;
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}

/* ━━━ Tabs ━━━ */
QTabWidget::pane {{
    border: 1px solid {BORDER};
    border-radius: 0 8px 8px 8px;
    background-color: {BG_CARD};
    padding: 8px;
}}
QTabBar::tab {{
    background-color: {BG_PRIMARY};
    color: {TEXT_DIM};
    border: 1px solid {BORDER};
    border-bottom: none;
    padding: 10px 22px;
    margin-right: 2px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    font-weight: 600;
    font-size: 12px;
}}
QTabBar::tab:selected {{
    background-color: {BG_CARD};
    color: {CYAN};
    border-color: {CYAN};
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
    width: 8px;
    margin: 0;
}}
QScrollBar::handle:vertical {{
    background: {BORDER};
    border-radius: 4px;
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
    height: 8px;
}}
QScrollBar::handle:horizontal {{
    background: {BORDER};
    border-radius: 4px;
    min-width: 40px;
}}

/* ━━━ Lists ━━━ */
QListWidget {{
    background-color: {BG_CARD};
    border: 1px solid {BORDER};
    border-radius: 8px;
    outline: none;
}}
QListWidget::item {{
    padding: 12px 16px;
    border-bottom: 1px solid {BORDER_DIM};
    color: {TEXT_SEC};
}}
QListWidget::item:hover {{
    background-color: {BG_HOVER};
    color: {TEXT};
}}
QListWidget::item:selected {{
    background-color: rgba(0, 217, 255, 0.1);
    color: {CYAN};
    border-left: 3px solid {CYAN};
}}

/* ━━━ Labels ━━━ */
QLabel {{
    color: {TEXT};
    background: transparent;
}}
QLabel[cssClass="title"] {{
    font-size: 26px;
    font-weight: 700;
    color: {TEXT_BRIGHT};
    letter-spacing: -0.5px;
}}
QLabel[cssClass="subtitle"] {{
    font-size: 13px;
    color: {TEXT_SEC};
}}
QLabel[cssClass="sectionTitle"] {{
    font-size: 15px;
    font-weight: 600;
    color: {CYAN};
}}
QLabel[cssClass="metric"] {{
    font-size: 32px;
    font-weight: 700;
    color: {CYAN};
}}
QLabel[cssClass="metricLabel"] {{
    font-size: 11px;
    font-weight: 600;
    color: {TEXT_DIM};
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}
QLabel[cssClass="riskLow"] {{
    font-size: 20px; font-weight: 800; color: {GREEN};
    padding: 16px; background: rgba(0, 230, 118, 0.08);
    border: 2px solid {GREEN}; border-radius: 10px;
}}
QLabel[cssClass="riskMedium"] {{
    font-size: 20px; font-weight: 800; color: {YELLOW};
    padding: 16px; background: rgba(255, 184, 0, 0.08);
    border: 2px solid {YELLOW}; border-radius: 10px;
}}
QLabel[cssClass="riskHigh"] {{
    font-size: 20px; font-weight: 800; color: {ORANGE};
    padding: 16px; background: rgba(255, 149, 0, 0.08);
    border: 2px solid {ORANGE}; border-radius: 10px;
}}
QLabel[cssClass="riskCritical"] {{
    font-size: 20px; font-weight: 800; color: {RED};
    padding: 16px; background: rgba(255, 59, 48, 0.08);
    border: 2px solid {RED}; border-radius: 10px;
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

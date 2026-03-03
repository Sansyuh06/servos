"""
Servos — Design System.
Faithful reproduction of the Servos.pdf presentation design:
warm grey backgrounds, lavender/purple accents, cream text.
"""

# ── Color Tokens ─────────────────────────────────────────────
# Pixel-sampled from Servos.pdf pages

BG_PRIMARY   = "#535353"   # Dominant warm grey (53-62% of pdf pages)
BG_SURFACE   = "#4a4a4a"   # Sidebar, slightly darker
BG_CARD      = "#5b595e"   # Card bg – purple-tinted grey
BG_ELEVATED  = "#615d66"   # Hover/elevated – purple-grey blobs
BG_HOVER     = "#6a6770"   # Lighter hover state
BG_INPUT     = "#4e4e50"   # Input field bg

BORDER       = "#6e6b73"   # Subtle border on cards
BORDER_FOCUS = "#9c8ab9"   # Focus = accent lavender
BORDER_DIM   = "#5a585c"   # Faint separators

# ── Accent palette (lavender/purple from PDF info cards) ─────
ACCENT       = "#9c8ab9"   # Primary lavender accent (12-22% on info pages)
ACCENT_DARK  = "#7b6b9a"   # Hover / pressed accent
ACCENT_LIGHT = "#bfb0d4"   # Light accent for subtle highlights
PURPLE       = "#9c8ab9"   # Alias

# ── Functional colors (slightly muted to fit warm palette) ───
CYAN         = "#6bc4d6"
BLUE         = "#7d9fd6"   # Softer blue
GREEN        = "#6dc06c"
RED          = "#d46a6a"
ORANGE       = "#d49a5a"
YELLOW       = "#d4c15a"
TEAL         = "#5ab8a8"

# ── Text (cream from PDF) ───────────────────────────────────
TEXT         = "#fff6e7"   # Cream – primary text
TEXT_SEC     = "#c5c0b8"   # Warm mid-grey for secondary
TEXT_DIM     = "#9a968e"   # De-emphasized labels
TEXT_BRIGHT  = "#ffffff"   # Maximum emphasis (sparkles, icons)

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
    border-color: {ACCENT};
}}
QPushButton:pressed {{
    background-color: {BG_ELEVATED};
}}
QPushButton:disabled {{
    color: {TEXT_DIM};
    border-color: {BORDER_DIM};
}}
QPushButton[cssClass="primary"] {{
    background: {ACCENT};
    border: 1px solid {ACCENT_LIGHT};
    color: #ffffff;
    font-weight: 600;
    border-radius: 8px;
}}
QPushButton[cssClass="primary"]:hover {{
    background: {ACCENT_DARK};
    border-color: {ACCENT};
}}
QPushButton[cssClass="success"] {{
    background-color: rgba(109, 192, 108, 0.15);
    border: 1px solid rgba(109, 192, 108, 0.35);
    color: {GREEN};
}}
QPushButton[cssClass="danger"] {{
    background-color: rgba(212, 106, 106, 0.15);
    border: 1px solid rgba(212, 106, 106, 0.35);
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
    background-color: {BG_ELEVATED};
    color: {TEXT};
}}
QPushButton[cssClass="navActive"] {{
    text-align: left;
    padding: 10px 16px;
    border: none;
    border-left: 2px solid {ACCENT};
    border-radius: 0px 6px 6px 0px;
    font-weight: 600;
    background-color: rgba(156, 138, 185, 0.12);
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
    selection-background-color: {ACCENT};
    selection-color: white;
}}
QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
    border-color: {ACCENT};
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
    border-color: {ACCENT};
}}
QComboBox::drop-down {{
    border: none;
    width: 28px;
}}
QComboBox QAbstractItemView {{
    background-color: {BG_CARD};
    border: 1px solid {BORDER};
    selection-background-color: {BG_ELEVATED};
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
        stop:0 {ACCENT_DARK}, stop:1 {ACCENT});
    border-radius: 5px;
}}

/* ━━━ Tables ━━━ */
QTableWidget {{
    background-color: {BG_CARD};
    border: 1px solid {BORDER};
    border-radius: 10px;
    gridline-color: {BORDER_DIM};
    selection-background-color: rgba(156, 138, 185, 0.18);
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
    background-color: {BG_ELEVATED};
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
    background: {ACCENT};
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
    background-color: {BG_ELEVATED};
    color: {TEXT};
}}
QListWidget::item:selected {{
    background-color: rgba(156, 138, 185, 0.15);
    color: {TEXT_BRIGHT};
    border-left: 3px solid {ACCENT};
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

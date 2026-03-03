"""
Servos – Custom Widgets inspired by 21st.dev / Aceternity / Magic UI.
Bento metric cards, terminal viewer, toast notifications, chat bubbles.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QGraphicsDropShadowEffect, QGraphicsOpacityEffect,
    QSizePolicy, QPushButton,
)
from PyQt6.QtCore import (
    Qt, QTimer, QPropertyAnimation, QPoint, QEasingCurve, QSize,
    pyqtProperty, QRect,
)
from PyQt6.QtGui import (
    QFont, QColor, QPainter, QPen, QBrush, QLinearGradient,
    QRadialGradient, QPainterPath,
)

from servos.gui.theme import (
    BG_PRIMARY, BG_SURFACE, BG_CARD, BG_ELEVATED, BG_HOVER,
    BORDER, CYAN, BLUE, GREEN, RED, ORANGE, YELLOW, PURPLE,
    TEXT, TEXT_SEC, TEXT_DIM, TEXT_BRIGHT,
)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Bento Metric Card  (gradient glow, large metric, label)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class BentoCard(QWidget):
    """Glassmorphic metric card with gradient border glow."""

    def __init__(self, icon: str, value: str, label: str,
                 accent: str = CYAN, parent=None):
        super().__init__(parent)
        self.accent = accent
        self._value = value
        self.setMinimumSize(200, 140)
        self.setSizePolicy(QSizePolicy.Policy.Expanding,
                           QSizePolicy.Policy.Fixed)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(20, 18, 20, 18)
        lay.setSpacing(4)

        # Icon row
        ic = QLabel(icon)
        ic.setFont(QFont("Segoe UI Emoji", 20))
        ic.setStyleSheet("background: transparent;")
        lay.addWidget(ic)

        # Value
        self.val_label = QLabel(value)
        self.val_label.setFont(QFont("Segoe UI", 36, QFont.Weight.ExtraBold))
        self.val_label.setStyleSheet(
            f"color: {TEXT_BRIGHT}; background: transparent;")
        lay.addWidget(self.val_label)

        # Label
        lbl = QLabel(label)
        lbl.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        lbl.setStyleSheet(
            f"color: {accent}; background: transparent; "
            f"letter-spacing: 1.2px; text-transform: uppercase;")
        lay.addWidget(lbl)

        self.setObjectName("val")  # for findChild

    def set_value(self, v: str):
        self._value = v
        self.val_label.setText(v)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        r = self.rect().adjusted(1, 1, -1, -1)

        # Background
        grad = QLinearGradient(0, 0, r.width(), r.height())
        grad.setColorAt(0, QColor(17, 24, 39, 200))
        grad.setColorAt(1, QColor(10, 15, 26, 220))
        path = QPainterPath()
        path.addRoundedRect(r.x(), r.y(), r.width(), r.height(), 16, 16)
        p.fillPath(path, QBrush(grad))

        # Border with subtle accent glow
        accent = QColor(self.accent)
        accent.setAlpha(50)
        pen = QPen(accent, 1)
        p.setPen(pen)
        p.drawRoundedRect(r, 16, 16)

        # Top-left corner glow
        glow = QRadialGradient(30, 30, 100)
        glow.setColorAt(0, QColor(self.accent).lighter(150))
        glow.setColorAt(1, QColor(0, 0, 0, 0))
        glow_color = QColor(self.accent)
        glow_color.setAlpha(20)
        glow.setColorAt(0, glow_color)
        p.setBrush(QBrush(glow))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(QPoint(30, 30), 80, 80)

        p.end()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Toast Notification  (slide-in notification bar)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class ToastNotification(QWidget):
    """Slide-in toast notification with auto-dismiss."""

    COLORS = {
        "info":    (CYAN,   "ℹ️"),
        "success": (GREEN,  "✅"),
        "warning": (ORANGE, "⚠️"),
        "error":   (RED,    "❌"),
    }

    def __init__(self, message: str, level: str = "info",
                 duration_ms: int = 4000, parent=None):
        super().__init__(parent)
        color, icon = self.COLORS.get(level, self.COLORS["info"])
        self.setFixedHeight(52)
        self.setMinimumWidth(350)
        self.setMaximumWidth(600)

        self.setStyleSheet(
            f"background: qlineargradient(x1:0,y1:0,x2:1,y2:0,"
            f"stop:0 rgba(17,24,39,0.95), stop:1 rgba(17,24,39,0.85));"
            f"border: 1px solid {color}; border-radius: 10px;")

        lay = QHBoxLayout(self)
        lay.setContentsMargins(16, 0, 16, 0)

        ic = QLabel(icon)
        ic.setFont(QFont("Segoe UI Emoji", 14))
        ic.setStyleSheet("background: transparent; border: none;")
        lay.addWidget(ic)

        msg = QLabel(message)
        msg.setFont(QFont("Segoe UI", 12, QFont.Weight.DemiBold))
        msg.setStyleSheet(
            f"color: {TEXT_BRIGHT}; background: transparent; border: none;")
        lay.addWidget(msg, 1)

        close = QPushButton("×")
        close.setFixedSize(24, 24)
        close.setStyleSheet(
            f"color: {TEXT_DIM}; background: transparent; "
            f"border: none; font-size: 16px; font-weight: bold;")
        close.clicked.connect(self._dismiss)
        lay.addWidget(close)

        # Position at top-right of parent
        if parent:
            self.move(parent.width() - self.width() - 20, 20)

        # Auto-dismiss
        QTimer.singleShot(duration_ms, self._dismiss)

    def _dismiss(self):
        self.hide()
        self.deleteLater()

    def show_toast(self):
        """Show with slide-in animation."""
        self.show()
        self.raise_()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Chat Bubble  (AI assistant style)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class ChatBubble(QWidget):
    """Message bubble for AI chat interface."""

    def __init__(self, message: str, is_user: bool = False,
                 sender: str = "", parent=None):
        super().__init__(parent)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 4, 0, 4)

        # Sender label
        if sender:
            sl = QLabel(sender)
            sl.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
            sl.setStyleSheet(
                f"color: {CYAN if not is_user else PURPLE}; "
                f"background: transparent;")
            align = (Qt.AlignmentFlag.AlignRight if is_user
                     else Qt.AlignmentFlag.AlignLeft)
            sl.setAlignment(align)
            lay.addWidget(sl)

        # Bubble
        bubble = QLabel(message)
        bubble.setWordWrap(True)
        bubble.setFont(QFont("Segoe UI", 12))

        if is_user:
            bubble.setStyleSheet(
                f"background: qlineargradient(x1:0,y1:0,x2:1,y2:1,"
                f"stop:0 #1d4ed8, stop:1 #3b82f6);"
                f"color: #ffffff; border-radius: 14px; "
                f"padding: 12px 18px; border: none;")
            bubble.setAlignment(Qt.AlignmentFlag.AlignRight)
        else:
            bubble.setStyleSheet(
                f"background: rgba(17, 24, 39, 0.9);"
                f"color: {TEXT}; border-radius: 14px; "
                f"padding: 12px 18px;"
                f"border: 1px solid rgba(255,255,255,0.05);")

        lay.addWidget(bubble)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Terminal Viewer  (animated terminal-style log)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TerminalViewer(QWidget):
    """Terminal-style output viewer with colored log lines."""

    def __init__(self, title: str = "Terminal", parent=None):
        super().__init__(parent)
        self.setStyleSheet(
            f"background: rgba(3, 7, 18, 0.95);"
            f"border: 1px solid rgba(255,255,255,0.06);"
            f"border-radius: 12px;")

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        # Title bar (macOS style dots)
        bar = QWidget()
        bar.setFixedHeight(36)
        bar.setStyleSheet(
            f"background: rgba(11, 15, 25, 0.9);"
            f"border-top-left-radius: 12px;"
            f"border-top-right-radius: 12px;"
            f"border-bottom: 1px solid rgba(255,255,255,0.06);")
        bl = QHBoxLayout(bar)
        bl.setContentsMargins(14, 0, 14, 0)

        # Traffic light dots
        for c in ["#ff5f56", "#ffbd2e", "#27c93f"]:
            dot = QLabel("●")
            dot.setFixedSize(14, 14)
            dot.setStyleSheet(
                f"color: {c}; font-size: 10px; background: transparent;")
            bl.addWidget(dot)

        tl = QLabel(f"  {title}")
        tl.setFont(QFont("Segoe UI", 10, QFont.Weight.DemiBold))
        tl.setStyleSheet(f"color: {TEXT_DIM}; background: transparent;")
        bl.addWidget(tl)
        bl.addStretch()
        lay.addWidget(bar)

        # Content
        from PyQt6.QtWidgets import QPlainTextEdit
        self.output = QPlainTextEdit()
        self.output.setReadOnly(True)
        self.output.setFont(QFont("Consolas", 11))
        self.output.setStyleSheet(
            f"background: transparent; color: {GREEN}; "
            f"border: none; padding: 12px; "
            f"selection-background-color: rgba(34, 211, 238, 0.3);")
        lay.addWidget(self.output)

    def append(self, text: str, color: str = None):
        self.output.appendPlainText(text)

    def clear(self):
        self.output.clear()

    def text(self):
        return self.output.toPlainText()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Status Pill  (colored status indicator)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class StatusPill(QLabel):
    """Rounded pill badge for status indicators."""

    STYLES = {
        "online":    (GREEN,  "● Online"),
        "offline":   (RED,    "● Offline"),
        "ready":     (GREEN,  "● Ready"),
        "running":   (CYAN,   "◉ Running"),
        "completed": (GREEN,  "✓ Completed"),
        "error":     (RED,    "✗ Error"),
        "warning":   (ORANGE, "⚠ Warning"),
    }

    def __init__(self, status: str = "ready", parent=None):
        super().__init__(parent)
        self.set_status(status)

    def set_status(self, status: str):
        color, text = self.STYLES.get(status, (TEXT_DIM, status))
        self.setText(f"  {text}  ")
        self.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.setStyleSheet(
            f"color: {color}; "
            f"background: rgba({self._hex_to_rgb(color)}, 0.12); "
            f"border: 1px solid rgba({self._hex_to_rgb(color)}, 0.3); "
            f"border-radius: 12px; padding: 4px 10px;")

    @staticmethod
    def _hex_to_rgb(hex_color: str) -> str:
        h = hex_color.lstrip("#")
        if len(h) == 6:
            return f"{int(h[0:2],16)},{int(h[2:4],16)},{int(h[4:6],16)}"
        return "255,255,255"

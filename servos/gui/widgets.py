"""
Servos – Custom Widgets inspired by 21st.dev / Vercel / Linear.
Refined, minimal, premium aesthetic. No "AI look".
"""

import random
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QGraphicsDropShadowEffect, QSizePolicy, QPushButton,
    QPlainTextEdit,
)
from PyQt6.QtCore import (
    Qt, QTimer, QPoint, QPointF, QRectF, QSize,
)
from PyQt6.QtGui import (
    QFont, QColor, QPainter, QPen, QBrush, QLinearGradient,
    QPainterPath,
)

from servos.gui.theme import (
    BG_PRIMARY, BG_SURFACE, BG_CARD, BG_ELEVATED, BG_HOVER,
    BORDER, CYAN, BLUE, GREEN, RED, ORANGE, YELLOW, PURPLE,
    TEXT, TEXT_SEC, TEXT_DIM, TEXT_BRIGHT,
)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Bento Metric Card  (Vercel/Linear style)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class BentoCard(QWidget):
    """
    Premium stat card:
      - Top: small label + accent dot
      - Middle: large value
      - Bottom: mini sparkline bar
    """

    def __init__(self, icon: str, value: str, label: str,
                 accent: str = CYAN, parent=None):
        super().__init__(parent)
        self.accent = accent
        self._value = value
        self._label = label
        self._icon = icon
        self._spark_pct = 0.0  # fill percentage for mini bar

        self.setMinimumSize(180, 130)
        self.setMaximumHeight(140)
        self.setSizePolicy(QSizePolicy.Policy.Expanding,
                           QSizePolicy.Policy.Fixed)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def set_value(self, v: str):
        self._value = v
        # Animate the sparkline to a random-ish fill for visual interest
        try:
            n = int(v)
            self._spark_pct = min(1.0, n / max(n + 2, 5))
        except ValueError:
            self._spark_pct = 0.5
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        r = QRectF(0.5, 0.5, w - 1, h - 1)

        # ── Background ──
        bg = QLinearGradient(0, 0, 0, h)
        bg.setColorAt(0.0, QColor(20, 27, 45, 240))
        bg.setColorAt(1.0, QColor(12, 17, 30, 250))
        path = QPainterPath()
        path.addRoundedRect(r, 14, 14)
        p.fillPath(path, QBrush(bg))

        # ── Border ──
        border_c = QColor(255, 255, 255, 15)
        p.setPen(QPen(border_c, 0.8))
        p.drawRoundedRect(r, 14, 14)

        # ── Accent dot (top-left) ──
        p.setPen(Qt.PenStyle.NoPen)
        dot_color = QColor(self.accent)
        dot_color.setAlpha(200)
        p.setBrush(QBrush(dot_color))
        p.drawEllipse(QPointF(22, 24), 4, 4)

        # ── Label text ──
        p.setPen(QColor(TEXT_SEC))
        p.setFont(QFont("Segoe UI", 10, QFont.Weight.DemiBold))
        p.drawText(34, 28, self._label)

        # ── Large value ──
        p.setPen(QColor(TEXT_BRIGHT))
        p.setFont(QFont("Segoe UI", 32, QFont.Weight.ExtraBold))
        p.drawText(22, 80, self._value)

        # ── Mini sparkline bar (bottom) ──
        bar_x = 22
        bar_y = h - 24
        bar_w = w - 44
        bar_h = 5

        # Track
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(255, 255, 255, 10))
        track = QPainterPath()
        track.addRoundedRect(bar_x, bar_y, bar_w, bar_h, 2.5, 2.5)
        p.fillPath(track, QBrush(QColor(255, 255, 255, 10)))

        # Fill
        fill_w = bar_w * self._spark_pct
        if fill_w > 0:
            fill_grad = QLinearGradient(bar_x, 0, bar_x + fill_w, 0)
            acc = QColor(self.accent)
            fill_grad.setColorAt(0.0, acc)
            acc2 = QColor(acc)
            acc2.setAlpha(120)
            fill_grad.setColorAt(1.0, acc2)
            fill_path = QPainterPath()
            fill_path.addRoundedRect(bar_x, bar_y, fill_w, bar_h, 2.5, 2.5)
            p.fillPath(fill_path, QBrush(fill_grad))

        p.end()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Section Header (clean typography)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class SectionHeader(QWidget):
    """Section divider with title and optional action button."""

    def __init__(self, title: str, action_text: str = None,
                 action_callback=None, parent=None):
        super().__init__(parent)
        self.setFixedHeight(36)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)

        lbl = QLabel(title)
        lbl.setFont(QFont("Segoe UI", 13, QFont.Weight.DemiBold))
        lbl.setStyleSheet(f"color: {TEXT}; background: transparent;")
        lay.addWidget(lbl)

        lay.addStretch()

        if action_text and action_callback:
            btn = QPushButton(action_text)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setFont(QFont("Segoe UI", 10))
            btn.setStyleSheet(
                f"color: {CYAN}; background: transparent; "
                f"border: none; padding: 4px 8px;")
            btn.clicked.connect(action_callback)
            lay.addWidget(btn)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Panel Card  (Linear/Vercel style container)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class PanelCard(QFrame):
    """Subtle bordered panel with no heavy visual chrome."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(
            f"PanelCard {{ "
            f"  background: rgba(15, 20, 35, 0.6); "
            f"  border: 1px solid rgba(255, 255, 255, 0.06); "
            f"  border-radius: 12px; "
            f"}}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Toast Notification
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
        self.setFixedHeight(48)
        self.setMinimumWidth(340)
        self.setMaximumWidth(560)

        self.setStyleSheet(
            f"background: rgba(15, 20, 35, 0.95);"
            f"border: 1px solid rgba(255,255,255,0.08); "
            f"border-left: 3px solid {color}; border-radius: 8px;")

        lay = QHBoxLayout(self)
        lay.setContentsMargins(14, 0, 14, 0)

        ic = QLabel(icon)
        ic.setFont(QFont("Segoe UI Emoji", 13))
        ic.setStyleSheet("background: transparent; border: none;")
        lay.addWidget(ic)

        msg = QLabel(message)
        msg.setFont(QFont("Segoe UI", 11))
        msg.setStyleSheet(
            f"color: {TEXT}; background: transparent; border: none;")
        lay.addWidget(msg, 1)

        close = QPushButton("×")
        close.setFixedSize(22, 22)
        close.setStyleSheet(
            f"color: {TEXT_DIM}; background: transparent; "
            f"border: none; font-size: 15px;")
        close.clicked.connect(self._dismiss)
        lay.addWidget(close)

        if parent:
            self.move(parent.width() - self.width() - 20, 16)

        QTimer.singleShot(duration_ms, self._dismiss)

    def _dismiss(self):
        self.hide()
        self.deleteLater()

    def show_toast(self):
        self.show()
        self.raise_()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Chat Bubble
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class ChatBubble(QWidget):
    """Message bubble for AI chat interface."""

    def __init__(self, message: str, is_user: bool = False,
                 sender: str = "", parent=None):
        super().__init__(parent)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 4, 0, 4)

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

        bubble = QLabel(message)
        bubble.setWordWrap(True)
        bubble.setFont(QFont("Segoe UI", 12))

        if is_user:
            bubble.setStyleSheet(
                f"background: qlineargradient(x1:0,y1:0,x2:1,y2:1,"
                f"stop:0 #1d4ed8, stop:1 #3b82f6);"
                f"color: #ffffff; border-radius: 14px; "
                f"padding: 12px 18px; border: none;")
        else:
            bubble.setStyleSheet(
                f"background: rgba(17, 24, 39, 0.9);"
                f"color: {TEXT}; border-radius: 14px; "
                f"padding: 12px 18px;"
                f"border: 1px solid rgba(255,255,255,0.05);")

        lay.addWidget(bubble)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Terminal Viewer  (macOS window style)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TerminalViewer(QWidget):
    """Terminal-style output viewer."""

    def __init__(self, title: str = "Terminal", parent=None):
        super().__init__(parent)
        self.setStyleSheet(
            f"background: rgba(3, 7, 18, 0.95);"
            f"border: 1px solid rgba(255,255,255,0.06);"
            f"border-radius: 10px;")

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        # Title bar
        bar = QWidget()
        bar.setFixedHeight(32)
        bar.setStyleSheet(
            f"background: rgba(11, 15, 25, 0.9);"
            f"border-top-left-radius: 10px;"
            f"border-top-right-radius: 10px;"
            f"border-bottom: 1px solid rgba(255,255,255,0.04);")
        bl = QHBoxLayout(bar)
        bl.setContentsMargins(12, 0, 12, 0)

        for c in ["#ff5f56", "#ffbd2e", "#27c93f"]:
            dot = QLabel("●")
            dot.setFixedSize(12, 12)
            dot.setStyleSheet(
                f"color: {c}; font-size: 9px; background: transparent;")
            bl.addWidget(dot)

        tl = QLabel(f"  {title}")
        tl.setFont(QFont("Segoe UI", 9))
        tl.setStyleSheet(f"color: {TEXT_DIM}; background: transparent;")
        bl.addWidget(tl)
        bl.addStretch()
        lay.addWidget(bar)

        self.output = QPlainTextEdit()
        self.output.setReadOnly(True)
        self.output.setFont(QFont("Consolas", 11))
        self.output.setStyleSheet(
            f"background: transparent; color: {GREEN}; "
            f"border: none; padding: 10px; "
            f"selection-background-color: rgba(34, 211, 238, 0.3);")
        lay.addWidget(self.output)

    def append(self, text: str, color: str = None):
        self.output.appendPlainText(text)

    def clear(self):
        self.output.clear()

    def text(self):
        return self.output.toPlainText()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# StatusPill  (colored status indicator)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class StatusPill(QLabel):
    """Rounded pill badge for status."""

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

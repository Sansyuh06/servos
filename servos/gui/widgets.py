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

        # ── Background (zinc) ──
        bg = QLinearGradient(0, 0, 0, h)
        bg.setColorAt(0.0, QColor(19, 19, 22))
        bg.setColorAt(1.0, QColor(14, 14, 17))
        path = QPainterPath()
        path.addRoundedRect(r, 10, 10)
        p.fillPath(path, QBrush(bg))

        # ── Border ──
        p.setPen(QPen(QColor(39, 39, 42), 1))
        p.drawRoundedRect(r, 10, 10)

        # ── Accent bar (top-left) ──
        p.setPen(Qt.PenStyle.NoPen)
        acc = QColor(self.accent)
        acc.setAlpha(160)
        bar_path = QPainterPath()
        bar_path.addRoundedRect(16, 16, 3, 20, 1.5, 1.5)
        p.fillPath(bar_path, QBrush(acc))

        # ── Label ──
        p.setPen(QColor(113, 113, 122))  # zinc-500
        p.setFont(QFont("Segoe UI", 10, QFont.Weight.DemiBold))
        p.drawText(28, 30, self._label)

        # ── Value ──
        p.setPen(QColor(250, 250, 250))  # zinc-50
        p.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        p.drawText(16, 78, self._value)

        # ── Sparkline bar ──
        bar_x, bar_y = 16, h - 22
        bar_w, bar_h = w - 32, 4

        p.setBrush(QColor(39, 39, 42))
        track = QPainterPath()
        track.addRoundedRect(bar_x, bar_y, bar_w, bar_h, 2, 2)
        p.fillPath(track, QBrush(QColor(39, 39, 42)))

        fill_w = bar_w * self._spark_pct
        if fill_w > 0:
            acc_fill = QColor(self.accent)
            acc_fill.setAlpha(180)
            fill_path = QPainterPath()
            fill_path.addRoundedRect(bar_x, bar_y, fill_w, bar_h, 2, 2)
            p.fillPath(fill_path, QBrush(acc_fill))

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


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Spatial Disk Showcase Card
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class DiskShowcaseCard(QWidget):
    """
    3D-perspective disk card showing drive details.
    Reactive gradient based on filesystem type.
    """

    FS_COLORS = {
        "NTFS":  ("#1d4ed8", "#3b82f6"),
        "FAT32": ("#047857", "#10b981"),
        "exFAT": ("#7c3aed", "#8b5cf6"),
        "ext4":  ("#dc2626", "#ef4444"),
    }
    DEFAULT_COLORS = ("#374151", "#6b7280")

    def __init__(self, drive_letter: str = "D:\\",
                 label: str = "USB Drive",
                 filesystem: str = "NTFS",
                 capacity: str = "14.6 GB",
                 used_pct: float = 0.45,
                 is_removable: bool = True,
                 parent=None):
        super().__init__(parent)
        self.drive_letter = drive_letter
        self.label = label
        self.filesystem = filesystem
        self.capacity = capacity
        self.used_pct = max(0.0, min(1.0, used_pct))
        self.is_removable = is_removable

        self.setFixedSize(220, 160)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()

        c1, c2 = self.FS_COLORS.get(
            self.filesystem, self.DEFAULT_COLORS)

        # Card background with gradient
        bg = QLinearGradient(0, 0, w, h)
        bg.setColorAt(0.0, QColor(c1))
        bg.setColorAt(1.0, QColor(c2))

        path = QPainterPath()
        path.addRoundedRect(QRectF(1, 1, w-2, h-2), 16, 16)
        p.fillPath(path, QBrush(bg))

        # Subtle inner glow
        inner = QLinearGradient(0, 0, 0, h)
        inner.setColorAt(0.0, QColor(255, 255, 255, 20))
        inner.setColorAt(0.5, QColor(255, 255, 255, 0))
        inner.setColorAt(1.0, QColor(0, 0, 0, 40))
        p.fillPath(path, QBrush(inner))

        # Border
        p.setPen(QPen(QColor(255, 255, 255, 25), 1))
        p.drawRoundedRect(QRectF(1, 1, w-2, h-2), 16, 16)

        # Drive letter (large)
        p.setPen(QColor(255, 255, 255, 220))
        p.setFont(QFont("Segoe UI", 28, QFont.Weight.ExtraBold))
        p.drawText(20, 48, self.drive_letter.rstrip("\\"))

        # Tag badge
        tag = "REMOVABLE" if self.is_removable else "FIXED"
        p.setFont(QFont("Segoe UI", 7, QFont.Weight.Bold))
        p.setPen(QColor(255, 255, 255, 180))
        tw = p.fontMetrics().horizontalAdvance(tag) + 14
        p.setBrush(QColor(0, 0, 0, 60))
        p.setPen(Qt.PenStyle.NoPen)
        tag_path = QPainterPath()
        tag_path.addRoundedRect(w - tw - 14, 14, tw, 20, 10, 10)
        p.fillPath(tag_path, QBrush(QColor(0, 0, 0, 60)))
        p.setPen(QColor(255, 255, 255, 180))
        p.drawText(int(w - tw - 14 + 7), 28, tag)

        # Label + FS
        p.setPen(QColor(255, 255, 255, 200))
        p.setFont(QFont("Segoe UI", 11, QFont.Weight.DemiBold))
        p.drawText(20, 74, self.label)

        p.setPen(QColor(255, 255, 255, 140))
        p.setFont(QFont("Segoe UI", 9))
        p.drawText(20, 92, f"{self.filesystem}  •  {self.capacity}")

        # Usage bar
        bar_y = h - 32
        bar_w = w - 40
        bar_h = 6

        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(0, 0, 0, 50))
        track = QPainterPath()
        track.addRoundedRect(20, bar_y, bar_w, bar_h, 3, 3)
        p.fillPath(track, QBrush(QColor(0, 0, 0, 50)))

        fill_w = bar_w * self.used_pct
        if fill_w > 0:
            p.setBrush(QColor(255, 255, 255, 180))
            fill = QPainterPath()
            fill.addRoundedRect(20, bar_y, fill_w, bar_h, 3, 3)
            p.fillPath(fill, QBrush(QColor(255, 255, 255, 180)))

        # Usage text
        p.setPen(QColor(255, 255, 255, 150))
        p.setFont(QFont("Segoe UI", 8))
        p.drawText(20, h - 10, f"{int(self.used_pct*100)}% used")

        p.end()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# HALIDE Topo Hero Background
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TopoHeroBackground(QWidget):
    """
    Topographic contour lines background with film grain.
    Inspired by HALIDE topo hero from 21st.dev.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._generate_contours()

    def _generate_contours(self):
        """Pre-compute contour ring data."""
        import math
        self._rings = []
        cx, cy = 0.5, 0.5  # center as fraction
        for i in range(12):
            r = 0.08 + i * 0.07
            alpha = max(8, 30 - i * 2)
            self._rings.append((cx, cy, r, alpha))
        # Off-center rings
        for ox, oy in [(0.25, 0.35), (0.72, 0.65), (0.15, 0.7)]:
            for i in range(6):
                r = 0.04 + i * 0.05
                alpha = max(5, 20 - i * 3)
                self._rings.append((ox, oy, r, alpha))

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()

        # Background gradient
        bg = QLinearGradient(0, 0, w, h)
        bg.setColorAt(0.0, QColor(3, 7, 18))
        bg.setColorAt(0.4, QColor(6, 12, 26))
        bg.setColorAt(1.0, QColor(3, 7, 18))
        p.fillRect(self.rect(), QBrush(bg))

        # Contour rings
        for cx_frac, cy_frac, r_frac, alpha in self._rings:
            cx = int(cx_frac * w)
            cy = int(cy_frac * h)
            r = int(r_frac * max(w, h))
            pen = QPen(QColor(34, 211, 238, alpha), 1)
            p.setPen(pen)
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawEllipse(QPointF(cx, cy), r, r * 0.7)

        # Film grain (sparse random dots)
        import random as rng
        rng.seed(42)
        p.setPen(Qt.PenStyle.NoPen)
        for _ in range(300):
            x = rng.randint(0, w)
            y = rng.randint(0, h)
            a = rng.randint(3, 12)
            p.setBrush(QColor(255, 255, 255, a))
            p.drawRect(x, y, 1, 1)

        p.end()


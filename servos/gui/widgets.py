"""
Servos – Custom Widgets inspired by 21st.dev components.
Clean zinc aesthetic with premium touches.
"""

import random
import math
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QGraphicsDropShadowEffect, QSizePolicy, QPushButton,
    QPlainTextEdit, QGridLayout,
)
from PyQt6.QtCore import (
    Qt, QTimer, QPoint, QPointF, QRectF, QSize,
)
from PyQt6.QtGui import (
    QFont, QColor, QPainter, QPen, QBrush, QLinearGradient,
    QPainterPath, QRadialGradient,
)

from servos.gui.theme import (
    BG_PRIMARY, BG_SURFACE, BG_CARD, BG_ELEVATED, BG_HOVER,
    BORDER, BORDER_DIM, CYAN, BLUE, GREEN, RED, ORANGE, YELLOW, PURPLE,
    TEXT, TEXT_SEC, TEXT_DIM, TEXT_BRIGHT,
)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Bento Metric Card
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class BentoCard(QWidget):
    """Metric card with accent bar, label, value, sparkline."""

    def __init__(self, icon: str, value: str, label: str,
                 accent: str = BLUE, parent=None):
        super().__init__(parent)
        self.accent = accent
        self._value = value
        self._label = label
        self._icon = icon
        self._spark_pct = 0.0

        self.setMinimumSize(160, 110)
        self.setMaximumHeight(120)
        self.setSizePolicy(QSizePolicy.Policy.Expanding,
                           QSizePolicy.Policy.Fixed)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def set_value(self, v: str):
        self._value = v
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

        # Background
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(19, 19, 22))
        path = QPainterPath()
        path.addRoundedRect(r, 10, 10)
        p.fillPath(path, QBrush(QColor(19, 19, 22)))

        # Border
        p.setPen(QPen(QColor(39, 39, 42), 1))
        p.drawRoundedRect(r, 10, 10)

        # Accent bar
        p.setPen(Qt.PenStyle.NoPen)
        acc = QColor(self.accent)
        acc.setAlpha(180)
        bar = QPainterPath()
        bar.addRoundedRect(14, 14, 3, 18, 1.5, 1.5)
        p.fillPath(bar, QBrush(acc))

        # Label
        p.setPen(QColor(113, 113, 122))
        p.setFont(QFont("Segoe UI", 9, QFont.Weight.DemiBold))
        p.drawText(26, 28, self._label)

        # Value
        p.setPen(QColor(250, 250, 250))
        p.setFont(QFont("Segoe UI", 26, QFont.Weight.Bold))
        p.drawText(14, 68, self._value)

        # Sparkline
        bx, by = 14, h - 18
        bw, bh = w - 28, 3
        p.setBrush(QColor(39, 39, 42))
        tp = QPainterPath()
        tp.addRoundedRect(bx, by, bw, bh, 1.5, 1.5)
        p.fillPath(tp, QBrush(QColor(39, 39, 42)))

        fw = bw * self._spark_pct
        if fw > 0:
            af = QColor(self.accent)
            af.setAlpha(200)
            fp = QPainterPath()
            fp.addRoundedRect(bx, by, fw, bh, 1.5, 1.5)
            p.fillPath(fp, QBrush(af))

        p.end()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Section Header
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class SectionHeader(QWidget):
    def __init__(self, title: str, action_text: str = None,
                 action_callback=None, parent=None):
        super().__init__(parent)
        self.setFixedHeight(32)
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
                f"color: {BLUE}; background: transparent; "
                f"border: none; padding: 4px 8px;")
            btn.clicked.connect(action_callback)
            lay.addWidget(btn)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Panel Card
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class PanelCard(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(
            f"PanelCard {{ "
            f"  background: {BG_CARD}; "
            f"  border: 1px solid {BORDER}; "
            f"  border-radius: 10px; "
            f"}}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Toast Notification
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class ToastNotification(QWidget):
    COLORS = {
        "info":    (BLUE,   "ℹ️"),
        "success": (GREEN,  "✅"),
        "warning": (ORANGE, "⚠️"),
        "error":   (RED,    "❌"),
    }

    def __init__(self, message: str, level: str = "info",
                 duration_ms: int = 4000, parent=None):
        super().__init__(parent)
        color, icon = self.COLORS.get(level, self.COLORS["info"])
        self.setFixedHeight(44)
        self.setMinimumWidth(320)
        self.setMaximumWidth(520)

        self.setStyleSheet(
            f"background: {BG_CARD}; "
            f"border: 1px solid {BORDER}; "
            f"border-left: 3px solid {color}; border-radius: 8px;")

        lay = QHBoxLayout(self)
        lay.setContentsMargins(12, 0, 12, 0)

        ic = QLabel(icon)
        ic.setFont(QFont("Segoe UI Emoji", 12))
        ic.setStyleSheet("background: transparent; border: none;")
        lay.addWidget(ic)

        msg = QLabel(message)
        msg.setFont(QFont("Segoe UI", 11))
        msg.setStyleSheet(
            f"color: {TEXT}; background: transparent; border: none;")
        lay.addWidget(msg, 1)

        close = QPushButton("×")
        close.setFixedSize(20, 20)
        close.setStyleSheet(
            f"color: {TEXT_DIM}; background: transparent; "
            f"border: none; font-size: 14px;")
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
    def __init__(self, message: str, is_user: bool = False,
                 sender: str = "", parent=None):
        super().__init__(parent)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 4, 0, 4)

        if sender:
            sl = QLabel(sender)
            sl.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
            sl.setStyleSheet(
                f"color: {BLUE if not is_user else PURPLE}; "
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
                f"background: {BLUE}; "
                f"color: #ffffff; border-radius: 12px; "
                f"padding: 10px 16px; border: none;")
        else:
            bubble.setStyleSheet(
                f"background: {BG_CARD}; "
                f"color: {TEXT}; border-radius: 12px; "
                f"padding: 10px 16px; "
                f"border: 1px solid {BORDER};")

        lay.addWidget(bubble)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Terminal Viewer
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TerminalViewer(QWidget):
    def __init__(self, title: str = "Terminal", parent=None):
        super().__init__(parent)
        self.setStyleSheet(
            f"background: {BG_PRIMARY}; "
            f"border: 1px solid {BORDER}; "
            f"border-radius: 8px;")

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        bar = QWidget()
        bar.setFixedHeight(30)
        bar.setStyleSheet(
            f"background: {BG_CARD}; "
            f"border-top-left-radius: 8px; "
            f"border-top-right-radius: 8px; "
            f"border-bottom: 1px solid {BORDER};")
        bl = QHBoxLayout(bar)
        bl.setContentsMargins(10, 0, 10, 0)

        for c in ["#ff5f56", "#ffbd2e", "#27c93f"]:
            dot = QLabel("●")
            dot.setFixedSize(10, 10)
            dot.setStyleSheet(
                f"color: {c}; font-size: 8px; background: transparent;")
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
            f"border: none; padding: 8px; "
            f"selection-background-color: rgba(59, 130, 246, 0.3);")
        lay.addWidget(self.output)

    def append(self, text: str, color: str = None):
        self.output.appendPlainText(text)

    def clear(self):
        self.output.clear()

    def text(self):
        return self.output.toPlainText()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# StatusPill
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class StatusPill(QLabel):
    STYLES = {
        "online":    (GREEN,  "● Online"),
        "offline":   (RED,    "● Offline"),
        "ready":     (GREEN,  "● Ready"),
        "running":   (BLUE,   "◉ Running"),
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
            f"background: rgba({self._hex_to_rgb(color)}, 0.1); "
            f"border: 1px solid rgba({self._hex_to_rgb(color)}, 0.25); "
            f"border-radius: 12px; padding: 4px 10px;")

    @staticmethod
    def _hex_to_rgb(hex_color: str) -> str:
        h = hex_color.lstrip("#")
        if len(h) == 6:
            return f"{int(h[0:2],16)},{int(h[2:4],16)},{int(h[4:6],16)}"
        return "255,255,255"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Spatial Device Showcase  (21st.dev/daiv09)
# Dark card with radial gradient, specs panel, status pill
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class SpatialDeviceCard(QWidget):
    """
    Spatial Product Showcase style device card.
    Radial gradient bg, large drive icon, specs on right, status pill.
    """

    FS_GRADIENTS = {
        "NTFS":  (QColor(15, 23, 42), QColor(30, 58, 138)),
        "FAT32": (QColor(5, 46, 22), QColor(22, 101, 52)),
        "exFAT": (QColor(46, 16, 101), QColor(88, 28, 135)),
        "ext4":  (QColor(69, 10, 10), QColor(127, 29, 29)),
    }
    DEFAULT_GRAD = (QColor(15, 15, 20), QColor(30, 30, 40))

    def __init__(self, drive_letter="D:\\", label="USB Drive",
                 filesystem="NTFS", capacity="14.6 GB",
                 used_pct=0.45, is_removable=True, parent=None):
        super().__init__(parent)
        self.drive_letter = drive_letter
        self.label = label
        self.filesystem = filesystem
        self.capacity = capacity
        self.used_pct = max(0.0, min(1.0, used_pct))
        self.is_removable = is_removable

        self.setFixedSize(280, 180)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()

        inner, outer = self.FS_GRADIENTS.get(
            self.filesystem, self.DEFAULT_GRAD)

        # Radial gradient background
        rg = QRadialGradient(w * 0.35, h * 0.4, max(w, h) * 0.7)
        rg.setColorAt(0.0, outer)
        rg.setColorAt(1.0, inner)

        card = QPainterPath()
        card.addRoundedRect(QRectF(0, 0, w, h), 14, 14)
        p.fillPath(card, QBrush(rg))

        # Border
        p.setPen(QPen(QColor(255, 255, 255, 12), 1))
        p.drawRoundedRect(QRectF(0.5, 0.5, w-1, h-1), 14, 14)

        # Large drive letter (left)
        p.setPen(QColor(255, 255, 255, 200))
        p.setFont(QFont("Segoe UI", 40, QFont.Weight.ExtraBold))
        letter = self.drive_letter.rstrip("\\").rstrip(":")
        p.drawText(24, 70, letter)

        # Status pill
        status = "CONNECTED" if self.is_removable else "FIXED"
        p.setFont(QFont("Segoe UI", 7, QFont.Weight.Bold))
        tw = p.fontMetrics().horizontalAdvance(status) + 16
        pill_x = 24
        pill_y = 82
        pill = QPainterPath()
        pill.addRoundedRect(pill_x, pill_y, tw, 18, 9, 9)
        p.setPen(Qt.PenStyle.NoPen)
        p.fillPath(pill, QBrush(QColor(34, 197, 94, 50)))
        p.setPen(QColor(34, 197, 94, 200))
        p.drawText(pill_x + 8, pill_y + 13, f"● {status}")

        # Right side: specs
        rx = w * 0.48
        p.setPen(QColor(255, 255, 255, 120))
        p.setFont(QFont("Segoe UI", 7, QFont.Weight.Bold))
        p.drawText(int(rx), 24, self.filesystem.upper())

        p.setPen(QColor(255, 255, 255, 230))
        p.setFont(QFont("Segoe UI", 15, QFont.Weight.Bold))
        p.drawText(int(rx), 46, self.label)

        p.setPen(QColor(255, 255, 255, 120))
        p.setFont(QFont("Segoe UI", 9))
        p.drawText(int(rx), 64, self.capacity)

        # Usage bar
        bar_x = int(rx)
        bar_y = 80
        bar_w = int(w - rx - 20)
        bar_h = 4

        p.setPen(Qt.PenStyle.NoPen)
        track = QPainterPath()
        track.addRoundedRect(bar_x, bar_y, bar_w, bar_h, 2, 2)
        p.fillPath(track, QBrush(QColor(255, 255, 255, 20)))

        fw = bar_w * self.used_pct
        if fw > 0:
            fill = QPainterPath()
            fill.addRoundedRect(bar_x, bar_y, fw, bar_h, 2, 2)
            p.fillPath(fill, QBrush(QColor(59, 130, 246, 200)))

        p.setPen(QColor(255, 255, 255, 100))
        p.setFont(QFont("Segoe UI", 8))
        p.drawText(bar_x, bar_y + 16, f"{int(self.used_pct*100)}% used")

        # Glow circles (spatial effect)
        for radius in [60, 90, 120]:
            glow = QColor(outer)
            glow.setAlpha(max(3, 12 - radius // 10))
            p.setPen(QPen(glow, 0.5))
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawEllipse(QPointF(w * 0.35, h * 0.4), radius, radius)

        p.end()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# HALIDE Topo Hero Background  (21st.dev/shivendra9795kumar)
# Monochrome topographical lines + film grain
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TopoHeroBackground(QWidget):
    """Topographic contour background with film grain."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._rings = []
        # Main peak
        for i in range(14):
            r = 0.06 + i * 0.06
            alpha = max(6, 28 - i * 2)
            self._rings.append((0.5, 0.45, r, alpha))
        # Secondary peaks
        for cx, cy in [(0.2, 0.3), (0.78, 0.6), (0.12, 0.75)]:
            for i in range(7):
                r = 0.03 + i * 0.045
                alpha = max(4, 18 - i * 2)
                self._rings.append((cx, cy, r, alpha))

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()

        # Background
        p.fillRect(self.rect(), QColor(9, 9, 11))

        # Contour rings
        for cx_f, cy_f, r_f, alpha in self._rings:
            cx, cy = int(cx_f * w), int(cy_f * h)
            r = int(r_f * max(w, h))
            p.setPen(QPen(QColor(161, 161, 170, alpha), 0.8))
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawEllipse(QPointF(cx, cy), r, r * 0.65)

        # Film grain
        random.seed(42)
        p.setPen(Qt.PenStyle.NoPen)
        for _ in range(400):
            x = random.randint(0, w)
            y = random.randint(0, h)
            a = random.randint(4, 16)
            p.setBrush(QColor(255, 255, 255, a))
            p.drawRect(x, y, 1, 1)

        p.end()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Showcase Grid Card  (21st.dev/dhileepkumargm)
# Bento-style card with badge, title, description
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class ShowcaseCard(QWidget):
    """
    Bento showcase card with gradient header, badge, title, description.
    Used in the Ultra Quality Showcase Grid layout.
    """

    def __init__(self, title: str, description: str = "",
                 badge: str = None, gradient_start: str = "#1a1a1f",
                 gradient_end: str = "#27272a",
                 accent: str = BLUE, parent=None):
        super().__init__(parent)
        self._title = title
        self._desc = description
        self._badge = badge
        self._g_start = gradient_start
        self._g_end = gradient_end
        self._accent = accent

        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(120)
        self.setSizePolicy(QSizePolicy.Policy.Expanding,
                           QSizePolicy.Policy.Expanding)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()

        # Card background
        bg = QLinearGradient(0, 0, w, h)
        bg.setColorAt(0.0, QColor(self._g_start))
        bg.setColorAt(1.0, QColor(self._g_end))
        card = QPainterPath()
        card.addRoundedRect(QRectF(0.5, 0.5, w-1, h-1), 12, 12)
        p.fillPath(card, QBrush(bg))

        # Border
        p.setPen(QPen(QColor(39, 39, 42), 1))
        p.drawRoundedRect(QRectF(0.5, 0.5, w-1, h-1), 12, 12)

        # Gradient image area (top half)
        top_h = int(h * 0.45)
        ig = QLinearGradient(0, 0, w, top_h)
        ig.setColorAt(0.0, QColor(self._accent).darker(200))
        ig.setColorAt(1.0, QColor(39, 39, 42))
        img_area = QPainterPath()
        img_area.addRoundedRect(QRectF(1, 1, w-2, top_h), 11, 11)
        p.fillPath(img_area, QBrush(ig))

        # Content area
        cy = top_h + 10

        # Badge
        if self._badge:
            p.setPen(Qt.PenStyle.NoPen)
            badge_w = len(self._badge) * 8 + 16
            bp = QPainterPath()
            bp.addRoundedRect(14, cy, badge_w, 20, 4, 4)
            badge_color = QColor(self._accent)
            badge_color.setAlpha(30)
            p.fillPath(bp, QBrush(badge_color))
            p.setPen(QColor(self._accent))
            p.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
            p.drawText(22, cy + 14, self._badge)
            cy += 28

        # Title
        p.setPen(QColor(250, 250, 250))
        p.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        p.drawText(QRectF(14, cy, w - 28, 40),
                   Qt.AlignmentFlag.AlignLeft | Qt.TextFlag.TextWordWrap,
                   self._title)
        cy += 32

        # Description
        if self._desc:
            p.setPen(QColor(113, 113, 122))
            p.setFont(QFont("Segoe UI", 10))
            p.drawText(QRectF(14, cy, w - 28, h - cy - 10),
                       Qt.AlignmentFlag.AlignLeft | Qt.TextFlag.TextWordWrap,
                       self._desc)

        p.end()


# Keep DiskShowcaseCard as alias for backward compat
DiskShowcaseCard = SpatialDeviceCard

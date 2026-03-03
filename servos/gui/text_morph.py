"""
Servos – Gooey Text Morphing Widget.
Inspired by 21st.dev/victorwelander/gooey-text-morphing.
Cross-fade animation cycling through text phrases.
"""

from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtWidgets import QGraphicsOpacityEffect


class MorphingText(QWidget):
    """
    Two overlapping labels that cross-fade to create
    a smooth text morphing effect.
    """

    def __init__(self, texts: list[str], morph_ms: int = 800,
                 cooldown_ms: int = 2000, font_size: int = 36,
                 color: str = "#ffffff", parent=None):
        super().__init__(parent)
        self._texts = texts or ["SERVOS"]
        self._index = 0
        self._morph_ms = morph_ms
        self._cooldown_ms = cooldown_ms

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet("background: transparent;")

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        # We stack two labels on top of each other
        self._container = QWidget()
        self._container.setStyleSheet("background: transparent;")
        lay.addWidget(self._container)

        fnt = QFont("Segoe UI", font_size, QFont.Weight.ExtraBold)

        self._label_a = QLabel(self._texts[0], self._container)
        self._label_a.setFont(fnt)
        self._label_a.setStyleSheet(f"color: {color}; background: transparent;")
        self._label_a.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._label_b = QLabel("", self._container)
        self._label_b.setFont(fnt)
        self._label_b.setStyleSheet(f"color: {color}; background: transparent;")
        self._label_b.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Opacity effects
        self._eff_a = QGraphicsOpacityEffect(self._label_a)
        self._eff_a.setOpacity(1.0)
        self._label_a.setGraphicsEffect(self._eff_a)

        self._eff_b = QGraphicsOpacityEffect(self._label_b)
        self._eff_b.setOpacity(0.0)
        self._label_b.setGraphicsEffect(self._eff_b)

        # Morph timer
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._morph)
        self._timer.start(cooldown_ms + morph_ms)

        # Initial morph after cooldown
        QTimer.singleShot(cooldown_ms, self._morph)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        w, h = self._container.width(), self._container.height()
        self._label_a.setGeometry(0, 0, w, h)
        self._label_b.setGeometry(0, 0, w, h)

    def _morph(self):
        self._index = (self._index + 1) % len(self._texts)
        next_text = self._texts[self._index]
        self._label_b.setText(next_text)

        # Fade out A
        anim_a = QPropertyAnimation(self._eff_a, b"opacity", self)
        anim_a.setDuration(self._morph_ms)
        anim_a.setStartValue(1.0)
        anim_a.setEndValue(0.0)
        anim_a.setEasingCurve(QEasingCurve.Type.InOutCubic)

        # Fade in B
        anim_b = QPropertyAnimation(self._eff_b, b"opacity", self)
        anim_b.setDuration(self._morph_ms)
        anim_b.setStartValue(0.0)
        anim_b.setEndValue(1.0)
        anim_b.setEasingCurve(QEasingCurve.Type.InOutCubic)

        anim_a.start()
        anim_b.start()
        self._anim_a = anim_a
        self._anim_b = anim_b

        # After morph, swap labels for next cycle
        QTimer.singleShot(self._morph_ms + 50, self._swap)

    def _swap(self):
        # Copy B text to A, reset opacities
        self._label_a.setText(self._label_b.text())
        self._eff_a.setOpacity(1.0)
        self._eff_b.setOpacity(0.0)

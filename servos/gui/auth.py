"""
Servos – Authentication System.
Real login with SQLite-backed user accounts and SHA-256 password hashing.
"""

import os
import hashlib
import sqlite3
from datetime import datetime

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QGraphicsOpacityEffect, QSpacerItem,
    QSizePolicy,
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QPainter, QLinearGradient, QBrush, QPainterPath

from servos.gui.theme import (
    BG_PRIMARY, BG_SURFACE, CYAN, BLUE, GREEN, RED,
    TEXT, TEXT_SEC, TEXT_DIM, TEXT_BRIGHT, BORDER,
)
from servos.config import get_config


# ── Database helpers ──

def _db_path() -> str:
    cfg = get_config()
    return os.path.join(cfg.get("data_dir", ""), "users.db")


def _hash_pw(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def _init_users_db():
    db = _db_path()
    os.makedirs(os.path.dirname(db), exist_ok=True)
    conn = sqlite3.connect(db)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def _user_exists() -> bool:
    _init_users_db()
    conn = sqlite3.connect(_db_path())
    count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    conn.close()
    return count > 0


def _create_user(username: str, password: str) -> bool:
    _init_users_db()
    try:
        conn = sqlite3.connect(_db_path())
        conn.execute(
            "INSERT INTO users (username, password_hash, created_at) VALUES (?, ?, ?)",
            (username, _hash_pw(password), datetime.now().isoformat()))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False


def _verify_user(username: str, password: str) -> bool:
    _init_users_db()
    conn = sqlite3.connect(_db_path())
    row = conn.execute(
        "SELECT password_hash FROM users WHERE username = ?",
        (username,)).fetchone()
    conn.close()
    if row and row[0] == _hash_pw(password):
        return True
    return False


# ── Login Widget ──

class LoginScreen(QWidget):
    """
    Full-screen login / create-account screen.
    Gradient border card, centered, dark background.
    Emits `login_success(username)` on valid login.
    """

    login_success = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._is_signup = not _user_exists()
        self._build()

    def _build(self):
        self.setStyleSheet(f"background: {BG_PRIMARY};")
        outer = QVBoxLayout(self)
        outer.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Card
        card = QWidget()
        card.setFixedSize(400, 460)
        card.setStyleSheet(
            f"background: #131316; "
            f"border: 1px solid {BORDER}; "
            f"border-radius: 16px;")
        cl = QVBoxLayout(card)
        cl.setContentsMargins(36, 36, 36, 36)
        cl.setSpacing(12)

        # Logo
        logo = QLabel("⚔️")
        logo.setFont(QFont("Segoe UI Emoji", 36))
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo.setStyleSheet("background: transparent;")
        cl.addWidget(logo)

        # Title
        title = QLabel("SERVOS")
        title.setFont(QFont("Segoe UI", 24, QFont.Weight.ExtraBold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(f"color: {TEXT_BRIGHT}; background: transparent; "
                            f"letter-spacing: 3px;")
        cl.addWidget(title)

        # Subtitle
        sub_text = "Create your account" if self._is_signup else "Sign in to continue"
        sub = QLabel(sub_text)
        sub.setFont(QFont("Segoe UI", 11))
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub.setStyleSheet(f"color: {TEXT_DIM}; background: transparent;")
        cl.addWidget(sub)

        cl.addSpacerItem(QSpacerItem(0, 16))

        # Username
        ulbl = QLabel("Username")
        ulbl.setFont(QFont("Segoe UI", 10, QFont.Weight.DemiBold))
        ulbl.setStyleSheet(f"color: {TEXT_SEC}; background: transparent;")
        cl.addWidget(ulbl)

        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Enter username")
        self.user_input.setMinimumHeight(40)
        self.user_input.setStyleSheet(
            f"background: {BG_PRIMARY}; color: {TEXT}; "
            f"border: 1px solid {BORDER}; "
            f"border-radius: 8px; padding: 10px 14px; font-size: 13px;")
        cl.addWidget(self.user_input)

        # Password
        plbl = QLabel("Password")
        plbl.setFont(QFont("Segoe UI", 10, QFont.Weight.DemiBold))
        plbl.setStyleSheet(f"color: {TEXT_SEC}; background: transparent;")
        cl.addWidget(plbl)

        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText("Enter password")
        self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pass_input.setMinimumHeight(40)
        self.pass_input.setStyleSheet(
            f"background: {BG_PRIMARY}; color: {TEXT}; "
            f"border: 1px solid {BORDER}; "
            f"border-radius: 8px; padding: 10px 14px; font-size: 13px;")
        self.pass_input.returnPressed.connect(self._submit)
        cl.addWidget(self.pass_input)

        cl.addSpacerItem(QSpacerItem(0, 10))

        # Submit button
        btn_text = "Create Account" if self._is_signup else "Sign In"
        self.submit_btn = QPushButton(f"→  {btn_text}")
        self.submit_btn.setMinimumHeight(44)
        self.submit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.submit_btn.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.submit_btn.setStyleSheet(
            f"QPushButton {{ "
            f"  color: #fff; background: {BLUE}; "
            f"  border: none; border-radius: 8px; "
            f"}}  "
            f"QPushButton:hover {{ background: #2563eb; }}")
        self.submit_btn.clicked.connect(self._submit)
        cl.addWidget(self.submit_btn)

        # Toggle link
        toggle_text = "Already have an account? Sign In" if self._is_signup else "No account? Create one"
        self.toggle_btn = QPushButton(toggle_text)
        self.toggle_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.toggle_btn.setStyleSheet(
            f"color: {BLUE}; background: transparent; "
            f"border: none; font-size: 11px;")
        self.toggle_btn.clicked.connect(self._toggle_mode)
        cl.addWidget(self.toggle_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        # Error label
        self.error_lbl = QLabel("")
        self.error_lbl.setFont(QFont("Segoe UI", 10))
        self.error_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.error_lbl.setStyleSheet(f"color: {RED}; background: transparent;")
        cl.addWidget(self.error_lbl)

        outer.addWidget(card)

    def _toggle_mode(self):
        self._is_signup = not self._is_signup
        if self._is_signup:
            self.submit_btn.setText("→  Create Account")
            self.toggle_btn.setText("Already have an account? Sign In")
        else:
            self.submit_btn.setText("→  Sign In")
            self.toggle_btn.setText("No account? Create one")
        self.error_lbl.setText("")

    def _submit(self):
        user = self.user_input.text().strip()
        pw = self.pass_input.text().strip()

        if not user or not pw:
            self.error_lbl.setText("Please enter both username and password")
            return

        if len(pw) < 4:
            self.error_lbl.setText("Password must be at least 4 characters")
            return

        if self._is_signup:
            if _create_user(user, pw):
                self.login_success.emit(user)
            else:
                self.error_lbl.setText("Username already taken")
        else:
            if _verify_user(user, pw):
                self.login_success.emit(user)
            else:
                self.error_lbl.setText("Invalid username or password")

    def paintEvent(self, event):
        p = QPainter(self)
        p.fillRect(self.rect(), QColor(9, 9, 11))
        p.end()

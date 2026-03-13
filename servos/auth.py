"""
Local offline authentication helpers for Servos.
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
import secrets
from typing import Dict, Optional, Tuple

from servos.config import ensure_dirs, get_config

_ITERATIONS = 200_000


def _users_path() -> str:
    cfg = get_config()
    return os.path.join(cfg["data_dir"], "users.json")


def _load_users() -> Dict[str, dict]:
    ensure_dirs()
    path = _users_path()
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as handle:
            data = json.load(handle)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _save_users(users: Dict[str, dict]) -> None:
    path = _users_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(users, handle, indent=2)


def _normalize_username(username: str) -> str:
    return (username or "").strip().lower()


def _hash_password(password: str, salt: bytes) -> str:
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        _ITERATIONS,
    )
    return base64.b64encode(digest).decode("ascii")


def user_exists(username: Optional[str] = None) -> bool:
    users = _load_users()
    if username is None:
        return bool(users)
    return _normalize_username(username) in users


def get_user(username: str) -> Optional[dict]:
    users = _load_users()
    user = users.get(_normalize_username(username))
    if not user:
        return None
    return dict(user)


def register_user(username: str, password: str, role: str = "investigator") -> Tuple[bool, str]:
    clean_username = _normalize_username(username)
    if not clean_username:
        return False, "Username is required."
    if len(password or "") < 8:
        return False, "Password must be at least 8 characters."

    users = _load_users()
    if clean_username in users:
        return False, "Username already exists."

    salt = secrets.token_bytes(16)
    users[clean_username] = {
        "username": clean_username,
        "role": role or "investigator",
        "salt": base64.b64encode(salt).decode("ascii"),
        "password_hash": _hash_password(password, salt),
    }
    _save_users(users)
    return True, clean_username


def verify_user(username: str, password: str) -> bool:
    user = get_user(username)
    if not user:
        return False
    try:
        salt = base64.b64decode(user["salt"])
    except Exception:
        return False
    candidate = _hash_password(password, salt)
    return secrets.compare_digest(candidate, user.get("password_hash", ""))

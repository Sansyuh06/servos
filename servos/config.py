"""
Servos – Application Configuration.
Manages settings with JSON persistence.
"""

import os
import json
from typing import Dict, Any

DEFAULT_CONFIG = {
    "app_name": "Servos",
    "version": "1.0.0",
    "tagline": "Forensics for the Rest of Us",

    # Paths
    "data_dir": os.path.join(os.path.expanduser("~"), ".servos"),
    "database_path": os.path.join(os.path.expanduser("~"), ".servos", "cases.db"),
    "backup_location": os.path.join(os.path.expanduser("~"), ".servos", "backups"),
    "reports_dir": os.path.join(os.path.expanduser("~"), ".servos", "reports"),
    "logs_dir": os.path.join(os.path.expanduser("~"), ".servos", "logs"),

    # LLM
    "llm_model": "llama3.1:8b",
    "llm_base_url": "http://localhost:11434",
    "llm_timeout": 30,
    "llm_enabled": True,

    # Detection
    "usb_poll_interval": 2.0,    # seconds
    "auto_detect_usb": True,
    # automatically launch a full investigation when a new drive appears
    "auto_investigate": True,
    # Investigation mode: "full", "hybrid", or "manual"
    "investigation_mode": "hybrid",
    # Background monitoring toggle
    "background_monitoring": True,

    # Analysis
    "max_file_size_mb": 500,     # skip files larger than this for hashing
    "hash_algorithms": ["md5", "sha256"],
    "entropy_threshold": 7.0,    # flag files above this
    "scan_hidden_files": True,

    # Monitoring toggles
    "enable_network_monitor": False,
    "enable_process_monitor": False,
    "enable_file_watcher": False,
    "watch_paths": [],

    # Report
    "default_report_format": "pdf",
    "include_timeline_in_report": True,

    # UI
    "color_theme": "dark",
}

_config: Dict[str, Any] = {}


def _config_path() -> str:
    return os.path.join(DEFAULT_CONFIG["data_dir"], "settings.json")


def get_config() -> Dict[str, Any]:
    """Load and return merged configuration."""
    global _config
    if _config:
        return _config

    _config = dict(DEFAULT_CONFIG)

    cfg_file = _config_path()
    if os.path.exists(cfg_file):
        try:
            with open(cfg_file, "r") as f:
                user_cfg = json.load(f)
            _config.update(user_cfg)
        except Exception:
            pass

    return _config


def save_config(updates: Dict[str, Any] = None):
    """Save current configuration to disk."""
    global _config
    if not _config:
        get_config()
    if updates:
        _config.update(updates)

    cfg_file = _config_path()
    os.makedirs(os.path.dirname(cfg_file), exist_ok=True)
    with open(cfg_file, "w") as f:
        json.dump(_config, f, indent=2)


def ensure_dirs():
    """Create all required directories."""
    cfg = get_config()
    for key in ["data_dir", "backup_location", "reports_dir", "logs_dir"]:
        path = cfg.get(key, "")
        if path:
            os.makedirs(path, exist_ok=True)

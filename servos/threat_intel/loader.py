"""
Servos – Threat Intelligence Loader.
Loads offline threat intel data: suspicious path patterns, YARA rules, MITRE techniques.
No hashing — detection is path-based + YARA + metadata only.
"""

import os
import re
import json
from pathlib import Path
from typing import List, Dict, Any

_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "threat_intel")


def load_suspicious_path_patterns() -> List[str]:
    """Load suspicious path/filename patterns from JSON."""
    path = os.path.join(_DATA_DIR, "suspicious_paths.json")
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_yara_rules() -> List[Path]:
    """Return paths to all .yar rule files."""
    rules_dir = os.path.join(_DATA_DIR, "yara_rules")
    if not os.path.isdir(rules_dir):
        return []
    return sorted(Path(rules_dir).glob("*.yar"))


def load_mitre_techniques() -> List[Dict[str, str]]:
    """Load MITRE ATT&CK techniques."""
    path = os.path.join(_DATA_DIR, "mitre_techniques.json")
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# ── Path-based threat matching ──────────────────────────────────

_cached_patterns: List[re.Pattern] = []


def _compile_patterns() -> List[re.Pattern]:
    """Compile suspicious path patterns into regex objects (cached)."""
    global _cached_patterns
    if _cached_patterns:
        return _cached_patterns
    raw = load_suspicious_path_patterns()
    for p in raw:
        try:
            _cached_patterns.append(re.compile(p, re.IGNORECASE))
        except re.error:
            # Treat as a literal substring match
            _cached_patterns.append(re.compile(re.escape(p), re.IGNORECASE))
    return _cached_patterns


def check_path_suspicious(filepath: str) -> List[str]:
    """
    Check if a file path matches any suspicious patterns.
    Returns list of matched pattern strings (empty = clean).
    """
    patterns = _compile_patterns()
    matched = []
    for pat in patterns:
        if pat.search(filepath):
            matched.append(pat.pattern)
    return matched


# ── YARA content-based matching (simple, no yara-python needed) ─

def parse_yara_rules_from_file(yar_path: str) -> List[Dict[str, Any]]:
    """
    Parse a .yar file into a list of rule dicts.
    Each rule has: name, meta (dict), strings (list of bytes), condition (str).
    This is a lightweight parser — no yara-python dependency.
    """
    rules = []
    content = Path(yar_path).read_text(encoding="utf-8", errors="ignore")

    # Split by rule definitions
    rule_blocks = re.split(r'\brule\s+(\w+)\s*\{', content)
    # rule_blocks: ['', name1, body1, name2, body2, ...]

    for i in range(1, len(rule_blocks) - 1, 2):
        name = rule_blocks[i]
        body = rule_blocks[i + 1]

        meta = {}
        strings_list = []
        severity = "medium"

        # Parse meta
        meta_match = re.search(r'meta:\s*(.*?)(?=strings:|condition:|\})', body, re.DOTALL)
        if meta_match:
            for line in meta_match.group(1).strip().splitlines():
                kv = line.strip().split("=", 1)
                if len(kv) == 2:
                    key = kv[0].strip()
                    val = kv[1].strip().strip('"')
                    meta[key] = val
                    if key == "severity":
                        severity = val

        # Parse strings
        strings_match = re.search(r'strings:\s*(.*?)(?=condition:|\})', body, re.DOTALL)
        if strings_match:
            for line in strings_match.group(1).strip().splitlines():
                str_match = re.search(r'"([^"]+)"', line)
                if str_match:
                    strings_list.append(str_match.group(1).encode("utf-8", errors="ignore"))

        rules.append({
            "name": name,
            "meta": meta,
            "strings": strings_list,
            "severity": severity,
            "source_file": os.path.basename(yar_path),
        })

    return rules


def load_all_parsed_rules() -> List[Dict[str, Any]]:
    """Load and parse all YARA rule files."""
    all_rules = []
    for yar_path in load_yara_rules():
        all_rules.extend(parse_yara_rules_from_file(str(yar_path)))
    return all_rules


# Scannable file extensions (for YARA content matching)
SCANNABLE_EXTENSIONS = {
    ".exe", ".dll", ".bat", ".ps1", ".vbs", ".vbe", ".js", ".jse",
    ".wsf", ".wsh", ".cmd", ".com", ".scr", ".hta", ".pif",
    ".docm", ".xlsm", ".pptm", ".doc", ".xls", ".ppt",
    ".py", ".rb", ".sh", ".php", ".asp", ".aspx", ".jsp",
    ".inf", ".reg", ".msi", ".sys", ".drv", ".cpl",
}


def scan_file_yara(filepath: str, rules: List[Dict] = None) -> List[Dict[str, str]]:
    """
    Scan a single file against parsed YARA rules.
    Returns list of matches: [{"rule": name, "severity": sev, "source": file}].
    Only scans files with scannable extensions.
    """
    ext = os.path.splitext(filepath)[1].lower()
    if ext not in SCANNABLE_EXTENSIONS:
        return []

    if rules is None:
        rules = load_all_parsed_rules()

    try:
        # Read file content (limit to first 1MB for performance)
        with open(filepath, "rb") as f:
            content = f.read(1024 * 1024)
    except (OSError, PermissionError):
        return []

    matches = []
    for rule in rules:
        matched_count = 0
        for pattern in rule["strings"]:
            if pattern.lower() in content.lower():
                matched_count += 1

        # Require at least the condition threshold (simplified: 2+ matches)
        threshold = 2
        if matched_count >= threshold:
            matches.append({
                "rule": rule["name"],
                "severity": rule["severity"],
                "source": rule["source_file"],
                "matched_strings": matched_count,
                "description": rule["meta"].get("description", ""),
            })

    return matches

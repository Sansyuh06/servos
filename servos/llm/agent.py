"""
Servos – Forensic Agent + System Automation.
AI Agent that intercepts chat messages, detects investigation intents AND
system automation commands, auto-executes them, and returns LLM-interpreted results.

Supports:
  - All forensic tools (scan, malware, logs, network, timeline, etc.)
  - System automation (open apps, delete/create/copy files, kill processes, etc.)
  - Shell command execution
  - File/folder management
"""

import os
import re
import json
import shutil
import signal
import subprocess
import traceback
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

from servos.config import get_config
from servos.llm.investigator import LLMInvestigator


# ── Tool Definitions ────────────────────────────────────────────

TOOLS = [
    # ── Forensic Investigation Tools ──
    {
        "id": "scan_files",
        "name": "File System Scanner",
        "description": "Scan a directory for suspicious files, hidden files, and file type analysis",
        "keywords": ["scan", "analyze files", "check disk", "file scan", "scan disk",
                     "scan drive", "scan directory", "scan folder", "filesystem"],
        "icon": "📂",
    },
    {
        "id": "detect_malware",
        "name": "Malware Detector",
        "description": "Run YARA rules and heuristic malware detection on files",
        "keywords": ["malware", "virus", "threat", "yara", "trojan", "ransomware",
                     "malicious", "infected", "suspicious exe", "detect malware"],
        "icon": "🛡️",
    },
    {
        "id": "analyze_logs",
        "name": "Log Analyzer",
        "description": "Analyze system and application logs for suspicious patterns",
        "keywords": ["logs", "log analysis", "event log", "syslog", "log file",
                     "analyze logs", "check logs", "audit log", "log entries"],
        "icon": "📋",
    },
    {
        "id": "network_scan",
        "name": "Network Scanner",
        "description": "Scan network connections, open ports, DNS cache, and ARP table",
        "keywords": ["network", "connections", "ports", "dns", "arp", "network scan",
                     "open ports", "listening", "netstat", "network connections"],
        "icon": "🌐",
    },
    {
        "id": "build_timeline",
        "name": "Timeline Builder",
        "description": "Build a chronological timeline of events from filesystem and logs",
        "keywords": ["timeline", "events", "chronology", "event timeline",
                     "build timeline", "time analysis", "temporal"],
        "icon": "⏱️",
    },
    {
        "id": "hash_files",
        "name": "File Hasher",
        "description": "Compute MD5, SHA1, SHA256 hashes for file integrity verification",
        "keywords": ["hash", "md5", "sha256", "sha1", "checksum", "file hash",
                     "integrity", "hash file", "compute hash"],
        "icon": "🔑",
    },
    {
        "id": "extract_artifacts",
        "name": "Artifact Extractor",
        "description": "Extract browser history, recent files, USB traces, and system artifacts",
        "keywords": ["artifacts", "browser history", "recent files", "usb traces",
                     "extract", "browser", "cookies", "downloads", "registry artifacts"],
        "icon": "🔍",
    },
    {
        "id": "check_duplicates",
        "name": "Duplicate File Detector",
        "description": "Find duplicate files by comparing hashes across directories",
        "keywords": ["duplicates", "duplicate files", "identical files", "duplicate",
                     "find duplicates", "same files", "copy detection"],
        "icon": "📑",
    },
    {
        "id": "threat_score",
        "name": "Threat Scorer",
        "description": "Calculate risk scores and threat assessments for findings",
        "keywords": ["risk", "threat score", "risk assessment", "severity",
                     "threat level", "risk score", "danger level", "threat assessment"],
        "icon": "⚠️",
    },
    {
        "id": "cyber_law",
        "name": "Cyber Law Reference",
        "description": "Look up Indian IT Act sections and cyber law references",
        "keywords": ["law", "it act", "legal", "section", "cyber law", "indian it act",
                     "legislation", "offense", "punishment", "66a", "43", "act 2000"],
        "icon": "⚖️",
    },
    {
        "id": "system_info",
        "name": "System Information",
        "description": "Gather system processes, memory usage, CPU info, and running services",
        "keywords": ["system info", "cpu", "running processes",
                     "services", "task manager", "process list", "ram usage",
                     "system status", "resource usage"],
        "icon": "💻",
    },
    {
        "id": "full_investigation",
        "name": "Full Investigation",
        "description": "Run a comprehensive forensic investigation using all available tools",
        "keywords": ["investigate", "full scan", "full auto", "complete scan",
                     "full investigation", "deep investigation", "investigate everything",
                     "comprehensive scan"],
        "icon": "🔬",
    },

    # ── System Automation Tools ──
    {
        "id": "open_path",
        "name": "Open File/Folder/App",
        "description": "Open a file, folder, URL, or application",
        "keywords": [],  # handled by priority detection
        "icon": "📁",
    },
    {
        "id": "delete_path",
        "name": "Delete File/Folder",
        "description": "Delete a file or directory from the system",
        "keywords": [],  # handled by priority detection
        "icon": "🗑️",
    },
    {
        "id": "create_path",
        "name": "Create File/Folder",
        "description": "Create a new file or directory",
        "keywords": [],
        "icon": "➕",
    },
    {
        "id": "copy_move",
        "name": "Copy/Move Files",
        "description": "Copy or move files between locations",
        "keywords": [],
        "icon": "📦",
    },
    {
        "id": "find_files",
        "name": "Find Files",
        "description": "Search for files by name or pattern",
        "keywords": [],
        "icon": "🔎",
    },
    {
        "id": "kill_process",
        "name": "Kill Process",
        "description": "Terminate a running process by name or PID",
        "keywords": [],
        "icon": "☠️",
    },
    {
        "id": "run_command",
        "name": "Run Command",
        "description": "Execute a system command",
        "keywords": [],
        "icon": "⚡",
    },
    {
        "id": "list_directory",
        "name": "List Directory",
        "description": "List the contents of a directory",
        "keywords": [],
        "icon": "📄",
    },
    {
        "id": "rename_path",
        "name": "Rename File/Folder",
        "description": "Rename a file or folder",
        "keywords": [],
        "icon": "✏️",
    },
    {
        "id": "screenshot",
        "name": "Take Screenshot",
        "description": "Take a screenshot of the current screen",
        "keywords": [],
        "icon": "📸",
    },
]


# ── Well-known apps for "open X" ────────────────────────────────

KNOWN_APPS = {
    "spotify": "spotify",
    "chrome": "chrome",
    "google chrome": "chrome",
    "firefox": "firefox",
    "mozilla firefox": "firefox",
    "edge": "msedge",
    "microsoft edge": "msedge",
    "notepad": "notepad",
    "calculator": "calc",
    "calc": "calc",
    "paint": "mspaint",
    "word": "winword",
    "excel": "excel",
    "powerpoint": "powerpnt",
    "outlook": "outlook",
    "teams": "msteams",
    "discord": "discord",
    "vscode": "code",
    "vs code": "code",
    "visual studio code": "code",
    "terminal": "wt",
    "cmd": "cmd",
    "powershell": "powershell",
    "task manager": "taskmgr",
    "file explorer": "explorer",
    "explorer": "explorer",
    "control panel": "control",
    "settings": "ms-settings:",
    "snipping tool": "snippingtool",
    "obs": "obs64",
    "steam": "steam",
    "telegram": "telegram",
    "whatsapp": "whatsapp",
    "vlc": "vlc",
    "brave": "brave",
    "opera": "opera",
    "git bash": "git-bash",
    "postman": "postman",
    "figma": "figma",
    "slack": "slack",
    "zoom": "zoom",
    "audacity": "audacity",
    "blender": "blender",
    "gimp": "gimp",
    "photoshop": "photoshop",
    "illustrator": "illustrator",
    "premiere": "premiere",
    "after effects": "afterfx",
    "android studio": "studio64",
    "pycharm": "pycharm64",
    "intellij": "idea64",
    "webstorm": "webstorm64",
}

SAFE_TOOL_IDS = {
    "scan_files",
    "detect_malware",
    "analyze_logs",
    "network_scan",
    "build_timeline",
    "hash_files",
    "extract_artifacts",
    "cyber_law",
    "system_info",
    "full_investigation",
}


# ── Intent Detection ────────────────────────────────────────────

def detect_intent(message: str) -> List[Dict]:
    """Detect which tools should be triggered based on the user's message."""
    msg_lower = message.lower().strip()

    # ── Priority 1: Action-verb prefix detection ──
    # These verbs ALWAYS map to a specific system tool, no matter what follows.
    action_map = [
        # (prefixes, tool_id)
        (["open ", "launch ", "start ", "play "], "open_path"),
        (["delete ", "remove ", "rm ", "del ", "erase "], "delete_path"),
        (["create ", "make ", "mkdir ", "touch ", "new "], "create_path"),
        (["copy ", "cp "], "copy_move"),
        (["move ", "mv "], "copy_move"),
        (["rename ", "ren "], "rename_path"),
        (["find ", "search ", "where is ", "locate "], "find_files"),
        (["kill ", "terminate ", "stop ", "end task ", "close "], "kill_process"),
        (["run ", "execute ", "cmd ", "exec "], "run_command"),
        (["list ", "ls ", "what's in ", "contents of ", "show files in "], "list_directory"),
        (["screenshot", "take screenshot", "capture screen", "snip"], "screenshot"),
    ]

    for prefixes, tool_id in action_map:
        for prefix in prefixes:
            if msg_lower.startswith(prefix) or msg_lower == prefix.strip():
                tool = next((t for t in TOOLS if t["id"] == tool_id), None)
                if tool:
                    return [{"tool": tool, "score": 100}]

    # ── Priority 2: Keyword-based forensic tool matching ──
    matched = []
    for tool in TOOLS:
        score = 0
        for keyword in tool.get("keywords", []):
            if keyword and keyword in msg_lower:
                score += len(keyword.split())
        if score > 0:
            matched.append({"tool": tool, "score": score})

    matched.sort(key=lambda x: x["score"], reverse=True)

    if any(m["tool"]["id"] == "full_investigation" for m in matched):
        return [m for m in matched if m["tool"]["id"] == "full_investigation"]

    return matched[:3]


# ── Path & Target Extraction ────────────────────────────────────

def _extract_path(message: str) -> str:
    """Try to extract a file/directory path from the user message."""
    path_match = re.search(r'[A-Z]:\\[^\s"\']+', message, re.IGNORECASE)
    if path_match:
        return path_match.group(0)
    path_match = re.search(r'/[^\s"\']+', message)
    if path_match and len(path_match.group(0)) > 2:
        return path_match.group(0)
    return os.environ.get("TEMP", os.getcwd())


def _extract_app_or_path(message: str) -> str:
    """Extract an app name, file path, or URL from the message."""
    msg_lower = message.lower().strip()

    # Strip action verbs from the beginning
    for prefix in ["open ", "launch ", "start ", "play ", "run ", "close ",
                    "kill ", "delete ", "remove ", "create ", "find ", "search ",
                    "copy ", "move ", "rename ", "list ", "execute ", "explore "]:
        if msg_lower.startswith(prefix):
            msg_lower = msg_lower[len(prefix):].strip()
            message = message[len(prefix):].strip()
            break

    # Check if it's a known app name
    for app_name, exe in KNOWN_APPS.items():
        if app_name in msg_lower:
            return exe

    # Check if it's a file path
    path_match = re.search(r'[A-Z]:\\[^\s"\']+', message, re.IGNORECASE)
    if path_match:
        return path_match.group(0)

    # Check if it's a URL
    url_match = re.search(r'https?://[^\s]+', message, re.IGNORECASE)
    if url_match:
        return url_match.group(0)

    # Return the raw text as potential app name
    cleaned = msg_lower.strip().strip('"').strip("'")
    return cleaned if cleaned else message


def _extract_two_paths(message: str) -> Tuple[str, str]:
    """Extract source and destination paths from copy/move commands."""
    paths = re.findall(r'[A-Z]:\\[^\s"\']+', message, re.IGNORECASE)
    if len(paths) >= 2:
        return paths[0], paths[1]
    # Look for "to" separator
    parts = re.split(r'\s+to\s+', message, flags=re.IGNORECASE)
    if len(parts) >= 2:
        src = _extract_path(parts[0])
        dst = _extract_path(parts[1])
        return src, dst
    if len(paths) == 1:
        return paths[0], os.path.dirname(paths[0])
    return "", ""


def _has_explicit_path(message: str) -> bool:
    return bool(re.search(r'[A-Z]:\\[^\s"\']+', message, re.IGNORECASE) or re.search(r'/[^\s"\']+', message))


# ── Tool Executor ───────────────────────────────────────────────

def execute_tool(tool_id: str, message: str) -> Dict[str, Any]:
    """Execute a tool and return structured results."""
    target = _extract_path(message)

    try:
        if tool_id == "scan_files":
            return _run_file_scan(target)
        elif tool_id == "detect_malware":
            return _run_malware_scan(target)
        elif tool_id == "analyze_logs":
            return _run_log_analysis(target)
        elif tool_id == "network_scan":
            return _run_network_scan()
        elif tool_id == "build_timeline":
            return _run_timeline(target)
        elif tool_id == "hash_files":
            return _run_hash(target)
        elif tool_id == "extract_artifacts":
            return _run_artifact_extraction(target)
        elif tool_id == "check_duplicates":
            return _run_duplicate_check(target)
        elif tool_id == "threat_score":
            return _run_threat_scoring(target)
        elif tool_id == "cyber_law":
            return _run_cyber_law_lookup(message)
        elif tool_id == "system_info":
            return _run_system_info()
        elif tool_id == "full_investigation":
            return _run_full_investigation(target)
        elif tool_id == "open_path":
            return _run_open(message)
        elif tool_id == "delete_path":
            return _run_delete(message)
        elif tool_id == "create_path":
            return _run_create(message)
        elif tool_id == "copy_move":
            return _run_copy_move(message)
        elif tool_id == "find_files":
            return _run_find_files(message)
        elif tool_id == "kill_process":
            return _run_kill_process(message)
        elif tool_id == "run_command":
            return _run_command(message)
        elif tool_id == "list_directory":
            return _run_list_directory(target)
        elif tool_id == "rename_path":
            return _run_rename(message)
        elif tool_id == "screenshot":
            return _run_screenshot()
        else:
            return {"error": f"Unknown tool: {tool_id}"}
    except Exception as e:
        return {"error": str(e), "traceback": traceback.format_exc()[-500:]}


# ════════════════════════════════════════════════════════════════
# ── FORENSIC TOOL HANDLERS ──
# ════════════════════════════════════════════════════════════════

def _run_file_scan(target: str) -> Dict:
    from servos.forensics.file_analyzer import FileAnalyzer
    result = FileAnalyzer().analyze(target)
    return {
        "total_files": result.total_files, "total_dirs": result.total_dirs,
        "total_size_mb": round(result.total_size_bytes / (1024 * 1024), 2),
        "hidden_files": result.hidden_files,
        "suspicious_count": len(result.suspicious_files),
        "suspicious_files": [
            {"name": f.filename, "reason": f.suspicious_reason, "entropy": round(f.entropy, 2)}
            for f in result.suspicious_files[:15]
        ],
        "top_types": dict(list(result.file_type_counts.items())[:10]),
    }

def _run_malware_scan(target: str) -> Dict:
    from servos.forensics.malware_detector import MalwareDetector
    result = MalwareDetector().scan(target)
    return {
        "risk_level": result.risk_level, "files_scanned": result.files_scanned,
        "suspicious_count": result.suspicious_count,
        "indicators": [
            {"rule": i.rule_name, "severity": i.severity, "file": os.path.basename(i.file_path),
             "description": i.description, "type": i.indicator_type}
            for i in result.indicators[:20]
        ],
    }

def _run_log_analysis(target: str) -> Dict:
    from servos.forensics.log_analyzer import LogAnalyzer
    analyzer = LogAnalyzer()
    targets = []
    if os.path.isdir(target):
        for root, _, files in os.walk(target):
            for filename in files:
                if filename.lower().endswith((".log", ".txt", ".evtx")):
                    targets.append(os.path.join(root, filename))
                if len(targets) >= 20:
                    break
            if len(targets) >= 20:
                break
    elif os.path.isfile(target):
        targets = [target]
    else:
        win_logs = os.path.expandvars(r"%SystemRoot%\System32\winevt\Logs")
        if os.path.isdir(win_logs):
            return _run_log_analysis(win_logs)
        return {"error": "No log files found at the specified path"}

    threats = []
    total_entries = 0
    for path in targets:
        total_entries += len(analyzer.analyze_file(path))
        threats.extend(analyzer.analyze_patterns(path))
    return {
        "files_analyzed": len(targets),
        "total_entries": total_entries,
        "suspicious_patterns": len(threats),
        "patterns": [
            {
                "pattern": threat.pattern_name,
                "severity": threat.severity,
                "file": os.path.basename(threat.file_path),
            }
            for threat in threats[:10]
        ],
    }

def _run_network_scan() -> Dict:
    from servos.forensics.network_scanner import NetworkScanner
    scanner = NetworkScanner()
    return {
        "interfaces": scanner.list_interfaces()[:10],
        "active_connections": scanner.active_connections()[:20],
        "listening_ports": scanner.listening_ports()[:15],
        "dns_cache": scanner.dns_cache()[:15],
        "arp_table": scanner.arp_table()[:15],
    }

def _run_timeline(target: str) -> Dict:
    from servos.forensics.file_analyzer import FileAnalyzer
    from servos.forensics.artifact_extractor import ArtifactExtractor
    from servos.forensics.timeline import TimelineBuilder
    timeline = TimelineBuilder().build(
        FileAnalyzer().analyze(target),
        ArtifactExtractor().extract_all(target),
    )
    return {
        "total_events": len(timeline.events), "anomalies": len(timeline.anomalies),
        "recent_events": [
            {"timestamp": e.timestamp[:19] if e.timestamp else "", "description": e.description,
             "severity": e.severity, "source": e.source}
            for e in timeline.events[-20:]
        ],
        "anomaly_details": [
            {"timestamp": a.timestamp[:19] if a.timestamp else "", "description": a.description,
             "severity": a.severity}
            for a in timeline.anomalies[:10]
        ],
    }

def _run_hash(target: str) -> Dict:
    from servos.forensics.hasher import FileHasher
    hasher = FileHasher()
    if os.path.isfile(target):
        return {"files": [{"path": target, **hasher.hash_file(target)}]}
    elif os.path.isdir(target):
        results = hasher.hash_directory(target)
        return {
            "total_hashed": len(results),
            "files": [{"path": r.get("file", ""), "md5": r.get("md5", ""), "sha256": r.get("sha256", "")}
                       for r in results[:20]],
        }
    return {"error": f"Path not found: {target}"}

def _run_artifact_extraction(target: str) -> Dict:
    from servos.forensics.artifact_extractor import ArtifactExtractor
    arts = ArtifactExtractor().extract_all(target)
    return {
        "browser_history": len(arts.browser_history), "recent_files": len(arts.recent_files),
        "registry_items": len(arts.registry_items),
        "log_entries": len(arts.log_entries),
        "top_browser": [{"url": h.content.get("url", ""), "title": h.content.get("title", "")} for h in arts.browser_history[:10]],
        "top_recent": [item.content.get("filename", "") for item in arts.recent_files[:10]],
        "suspicious_domains": [
            item.content.get("url", "")
            for item in arts.browser_history[:10]
            if item.suspicious_score >= 0.5
        ],
    }

def _run_duplicate_check(target: str) -> Dict:
    from servos.forensics.duplicate_detector import DuplicateDetector
    dups = DuplicateDetector().find_duplicates(target)
    return {
        "total_groups": len(dups),
        "duplicate_groups": [
            {"hash": group.get("hash", "")[:16], "count": len(group.get("files", [])),
             "files": [os.path.basename(f) for f in group.get("files", [])[:5]]}
            for group in dups[:10]
        ],
    }

def _run_threat_scoring(target: str) -> Dict:
    from servos.forensics.threat_scorer import ThreatScorer
    from servos.forensics.file_analyzer import FileAnalyzer
    from servos.forensics.malware_detector import MalwareDetector
    fa = FileAnalyzer().analyze(target)
    md = MalwareDetector().scan(target)
    score = ThreatScorer().score({"file_system": fa, "malware": md})
    return {
        "overall_risk": score.get("overall_risk", "UNKNOWN"),
        "risk_score": score.get("risk_score", 0),
        "breakdown": score.get("breakdown", {}),
        "recommendations": score.get("recommendations", [])[:5],
    }

def _run_cyber_law_lookup(message: str) -> Dict:
    from servos.reference.it_act import lookup
    query = message.lower()
    for prefix in ["what is ", "what does ", "tell me about ", "explain ", "look up ",
                   "search for ", "find ", "show me "]:
        if query.startswith(prefix):
            query = query[len(prefix):]
            break
    results = lookup(query)
    return {
        "type": "cyber_law_lookup", "query": query[:100],
        "results": [
            {"section": r.section_id, "title": r.title, "description": r.description[:300],
             "punishment": r.punishment, "relevance": round(r.relevance, 2)}
            for r in results
        ],
    }

def _run_system_info() -> Dict:
    import psutil
    cpu_percent = psutil.cpu_percent(interval=0.5)
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    procs = []
    for p in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"]):
        try:
            procs.append(p.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    procs.sort(key=lambda x: x.get("memory_percent", 0) or 0, reverse=True)
    return {
        "cpu_percent": cpu_percent, "cpu_cores": psutil.cpu_count(),
        "memory_total_gb": round(mem.total / (1024 ** 3), 2),
        "memory_used_percent": mem.percent,
        "disk_total_gb": round(disk.total / (1024 ** 3), 2),
        "disk_used_percent": round(disk.used / disk.total * 100, 1),
        "total_processes": len(procs),
        "top_processes": [
            {"pid": p["pid"], "name": p["name"],
             "cpu": round(p.get("cpu_percent", 0) or 0, 1),
             "mem": round(p.get("memory_percent", 0) or 0, 1)}
            for p in procs[:10]
        ],
    }

def _run_full_investigation(target: str) -> Dict:
    combined = {}
    for tid in ["scan_files", "detect_malware", "analyze_logs", "network_scan", "extract_artifacts", "system_info"]:
        try:
            combined[tid] = execute_tool(tid, target)
        except Exception as e:
            combined[tid] = {"error": str(e)}
    return combined


# ════════════════════════════════════════════════════════════════
# ── SYSTEM AUTOMATION HANDLERS ──
# ════════════════════════════════════════════════════════════════

def _run_open(message: str) -> Dict:
    """Open any file, folder, URL or application."""
    target = _extract_app_or_path(message)

    # Check known apps first
    for app_name, exe in KNOWN_APPS.items():
        if app_name in message.lower():
            try:
                subprocess.Popen(exe, shell=True)
                return {"opened": True, "target": app_name, "type": "application", "executable": exe}
            except Exception as e:
                return {"error": f"Could not launch {app_name}: {e}", "target": app_name}

    # URL?
    if target.startswith("http://") or target.startswith("https://"):
        os.startfile(target)
        return {"opened": True, "target": target, "type": "url"}

    # File/directory path?
    if os.path.exists(target):
        os.startfile(target)
        is_file = os.path.isfile(target)
        return {
            "opened": True, "path": target,
            "type": "file" if is_file else "directory",
            "name": os.path.basename(target),
            "size_kb": round(os.path.getsize(target) / 1024, 1) if is_file else None,
        }

    # Try as a command directly
    try:
        subprocess.Popen(target, shell=True)
        return {"opened": True, "target": target, "type": "command"}
    except Exception:
        return {"error": f"Could not open: {target}. Not a known app, file, or URL.", "target": target}


def _run_delete(message: str) -> Dict:
    """Delete a file or directory."""
    target = _extract_path(message)
    if not os.path.exists(target):
        return {"error": f"Path not found: {target}"}

    name = os.path.basename(target)
    if os.path.isfile(target):
        size = os.path.getsize(target)
        os.remove(target)
        return {"deleted": True, "path": target, "type": "file", "name": name,
                "size_kb": round(size / 1024, 1)}
    elif os.path.isdir(target):
        count = sum(len(files) for _, _, files in os.walk(target))
        shutil.rmtree(target)
        return {"deleted": True, "path": target, "type": "directory", "name": name,
                "files_removed": count}
    return {"error": f"Cannot delete: {target}"}


def _run_create(message: str) -> Dict:
    """Create a file or directory."""
    target = _extract_path(message)
    msg_lower = message.lower()

    # Determine if user wants a folder or file
    is_folder = any(w in msg_lower for w in ["folder", "directory", "dir", "mkdir"])

    if is_folder:
        os.makedirs(target, exist_ok=True)
        return {"created": True, "path": target, "type": "directory", "name": os.path.basename(target)}
    else:
        # Create file (and parent dirs)
        parent = os.path.dirname(target)
        if parent:
            os.makedirs(parent, exist_ok=True)
        with open(target, "w") as f:
            f.write("")
        return {"created": True, "path": target, "type": "file", "name": os.path.basename(target)}


def _run_copy_move(message: str) -> Dict:
    """Copy or move files."""
    src, dst = _extract_two_paths(message)
    if not src:
        return {"error": "Could not find source path in your message"}
    if not os.path.exists(src):
        return {"error": f"Source not found: {src}"}

    is_move = any(w in message.lower() for w in ["move", "mv"])
    action = "moved" if is_move else "copied"

    if is_move:
        shutil.move(src, dst)
    else:
        if os.path.isdir(src):
            shutil.copytree(src, dst, dirs_exist_ok=True)
        else:
            shutil.copy2(src, dst)

    return {action: True, "source": src, "destination": dst,
            "name": os.path.basename(src), "type": "directory" if os.path.isdir(dst) else "file"}


def _run_find_files(message: str) -> Dict:
    """Search for files by name or pattern."""
    msg_lower = message.lower().strip()
    for prefix in ["find ", "search ", "search for ", "where is ", "locate "]:
        if msg_lower.startswith(prefix):
            msg_lower = msg_lower[len(prefix):]
            break

    # Extract search pattern and optional directory
    pattern = msg_lower.strip().strip('"').strip("'")
    search_dir = _extract_path(message)

    # If no explicit path, search common locations
    if search_dir == os.environ.get("TEMP", os.getcwd()):
        search_dir = os.path.expanduser("~")

    found = []
    try:
        for root, dirs, files in os.walk(search_dir):
            # Skip hidden/system dirs
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in
                       ['node_modules', '__pycache__', '.git', 'AppData', '$Recycle.Bin']]
            for f in files:
                if pattern in f.lower():
                    full = os.path.join(root, f)
                    try:
                        found.append({"name": f, "path": full,
                                      "size_kb": round(os.path.getsize(full) / 1024, 1)})
                    except OSError:
                        pass
            if len(found) >= 25:
                break
    except PermissionError:
        pass

    return {"pattern": pattern, "search_dir": search_dir,
            "total_found": len(found), "results": found[:25]}


def _run_kill_process(message: str) -> Dict:
    """Kill a process by name or PID."""
    import psutil
    msg_lower = message.lower().strip()
    for prefix in ["kill ", "terminate ", "stop ", "close ", "end task ", "end "]:
        if msg_lower.startswith(prefix):
            msg_lower = msg_lower[len(prefix):]
            break

    target = msg_lower.strip()

    # Try as PID first
    try:
        pid = int(target)
        p = psutil.Process(pid)
        name = p.name()
        p.terminate()
        return {"killed": True, "pid": pid, "name": name}
    except (ValueError, psutil.NoSuchProcess):
        pass

    # Search by name
    killed = []
    for proc in psutil.process_iter(["pid", "name"]):
        try:
            if target in proc.info["name"].lower():
                proc.terminate()
                killed.append({"pid": proc.info["pid"], "name": proc.info["name"]})
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    if killed:
        return {"killed": True, "target": target, "processes_terminated": killed}
    return {"error": f"No process matching '{target}' found", "target": target}


def _run_command(message: str) -> Dict:
    """Execute a shell command."""
    msg_lower = message.lower().strip()
    for prefix in ["run ", "execute ", "exec ", "cmd "]:
        if msg_lower.startswith(prefix):
            message = message[len(prefix):].strip()
            break

    cmd = message.strip().strip('"').strip("'")
    if not cmd:
        return {"error": "No command specified"}

    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        return {
            "command": cmd,
            "exit_code": result.returncode,
            "output": result.stdout[:3000] if result.stdout else "",
            "error": result.stderr[:500] if result.stderr else None,
        }
    except subprocess.TimeoutExpired:
        return {"command": cmd, "error": "Command timed out after 30 seconds"}
    except Exception as e:
        return {"command": cmd, "error": str(e)}


def _run_list_directory(target: str) -> Dict:
    """List directory contents."""
    if not os.path.isdir(target):
        return {"error": f"Not a directory: {target}"}
    entries = []
    try:
        for entry in os.scandir(target):
            info = {"name": entry.name, "is_dir": entry.is_dir(), "is_file": entry.is_file()}
            try:
                stat = entry.stat()
                info["size_kb"] = round(stat.st_size / 1024, 1) if entry.is_file() else None
                info["modified"] = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")
            except (OSError, PermissionError):
                pass
            entries.append(info)
            if len(entries) >= 50:
                break
    except PermissionError:
        return {"error": f"Permission denied: {target}"}
    return {
        "path": target, "total_entries": len(entries),
        "directories": sum(1 for e in entries if e["is_dir"]),
        "files": sum(1 for e in entries if e["is_file"]),
        "entries": entries,
    }


def _run_rename(message: str) -> Dict:
    """Rename a file or folder."""
    # Try to extract "rename X to Y"
    match = re.search(r'rename\s+(.+?)\s+to\s+(.+)', message, re.IGNORECASE)
    if match:
        old = match.group(1).strip().strip('"')
        new_name = match.group(2).strip().strip('"')
        if os.path.exists(old):
            parent = os.path.dirname(old)
            new_path = os.path.join(parent, new_name) if not os.path.dirname(new_name) else new_name
            os.rename(old, new_path)
            return {"renamed": True, "from": old, "to": new_path}
        return {"error": f"Path not found: {old}"}
    return {"error": "Use format: rename <path> to <new_name>"}


def _run_screenshot() -> Dict:
    """Take a screenshot."""
    try:
        import pyautogui
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = os.path.join(os.path.expanduser("~"), "Desktop", f"screenshot_{ts}.png")
        screenshot = pyautogui.screenshot()
        screenshot.save(path)
        return {"captured": True, "path": path, "timestamp": ts}
    except ImportError:
        # Fallback without pyautogui
        try:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            path = os.path.join(os.path.expanduser("~"), "Desktop", f"screenshot_{ts}.png")
            subprocess.run(
                f'powershell -command "Add-Type -AssemblyName System.Windows.Forms; '
                f'[System.Windows.Forms.Screen]::PrimaryScreen | ForEach-Object {{ '
                f'$bitmap = New-Object System.Drawing.Bitmap($_.Bounds.Width, $_.Bounds.Height); '
                f'$graphics = [System.Drawing.Graphics]::FromImage($bitmap); '
                f'$graphics.CopyFromScreen($_.Bounds.Location, [System.Drawing.Point]::Empty, $_.Bounds.Size); '
                f'$bitmap.Save(\'{path}\'); }}"',
                shell=True, timeout=10
            )
            if os.path.exists(path):
                return {"captured": True, "path": path, "timestamp": ts}
        except Exception:
            pass
        return {"error": "Screenshot requires pyautogui. Install with: pip install pyautogui"}


# ════════════════════════════════════════════════════════════════
# ── MAIN AGENT CLASS ──
# ════════════════════════════════════════════════════════════════

class ForensicAgent:
    """AI Agent that auto-executes forensic tools and system commands."""

    def __init__(self):
        self.llm = LLMInvestigator()

    def process(
        self,
        message: str,
        history: list = None,
        case_id: str = None,
        active_case: Optional[Dict[str, Any]] = None,
        allow_unsafe: bool = False,
    ) -> Dict[str, Any]:
        history = history or []
        intents = detect_intent(message)
        if not allow_unsafe:
            intents = [intent for intent in intents if intent["tool"]["id"] in SAFE_TOOL_IDS]

        if not intents:
            return self._regular_chat(message, history, active_case)

        actions = []
        all_results = {}
        case_target = ""
        if active_case:
            device_info = active_case.get("device_info") or {}
            backup = active_case.get("backup") or {}
            case_target = (
                device_info.get("mount_point")
                or device_info.get("path")
                or backup.get("backup_path")
                or ""
            )
        targeted_tools = {
            "scan_files",
            "detect_malware",
            "analyze_logs",
            "build_timeline",
            "hash_files",
            "extract_artifacts",
            "full_investigation",
        }

        for intent in intents:
            tool = intent["tool"]
            execution_message = message
            if case_target and tool["id"] in targeted_tools and not _has_explicit_path(message):
                execution_message = f"{message} {case_target}"
            result = execute_tool(tool["id"], execution_message)
            actions.append({
                "tool_id": tool["id"],
                "tool_name": tool["name"],
                "icon": tool["icon"],
                "status": "error" if "error" in result and not any(
                    k for k in result if k != "error" and k != "traceback"
                ) else "completed",
                "summary": self._summarize_result(tool["id"], result),
            })
            all_results[tool["id"]] = result

        interpretation = self._interpret_results(message, all_results, history)
        model_used = self.llm.model if self.llm.is_available() else "offline-fallback"
        sources = [
            {"type": "agent_execution",
             "label": f"Agent: {len(actions)} action(s)",
             "data": {"tools": ", ".join(a["tool_name"] for a in actions),
                      "timestamp": datetime.utcnow().isoformat()[:19]}},
            {"type": "model_info", "label": f"Model: {model_used}",
             "data": {"status": "connected" if self.llm.is_available() else "offline",
                      "model": model_used}},
        ]
        if active_case:
            sources.insert(0, {
                "type": "case_context",
                "label": f"Case {active_case.get('id', 'UNKNOWN')}",
                "data": {
                    "device": (active_case.get("device_info") or {}).get("name", "Unknown"),
                    "risk": (active_case.get("interpretation") or {}).get("risk", "UNKNOWN"),
                },
            })

        return {
            "response": interpretation,
            "sources": sources,
            "model": model_used,
            "actions": actions,
            "raw_results": all_results,
        }

    def _regular_chat(self, message: str, history: list, active_case: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if self.llm.is_available():
            response_text = self.llm.chat(message, history, active_case=active_case)
            model_used = self.llm.model
        else:
            response_text = self.llm.chat(message, history, active_case=active_case)
            model_used = "offline-fallback"

        context_info = []
        if history:
            topic_words = set()
            for msg in history[-5:]:
                words = msg.get("content", "").split()[:5]
                topic_words.update(w.lower() for w in words if len(w) > 3)
            if topic_words:
                context_info.append({
                    "type": "conversation", "label": "Active Conversation",
                    "data": {"messages": len(history),
                             "topics": ", ".join(list(topic_words)[:6])},
                })
        context_info.append({
            "type": "model_info", "label": f"Model: {model_used}",
            "data": {"status": "connected" if self.llm.is_available() else "offline",
                     "model": model_used},
        })
        if active_case:
            context_info.insert(0, {
                "type": "case_context",
                "label": f"Case {active_case.get('id', 'UNKNOWN')}",
                "data": {
                    "device": (active_case.get("device_info") or {}).get("name", "Unknown"),
                    "risk": (active_case.get("interpretation") or {}).get("risk", "UNKNOWN"),
                },
            })

        return {"response": response_text, "sources": context_info,
                "model": model_used, "actions": []}

    def _interpret_results(self, message: str, results: Dict, history: list) -> str:
        context_parts = []
        for tool_id, data in results.items():
            tool_name = next((t["name"] for t in TOOLS if t["id"] == tool_id), tool_id)
            if isinstance(data, dict) and "error" in data and len(data) <= 2:
                context_parts.append(f"[{tool_name}] Error: {data['error']}")
            else:
                data_str = json.dumps(data, default=str)
                if len(data_str) > 2000:
                    data_str = data_str[:2000] + "... (truncated)"
                context_parts.append(f"[{tool_name}] Results:\n{data_str}")

        context_block = "\n\n".join(context_parts)

        prompt = f"""You are Servos AI, an expert offline forensic investigation assistant and system automation agent.
The user asked: "{message}"

I automatically executed the following actions and obtained these results:

{context_block}

Provide a brief, clear response:
- Confirm what was done
- Show key results or details
- Suggest follow-up actions if relevant

Be concise. Use markdown formatting."""

        if self.llm.is_available():
            response = self.llm._generate(prompt)
            if response and not response.startswith("[LLM Error"):
                return response.strip()

        return self._fallback_interpretation(results)

    def _fallback_interpretation(self, results: Dict) -> str:
        parts = ["## ✅ Actions Completed\n"]
        for tool_id, data in results.items():
            tool = next((t for t in TOOLS if t["id"] == tool_id), None)
            if not tool:
                continue
            parts.append(f"### {tool['icon']} {tool['name']}\n")
            if isinstance(data, dict):
                if "error" in data and len(data) <= 2:
                    parts.append(f"⚠️ Error: {data['error']}\n")
                    continue
                for key, val in data.items():
                    if key in ("error", "traceback"):
                        continue
                    if isinstance(val, list) and len(val) > 5:
                        parts.append(f"- **{key.replace('_', ' ').title()}**: {len(val)} items")
                    elif isinstance(val, (int, float, str, bool)):
                        parts.append(f"- **{key.replace('_', ' ').title()}**: {val}")
            parts.append("")
        return "\n".join(parts)

    @staticmethod
    def _summarize_result(tool_id: str, result: Dict) -> str:
        if "error" in result and len(result) <= 2:
            return f"Error: {str(result['error'])[:80]}"

        summaries = {
            "scan_files": lambda r: f"Scanned {r.get('total_files', 0)} files, {r.get('suspicious_count', 0)} suspicious",
            "detect_malware": lambda r: f"Risk: {r.get('risk_level', 'N/A')}, {len(r.get('indicators', []))} indicators",
            "analyze_logs": lambda r: f"Analyzed {r.get('files_analyzed', 0)} logs, {r.get('suspicious_patterns', 0)} suspicious",
            "network_scan": lambda r: f"{len(r.get('active_connections', []))} connections, {len(r.get('listening_ports', []))} ports",
            "build_timeline": lambda r: f"{r.get('total_events', 0)} events, {r.get('anomalies', 0)} anomalies",
            "hash_files": lambda r: f"Hashed {r.get('total_hashed', len(r.get('files', [])))} files",
            "extract_artifacts": lambda r: f"{r.get('browser_history', 0)} browser, {r.get('recent_files', 0)} recent",
            "check_duplicates": lambda r: f"{r.get('total_groups', 0)} duplicate groups",
            "threat_score": lambda r: f"Risk: {r.get('overall_risk', 'N/A')} ({r.get('risk_score', 0)})",
            "cyber_law": lambda r: f"Found {len(r.get('results', []))} references",
            "system_info": lambda r: f"CPU: {r.get('cpu_percent', 0)}%, RAM: {r.get('memory_used_percent', 0)}%",
            "full_investigation": lambda r: f"Completed {len(r)} scans",
            "open_path": lambda r: f"Opened {r.get('type', 'target')}: {r.get('target', r.get('name', r.get('path', '')))}",
            "delete_path": lambda r: f"Deleted {r.get('type', 'path')}: {r.get('name', '')}",
            "create_path": lambda r: f"Created {r.get('type', 'path')}: {r.get('name', '')}",
            "copy_move": lambda r: f"{'Moved' if r.get('moved') else 'Copied'} {r.get('name', '')}",
            "find_files": lambda r: f"Found {r.get('total_found', 0)} files matching '{r.get('pattern', '')}'",
            "kill_process": lambda r: f"Terminated {len(r.get('processes_terminated', [{'x':1}]))} process(es)",
            "run_command": lambda r: f"Ran: {r.get('command', '?')[:40]} (exit {r.get('exit_code', '?')})",
            "list_directory": lambda r: f"{r.get('directories', 0)} dirs, {r.get('files', 0)} files",
            "rename_path": lambda r: f"Renamed to: {os.path.basename(r.get('to', ''))}",
            "screenshot": lambda r: f"Saved: {os.path.basename(r.get('path', ''))}",
        }

        fn = summaries.get(tool_id)
        if fn:
            try:
                return fn(result)
            except Exception:
                pass
        return "Completed"

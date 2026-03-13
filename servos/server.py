"""
Servos – FastAPI Web Server.
REST API that wraps all Servos forensic modules + serves the web UI.
"""

import os
import json
import asyncio
import re
import traceback
import uuid
from dataclasses import asdict, is_dataclass
from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple

from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from pydantic import BaseModel

from servos.auth import (
    get_user as _get_user,
    register_user as _register_user,
    user_exists as _user_exists,
    verify_user as _verify_user,
)
from servos.config import get_config, save_config, ensure_dirs
from servos.models.schema import (
    DeviceInfo, Case, ForensicFindings, LLMInterpretation,
    init_db, get_session, CaseRecord,
)
from servos.detection.usb_monitor import USBDetectionService
from servos.detection.network_monitor import NetworkMonitor
from servos.detection.process_monitor import ProcessMonitor
from servos.detection.file_watcher import FileWatcher
from servos.detection.alert_engine import AlertEngine
from servos.detection.multiscan_coordinator import MultiScanCoordinator
from servos.preservation.backup import EvidenceBackup
from servos.forensics.file_analyzer import FileAnalyzer
from servos.forensics.hasher import FileHasher
from servos.forensics.artifact_extractor import ArtifactExtractor
from servos.forensics.malware_detector import MalwareDetector
from servos.forensics.duplicate_detector import DuplicateDetector
from servos.forensics.timeline import TimelineBuilder
from servos.forensics.memory_scanner import MemoryScanner
from servos.forensics.log_analyzer import LogAnalyzer
from servos.forensics.registry_analyzer import RegistryAnalyzer
from servos.forensics.deep_malware_scanner import DeepMalwareScanner
from servos.forensics.network_scanner import NetworkScanner
from servos.llm.investigator import LLMInvestigator
from servos.llm.agent import ForensicAgent
from servos.legal.advisor import (
    get_admissibility_tips,
    get_evidence_handling_guide,
    get_full_legal_reference,
    get_key_precedents,
    get_legal_checklist,
    get_section_summary,
)
from servos.reports.generator import ReportGenerator
from servos.playbooks.engine import PlaybookEngine
from servos.reference.it_act import lookup as lookup_it_act

# ── App setup ────────────────────────────────────────────────
app = FastAPI(title="Servos", version="1.0.0",
              description="Offline AI Forensic Assistant")

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")

# In-memory investigation progress store
_investigations: dict = {}

# In-memory alerts store (recent events)
_alerts: list = []

# ── Pydantic request models ─────────────────────────────────

class InvestigateRequest(BaseModel):
    device_path: str
    mount_point: str
    device_name: str = "Unknown"
    mode: str = "full_auto"
    investigator: str = "Investigator"

class ScanRequest(BaseModel):
    target_path: str

class SettingsUpdate(BaseModel):
    settings: dict

class AuthRequest(BaseModel):
    username: str
    password: str
    role: str = "investigator"

class GoogleAuthRequest(BaseModel):
    token: str


AVAILABLE_TOOLS = [
    {"id": "fs-scan", "name": "File System Scan", "category": "Disk", "status": "available", "last_run": None},
    {"id": "artifact-extract", "name": "Artifact Extraction", "category": "Artifacts", "status": "available", "last_run": None},
    {"id": "timeline-rebuild", "name": "Timeline Rebuild", "category": "Timeline", "status": "available", "last_run": None},
    {"id": "malware-scan", "name": "Malware Scan", "category": "Malware", "status": "available", "last_run": None},
    {"id": "deep-malware", "name": "Deep Malware Scan", "category": "Malware", "status": "available", "last_run": None},
    {"id": "hash-integrity", "name": "Hash Integrity", "category": "Integrity", "status": "available", "last_run": None},
    {"id": "network-scan", "name": "Network Scan", "category": "Network", "status": "available", "last_run": None},
    {"id": "memory-scan", "name": "Memory Scan", "category": "Memory", "status": "available", "last_run": None},
    {"id": "log-analysis", "name": "Log Analysis", "category": "Logs", "status": "available", "last_run": None},
    {"id": "registry-analysis", "name": "Registry Analysis", "category": "Registry", "status": "available", "last_run": None},
    {"id": "case-legal-brief", "name": "Legal Case Brief", "category": "Legal", "status": "available", "last_run": None},
]

_scan_jobs: Dict[str, Dict[str, Any]] = {}


def _record_alert(alert: dict):
    alert["timestamp"] = datetime.utcnow().isoformat()
    _alerts.insert(0, alert)
    if len(_alerts) > 200:
        _alerts.pop()


def _stop_monitor(attr_name: str):
    monitor = getattr(app.state, attr_name, None)
    if monitor:
        try:
            stop_fn = getattr(monitor, "stop", None) or getattr(monitor, "stop_monitoring", None)
            if stop_fn:
                stop_fn()
        except Exception:
            pass
        setattr(app.state, attr_name, None)


def _start_monitors(conf: Dict[str, Any]):
    alert_engine = getattr(app.state, "alert_engine", None)
    if not alert_engine:
        return

    for attr in ("network_monitor", "process_monitor", "file_watcher"):
        _stop_monitor(attr)

    if conf.get("enable_network_monitor"):
        network_monitor = NetworkMonitor(
            callback=lambda event: alert_engine.process_event(
                {"event_type": "NETWORK_ANOMALY", "details": event}
            )
        )
        network_monitor.start()
        app.state.network_monitor = network_monitor

    if conf.get("enable_process_monitor"):
        process_monitor = ProcessMonitor(
            callback=lambda event: alert_engine.process_event(
                {"event_type": "PROCESS_NEW", "details": event}
            )
        )
        process_monitor.start()
        app.state.process_monitor = process_monitor

    if conf.get("enable_file_watcher"):
        watch_paths = conf.get("watch_paths") or [conf.get("data_dir", os.path.expanduser("~"))]
        file_watcher = FileWatcher(
            paths=watch_paths,
            callback=lambda event: alert_engine.process_event(
                {"event_type": "FILE_MODIFIED", **event}
            ),
        )
        file_watcher.start()
        app.state.file_watcher = file_watcher


def _serialize_for_json(value: Any) -> Any:
    if is_dataclass(value):
        return asdict(value)
    if isinstance(value, dict):
        return {key: _serialize_for_json(val) for key, val in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_serialize_for_json(item) for item in value]
    return value


def _extract_case_reference(message: str) -> Tuple[str, Optional[str]]:
    match = re.search(r"\[Case:([^\]]+)\]", message or "", re.IGNORECASE)
    if not match:
        return message, None
    clean_message = re.sub(r"\[Case:[^\]]+\]\s*", "", message).strip()
    return clean_message, match.group(1).strip()


def _summarize_findings_payload(findings: Dict[str, Any]) -> Dict[str, Any]:
    findings = findings or {}
    payload: Dict[str, Any] = {}

    file_system = findings.get("file_system") or {}
    suspicious_files = file_system.get("suspicious_files") or []
    if file_system:
        payload["file_system"] = {
            "total_files": file_system.get("total_files", 0),
            "suspicious": len(suspicious_files),
            "types": dict(list((file_system.get("file_type_counts") or {}).items())[:10]),
        }
        payload["suspicious_files"] = [
            {
                "name": item.get("filename", ""),
                "path": item.get("full_path", ""),
                "reason": item.get("suspicious_reason", ""),
                "entropy": item.get("entropy", 0),
            }
            for item in suspicious_files[:20]
        ]

    malware = findings.get("malware") or {}
    indicators = malware.get("indicators") or []
    if malware:
        payload["malware"] = {
            "risk_level": malware.get("risk_level", "UNKNOWN"),
            "indicators": len(indicators),
        }
        payload["malware_indicators"] = [
            {
                "rule": item.get("rule_name", ""),
                "severity": item.get("severity", ""),
                "file": os.path.basename(item.get("file_path", "")),
                "description": item.get("description", ""),
            }
            for item in indicators[:20]
        ]

    artifacts = findings.get("artifacts") or {}
    if artifacts:
        payload["artifacts"] = {
            "browser": len(artifacts.get("browser_history") or []),
            "recent": len(artifacts.get("recent_files") or []),
            "registry": len(artifacts.get("registry_items") or []),
            "logs": len(artifacts.get("log_entries") or []),
        }

    timeline = findings.get("timeline") or {}
    if timeline:
        payload["timeline_events"] = [
            {
                "timestamp": (item.get("timestamp") or "")[:19],
                "description": item.get("description", ""),
                "severity": item.get("severity", ""),
            }
            for item in (timeline.get("events") or [])[:50]
        ]
        payload["timeline_anomalies"] = [
            {
                "type": item.get("anomaly_type", ""),
                "description": item.get("description", ""),
                "severity": item.get("severity", ""),
                "event_count": item.get("event_count", 0),
            }
            for item in (timeline.get("anomalies") or [])[:10]
        ]

    payload["integrity_hashes"] = findings.get("integrity_hashes") or {}
    return payload


def _build_case_legal_references(findings: Dict[str, Any]) -> List[Dict[str, Any]]:
    keywords: List[str] = []
    suspicious_files = ((findings.get("file_system") or {}).get("suspicious_files") or [])
    if suspicious_files:
        keywords.append("unauthorized access suspicious files")
    malware = findings.get("malware") or {}
    if malware.get("indicators"):
        keywords.append("malware hacking")
    browser_history = ((findings.get("artifacts") or {}).get("browser_history") or [])
    if any((item.get("suspicious_score", 0) or 0) >= 0.5 for item in browser_history):
        keywords.append("fraud phishing privacy")

    query = " ".join(keywords).strip()
    if not query:
        return []

    return [
        {
            "section_id": result.section_id,
            "title": result.title,
            "description": result.description,
            "punishment": result.punishment,
            "relevance": result.relevance,
        }
        for result in lookup_it_act(query)
    ]


def _build_case_payload(record: CaseRecord) -> Dict[str, Any]:
    raw_findings = json.loads(record.findings_json) if record.findings_json else {}
    return {
        "id": record.id,
        "created_at": record.created_at,
        "investigator": record.investigator,
        "mode": record.mode,
        "status": record.status,
        "report_path": record.report_path,
        "device_info": json.loads(record.device_info_json) if record.device_info_json else {},
        "backup": json.loads(record.backup_json) if record.backup_json else {},
        "findings": _summarize_findings_payload(raw_findings),
        "full_findings": raw_findings,
        "interpretation": json.loads(record.interpretation_json) if record.interpretation_json else {},
        "legal_references": _build_case_legal_references(raw_findings),
    }


def _load_case_payload(case_id: str) -> Optional[Dict[str, Any]]:
    live = _investigations.get(case_id)
    if live and live.get("case"):
        return _case_to_dict(live["case"])

    session = get_session()
    try:
        record = session.query(CaseRecord).filter_by(id=case_id).first()
        if not record:
            return None
        return _build_case_payload(record)
    finally:
        session.close()


def _resolve_tool_target(case_id: Optional[str], target_path: Optional[str]) -> Tuple[str, Optional[Dict[str, Any]]]:
    case_payload = _load_case_payload(case_id) if case_id else None
    if target_path and os.path.exists(target_path):
        return target_path, case_payload
    if case_payload:
        device_info = case_payload.get("device_info") or {}
        backup = case_payload.get("backup") or {}
        for candidate in (
            device_info.get("mount_point"),
            device_info.get("path"),
            backup.get("backup_path"),
        ):
            if candidate and os.path.exists(candidate):
                return candidate, case_payload
    fallback = get_config().get("data_dir", os.path.expanduser("~"))
    return fallback, case_payload


def _discover_log_targets(target_path: str) -> List[str]:
    if target_path and os.path.isfile(target_path):
        return [target_path]
    if target_path and os.path.isdir(target_path):
        candidates: List[str] = []
        for root, _, files in os.walk(target_path):
            for filename in files:
                if filename.lower().endswith((".log", ".txt", ".evtx")):
                    candidates.append(os.path.join(root, filename))
                if len(candidates) >= 25:
                    return candidates
        return candidates

    windows_logs = os.path.expandvars(r"%SystemRoot%\System32\winevt\Logs")
    if os.path.isdir(windows_logs):
        return _discover_log_targets(windows_logs)
    if os.path.isdir("/var/log"):
        return _discover_log_targets("/var/log")
    return []


def _discover_registry_hives(target_path: str) -> List[str]:
    hive_names = {"SYSTEM", "SOFTWARE", "SAM", "SECURITY", "NTUSER.DAT"}
    if target_path and os.path.isfile(target_path):
        return [target_path]
    if not target_path or not os.path.isdir(target_path):
        return []

    matches: List[str] = []
    for root, _, files in os.walk(target_path):
        for filename in files:
            if filename.upper() in hive_names:
                matches.append(os.path.join(root, filename))
            if len(matches) >= 5:
                return matches
    return matches


def _execute_tool(tool_id: str, target_path: str, case_payload: Optional[Dict[str, Any]] = None, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    options = options or {}

    if tool_id == "fs-scan":
        analysis = FileAnalyzer().analyze(target_path)
        return {
            "target": target_path,
            "total_files": analysis.total_files,
            "total_dirs": analysis.total_dirs,
            "total_size_bytes": analysis.total_size_bytes,
            "hidden_files": analysis.hidden_files,
            "suspicious_files": [
                {
                    "name": item.filename,
                    "path": item.full_path,
                    "reason": item.suspicious_reason,
                    "entropy": item.entropy,
                }
                for item in analysis.suspicious_files[:25]
            ],
            "file_types": dict(list(analysis.file_type_counts.items())[:20]),
        }

    if tool_id == "artifact-extract":
        artifacts = ArtifactExtractor().extract_all(target_path)
        suspicious_domains = [
            item.content.get("url", "")
            for item in artifacts.browser_history
            if item.suspicious_score >= 0.5
        ]
        return {
            "target": target_path,
            "browser_history": len(artifacts.browser_history),
            "recent_files": len(artifacts.recent_files),
            "registry_items": len(artifacts.registry_items),
            "log_entries": len(artifacts.log_entries),
            "suspicious_domains": suspicious_domains[:15],
        }

    if tool_id == "timeline-rebuild":
        analysis = FileAnalyzer().analyze(target_path)
        artifacts = ArtifactExtractor().extract_all(target_path)
        timeline = TimelineBuilder().build(analysis, artifacts)
        return {
            "target": target_path,
            "events": len(timeline.events),
            "suspicious_windows": timeline.suspicious_windows,
            "anomalies": _serialize_for_json(timeline.anomalies[:10]),
        }

    if tool_id == "malware-scan":
        malware = MalwareDetector().scan(target_path)
        return {
            "target": target_path,
            "risk_level": malware.risk_level,
            "files_scanned": malware.files_scanned,
            "suspicious_count": malware.suspicious_count,
            "indicators": [
                {
                    "type": item.indicator_type,
                    "file": item.file_path,
                    "description": item.description,
                    "severity": item.severity,
                    "rule": item.rule_name,
                    "confidence": item.confidence,
                }
                for item in malware.indicators[:30]
            ],
        }

    if tool_id == "deep-malware":
        findings = DeepMalwareScanner().scan_path(target_path, options.get("yara_rules"))
        return {"target": target_path, "findings": findings[:50], "count": len(findings)}

    if tool_id == "hash-integrity":
        cfg = get_config()
        hashes = FileHasher().hash_directory(
            target_path,
            max_file_size=cfg.get("max_file_size_mb", 500) * 1024 * 1024,
        )
        integrity_map = {
            item["file"]: item["sha256"]
            for item in hashes
            if item.get("sha256") and item.get("sha256") != "ERROR"
        }
        duplicates = DuplicateDetector().find_duplicates(integrity_map)
        return {
            "target": target_path,
            "total_hashed": len(hashes),
            "duplicate_groups": [
                {"sha256": sha256, "count": len(paths), "files": paths[:5]}
                for sha256, paths in list(duplicates.items())[:10]
            ],
            "sample_hashes": hashes[:20],
        }

    if tool_id == "network-scan":
        scanner = NetworkScanner()
        return {
            "interfaces": scanner.list_interfaces(),
            "connections": scanner.active_connections()[:50],
            "listening_ports": scanner.listening_ports()[:30],
            "dns_cache": scanner.dns_cache()[:50],
            "arp_table": scanner.arp_table()[:50],
        }

    if tool_id == "memory-scan":
        captures_dir = os.path.join(get_config().get("data_dir", os.path.expanduser("~")), "captures")
        os.makedirs(captures_dir, exist_ok=True)
        dump_path = options.get("dump_path") or os.path.join(
            captures_dir,
            f"ramdump_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.bin",
        )
        captured = MemoryScanner().capture_ram(dump_path)
        if not captured:
            return {
                "captured": False,
                "dump_path": dump_path,
                "error": "Memory acquisition tool is not installed or capture failed.",
            }
        plugin = options.get("plugin", "pslist")
        preview = MemoryScanner().analyze_dump(dump_path, plugin)[:25]
        return {
            "captured": True,
            "dump_path": dump_path,
            "plugin": plugin,
            "analysis_preview": preview,
        }

    if tool_id == "log-analysis":
        analyzer = LogAnalyzer()
        targets = _discover_log_targets(target_path)
        if not targets:
            return {"target": target_path, "files_analyzed": 0, "threats": [], "error": "No log files found."}
        threats = []
        for path in targets:
            for threat in analyzer.analyze_patterns(path)[:20]:
                threats.append(
                    {
                        "pattern_name": threat.pattern_name,
                        "severity": threat.severity,
                        "timestamp": threat.timestamp,
                        "file_path": threat.file_path,
                        "matched_line": threat.matched_line[:200],
                    }
                )
        return {
            "target": target_path,
            "files_analyzed": len(targets),
            "threats": threats[:50],
            "raw_samples": {path: analyzer.analyze_file(path)[:5] for path in targets[:5]},
        }

    if tool_id == "registry-analysis":
        hives = _discover_registry_hives(target_path)
        if not hives:
            return {"target": target_path, "hives": [], "error": "No registry hives found."}
        analyzer = RegistryAnalyzer()
        results = []
        for hive_path in hives:
            try:
                hive = analyzer.load_hive(hive_path)
                keys = analyzer.list_keys(hive)
                results.append({"hive_path": hive_path, "top_keys": dict(list(keys.items())[:25])})
            except Exception as exc:
                results.append({"hive_path": hive_path, "error": str(exc)})
        return {"target": target_path, "hives": results}

    if tool_id == "case-legal-brief":
        findings = (case_payload or {}).get("full_findings") or {}
        return {
            "case_id": (case_payload or {}).get("id"),
            "references": _build_case_legal_references(findings),
            "checklist": get_legal_checklist(),
            "admissibility_tips": get_admissibility_tips(),
        }

    raise HTTPException(404, "Unknown tool")

# ── Lifecycle ────────────────────────────────────────────────

@app.on_event("startup")
async def startup():
    ensure_dirs()
    init_db()

    app.state.alert_engine = AlertEngine(callback=_record_alert)
    app.state.agent = ForensicAgent()
    cfg = get_config()
    loop = asyncio.get_running_loop()

    def _usb_callback(dev):
        app.state.alert_engine.process_event(
            {"event_type": "USB_CONNECTED", "device": dev.to_dict() if hasattr(dev, "to_dict") else {}}
        )
        if not get_config().get("auto_investigate", False):
            return
        case = Case(device_info=dev, mode="full_auto")
        _investigations[case.id] = {
            "status": "started",
            "progress": 0,
            "step": "Initializing...",
            "case": case,
            "result": None,
            "error": None,
        }
        asyncio.run_coroutine_threadsafe(_run_investigation(case.id, dev, "full_auto"), loop)

    svc = USBDetectionService(callback=_usb_callback, poll_interval=cfg.get("usb_poll_interval", 2.0))
    if cfg.get("auto_detect_usb", True):
        svc.start_monitoring()
    app.state.usb_service = svc

    _start_monitors(cfg)


@app.on_event("shutdown")
async def shutdown():
    _stop_monitor("usb_service")
    _stop_monitor("network_monitor")
    _stop_monitor("process_monitor")
    _stop_monitor("file_watcher")

# ── API: Devices ─────────────────────────────────────────────

@app.get("/api/devices")
async def list_devices():
    svc = USBDetectionService()
    devices = svc.detect_devices()
    return {"devices": [d.to_dict() for d in devices]}

# ── API: Auth ────────────────────────────────────────────────

@app.post("/api/auth/login")
async def login(req: AuthRequest):
    if _verify_user(req.username, req.password):
        user = _get_user(req.username) or {}
        return {
            "status": "success",
            "username": user.get("username", req.username.strip().lower()),
            "role": user.get("role", req.role),
        }
    if not _user_exists():
        raise HTTPException(401, "No local accounts found. Register an offline investigator account first.")
    raise HTTPException(401, "Invalid username or password")

@app.post("/api/auth/register")
async def register(req: AuthRequest):
    ok, value = _register_user(req.username, req.password, req.role)
    if ok:
        return {"status": "success", "username": value, "role": req.role}
    raise HTTPException(400, value)

@app.post("/api/auth/google")
async def google_login(req: GoogleAuthRequest):
    raise HTTPException(400, "Google authentication is disabled in the offline build.")

# ── API: Quick Scan ──────────────────────────────────────────

@app.post("/api/scan")
async def quick_scan(req: ScanRequest):
    if not os.path.exists(req.target_path):
        raise HTTPException(404, "Path not found")

    fa = FileAnalyzer()
    analysis = fa.analyze(req.target_path)

    md = MalwareDetector()
    malware = md.scan(req.target_path)

    return {
        "total_files": analysis.total_files,
        "total_dirs": analysis.total_dirs,
        "total_size": analysis.total_size_bytes,
        "hidden_files": analysis.hidden_files,
        "suspicious_files": [
            {"name": f.filename, "path": f.full_path, "reason": f.suspicious_reason,
             "size": f.file_size, "entropy": f.entropy}
            for f in analysis.suspicious_files[:30]
        ],
        "file_types": dict(list(analysis.file_type_counts.items())[:20]),
        "malware": {
            "risk_level": malware.risk_level,
            "files_scanned": malware.files_scanned,
            "suspicious_count": malware.suspicious_count,
            "indicators": [
                {"type": i.indicator_type, "file": i.file_path,
                 "description": i.description, "severity": i.severity,
                 "rule": i.rule_name, "confidence": i.confidence}
                for i in malware.indicators[:30]
            ],
        },
    }

# ── API: Investigate ─────────────────────────────────────────

@app.post("/api/investigate")
async def start_investigation(req: InvestigateRequest, bg: BackgroundTasks):
    if not os.path.exists(req.mount_point):
        raise HTTPException(404, "Mount point not found")

    device = DeviceInfo(
        path=req.device_path, name=req.device_name,
        mount_point=req.mount_point,
    )
    try:
        usage = __import__("psutil").disk_usage(req.mount_point)
        device.capacity_bytes = usage.total
    except Exception:
        pass

    case = Case(device_info=device, mode=req.mode, investigator=req.investigator)

    _investigations[case.id] = {
        "status": "started", "progress": 0, "step": "Initializing...",
        "case": case, "result": None, "error": None,
    }

    bg.add_task(_run_investigation, case.id, device, req.mode)
    return {"case_id": case.id, "status": "started"}


async def _run_investigation(case_id: str, device: DeviceInfo, mode: str):
    inv = _investigations[case_id]
    case = inv["case"]
    cfg = get_config()

    try:
        # Step 1: Backup
        inv.update(status="running", progress=10, step="Creating forensic backup...")
        backup_svc = EvidenceBackup()
        case.backup = backup_svc.create_backup(device.mount_point, case.id)

        # Step 2: File System
        inv.update(progress=25, step="Analyzing file system...")
        findings = ForensicFindings()
        findings.file_system = FileAnalyzer().analyze(device.mount_point)

        # Step 3: Hashing
        inv.update(progress=40, step="Hashing files...")
        hasher = FileHasher()
        paths = [f.full_path for f in findings.file_system.files[:500]]
        hashes = hasher.hash_files(paths)
        findings.integrity_hashes = {r["file"]: r["sha256"] for r in hashes if r["sha256"] != "ERROR"}

        # Step 4: Artifacts
        inv.update(progress=55, step="Extracting artifacts...")
        findings.artifacts = ArtifactExtractor().extract_all(device.mount_point)

        # Step 5: Malware
        inv.update(progress=65, step="Scanning for malware...")
        findings.malware = MalwareDetector().scan(device.mount_point)

        # Step 6: Timeline
        inv.update(progress=75, step="Building timeline...")
        findings.timeline = TimelineBuilder().build(findings.file_system, findings.artifacts)
        case.findings = findings

        # Step 7: LLM
        inv.update(progress=85, step="AI analysis...")
        llm = LLMInvestigator()
        interp = LLMInterpretation()
        fd = _findings_dict(findings)
        interp.recommendations = llm.suggest_next_steps(fd)
        interp.summary = llm.generate_summary({"id": case.id, "device_info": device.to_dict(), "findings": fd})
        interp.risk_assessment = findings.malware.risk_level if findings.malware else "UNKNOWN"
        case.interpretation = interp

        # Step 8: Reports
        inv.update(progress=95, step="Generating reports...")
        reports_dir = cfg.get("reports_dir", os.path.join(os.path.expanduser("~"), ".servos", "reports"))
        os.makedirs(reports_dir, exist_ok=True)
        gen = ReportGenerator()
        case.report_path = gen.generate_txt(case, os.path.join(reports_dir, f"{case.id}_report.txt"))
        gen.generate_json(case, os.path.join(reports_dir, f"{case.id}_report.json"))
        try:
            gen.generate_pdf(case, os.path.join(reports_dir, f"{case.id}_report.pdf"))
        except Exception:
            pass

        case.status = "completed"
        inv.update(status="completed", progress=100, step="Investigation complete!", result=_case_to_dict(case))

        # Save to DB
        _save_case_to_db(case)

    except Exception as e:
        inv.update(status="error", step=f"Error: {str(e)}", error=traceback.format_exc())


@app.get("/api/investigate/{case_id}/status")
async def investigation_status(case_id: str):
    inv = _investigations.get(case_id)
    if not inv:
        raise HTTPException(404, "Investigation not found")
    return {
        "status": inv["status"], "progress": inv["progress"],
        "step": inv["step"], "result": inv.get("result"),
        "error": inv.get("error"),
    }

# ── API: Cases ───────────────────────────────────────────────

@app.get("/api/cases")
async def list_cases():
    session = get_session()
    try:
        records = session.query(CaseRecord).order_by(CaseRecord.created_at.desc()).limit(50).all()
        result = []
        for record in records:
            payload = _build_case_payload(record)
            result.append(
                {
                    "id": payload["id"],
                    "created_at": payload["created_at"],
                    "investigator": payload["investigator"],
                    "mode": payload["mode"],
                    "status": payload["status"],
                    "report_path": payload["report_path"],
                    "device_info": payload["device_info"],
                    "risk": (payload.get("interpretation") or {}).get("risk"),
                }
            )
        return {"cases": result}
    finally:
        session.close()

@app.get("/api/cases/{case_id}")
async def get_case(case_id: str):
    payload = _load_case_payload(case_id)
    if not payload:
        raise HTTPException(404, "Case not found")
    return payload


@app.get("/api/cases/{case_id}/legal")
async def get_case_legal(case_id: str):
    payload = _load_case_payload(case_id)
    if not payload:
        raise HTTPException(404, "Case not found")
    return {
        "case_id": case_id,
        "references": payload.get("legal_references", []),
        "checklist": get_legal_checklist(),
        "admissibility_tips": get_admissibility_tips(),
    }

# ── API: Reports ─────────────────────────────────────────────

@app.get("/api/reports/{case_id}/{fmt}")
async def download_report(case_id: str, fmt: str):
    cfg = get_config()
    reports_dir = cfg.get("reports_dir", os.path.join(os.path.expanduser("~"), ".servos", "reports"))
    path = os.path.join(reports_dir, f"{case_id}_report.{fmt}")
    if not os.path.exists(path):
        raise HTTPException(404, "Report not found")
    media = {"txt": "text/plain", "json": "application/json", "pdf": "application/pdf",
             "csv": "text/csv"}.get(fmt, "application/octet-stream")
    return FileResponse(path, media_type=media, filename=f"{case_id}_report.{fmt}")


@app.get("/api/legal/full")
async def legal_full():
    full = get_full_legal_reference()
    return {
        "sections": full.get("sections", {}),
        "checklist": full.get("checklist", get_legal_checklist()),
        "admissibility_tips": full.get("tips", get_admissibility_tips()),
        "evidence_handling": full.get("evidence_handling", get_evidence_handling_guide()),
        "precedents": full.get("precedents", get_key_precedents()),
    }


@app.get("/api/legal/sections/{section_id}")
async def legal_section(section_id: str):
    return get_section_summary(section_id)


@app.get("/api/legal/search")
async def legal_search(q: str = Query(..., min_length=2)):
    results = lookup_it_act(q)
    return {
        "results": [
            {
                "section_id": result.section_id,
                "title": result.title,
                "description": result.description,
                "punishment": result.punishment,
                "relevance": result.relevance,
            }
            for result in results
        ]
    }

# ── API: Tools / Workbench ─────────────────────────────────────

@app.get("/api/tools/available")
async def available_tools():
    return {"tools": AVAILABLE_TOOLS}

class ToolRunRequest(BaseModel):
    tool_id: str
    case_id: Optional[str] = None
    target_path: Optional[str] = None
    options: Optional[Dict[str, Any]] = None

# ── API: Network Scanning ───────────────────────────────────────

@app.get("/api/network/interfaces")
async def network_interfaces():
    from servos.forensics.network_scanner import NetworkScanner
    return {"interfaces": NetworkScanner().list_interfaces()}

@app.get("/api/network/connections")
async def network_connections():
    from servos.forensics.network_scanner import NetworkScanner
    return {"connections": NetworkScanner().active_connections()}

@app.get("/api/network/listen")
async def network_listen():
    from servos.forensics.network_scanner import NetworkScanner
    return {"ports": NetworkScanner().listening_ports()}

@app.get("/api/network/arp")
async def network_arp():
    from servos.forensics.network_scanner import NetworkScanner
    return {"arp": NetworkScanner().arp_table()}

@app.get("/api/network/dns")
async def network_dns():
    from servos.forensics.network_scanner import NetworkScanner
    return {"dns": NetworkScanner().dns_cache()}

# ── API: Memory Scanning ───────────────────────────────────────

@app.post("/api/memory/capture")
async def memory_capture():
    path = os.path.join(get_config().get("data_dir"), "ramdump.bin")
    success = MemoryScanner().capture_ram(path)
    return {
        "success": success,
        "path": path if success else "",
        "error": None if success else "Memory acquisition tool is unavailable or capture failed.",
    }

@app.post("/api/memory/analyze")
async def memory_analyze(req: dict):
    dump = req.get("dump_path")
    plugin = req.get("plugin", "pslist")
    results = MemoryScanner().analyze_dump(dump, plugin)
    return {"output": results}

# ── API: Log Analysis ─────────────────────────────────────────

@app.post("/api/logs/analyze")
async def logs_analyze(req: dict):
    path = req.get("path")
    analyzer = LogAnalyzer()
    if os.path.isdir(path):
        result = analyzer.analyze_directory(path)
    else:
        result = {path: analyzer.analyze_file(path)}
    return {"results": result}

# ── API: Registry Analysis ────────────────────────────────────

@app.post("/api/registry/analyze")
async def registry_analyze(req: dict):
    path = req.get("hive_path")
    analyzer = RegistryAnalyzer()
    hive = analyzer.load_hive(path)
    return {"keys": analyzer.list_keys(hive)}

# ── API: Deep Malware Scan ────────────────────────────────────

@app.post("/api/malware/deep")
async def malware_deep(req: dict):
    root = req.get("root")
    rules = req.get("yara_rules")
    dms = DeepMalwareScanner()
    findings = dms.scan_path(root, rules)
    return {"findings": findings}

@app.post("/api/tools/run")
async def run_tool(req: ToolRunRequest):
    target_path, case_payload = _resolve_tool_target(req.case_id, req.target_path)
    result = _execute_tool(req.tool_id, target_path, case_payload, req.options)
    return {
        "status": "completed",
        "tool_id": req.tool_id,
        "case_id": req.case_id,
        "target": target_path,
        "ran_at": datetime.utcnow().isoformat(),
        "result": result,
    }

# ── API: Settings ────────────────────────────────────────────

@app.get("/api/settings")
async def get_settings():
    return {"settings": get_config()}

@app.put("/api/settings")
async def update_settings(req: SettingsUpdate):
    save_config(req.settings)
    # if usb poll interval changed, restart usb monitoring
    if "usb_poll_interval" in req.settings or "auto_investigate" in req.settings or "auto_detect_usb" in req.settings:
        svc: USBDetectionService = getattr(app.state, "usb_service", None)
        if svc:
            cfg = get_config()
            svc.stop_monitoring()
            svc.poll_interval = cfg.get("usb_poll_interval", svc.poll_interval)
            if cfg.get("auto_detect_usb", True):
                svc.start_monitoring()
    # if any monitoring toggle changed, restart monitors
    monitor_keys = ["enable_network_monitor", "enable_process_monitor", "enable_file_watcher", "watch_paths"]
    if any(k in req.settings for k in monitor_keys):
        _start_monitors(get_config())
    return {"settings": get_config()}


# ── API: Alerts / Monitoring ─────────────────────────────────

@app.get("/api/alerts")
async def list_alerts(limit: int = 50):
    # return most recent alerts, optionally limited
    return {"alerts": _alerts[:limit]}

# ── MultiScan Jobs ──────────────────────────────────────────

async def _run_multiscan_job(job_id: str, tools: list, target: str):
    job = _scan_jobs.get(job_id)
    if not job:
        return
    job["status"] = "running"
    job["progress"] = 0
    job["results"] = []
    job["start_time"] = datetime.utcnow().isoformat()

    total = max(len(tools), 1)

    def _wrap(tool_id: str):
        return lambda: {"tool": tool_id, "result": _execute_tool(tool_id, target, None, None)}

    def cb(result):
        job["results"].append(result)
        job["progress"] = int((len(job["results"]) / total) * 100)

    coord = MultiScanCoordinator([_wrap(tool_id) for tool_id in tools], callback=cb)
    if job.get("cancel"):
        job["status"] = "cancelled"
    else:
        try:
            coord.run_all()
            job["status"] = "cancelled" if job.get("cancel") else "completed"
        except Exception as exc:
            job["status"] = "error"
            job["results"].append({"error": str(exc)})
    job["end_time"] = datetime.utcnow().isoformat()

@app.post("/api/multiscan")
async def start_multiscan(req: dict, bg: BackgroundTasks):
    tools = req.get("tools", [])
    target = req.get("target", "/")
    job_id = uuid.uuid4().hex
    _scan_jobs[job_id] = {
        "id": job_id,
        "tools": tools,
        "target": target,
        "status": "queued",
        "progress": 0,
        "results": [],
        "cancel": False,
    }
    bg.add_task(_run_multiscan_job, job_id, tools, target)
    return {"job_id": job_id, "status": "queued"}

@app.get("/api/multiscan/{job_id}/status")
async def scan_status(job_id: str):
    job = _scan_jobs.get(job_id)
    if not job:
        raise HTTPException(404, "Scan job not found")
    return {k: job[k] for k in ['id', 'status', 'progress', 'tools', 'target', 'results', 'start_time', 'end_time']}

@app.post("/api/multiscan/{job_id}/cancel")
async def cancel_scan(job_id: str):
    job = _scan_jobs.get(job_id)
    if not job:
        raise HTTPException(404, "Scan job not found")
    job['cancel'] = True
    return {"status": "cancelling"}


# ── API: Playbooks ───────────────────────────────────────────

@app.get("/api/playbooks")
async def list_playbooks():
    engine = PlaybookEngine()
    pbs = engine.list_playbooks()
    return {"playbooks": [
        {"name": pb.name, "description": pb.description, "version": pb.version,
         "steps": len(pb.steps), "metadata": pb.metadata}
        for pb in pbs
    ]}

# ── API: LLM Status ─────────────────────────────────────────

@app.get("/api/llm/status")
async def llm_status():
    llm = LLMInvestigator()
    available = llm.is_available()
    return {"available": available, "model": llm.model, "base_url": llm.base_url}

# ── API: RAG Chat ────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str
    history: Optional[List[dict]] = None
    case_id: Optional[str] = None

@app.post("/api/chat")
async def general_chat(req: ChatRequest):
    history = req.history or []
    message, embedded_case_id = _extract_case_reference(req.message)
    active_case_id = req.case_id or embedded_case_id
    active_case = _load_case_payload(active_case_id) if active_case_id else None

    agent: ForensicAgent = getattr(app.state, "agent", None) or ForensicAgent()
    response = agent.process(
        message,
        history=history,
        case_id=active_case_id,
        active_case=active_case,
        allow_unsafe=False,
    )

    if active_case:
        response.setdefault("sources", []).insert(
            0,
            {
                "type": "case_context",
                "label": f"Case: {active_case['id']}",
                "data": {
                    "risk": (active_case.get("interpretation") or {}).get("risk", "UNKNOWN"),
                    "device": (active_case.get("device_info") or {}).get("name", "Unknown"),
                },
            },
        )
    return response


# ── Serve static frontend (React SPA) ────────────────────────

# Serve Vite-built assets
if os.path.isdir(os.path.join(STATIC_DIR, "assets")):
    app.mount("/assets", StaticFiles(directory=os.path.join(STATIC_DIR, "assets")), name="assets")

@app.get("/")
async def index():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))

# Catch-all for React client-side routing (login, investigate, workspace, etc.)
@app.get("/{path:path}")
async def spa_fallback(path: str):
    # Don't override API routes or actual static files
    file_path = os.path.join(STATIC_DIR, path)
    if os.path.isfile(file_path):
        return FileResponse(file_path)
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))

# ── Helpers ──────────────────────────────────────────────────

def _findings_dict(findings: ForensicFindings) -> dict:
    d = {}
    if findings.file_system:
        d["file_system"] = {"total_files": findings.file_system.total_files,
                            "suspicious": len(findings.file_system.suspicious_files),
                            "types": dict(list(findings.file_system.file_type_counts.items())[:10])}
    if findings.malware:
        d["malware"] = {"risk_level": findings.malware.risk_level,
                        "indicators": len(findings.malware.indicators)}
    if findings.artifacts:
        d["artifacts"] = {"browser": len(findings.artifacts.browser_history),
                          "recent": len(findings.artifacts.recent_files),
                          "registry": len(findings.artifacts.registry_items),
                          "logs": len(findings.artifacts.log_entries)}
    return d

def _case_to_dict(case: Case) -> dict:
    d = case.to_dict()
    if case.findings:
        raw_findings = _serialize_for_json(case.findings)
        d["findings"] = _summarize_findings_payload(raw_findings)
        d["full_findings"] = raw_findings
        d["legal_references"] = _build_case_legal_references(raw_findings)
    if case.interpretation:
        d["interpretation"] = {
            "risk": case.interpretation.risk_assessment,
            "summary": case.interpretation.summary,
            "recommendations": case.interpretation.recommendations,
        }
    if case.backup:
        d["backup"] = case.backup.to_dict()
    return d

def _save_case_to_db(case: Case):
    session = None
    try:
        session = get_session()
        record = CaseRecord(
            id=case.id, created_at=case.created_at, investigator=case.investigator,
            mode=case.mode, status=case.status, report_path=case.report_path or "",
            device_info_json=json.dumps(_serialize_for_json(case.device_info) if case.device_info else {}),
            backup_json=json.dumps(_serialize_for_json(case.backup) if case.backup else {}),
            findings_json=json.dumps(_serialize_for_json(case.findings) if case.findings else {}),
            interpretation_json=json.dumps({
                "risk": case.interpretation.risk_assessment,
                "summary": case.interpretation.summary,
                "recommendations": case.interpretation.recommendations,
            } if case.interpretation else {}),
        )
        session.merge(record)
        session.commit()
    except Exception:
        pass
    finally:
        if session:
            session.close()

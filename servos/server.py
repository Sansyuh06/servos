"""
Servos – FastAPI Web Server.
REST API that wraps all Servos forensic modules + serves the web UI.
"""

import os
import json
import asyncio
import traceback
from datetime import datetime
from typing import Optional, List

from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from pydantic import BaseModel

from servos.config import get_config, save_config, ensure_dirs
from servos.models.schema import (
    DeviceInfo, Case, ForensicFindings, LLMInterpretation,
    init_db, get_session, CaseRecord,
)

from servos.gui.auth import _verify_user, _create_user, _user_exists
from servos.detection.usb_monitor import USBDetectionService
from servos.preservation.backup import EvidenceBackup
from servos.forensics.file_analyzer import FileAnalyzer
from servos.forensics.hasher import FileHasher
from servos.forensics.artifact_extractor import ArtifactExtractor
from servos.forensics.malware_detector import MalwareDetector
from servos.forensics.timeline import TimelineBuilder
from servos.llm.investigator import LLMInvestigator
from servos.reports.generator import ReportGenerator
from servos.playbooks.engine import PlaybookEngine

# ── App setup ────────────────────────────────────────────────
app = FastAPI(title="Servos", version="1.0.0",
              description="Offline AI Forensic Assistant")

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")

# In-memory investigation progress store
_investigations: dict = {}

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

# ── Lifecycle ────────────────────────────────────────────────

@app.on_event("startup")
async def startup():
    ensure_dirs()
    init_db()

    # start USB monitor for automatic investigations if enabled
    cfg = get_config()
    poll = cfg.get("usb_poll_interval", 2.0)
    loop = asyncio.get_event_loop()

    def _usb_callback(dev):
        # executed in USBDetectionService thread
        cfg2 = get_config()
        if not cfg2.get("auto_investigate", False):
            return
        # schedule the investigation on the FastAPI event loop
        case = Case(device_info=dev, mode="full_auto")
        _investigations[case.id] = {
            "status": "started", "progress": 0, "step": "Initializing...",
            "case": case, "result": None, "error": None,
        }
        asyncio.run_coroutine_threadsafe(_run_investigation(case.id, dev, "full_auto"), loop)

    svc = USBDetectionService(callback=_usb_callback, poll_interval=poll)
    svc.start_monitoring()
    app.state.usb_service = svc

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
        return {"status": "success", "username": req.username, "role": req.role}
    raise HTTPException(401, "Invalid username or password")

@app.post("/api/auth/register")
async def register(req: AuthRequest):
    if _create_user(req.username, req.password):
        return {"status": "success", "username": req.username, "role": req.role}
    raise HTTPException(400, "Username already taken")

@app.post("/api/auth/google")
async def google_login(req: GoogleAuthRequest):
    """Mock Google OAuth callback. In production this would exchange an auth code for a token and fetch user info."""
    # We now receive req.token from the frontend successfully
    username = "Google User"
    if not _user_exists() or not _verify_user(username, "google_oauth_mock"):
        _create_user(username, "google_oauth_mock")
    return {"status": "success", "username": username, "role": "investigator"}

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
    records = session.query(CaseRecord).order_by(CaseRecord.created_at.desc()).limit(50).all()
    result = []
    for r in records:
        result.append({
            "id": r.id, "created_at": r.created_at, "investigator": r.investigator,
            "mode": r.mode, "status": r.status, "report_path": r.report_path,
            "device_info": json.loads(r.device_info_json) if r.device_info_json else {},
        })
    session.close()
    return {"cases": result}

@app.get("/api/cases/{case_id}")
async def get_case(case_id: str):
    session = get_session()
    r = session.query(CaseRecord).filter_by(id=case_id).first()
    session.close()
    if not r:
        raise HTTPException(404, "Case not found")
    return {
        "id": r.id, "created_at": r.created_at, "investigator": r.investigator,
        "mode": r.mode, "status": r.status, "report_path": r.report_path,
        "device_info": json.loads(r.device_info_json) if r.device_info_json else {},
        "backup": json.loads(r.backup_json) if r.backup_json else {},
        "findings": json.loads(r.findings_json) if r.findings_json else {},
        "interpretation": json.loads(r.interpretation_json) if r.interpretation_json else {},
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

# ── API: Tools / Workbench ─────────────────────────────────────

@app.get("/api/tools/available")
async def available_tools():
    # In a real implementation this would inspect installed utilities or configuration.
    tools = [
        {"id": "fs-scan", "name": "File System Scan", "category": "Disk", "status": "available", "last_run": None},
        {"id": "malware-scan", "name": "Malware Scan", "category": "Malware", "status": "available", "last_run": None},
        {"id": "hash-integrity", "name": "Hash Integrity", "category": "Disk", "status": "available", "last_run": None},
        {"id": "network-scan", "name": "Network Scan", "category": "Network", "status": "available", "last_run": None},
        {"id": "memory-scan", "name": "Memory Scan", "category": "Memory", "status": "available", "last_run": None},
        {"id": "log-analysis", "name": "Log Analysis", "category": "Logs", "status": "available", "last_run": None},
        {"id": "registry-analysis", "name": "Registry Analysis", "category": "Registry", "status": "available", "last_run": None},
        {"id": "deep-malware", "name": "Malware Deep Scan", "category": "Malware", "status": "available", "last_run": None},
    ]
    return {"tools": tools}

class ToolRunRequest(BaseModel):
    tool_id: str
    case_id: Optional[str] = None

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
    from servos.forensics.memory_scanner import MemoryScanner
    path = os.path.join(get_config().get("data_dir"), "ramdump.bin")
    success = MemoryScanner().capture_ram(path)
    return {"success": success, "path": path if success else ""}

@app.post("/api/memory/analyze")
async def memory_analyze(req: dict):
    from servos.forensics.memory_scanner import MemoryScanner
    dump = req.get("dump_path")
    plugin = req.get("plugin", "pslist")
    results = MemoryScanner().analyze_dump(dump, plugin)
    return {"output": results}

# ── API: Log Analysis ─────────────────────────────────────────

@app.post("/api/logs/analyze")
async def logs_analyze(req: dict):
    from servos.forensics.log_analyzer import LogAnalyzer
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
    from servos.forensics.registry_analyzer import RegistryAnalyzer
    path = req.get("hive_path")
    analyzer = RegistryAnalyzer()
    hive = analyzer.load_hive(path)
    return {"keys": analyzer.list_keys(hive)}

# ── API: Deep Malware Scan ────────────────────────────────────

@app.post("/api/malware/deep")
async def malware_deep(req: dict):
    from servos.forensics.deep_malware_scanner import DeepMalwareScanner
    root = req.get("root")
    rules = req.get("yara_rules")
    dms = DeepMalwareScanner()
    findings = dms.scan_path(root, rules)
    return {"findings": findings}

@app.post("/api/tools/run")
async def run_tool(req: ToolRunRequest):
    # stub implementation: in a full system this would enqueue the tool execution
    # and stream output via WebSocket. Here we simply acknowledge.
    return {"status": "scheduled", "tool_id": req.tool_id, "case_id": req.case_id}

# ── API: Settings ────────────────────────────────────────────

@app.get("/api/settings")
async def get_settings():
    return {"settings": get_config()}

@app.put("/api/settings")
async def update_settings(req: SettingsUpdate):
    save_config(req.settings)
    # if usb poll interval changed, restart monitor
    if "usb_poll_interval" in req.settings or "auto_investigate" in req.settings:
        svc: USBDetectionService = getattr(app.state, "usb_service", None)
        if svc:
            svc.stop_monitoring()
            cfg = get_config()
            svc.poll_interval = cfg.get("usb_poll_interval", svc.poll_interval)
            svc.start_monitoring()
    return {"settings": get_config()}

@app.put("/api/settings")
async def update_settings(req: SettingsUpdate):
    save_config(req.settings)
    return {"settings": get_config()}

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

@app.post("/api/chat")
async def general_chat(req: ChatRequest):
    """General-purpose conversational AI chat with multi-turn context."""
    llm = LLMInvestigator()

    history = req.history or []

    # Generate response using conversation history for context
    if llm.is_available():
        response_text = llm.chat(req.message, history)
        model_used = llm.model
    else:
        response_text = llm._fallback_chat(req.message)
        model_used = "offline-fallback"

    # Build lightweight context info for the sidebar
    context_info = []
    if history:
        topic_words = set()
        for msg in history[-5:]:
            words = msg.get("content", "").split()[:5]
            topic_words.update(w.lower() for w in words if len(w) > 3)
        if topic_words:
            context_info.append({
                "type": "conversation",
                "label": "Active Conversation",
                "data": {
                    "messages": len(history),
                    "topics": ", ".join(list(topic_words)[:6]),
                }
            })

    context_info.append({
        "type": "model_info",
        "label": f"Model: {model_used}",
        "data": {
            "status": "connected" if llm.is_available() else "offline",
            "model": model_used,
        }
    })

    return {
        "response": response_text,
        "sources": context_info,
        "model": model_used,
    }


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
        d["findings"] = _findings_dict(case.findings)
        if case.findings.file_system:
            d["findings"]["suspicious_files"] = [
                {"name": f.filename, "reason": f.suspicious_reason, "entropy": f.entropy}
                for f in case.findings.file_system.suspicious_files[:20]
            ]
        if case.findings.malware:
            d["findings"]["malware_indicators"] = [
                {"rule": i.rule_name, "severity": i.severity, "file": os.path.basename(i.file_path),
                 "description": i.description}
                for i in case.findings.malware.indicators[:20]
            ]
        if case.findings.timeline:
            d["findings"]["timeline_events"] = [
                {"timestamp": e.timestamp[:19] if e.timestamp else "", "description": e.description,
                 "severity": e.severity}
                for e in case.findings.timeline.events[:50]
            ]
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
    try:
        session = get_session()
        record = CaseRecord(
            id=case.id, created_at=case.created_at, investigator=case.investigator,
            mode=case.mode, status=case.status, report_path=case.report_path or "",
            device_info_json=json.dumps(case.device_info.to_dict() if case.device_info else {}),
            backup_json=json.dumps(case.backup.to_dict() if case.backup else {}),
            findings_json=json.dumps(_findings_dict(case.findings) if case.findings else {}),
            interpretation_json=json.dumps({
                "risk": case.interpretation.risk_assessment,
                "summary": case.interpretation.summary,
                "recommendations": case.interpretation.recommendations,
            } if case.interpretation else {}),
        )
        session.merge(record)
        session.commit()
        session.close()
    except Exception:
        pass

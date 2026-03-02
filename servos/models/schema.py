"""
Servos – Core Data Models & Database Schema.
Pydantic models for runtime data + SQLAlchemy ORM for persistence.
"""

from __future__ import annotations
import os
import json
from datetime import datetime
from typing import Optional, List, Dict, Tuple, Any
from dataclasses import dataclass, field, asdict

from sqlalchemy import create_engine, Column, String, DateTime, Float, Text, Integer, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

# ---------------------------------------------------------------------------
# Pydantic-style data classes  (using stdlib dataclasses for fewer deps)
# ---------------------------------------------------------------------------

@dataclass
class DeviceInfo:
    """Information about a connected storage device."""
    path: str                     # Drive letter or device path
    name: str = "Unknown Device"
    capacity_bytes: int = 0
    mount_point: str = ""
    is_removable: bool = True
    detected_at: str = ""
    filesystem: str = "Unknown"
    serial: str = ""

    def __post_init__(self):
        if not self.detected_at:
            self.detected_at = datetime.now().isoformat()

    def to_dict(self) -> dict:
        return asdict(self)

    @property
    def capacity_human(self) -> str:
        b = self.capacity_bytes
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if b < 1024:
                return f"{b:.1f} {unit}"
            b /= 1024
        return f"{b:.1f} PB"


@dataclass
class BackupResult:
    """Result of creating a forensic backup."""
    backup_path: str
    hash_md5: str = ""
    hash_sha256: str = ""
    size_bytes: int = 0
    created_at: str = ""
    device_info: Optional[Dict] = None
    files_backed_up: int = 0

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class FileMetadata:
    """Metadata for a single file."""
    filename: str
    full_path: str
    file_size: int = 0
    created: str = ""
    modified: str = ""
    accessed: str = ""
    is_hidden: bool = False
    is_system: bool = False
    extension: str = ""
    entropy: float = 0.0
    hash_md5: str = ""
    hash_sha256: str = ""
    suspicious: bool = False
    suspicious_reason: str = ""


@dataclass
class FileSystemAnalysis:
    """Results of file system analysis."""
    total_files: int = 0
    total_dirs: int = 0
    total_size_bytes: int = 0
    files: List[FileMetadata] = field(default_factory=list)
    file_type_counts: Dict[str, int] = field(default_factory=dict)
    hidden_files: int = 0
    suspicious_files: List[FileMetadata] = field(default_factory=list)


@dataclass
class ArtifactItem:
    """A single forensic artifact."""
    artifact_type: str       # 'browser_history', 'recent_file', 'registry', 'log'
    timestamp: str = ""
    description: str = ""
    content: Dict[str, Any] = field(default_factory=dict)
    suspicious_score: float = 0.0
    source_path: str = ""


@dataclass
class ArtifactResult:
    """Collection of extracted artifacts."""
    browser_history: List[ArtifactItem] = field(default_factory=list)
    recent_files: List[ArtifactItem] = field(default_factory=list)
    registry_items: List[ArtifactItem] = field(default_factory=list)
    log_entries: List[ArtifactItem] = field(default_factory=list)
    total_artifacts: int = 0

    def all_artifacts(self) -> List[ArtifactItem]:
        return self.browser_history + self.recent_files + self.registry_items + self.log_entries


@dataclass
class MalwareIndicator:
    """A single malware indicator."""
    indicator_type: str        # 'yara_match', 'entropy_high', 'extension_mismatch', 'suspicious_name'
    file_path: str = ""
    description: str = ""
    severity: str = "low"      # 'low', 'medium', 'high', 'critical'
    rule_name: str = ""
    confidence: float = 0.0


@dataclass
class MalwareResult:
    """Results of malware detection."""
    indicators: List[MalwareIndicator] = field(default_factory=list)
    files_scanned: int = 0
    suspicious_count: int = 0
    clean_count: int = 0
    risk_level: str = "LOW"    # LOW, MEDIUM, HIGH, CRITICAL


@dataclass
class TimelineEvent:
    """A single event in the investigation timeline."""
    timestamp: str
    description: str
    event_type: str = "file"   # 'file', 'artifact', 'system', 'user_action'
    severity: str = "info"     # 'info', 'low', 'medium', 'high'
    source: str = ""


@dataclass
class Timeline:
    """Reconstructed activity timeline."""
    events: List[TimelineEvent] = field(default_factory=list)
    date_range_start: str = ""
    date_range_end: str = ""
    suspicious_windows: List[Tuple[str, str]] = field(default_factory=list)


@dataclass
class ForensicFindings:
    """Combined forensic analysis results."""
    file_system: Optional[FileSystemAnalysis] = None
    artifacts: Optional[ArtifactResult] = None
    malware: Optional[MalwareResult] = None
    timeline: Optional[Timeline] = None
    integrity_hashes: Dict[str, str] = field(default_factory=dict)


@dataclass
class LLMInterpretation:
    """LLM-generated interpretation of findings."""
    summary: str = ""
    risk_assessment: str = "UNKNOWN"
    recommendations: List[str] = field(default_factory=list)
    clarifying_questions: List[str] = field(default_factory=list)


@dataclass
class Case:
    """A complete investigation case."""
    id: str = ""
    created_at: str = ""
    investigator: str = "Investigator"
    device_info: Optional[DeviceInfo] = None
    mode: str = "full_auto"     # 'full_auto', 'hybrid', 'manual'
    status: str = "active"      # 'active', 'paused', 'completed', 'closed'
    backup: Optional[BackupResult] = None
    findings: Optional[ForensicFindings] = None
    interpretation: Optional[LLMInterpretation] = None
    report_path: str = ""

    def __post_init__(self):
        if not self.id:
            now = datetime.now()
            self.id = f"CASE-{now.strftime('%Y-%m-%d')}-{now.strftime('%H%M%S')}"
        if not self.created_at:
            self.created_at = datetime.now().isoformat()

    def to_dict(self) -> dict:
        d = {
            "id": self.id,
            "created_at": self.created_at,
            "investigator": self.investigator,
            "mode": self.mode,
            "status": self.status,
            "report_path": self.report_path,
        }
        if self.device_info:
            d["device_info"] = self.device_info.to_dict()
        if self.backup:
            d["backup"] = self.backup.to_dict()
        return d


# ---------------------------------------------------------------------------
# SQLAlchemy ORM Models
# ---------------------------------------------------------------------------

Base = declarative_base()


class CaseRecord(Base):
    """Persistent case storage."""
    __tablename__ = "cases"

    id = Column(String, primary_key=True)
    created_at = Column(String, default=lambda: datetime.now().isoformat())
    investigator = Column(String, default="Investigator")
    device_info_json = Column(Text, default="{}")
    mode = Column(String, default="full_auto")
    status = Column(String, default="active")
    backup_json = Column(Text, default="{}")
    findings_json = Column(Text, default="{}")
    interpretation_json = Column(Text, default="{}")
    report_path = Column(String, default="")

    artifacts = relationship("ArtifactRecord", back_populates="case", cascade="all, delete-orphan")


class ArtifactRecord(Base):
    """Persistent artifact storage."""
    __tablename__ = "artifacts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    case_id = Column(String, ForeignKey("cases.id"))
    artifact_type = Column(String)
    timestamp = Column(String)
    description = Column(Text, default="")
    content_json = Column(Text, default="{}")
    suspicious_score = Column(Float, default=0.0)

    case = relationship("CaseRecord", back_populates="artifacts")


class PlaybookRecord(Base):
    """Stored playbook metadata."""
    __tablename__ = "playbooks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True)
    description = Column(Text, default="")
    file_path = Column(String, default="")
    created_at = Column(String, default=lambda: datetime.now().isoformat())


# ---------------------------------------------------------------------------
# Database session management
# ---------------------------------------------------------------------------

_engine = None
_Session = None


def get_db_path() -> str:
    """Return the path to the SQLite database."""
    from servos.config import get_config
    cfg = get_config()
    return cfg.get("database_path", os.path.join(os.path.expanduser("~"), ".servos", "cases.db"))


def init_db(db_path: Optional[str] = None):
    """Initialize the database, creating tables if needed."""
    global _engine, _Session
    if db_path is None:
        db_path = get_db_path()
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    _engine = create_engine(f"sqlite:///{db_path}", echo=False)
    Base.metadata.create_all(_engine)
    _Session = sessionmaker(bind=_engine)


def get_session():
    """Get a database session."""
    global _Session
    if _Session is None:
        init_db()
    return _Session()

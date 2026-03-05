"""
Servos – Native Desktop Application (PyQt6).
Professional forensic workstation UI wrapping all Servos modules.
"""

import sys
import os
import json
import traceback
from datetime import datetime
from dataclasses import asdict

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QStackedWidget, QPushButton, QLabel, QListWidget, QListWidgetItem,
    QTextEdit, QLineEdit, QComboBox, QProgressBar, QFileDialog,
    QMessageBox, QGroupBox, QScrollArea, QSplitter, QFrame,
    QTableWidget, QTableWidgetItem, QHeaderView, QSizePolicy,
    QTabWidget, QSpacerItem, QTreeWidget, QTreeWidgetItem,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QSize
from PyQt6.QtGui import QFont, QColor, QPalette, QIcon, QAction

from servos.config import get_config, save_config, ensure_dirs
from servos.models.schema import (
    DeviceInfo, Case, ForensicFindings, LLMInterpretation,
    init_db, get_session, CaseRecord,
)
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
from servos.gui.widgets.risk_dashboard import RiskDashboard


# ═══════════════════════════════════════════════════════════════
# Color palette
# ═══════════════════════════════════════════════════════════════
DARK_BG = "#0d1117"
CARD_BG = "#161b22"
BORDER = "#30363d"
ACCENT = "#58a6ff"
GREEN = "#3fb950"
RED = "#f85149"
ORANGE = "#d29922"
YELLOW = "#e3b341"
TEXT = "#e6edf3"
TEXT_DIM = "#8b949e"
PURPLE = "#bc8cff"

STYLESHEET = f"""
QMainWindow, QWidget {{
    background-color: {DARK_BG};
    color: {TEXT};
    font-family: 'Segoe UI', 'Inter', sans-serif;
    font-size: 13px;
}}
QLabel {{
    color: {TEXT};
}}
QPushButton {{
    background-color: {CARD_BG};
    color: {TEXT};
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 8px 18px;
    font-weight: 600;
    font-size: 13px;
}}
QPushButton:hover {{
    background-color: #1f2937;
    border-color: {ACCENT};
}}
QPushButton:pressed {{
    background-color: #0d1117;
}}
QPushButton#primary {{
    background-color: #238636;
    border-color: #2ea043;
    color: white;
}}
QPushButton#primary:hover {{
    background-color: #2ea043;
}}
QPushButton#danger {{
    background-color: #da3633;
    border-color: #f85149;
    color: white;
}}
QLineEdit, QComboBox, QTextEdit {{
    background-color: #0d1117;
    color: {TEXT};
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 13px;
    selection-background-color: {ACCENT};
}}
QLineEdit:focus, QTextEdit:focus {{
    border-color: {ACCENT};
}}
QGroupBox {{
    background-color: {CARD_BG};
    border: 1px solid {BORDER};
    border-radius: 8px;
    margin-top: 12px;
    padding: 16px;
    padding-top: 28px;
    font-weight: 600;
    font-size: 14px;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    left: 16px;
    padding: 0 8px;
    color: {ACCENT};
}}
QProgressBar {{
    background-color: #1c2128;
    border: 1px solid {BORDER};
    border-radius: 4px;
    text-align: center;
    color: {TEXT};
    font-size: 12px;
    height: 22px;
}}
QProgressBar::chunk {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #238636, stop:1 #58a6ff);
    border-radius: 3px;
}}
QTableWidget {{
    background-color: {CARD_BG};
    border: 1px solid {BORDER};
    border-radius: 6px;
    gridline-color: {BORDER};
    selection-background-color: #1f2937;
    font-size: 12px;
}}
QTableWidget::item {{
    padding: 6px;
    border-bottom: 1px solid #21262d;
}}
QHeaderView::section {{
    background-color: #161b22;
    color: {TEXT_DIM};
    border: none;
    border-bottom: 1px solid {BORDER};
    padding: 8px;
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
}}
QTabWidget::pane {{
    border: 1px solid {BORDER};
    border-radius: 8px;
    background-color: {CARD_BG};
}}
QTabBar::tab {{
    background-color: {DARK_BG};
    color: {TEXT_DIM};
    border: 1px solid {BORDER};
    border-bottom: none;
    padding: 10px 20px;
    margin-right: 2px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    font-weight: 600;
}}
QTabBar::tab:selected {{
    background-color: {CARD_BG};
    color: {ACCENT};
    border-color: {ACCENT};
}}
QScrollArea {{
    border: none;
    background: transparent;
}}
QScrollBar:vertical {{
    background: {DARK_BG};
    width: 8px;
    border-radius: 4px;
}}
QScrollBar::handle:vertical {{
    background: {BORDER};
    border-radius: 4px;
    min-height: 30px;
}}
QScrollBar::handle:vertical:hover {{
    background: {TEXT_DIM};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}
QTreeWidget {{
    background-color: {CARD_BG};
    border: 1px solid {BORDER};
    border-radius: 6px;
    font-size: 12px;
}}
QTreeWidget::item {{
    padding: 4px;
}}
QTreeWidget::item:selected {{
    background-color: #1f2937;
}}
QListWidget {{
    background-color: {CARD_BG};
    border: 1px solid {BORDER};
    border-radius: 6px;
}}
QListWidget::item {{
    padding: 10px;
    border-bottom: 1px solid #21262d;
}}
QListWidget::item:hover {{
    background-color: #1f2937;
}}
QListWidget::item:selected {{
    background-color: #1f2937;
    color: {ACCENT};
}}
QSplitter::handle {{
    background-color: {BORDER};
    width: 1px;
}}
"""


# ═══════════════════════════════════════════════════════════════
# Worker thread for background investigations
# ═══════════════════════════════════════════════════════════════

class InvestigationWorker(QThread):
    progress = pyqtSignal(int, str)  # percent, step description
    finished = pyqtSignal(object)    # Case object
    error = pyqtSignal(str)

    def __init__(self, device: DeviceInfo, mode: str, investigator: str):
        super().__init__()
        self.device = device
        self.mode = mode
        self.investigator = investigator

    def run(self):
        try:
            cfg = get_config()
            case = Case(device_info=self.device, mode=self.mode,
                        investigator=self.investigator)

            # Step 1: Backup
            self.progress.emit(5, "Creating forensic backup...")
            backup_svc = EvidenceBackup()
            case.backup = backup_svc.create_backup(
                self.device.mount_point, case.id)
            self.progress.emit(15, f"Backup complete — {case.backup.files_backed_up} files")

            # Step 2: File System Analysis
            self.progress.emit(20, "Analyzing file system...")
            findings = ForensicFindings()
            findings.file_system = FileAnalyzer().analyze(self.device.mount_point)
            self.progress.emit(35, f"Found {findings.file_system.total_files} files")

            # Step 3: Hashing
            self.progress.emit(40, "Hashing files for integrity...")
            hasher = FileHasher()
            paths = [f.full_path for f in findings.file_system.files[:500]]
            hashes = hasher.hash_files(paths)
            findings.integrity_hashes = {
                r["file"]: r["sha256"] for r in hashes
                if r["sha256"] != "ERROR"
            }
            self.progress.emit(50, f"Hashed {len(findings.integrity_hashes)} files")

            # Step 4: Artifact Extraction
            self.progress.emit(55, "Extracting forensic artifacts...")
            findings.artifacts = ArtifactExtractor().extract_all(
                self.device.mount_point)
            self.progress.emit(65, f"Extracted {findings.artifacts.total_artifacts} artifacts")

            # Step 5: Malware Detection
            self.progress.emit(68, "Scanning for malware indicators...")
            findings.malware = MalwareDetector().scan(self.device.mount_point)
            self.progress.emit(75, f"Malware scan: {findings.malware.risk_level}")

            # Step 6: Timeline
            self.progress.emit(78, "Building activity timeline...")
            findings.timeline = TimelineBuilder().build(
                findings.file_system, findings.artifacts)
            self.progress.emit(82, f"Timeline: {len(findings.timeline.events)} events")

            case.findings = findings

            # Step 7: LLM Interpretation
            self.progress.emit(85, "Running AI analysis...")
            llm = LLMInvestigator()
            interp = LLMInterpretation()
            fd = {}
            if findings.file_system:
                fd["file_system"] = {
                    "total_files": findings.file_system.total_files,
                    "suspicious": len(findings.file_system.suspicious_files),
                }
            if findings.malware:
                fd["malware"] = {
                    "risk_level": findings.malware.risk_level,
                    "indicators": len(findings.malware.indicators),
                }
            if findings.artifacts:
                fd["artifacts"] = {
                    "browser": len(findings.artifacts.browser_history),
                    "recent": len(findings.artifacts.recent_files),
                }
            interp.recommendations = llm.suggest_next_steps(fd)
            interp.summary = llm.generate_summary({
                "id": case.id,
                "device_info": self.device.to_dict(),
                "findings": fd,
            })
            interp.risk_assessment = (findings.malware.risk_level
                                      if findings.malware else "UNKNOWN")
            case.interpretation = interp
            self.progress.emit(90, "AI analysis complete")

            # Step 8: Report Generation
            self.progress.emit(92, "Generating reports...")
            reports_dir = cfg.get("reports_dir",
                                   os.path.join(os.path.expanduser("~"),
                                                ".servos", "reports"))
            os.makedirs(reports_dir, exist_ok=True)
            gen = ReportGenerator()
            txt_path = os.path.join(reports_dir, f"{case.id}_report.txt")
            gen.generate_txt(case, txt_path)
            json_path = os.path.join(reports_dir, f"{case.id}_report.json")
            gen.generate_json(case, json_path)
            try:
                pdf_path = os.path.join(reports_dir, f"{case.id}_report.pdf")
                gen.generate_pdf(case, pdf_path)
                case.report_path = pdf_path
            except Exception:
                case.report_path = txt_path

            csv_path = os.path.join(reports_dir, f"{case.id}_artifacts.csv")
            gen.generate_csv(case, csv_path)

            case.status = "completed"
            self.progress.emit(100, "Investigation complete!")

            # Save to DB
            self._save_to_db(case)

            self.finished.emit(case)

        except Exception as e:
            self.error.emit(f"{str(e)}\n\n{traceback.format_exc()}")

    @staticmethod
    def _save_to_db(case):
        try:
            session = get_session()
            record = CaseRecord(
                id=case.id, created_at=case.created_at,
                investigator=case.investigator, mode=case.mode,
                status=case.status, report_path=case.report_path or "",
                device_info_json=json.dumps(
                    case.device_info.to_dict() if case.device_info else {}),
                backup_json=json.dumps(
                    case.backup.to_dict() if case.backup else {}),
            )
            session.merge(record)
            session.commit()
            session.close()
        except Exception:
            pass


# ═══════════════════════════════════════════════════════════════
# Main Window
# ═══════════════════════════════════════════════════════════════

class ServosApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Servos — Offline AI Forensic Assistant")
        self.setMinimumSize(1200, 750)
        self.resize(1400, 850)

        ensure_dirs()
        init_db()

        self.current_case = None
        self.worker = None

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Sidebar
        sidebar = self._build_sidebar()
        main_layout.addWidget(sidebar)

        # Stacked pages
        self.pages = QStackedWidget()
        main_layout.addWidget(self.pages, 1)

        self.dashboard_page = self._build_dashboard()
        self.investigate_page = self._build_investigate()
        self.scan_page = self._build_scan()
        self.cases_page = self._build_cases()
        self.results_page = self._build_results()

        self.pages.addWidget(self.dashboard_page)     # 0
        self.pages.addWidget(self.investigate_page)    # 1
        self.pages.addWidget(self.scan_page)           # 2
        self.pages.addWidget(self.cases_page)          # 3
        self.pages.addWidget(self.results_page)        # 4

        self.pages.setCurrentIndex(0)
        self._refresh_dashboard()

    # ──────────────────────────────────────────────────────────
    # Sidebar
    # ──────────────────────────────────────────────────────────

    def _build_sidebar(self):
        sidebar = QFrame()
        sidebar.setFixedWidth(240)
        sidebar.setStyleSheet(f"""
            QFrame {{
                background-color: {CARD_BG};
                border-right: 1px solid {BORDER};
            }}
        """)
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(16, 20, 16, 16)
        layout.setSpacing(4)

        # Brand
        brand = QLabel("🛡️  SERVOS")
        brand.setFont(QFont("Segoe UI", 18, QFont.Weight.ExtraBold))
        brand.setStyleSheet(f"color: {ACCENT}; padding-bottom: 2px;")
        layout.addWidget(brand)

        tagline = QLabel("Forensics for the Rest of Us")
        tagline.setStyleSheet(f"color: {TEXT_DIM}; font-size: 10px; padding-bottom: 16px;")
        layout.addWidget(tagline)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"background-color: {BORDER}; max-height: 1px;")
        layout.addWidget(sep)
        layout.addSpacing(12)

        nav_items = [
            ("📊  Dashboard", 0),
            ("🔍  New Investigation", 1),
            ("⚡  Quick Scan", 2),
            ("📁  Past Cases", 3),
        ]
        self.nav_buttons = []
        for label, idx in nav_items:
            btn = QPushButton(label)
            btn.setStyleSheet(f"""
                QPushButton {{
                    text-align: left;
                    padding: 12px 16px;
                    border: none;
                    border-radius: 6px;
                    font-size: 13px;
                    font-weight: 500;
                }}
                QPushButton:hover {{
                    background-color: #1f2937;
                }}
            """)
            btn.clicked.connect(lambda checked, i=idx: self._nav_to(i))
            layout.addWidget(btn)
            self.nav_buttons.append(btn)

        layout.addStretch()

        # LLM status
        self.llm_label = QLabel("⚫  LLM: Checking...")
        self.llm_label.setStyleSheet(f"color: {TEXT_DIM}; font-size: 11px; padding: 8px;")
        layout.addWidget(self.llm_label)
        QTimer.singleShot(1000, self._check_llm)

        ver = QLabel("Servos v1.0.0 — Offline AI Forensic Assistant")
        ver.setStyleSheet(f"color: {TEXT_DIM}; font-size: 10px; padding: 4px 8px;")
        layout.addWidget(ver)

        return sidebar

    def _nav_to(self, idx):
        self.pages.setCurrentIndex(idx)
        for i, btn in enumerate(self.nav_buttons):
            if i == idx:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        text-align: left; padding: 12px 16px; border: none;
                        border-radius: 6px; font-size: 13px; font-weight: 600;
                        background-color: #1f2937; color: {ACCENT};
                        border-left: 3px solid {ACCENT};
                    }}
                """)
            else:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        text-align: left; padding: 12px 16px; border: none;
                        border-radius: 6px; font-size: 13px; font-weight: 500;
                    }}
                    QPushButton:hover {{ background-color: #1f2937; }}
                """)

        if idx == 0:
            self._refresh_dashboard()
        elif idx == 1:
            self._refresh_devices()
        elif idx == 3:
            self._refresh_cases()

    def _check_llm(self):
        llm = LLMInvestigator()
        if llm.is_available():
            self.llm_label.setText(f"🟢  LLM: {llm.model}")
            self.llm_label.setStyleSheet(f"color: {GREEN}; font-size: 11px; padding: 8px;")
        else:
            self.llm_label.setText("🟡  LLM: Offline (rule-based fallback)")
            self.llm_label.setStyleSheet(f"color: {ORANGE}; font-size: 11px; padding: 8px;")

    # ──────────────────────────────────────────────────────────
    # Dashboard
    # ──────────────────────────────────────────────────────────

    def _build_dashboard(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(20)

        title = QLabel("Dashboard")
        title.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        layout.addWidget(title)

        # Stats row
        stats_layout = QHBoxLayout()
        self.stat_cases = self._stat_card("📁", "0", "Total Cases")
        self.stat_devices = self._stat_card("💾", "0", "Devices")
        self.stat_completed = self._stat_card("✅", "0", "Completed")
        self.stat_active = self._stat_card("🔴", "0", "Active")
        stats_layout.addWidget(self.stat_cases)
        stats_layout.addWidget(self.stat_devices)
        stats_layout.addWidget(self.stat_completed)
        stats_layout.addWidget(self.stat_active)
        layout.addLayout(stats_layout)

        # Quick actions
        actions_group = QGroupBox("Quick Actions")
        actions_layout = QHBoxLayout(actions_group)
        btn_new = QPushButton("🔍  New Investigation")
        btn_new.setObjectName("primary")
        btn_new.clicked.connect(lambda: self._nav_to(1))
        actions_layout.addWidget(btn_new)

        btn_scan = QPushButton("⚡  Quick Scan")
        btn_scan.clicked.connect(lambda: self._nav_to(2))
        actions_layout.addWidget(btn_scan)

        btn_cases = QPushButton("📁  View Cases")
        btn_cases.clicked.connect(lambda: self._nav_to(3))
        actions_layout.addWidget(btn_cases)
        actions_layout.addStretch()
        layout.addWidget(actions_group)

        # Recent cases
        self.recent_table = QTableWidget(0, 4)
        self.recent_table.setHorizontalHeaderLabels(["Case ID", "Date", "Status", "Mode"])
        self.recent_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.recent_table.setMinimumHeight(200)
        self.recent_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        recent_group = QGroupBox("Recent Cases")
        rl = QVBoxLayout(recent_group)
        rl.addWidget(self.recent_table)
        layout.addWidget(recent_group)

        layout.addStretch()
        scroll.setWidget(page)
        return scroll

    def _stat_card(self, icon, value, label):
        card = QGroupBox()
        card.setStyleSheet(f"""
            QGroupBox {{
                background-color: {CARD_BG};
                border: 1px solid {BORDER};
                border-radius: 8px;
                padding: 16px;
            }}
        """)
        vl = QVBoxLayout(card)
        vl.setSpacing(4)
        ic = QLabel(icon)
        ic.setFont(QFont("Segoe UI", 22))
        vl.addWidget(ic)
        val_label = QLabel(value)
        val_label.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        val_label.setStyleSheet(f"color: {ACCENT};")
        val_label.setObjectName("statValue")
        vl.addWidget(val_label)
        desc = QLabel(label)
        desc.setStyleSheet(f"color: {TEXT_DIM}; font-size: 12px;")
        vl.addWidget(desc)
        return card

    def _refresh_dashboard(self):
        try:
            svc = USBDetectionService()
            devs = svc.detect_devices()
            session = get_session()
            records = session.query(CaseRecord).order_by(
                CaseRecord.created_at.desc()).limit(20).all()
            completed = [r for r in records if r.status == "completed"]
            active = [r for r in records if r.status == "active"]

            self.stat_cases.findChild(QLabel, "statValue").setText(str(len(records)))
            self.stat_devices.findChild(QLabel, "statValue").setText(str(len(devs)))
            self.stat_completed.findChild(QLabel, "statValue").setText(str(len(completed)))
            self.stat_active.findChild(QLabel, "statValue").setText(str(len(active)))

            self.recent_table.setRowCount(min(len(records), 10))
            for i, r in enumerate(records[:10]):
                self.recent_table.setItem(i, 0, QTableWidgetItem(r.id))
                self.recent_table.setItem(i, 1, QTableWidgetItem((r.created_at or "")[:19]))
                self.recent_table.setItem(i, 2, QTableWidgetItem(r.status))
                self.recent_table.setItem(i, 3, QTableWidgetItem(r.mode))
            session.close()
        except Exception:
            pass

    # ──────────────────────────────────────────────────────────
    # New Investigation
    # ──────────────────────────────────────────────────────────

    def _build_investigate(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(20)

        title = QLabel("🔍  New Investigation")
        title.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        layout.addWidget(title)

        # Target selection
        target_group = QGroupBox("Step 1 — Select Target")
        tl = QVBoxLayout(target_group)

        self.device_list = QListWidget()
        self.device_list.setMinimumHeight(120)
        tl.addWidget(self.device_list)

        path_row = QHBoxLayout()
        path_row.addWidget(QLabel("Or enter path:"))
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("e.g. D:\\ or E:\\SuspiciousUSB")
        path_row.addWidget(self.path_input, 1)
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self._browse_path)
        path_row.addWidget(browse_btn)
        tl.addLayout(path_row)

        refresh_btn = QPushButton("🔄  Refresh Devices")
        refresh_btn.clicked.connect(self._refresh_devices)
        tl.addWidget(refresh_btn)
        layout.addWidget(target_group)

        # Mode
        mode_group = QGroupBox("Step 2 — Investigation Mode")
        ml = QVBoxLayout(mode_group)
        self.mode_combo = QComboBox()
        self.mode_combo.addItems([
            "Full Automation – Servos handles everything",
            "Hybrid – Approve each step",
            "Manual – Guided checklists",
        ])
        ml.addWidget(self.mode_combo)
        layout.addWidget(mode_group)

        # Investigator
        inv_group = QGroupBox("Step 3 — Investigator")
        il = QVBoxLayout(inv_group)
        self.investigator_input = QLineEdit("Investigator")
        self.investigator_input.setPlaceholderText("Your name")
        il.addWidget(self.investigator_input)
        layout.addWidget(inv_group)

        # Progress area
        self.inv_progress_group = QGroupBox("Investigation Progress")
        pl = QVBoxLayout(self.inv_progress_group)
        self.inv_status_label = QLabel("Ready to start")
        self.inv_status_label.setStyleSheet(f"color: {TEXT_DIM}; font-size: 13px;")
        pl.addWidget(self.inv_status_label)
        self.inv_progress_bar = QProgressBar()
        self.inv_progress_bar.setRange(0, 100)
        self.inv_progress_bar.setValue(0)
        pl.addWidget(self.inv_progress_bar)
        self.inv_log = QTextEdit()
        self.inv_log.setReadOnly(True)
        self.inv_log.setMaximumHeight(150)
        self.inv_log.setStyleSheet(f"font-family: 'Consolas', monospace; font-size: 11px; background-color: #0d1117;")
        pl.addWidget(self.inv_log)
        layout.addWidget(self.inv_progress_group)

        # Start button
        self.start_btn = QPushButton("🚀  Start Investigation")
        self.start_btn.setObjectName("primary")
        self.start_btn.setMinimumHeight(48)
        self.start_btn.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        self.start_btn.clicked.connect(self._start_investigation)
        layout.addWidget(self.start_btn)

        layout.addStretch()
        scroll.setWidget(page)
        return scroll

    def _browse_path(self):
        path = QFileDialog.getExistingDirectory(self, "Select Target Directory")
        if path:
            self.path_input.setText(path)

    def _refresh_devices(self):
        self.device_list.clear()
        svc = USBDetectionService()
        devices = svc.detect_devices()
        self._devices = devices
        for d in devices:
            removable = "🔌 REMOVABLE" if d.is_removable else "💾 Fixed"
            item = QListWidgetItem(
                f"{d.mount_point}  —  {d.name}  |  {d.capacity_human}  |  {d.filesystem}  |  {removable}"
            )
            self.device_list.addItem(item)

    def _start_investigation(self):
        # Determine target
        manual_path = self.path_input.text().strip()
        selected_idx = self.device_list.currentRow()

        if manual_path and os.path.exists(manual_path):
            import psutil
            device = DeviceInfo(
                path=manual_path, name=manual_path,
                mount_point=manual_path,
            )
            try:
                usage = psutil.disk_usage(manual_path)
                device.capacity_bytes = usage.total
            except Exception:
                pass
        elif selected_idx >= 0 and hasattr(self, '_devices'):
            device = self._devices[selected_idx]
        else:
            QMessageBox.warning(self, "No Target",
                                "Select a device or enter a valid path.")
            return

        mode_map = {0: "full_auto", 1: "hybrid", 2: "manual"}
        mode = mode_map.get(self.mode_combo.currentIndex(), "full_auto")
        investigator = self.investigator_input.text() or "Investigator"

        # Reset UI
        self.inv_progress_bar.setValue(0)
        self.inv_log.clear()
        self.inv_status_label.setText("Starting...")
        self.inv_status_label.setStyleSheet(f"color: {ACCENT}; font-size: 13px;")
        self.start_btn.setEnabled(False)
        self.start_btn.setText("⏳  Running...")

        # Launch worker thread
        self.worker = InvestigationWorker(device, mode, investigator)
        self.worker.progress.connect(self._on_progress)
        self.worker.finished.connect(self._on_finished)
        self.worker.error.connect(self._on_error)
        self.worker.start()

    def _on_progress(self, percent, step):
        self.inv_progress_bar.setValue(percent)
        self.inv_status_label.setText(step)
        self.inv_log.append(f"[{percent:3d}%]  {step}")

    def _on_finished(self, case):
        self.current_case = case
        self.inv_status_label.setText("✅  Investigation complete!")
        self.inv_status_label.setStyleSheet(f"color: {GREEN}; font-size: 13px; font-weight: bold;")
        self.start_btn.setEnabled(True)
        self.start_btn.setText("🚀  Start Investigation")
        self.inv_log.append(f"\n✅  Case {case.id} completed.")
        self.inv_log.append(f"📄  Report: {case.report_path}")

        # Populate results page and navigate
        self._populate_results(case)
        self.pages.setCurrentIndex(4)

    def _on_error(self, msg):
        self.inv_status_label.setText("❌  Error occurred")
        self.inv_status_label.setStyleSheet(f"color: {RED}; font-size: 13px;")
        self.inv_log.append(f"\n❌  ERROR:\n{msg}")
        self.start_btn.setEnabled(True)
        self.start_btn.setText("🚀  Start Investigation")
        QMessageBox.critical(self, "Investigation Error", msg[:500])

    def _save_case_notes(self):
        """Write the current notes field back to the database."""
        if not hasattr(self, 'current_case') or self.current_case is None:
            return
        text = self.notes_edit.toPlainText()
        self.current_case.notes = text
        try:
            sess = get_session()
            rec = sess.query(CaseRecord).get(self.current_case.id)
            if rec:
                rec.notes = text
                sess.commit()
            sess.close()
        except Exception:
            pass

    # ──────────────────────────────────────────────────────────
    # Quick Scan
    # ──────────────────────────────────────────────────────────

    def _build_scan(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(20)

        title = QLabel("⚡  Quick Scan")
        title.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        layout.addWidget(title)

        # Path input
        input_group = QGroupBox("Target Path")
        il = QHBoxLayout(input_group)
        self.scan_path_input = QLineEdit()
        self.scan_path_input.setPlaceholderText("Enter path to scan...")
        il.addWidget(self.scan_path_input, 1)
        browse = QPushButton("Browse...")
        browse.clicked.connect(lambda: self.scan_path_input.setText(
            QFileDialog.getExistingDirectory(self, "Select Directory") or
            self.scan_path_input.text()))
        il.addWidget(browse)
        scan_btn = QPushButton("⚡  Scan")
        scan_btn.setObjectName("primary")
        scan_btn.clicked.connect(self._run_scan)
        il.addWidget(scan_btn)
        layout.addWidget(input_group)

        # Results
        self.scan_results = QTextEdit()
        self.scan_results.setReadOnly(True)
        self.scan_results.setStyleSheet(f"font-family: 'Consolas', monospace; font-size: 12px; background: #0d1117; padding: 12px;")
        self.scan_results.setMinimumHeight(400)
        layout.addWidget(self.scan_results)

        layout.addStretch()
        scroll.setWidget(page)
        return scroll

    def _run_scan(self):
        path = self.scan_path_input.text().strip()
        if not path or not os.path.exists(path):
            QMessageBox.warning(self, "Invalid Path", "Enter a valid directory.")
            return

        self.scan_results.clear()
        self.scan_results.append(f"Scanning {path}...\n")
        QApplication.processEvents()

        try:
            # File system
            fa = FileAnalyzer()
            analysis = fa.analyze(path)
            self.scan_results.append(f"═══ FILE SYSTEM ═══")
            self.scan_results.append(f"  Files: {analysis.total_files}")
            self.scan_results.append(f"  Directories: {analysis.total_dirs}")
            self.scan_results.append(f"  Total Size: {analysis.total_size_bytes:,} bytes")
            self.scan_results.append(f"  Hidden: {analysis.hidden_files}")
            self.scan_results.append(f"  Suspicious: {len(analysis.suspicious_files)}")
            self.scan_results.append("")

            if analysis.file_type_counts:
                self.scan_results.append("  File Types:")
                for ext, count in list(analysis.file_type_counts.items())[:15]:
                    self.scan_results.append(f"    {ext:15s} {count}")
                self.scan_results.append("")
            QApplication.processEvents()

            if analysis.suspicious_files:
                self.scan_results.append(f"⚠️  SUSPICIOUS FILES ({len(analysis.suspicious_files)}):")
                for sf in analysis.suspicious_files[:20]:
                    self.scan_results.append(f"  • {sf.filename}")
                    self.scan_results.append(f"    Reason: {sf.suspicious_reason}")
                    self.scan_results.append(f"    Entropy: {sf.entropy:.2f}  |  Size: {sf.file_size:,}")
                    self.scan_results.append("")
            QApplication.processEvents()

            # Malware
            md = MalwareDetector()
            result = md.scan(path)
            self.scan_results.append(f"═══ MALWARE SCAN ═══")
            self.scan_results.append(f"  Risk Level: {result.risk_level}")
            self.scan_results.append(f"  Files Scanned: {result.files_scanned}")
            self.scan_results.append(f"  Suspicious: {result.suspicious_count}")
            self.scan_results.append(f"  Clean: {result.clean_count}")
            self.scan_results.append(f"  Indicators: {len(result.indicators)}")
            self.scan_results.append("")

            if result.indicators:
                for ind in result.indicators[:15]:
                    sev = ind.severity.upper()
                    self.scan_results.append(f"  [{sev}] {ind.rule_name}")
                    self.scan_results.append(f"    File: {os.path.basename(ind.file_path)}")
                    self.scan_results.append(f"    {ind.description}")
                    self.scan_results.append("")

            self.scan_results.append("✅  Scan complete.")

        except Exception as e:
            self.scan_results.append(f"\n❌  Error: {e}")

    # ──────────────────────────────────────────────────────────
    # Past Cases
    # ──────────────────────────────────────────────────────────

    def _build_cases(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(20)

        title = QLabel("📁  Past Cases")
        title.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        layout.addWidget(title)

        self.cases_table = QTableWidget(0, 5)
        self.cases_table.setHorizontalHeaderLabels(
            ["Case ID", "Date", "Device", "Mode", "Status"])
        self.cases_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch)
        self.cases_table.setMinimumHeight(300)
        self.cases_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.cases_table.doubleClicked.connect(self._open_case_report)
        layout.addWidget(self.cases_table)

        btn_row = QHBoxLayout()
        refresh = QPushButton("🔄  Refresh")
        refresh.clicked.connect(self._refresh_cases)
        btn_row.addWidget(refresh)
        open_btn = QPushButton("📄  Open Report")
        open_btn.clicked.connect(self._open_case_report)
        btn_row.addWidget(open_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        layout.addStretch()
        scroll.setWidget(page)
        return scroll

    def _refresh_cases(self):
        try:
            session = get_session()
            records = session.query(CaseRecord).order_by(
                CaseRecord.created_at.desc()).limit(50).all()
            self.cases_table.setRowCount(len(records))
            self._case_records = records
            for i, r in enumerate(records):
                self.cases_table.setItem(i, 0, QTableWidgetItem(r.id))
                self.cases_table.setItem(i, 1, QTableWidgetItem((r.created_at or "")[:19]))
                dev = json.loads(r.device_info_json) if r.device_info_json else {}
                self.cases_table.setItem(i, 2, QTableWidgetItem(dev.get("name", "—")))
                self.cases_table.setItem(i, 3, QTableWidgetItem(r.mode))
                self.cases_table.setItem(i, 4, QTableWidgetItem(r.status))
            session.close()
        except Exception:
            pass

    def _open_case_report(self):
        row = self.cases_table.currentRow()
        if row < 0 or not hasattr(self, '_case_records'):
            return
        record = self._case_records[row]
        if record.report_path and os.path.exists(record.report_path):
            os.startfile(record.report_path)
        else:
            # Try to find report by case ID
            cfg = get_config()
            rd = cfg.get("reports_dir", "")
            for ext in ["pdf", "txt", "json"]:
                p = os.path.join(rd, f"{record.id}_report.{ext}")
                if os.path.exists(p):
                    os.startfile(p)
                    return
            QMessageBox.information(self, "No Report",
                                     f"No report found for {record.id}")

    # ──────────────────────────────────────────────────────────
    # Results Page (shown after investigation completes)
    # ──────────────────────────────────────────────────────────

    def _build_results(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        page = QWidget()
        self.results_layout = QVBoxLayout(page)
        self.results_layout.setContentsMargins(32, 28, 32, 28)
        self.results_layout.setSpacing(16)
        scroll.setWidget(page)
        return scroll

    def _populate_results(self, case: Case):
        # Clear previous
        while self.results_layout.count():
            item = self.results_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        layout = self.results_layout

        # Header
        header = QLabel(f"📋  Investigation Results — {case.id}")
        header.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        layout.addWidget(header)

        # Risk assessment
        risk = "UNKNOWN"
        if case.interpretation:
            risk = case.interpretation.risk_assessment
        elif case.findings and case.findings.malware:
            risk = case.findings.malware.risk_level

        risk_colors = {"LOW": GREEN, "MEDIUM": YELLOW, "HIGH": ORANGE, "CRITICAL": RED}
        rc = risk_colors.get(risk, TEXT_DIM)
        risk_label = QLabel(f"Risk Level:  {risk}")
        risk_label.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        risk_label.setStyleSheet(f"color: {rc}; padding: 12px; background: {CARD_BG}; border: 2px solid {rc}; border-radius: 8px;")
        risk_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(risk_label)

        # investigator notes editor with auto-save
        notes_group = QGroupBox("Investigator Notes")
        nlay = QVBoxLayout(notes_group)
        self.notes_edit = QTextEdit()
        self.notes_edit.setPlainText(case.notes or "")
        self.notes_edit.setStyleSheet("background-color: #0d1117;")
        nlay.addWidget(self.notes_edit)
        layout.addWidget(notes_group)

        self.notes_timer = QTimer(self)
        self.notes_timer.setSingleShot(True)
        self.notes_edit.textChanged.connect(lambda: self.notes_timer.start(2000))
        self.notes_timer.timeout.connect(self._save_case_notes)

        # risk dashboard widget
        self.risk_dashboard = RiskDashboard()
        # wire export button to open existing report
        self.risk_dashboard.export_requested.connect(lambda: os.startfile(case.report_path) if case.report_path else None)
        layout.addWidget(self.risk_dashboard)

        # Tabs
        tabs = QTabWidget()

        # Summary tab
        summary_w = QTextEdit()
        summary_w.setReadOnly(True)
        summary_w.setStyleSheet("font-size: 13px; padding: 12px; background: #0d1117;")
        summary_text = ""
        if case.interpretation:
            summary_text += f"AI Summary:\n{case.interpretation.summary}\n\n"
            if case.interpretation.recommendations:
                summary_text += "Recommendations:\n"
                for r in case.interpretation.recommendations:
                    summary_text += f"  • {r}\n"
                summary_text += "\n"
        summary_text += f"Case ID: {case.id}\n"
        summary_text += f"Date: {case.created_at}\n"
        summary_text += f"Investigator: {case.investigator}\n"
        summary_text += f"Mode: {case.mode}\n"
        summary_text += f"Status: {case.status}\n"
        if case.device_info:
            summary_text += f"\nDevice: {case.device_info.name}\n"
            summary_text += f"Path: {case.device_info.path}\n"
            summary_text += f"Capacity: {case.device_info.capacity_human}\n"
        summary_w.setText(summary_text)
        tabs.addTab(summary_w, "📊 Summary")

        # Files tab
        if case.findings and case.findings.file_system:
            fs = case.findings.file_system
            files_w = QTableWidget(
                min(len(fs.suspicious_files), 50), 4)
            files_w.setHorizontalHeaderLabels(["File", "Reason", "Entropy", "Size"])
            files_w.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            files_w.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
            for i, f in enumerate(fs.suspicious_files[:50]):
                files_w.setItem(i, 0, QTableWidgetItem(f.filename))
                files_w.setItem(i, 1, QTableWidgetItem(f.suspicious_reason))
                files_w.setItem(i, 2, QTableWidgetItem(f"{f.entropy:.2f}"))
                files_w.setItem(i, 3, QTableWidgetItem(f"{f.file_size:,}"))
            tabs.addTab(files_w,
                        f"⚠️ Suspicious ({len(fs.suspicious_files)})")

        # Malware tab
        if case.findings and case.findings.malware:
            mal = case.findings.malware
            mal_w = QTableWidget(len(mal.indicators), 4)
            mal_w.setHorizontalHeaderLabels(["Severity", "Rule", "File", "Description"])
            mal_w.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            mal_w.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
            for i, ind in enumerate(mal.indicators):
                sev = QTableWidgetItem(ind.severity.upper())
                if ind.severity in ("critical", "high"):
                    sev.setForeground(QColor(RED))
                elif ind.severity == "medium":
                    sev.setForeground(QColor(ORANGE))
                mal_w.setItem(i, 0, sev)
                mal_w.setItem(i, 1, QTableWidgetItem(ind.rule_name))
                mal_w.setItem(i, 2, QTableWidgetItem(os.path.basename(ind.file_path)))
                mal_w.setItem(i, 3, QTableWidgetItem(ind.description))
            tabs.addTab(mal_w,
                        f"🦠 Malware ({len(mal.indicators)})")

        # Artifacts tab
        if case.findings and case.findings.artifacts:
            art = case.findings.artifacts
            art_w = QTableWidget(min(len(art.all_artifacts()), 100), 4)
            art_w.setHorizontalHeaderLabels(["Type", "Timestamp", "Description", "Score"])
            art_w.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            art_w.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
            for i, a in enumerate(art.all_artifacts()[:100]):
                art_w.setItem(i, 0, QTableWidgetItem(a.artifact_type))
                art_w.setItem(i, 1, QTableWidgetItem((a.timestamp or "")[:19]))
                art_w.setItem(i, 2, QTableWidgetItem(a.description[:100]))
                art_w.setItem(i, 3, QTableWidgetItem(f"{a.suspicious_score:.2f}"))
            tabs.addTab(art_w,
                        f"🔎 Artifacts ({art.total_artifacts})")

        # Timeline tab
        if case.findings and case.findings.timeline:
            tl = case.findings.timeline
            tb = TimelineBuilder()
            tl_text = tb.format_ascii_timeline(tl, max_events=50)
            tl_w = QTextEdit()
            tl_w.setReadOnly(True)
            tl_w.setStyleSheet("font-family: 'Consolas', monospace; font-size: 11px; background: #0d1117;")
            tl_w.setText(tl_text)
            tabs.addTab(tl_w,
                        f"📅 Timeline ({len(tl.events)})")

        # Chain of Custody tab
        if case.backup:
            loc_w = QTextEdit()
            loc_w.setReadOnly(True)
            loc_w.setStyleSheet("font-family: 'Consolas', monospace; font-size: 12px; background: #0d1117;")
            loc_text = f"""CHAIN OF CUSTODY
═══════════════════════════════════════════
Backup Path:     {case.backup.backup_path}
Files Backed Up: {case.backup.files_backed_up}
Size:            {case.backup.size_bytes:,} bytes
Created:         {case.backup.created_at}
MD5:             {case.backup.hash_md5}
SHA-256:         {case.backup.hash_sha256}
═══════════════════════════════════════════"""
            loc_w.setText(loc_text)
            tabs.addTab(loc_w, "🔒 Chain of Custody")

        layout.addWidget(tabs)

        # Action buttons
        btn_row = QHBoxLayout()
        if case.report_path and os.path.exists(case.report_path):
            open_btn = QPushButton("📄  Open Report")
            open_btn.setObjectName("primary")
            open_btn.clicked.connect(lambda: os.startfile(case.report_path))
            btn_row.addWidget(open_btn)

        cfg = get_config()
        rd = cfg.get("reports_dir", "")
        for fmt, icon in [("txt", "📝"), ("json", "📋"), ("pdf", "📕")]:
            p = os.path.join(rd, f"{case.id}_report.{fmt}")
            if os.path.exists(p):
                b = QPushButton(f"{icon}  {fmt.upper()}")
                b.clicked.connect(lambda checked, path=p: os.startfile(path))
                btn_row.addWidget(b)

        back_btn = QPushButton("← Back to Dashboard")
        back_btn.clicked.connect(lambda: self._nav_to(0))
        btn_row.addWidget(back_btn)
        btn_row.addStretch()

        btn_widget = QWidget()
        btn_widget.setLayout(btn_row)
        layout.addWidget(btn_widget)

        # populate risk dashboard data (after tabs built)
        try:
            top = []
            if case.findings and getattr(case.findings, 'threat_summary', None):
                top = case.findings.threat_summary.top_threats
            self.risk_dashboard.update(
                case,
                top_threats=top,
                anomalies=(case.findings.timeline.anomalies if case.findings and case.findings.timeline else []),
                itact=(case.findings.it_act_suggestions if hasattr(case.findings, 'it_act_suggestions') else []),
                log_threats=(case.findings.log_threats if hasattr(case.findings, 'log_threats') else []),
                deleted_exes=(case.findings.deleted_files if hasattr(case.findings, 'deleted_files') else [])
            )
        except Exception:
            pass

        layout.addStretch()


# ═══════════════════════════════════════════════════════════════
# Entry point
# ═══════════════════════════════════════════════════════════════

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(STYLESHEET)

    # Dark palette
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(DARK_BG))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(TEXT))
    palette.setColor(QPalette.ColorRole.Base, QColor(DARK_BG))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(CARD_BG))
    palette.setColor(QPalette.ColorRole.Text, QColor(TEXT))
    palette.setColor(QPalette.ColorRole.Button, QColor(CARD_BG))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(TEXT))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(ACCENT))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))
    app.setPalette(palette)

    window = ServosApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

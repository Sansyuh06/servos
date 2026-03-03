"""
Servos – Enterprise Main Window.
Professional forensic workstation with 7 pages.
"""

import os
import sys
import json
import shutil
import subprocess
import hashlib
from datetime import datetime

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QStackedWidget, QPushButton, QLabel, QListWidget, QListWidgetItem,
    QTextEdit, QPlainTextEdit, QLineEdit, QComboBox, QProgressBar,
    QFileDialog, QMessageBox, QGroupBox, QScrollArea, QFrame,
    QTableWidget, QTableWidgetItem, QHeaderView, QTabWidget,
    QSpacerItem, QSizePolicy, QGridLayout,
)
from PyQt6.QtCore import Qt, QTimer, QSize
from PyQt6.QtGui import QFont, QPalette, QColor

from servos.gui.theme import (
    STYLESHEET, BG_PRIMARY, BG_SURFACE, BG_CARD, BG_ELEVATED,
    BORDER, CYAN, GREEN, RED, ORANGE, YELLOW, TEXT, TEXT_SEC, TEXT_DIM,
)
from servos.gui.workers import InvestigationWorker, ScanWorker, DeviceRefreshWorker
from servos.gui.widgets import BentoCard, TerminalViewer, ToastNotification, StatusPill
from servos.config import get_config, save_config, ensure_dirs
from servos.models.schema import (
    DeviceInfo, Case, init_db, get_session, CaseRecord,
)
from servos.detection.usb_monitor import USBDetectionService
from servos.llm.investigator import LLMInvestigator
from servos.forensics.timeline import TimelineBuilder
from servos.playbooks.engine import PlaybookEngine


def _sep():
    """Horizontal separator."""
    f = QFrame()
    f.setFrameShape(QFrame.Shape.HLine)
    f.setProperty("cssClass", "separator")
    return f


def _label(text, css_class=None, **kwargs):
    lbl = QLabel(text)
    if css_class:
        lbl.setProperty("cssClass", css_class)
    for k, v in kwargs.items():
        if k == "align":
            lbl.setAlignment(v)
        elif k == "wrap":
            lbl.setWordWrap(v)
    return lbl


class ServosMainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Servos — Offline AI Forensic Assistant")
        self.setMinimumSize(1280, 800)
        self.resize(1440, 900)

        ensure_dirs()
        init_db()

        self.current_case = None
        self.worker = None
        self._devices = []

        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._build_sidebar())

        self.pages = QStackedWidget()
        root.addWidget(self.pages, 1)

        self.pages.addWidget(self._build_dashboard())     # 0
        self.pages.addWidget(self._build_investigate())    # 1
        self.pages.addWidget(self._build_scan())           # 2
        self.pages.addWidget(self._build_cases())          # 3
        self.pages.addWidget(self._build_results())        # 4
        self.pages.addWidget(self._build_playbooks())      # 5
        self.pages.addWidget(self._build_settings())       # 6
        self.pages.addWidget(self._build_automate())       # 7

        self._nav_to(0)
        QTimer.singleShot(500, self._check_llm)

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Sidebar
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def _build_sidebar(self):
        sidebar = QFrame()
        sidebar.setFixedWidth(260)
        sidebar.setStyleSheet(
            f"QFrame {{ background: {BG_SURFACE}; "
            f"border-right: 1px solid {BORDER}; }}")
        lay = QVBoxLayout(sidebar)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        # Brand
        brand_w = QWidget()
        brand_w.setStyleSheet(f"background: transparent;")
        bl = QVBoxLayout(brand_w)
        bl.setContentsMargins(24, 24, 24, 20)

        name = QLabel("⚔️  SERVOS")
        name.setFont(QFont("Segoe UI", 20, QFont.Weight.ExtraBold))
        name.setStyleSheet(f"color: {CYAN}; background: transparent;")
        bl.addWidget(name)

        tag = QLabel("Offline AI Forensic Assistant")
        tag.setStyleSheet(
            f"color: {TEXT_DIM}; font-size: 10px; "
            f"letter-spacing: 0.8px; background: transparent;")
        bl.addWidget(tag)
        lay.addWidget(brand_w)

        lay.addWidget(_sep())

        # Nav items
        nav_data = [
            ("📊  Dashboard",          0),
            ("🔍  New Investigation",   1),
            ("⚡  Quick Scan",          2),
            ("📁  Case Management",     3),
            ("🤖  Automate Task",       7),
            ("📋  Playbooks",           5),
            ("⚙️  Settings",            6),
        ]
        self.nav_btns = []
        nav_w = QWidget()
        nav_w.setStyleSheet("background: transparent;")
        nl = QVBoxLayout(nav_w)
        nl.setContentsMargins(12, 16, 12, 8)
        nl.setSpacing(2)

        for label, idx in nav_data:
            btn = QPushButton(label)
            btn.setProperty("cssClass", "nav")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda _, i=idx: self._nav_to(i))
            nl.addWidget(btn)
            self.nav_btns.append((btn, idx))

        lay.addWidget(nav_w)
        lay.addStretch()

        # LLM status
        status_w = QWidget()
        status_w.setStyleSheet("background: transparent;")
        sl = QVBoxLayout(status_w)
        sl.setContentsMargins(20, 8, 20, 16)

        lay.addWidget(_sep())

        self.llm_label = QLabel("⚫  LLM: Checking…")
        self.llm_label.setStyleSheet(
            f"color: {TEXT_DIM}; font-size: 11px; "
            f"padding: 4px; background: transparent;")
        sl.addWidget(self.llm_label)

        ver = QLabel("v1.0.0  •  CyberHack V4")
        ver.setStyleSheet(
            f"color: {TEXT_DIM}; font-size: 10px; background: transparent;")
        sl.addWidget(ver)
        lay.addWidget(status_w)

        return sidebar

    def _nav_to(self, idx):
        self.pages.setCurrentIndex(idx)
        for btn, bidx in self.nav_btns:
            btn.setProperty("cssClass",
                            "navActive" if bidx == idx else "nav")
            btn.style().unpolish(btn)
            btn.style().polish(btn)

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
            self.llm_label.setStyleSheet(
                f"color: {GREEN}; font-size: 11px; "
                f"background: transparent;")
        else:
            self.llm_label.setText("🟡  LLM: Offline (rule-based)")
            self.llm_label.setStyleSheet(
                f"color: {ORANGE}; font-size: 11px; "
                f"background: transparent;")

    def _show_toast(self, msg, level="info"):
        toast = ToastNotification(msg, level, parent=self)
        toast.show_toast()

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Page 0: Dashboard
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def _build_dashboard(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(36, 32, 36, 32)
        lay.setSpacing(24)

        lay.addWidget(_label("Dashboard", "title"))
        lay.addWidget(_label(
            "Real-time overview of your forensic operations", "subtitle"))

        # Metrics row
        metrics = QHBoxLayout()
        metrics.setSpacing(16)
        self._m_cases = BentoCard("📁", "0", "TOTAL CASES", CYAN)
        self._m_devices = BentoCard("💾", "0", "DEVICES", BLUE)
        self._m_done = BentoCard("✅", "0", "COMPLETED", GREEN)
        self._m_active = BentoCard("🛡️", "0", "ACTIVE", PURPLE)
        for w in [self._m_cases, self._m_devices, self._m_done, self._m_active]:
            metrics.addWidget(w)
        lay.addLayout(metrics)

        # Two-column area
        cols = QHBoxLayout()
        cols.setSpacing(20)

        # Recent cases
        left = QGroupBox("Recent Cases")
        ll = QVBoxLayout(left)
        self.recent_table = QTableWidget(0, 4)
        self.recent_table.setHorizontalHeaderLabels(
            ["Case ID", "Date", "Status", "Mode"])
        self.recent_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch)
        self.recent_table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers)
        self.recent_table.setAlternatingRowColors(True)
        ll.addWidget(self.recent_table)
        cols.addWidget(left, 1)

        # Connected devices
        right = QGroupBox("Connected Devices")
        rl = QVBoxLayout(right)
        self.dash_devices = QTableWidget(0, 4)
        self.dash_devices.setHorizontalHeaderLabels(
            ["Device", "Mount", "FS", "Capacity"])
        self.dash_devices.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch)
        self.dash_devices.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers)
        self.dash_devices.setAlternatingRowColors(True)
        rl.addWidget(self.dash_devices)
        cols.addWidget(right, 1)
        lay.addLayout(cols)

        # Quick actions
        actions = QGroupBox("Quick Actions")
        al = QHBoxLayout(actions)
        for text, idx, css in [
            ("🔍  New Investigation", 1, "primary"),
            ("⚡  Quick Scan", 2, ""),
            ("📁  View Cases", 3, ""),
            ("📋  Playbooks", 5, ""),
        ]:
            b = QPushButton(text)
            if css:
                b.setProperty("cssClass", css)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.clicked.connect(lambda _, i=idx: self._nav_to(i))
            al.addWidget(b)
        al.addStretch()
        lay.addWidget(actions)

        lay.addStretch()
        scroll.setWidget(page)
        return scroll

    def _metric_card(self, icon, value, label):
        card = QGroupBox()
        card.setMinimumHeight(120)
        vl = QVBoxLayout(card)
        vl.setSpacing(4)
        ic = QLabel(icon)
        ic.setFont(QFont("Segoe UI", 22))
        ic.setStyleSheet("background: transparent;")
        vl.addWidget(ic)
        val = QLabel(value)
        val.setProperty("cssClass", "metric")
        val.setObjectName("val")
        val.setStyleSheet(f"background: transparent; color: {CYAN};")
        vl.addWidget(val)
        desc = QLabel(label)
        desc.setProperty("cssClass", "metricLabel")
        desc.setStyleSheet(f"background: transparent; color: {TEXT_DIM};")
        vl.addWidget(desc)
        return card

    def _refresh_dashboard(self):
        try:
            svc = USBDetectionService()
            devs = svc.detect_devices()
            s = get_session()
            recs = s.query(CaseRecord).order_by(
                CaseRecord.created_at.desc()).limit(20).all()
            done = sum(1 for r in recs if r.status == "completed")
            active = sum(1 for r in recs if r.status == "active")

            self._m_cases.set_value(str(len(recs)))
            self._m_devices.set_value(str(len(devs)))
            self._m_done.set_value(str(done))
            self._m_active.set_value(str(active))

            self.recent_table.setRowCount(min(len(recs), 10))
            for i, r in enumerate(recs[:10]):
                self.recent_table.setItem(i, 0, QTableWidgetItem(r.id))
                self.recent_table.setItem(i, 1, QTableWidgetItem(
                    (r.created_at or "")[:19]))
                si = QTableWidgetItem(r.status)
                si.setForeground(QColor(
                    GREEN if r.status == "completed" else
                    CYAN if r.status == "active" else YELLOW))
                self.recent_table.setItem(i, 2, si)
                self.recent_table.setItem(i, 3, QTableWidgetItem(r.mode))

            self.dash_devices.setRowCount(len(devs))
            for i, d in enumerate(devs):
                self.dash_devices.setItem(i, 0, QTableWidgetItem(
                    d.name or d.path))
                self.dash_devices.setItem(i, 1, QTableWidgetItem(
                    d.mount_point))
                self.dash_devices.setItem(i, 2, QTableWidgetItem(
                    d.filesystem))
                self.dash_devices.setItem(i, 3, QTableWidgetItem(
                    d.capacity_human))
            s.close()
        except Exception:
            pass

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Page 1: New Investigation
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def _build_investigate(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(36, 32, 36, 32)
        lay.setSpacing(20)

        lay.addWidget(_label("🔍  New Investigation", "title"))
        lay.addWidget(_label(
            "Select a target device, choose a mode, and run "
            "a complete forensic analysis", "subtitle"))

        # Step 1: Target
        g1 = QGroupBox("STEP 1 — Select Target Device")
        l1 = QVBoxLayout(g1)

        self.device_list = QListWidget()
        self.device_list.setMinimumHeight(100)
        l1.addWidget(self.device_list)

        row = QHBoxLayout()
        row.addWidget(QLabel("Manual path:"))
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText(
            "Enter directory path, e.g. D:\\ or E:\\Evidence")
        row.addWidget(self.path_input, 1)
        browse = QPushButton("Browse…")
        browse.clicked.connect(self._browse_target)
        row.addWidget(browse)
        l1.addLayout(row)

        ref = QPushButton("🔄  Refresh Devices")
        ref.clicked.connect(self._refresh_devices)
        l1.addWidget(ref)
        lay.addWidget(g1)

        # Step 2: Mode
        g2 = QGroupBox("STEP 2 — Investigation Mode")
        l2 = QVBoxLayout(g2)
        self.mode_combo = QComboBox()
        self.mode_combo.addItems([
            "🤖  Full Automation — Servos handles everything end-to-end",
            "🤝  Hybrid — Step-by-step with your approval",
            "🧑‍💻  Manual — Guided expert mode, you execute",
        ])
        l2.addWidget(self.mode_combo)
        lay.addWidget(g2)

        # Step 3: Investigator
        g3 = QGroupBox("STEP 3 — Investigator Details")
        l3 = QVBoxLayout(g3)
        self.investigator_input = QLineEdit("Investigator")
        self.investigator_input.setPlaceholderText("Your name")
        l3.addWidget(self.investigator_input)
        lay.addWidget(g3)

        # Progress
        g4 = QGroupBox("Investigation Progress")
        l4 = QVBoxLayout(g4)
        self.inv_status = _label("Ready to start", "subtitle")
        l4.addWidget(self.inv_status)
        self.inv_bar = QProgressBar()
        self.inv_bar.setRange(0, 100)
        l4.addWidget(self.inv_bar)
        self.inv_log = TerminalViewer("Investigation Log")
        self.inv_log.setMaximumHeight(200)
        l4.addWidget(self.inv_log)
        lay.addWidget(g4)

        # Start
        self.start_btn = QPushButton("🚀  Start Investigation")
        self.start_btn.setProperty("cssClass", "primary")
        self.start_btn.setMinimumHeight(50)
        self.start_btn.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        self.start_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.start_btn.clicked.connect(self._start_investigation)
        lay.addWidget(self.start_btn)

        lay.addStretch()
        scroll.setWidget(page)
        return scroll

    def _browse_target(self):
        p = QFileDialog.getExistingDirectory(self, "Select Target")
        if p:
            self.path_input.setText(p)

    def _refresh_devices(self):
        self.device_list.clear()
        w = DeviceRefreshWorker()
        w.finished.connect(self._on_devices)
        w.start()
        self._dev_worker = w

    def _on_devices(self, devices):
        self._devices = devices
        self.device_list.clear()
        for d in devices:
            tag = "🔌 REMOVABLE" if d.is_removable else "💾 Fixed"
            self.device_list.addItem(
                f"{d.mount_point}  —  {d.name}  |  {d.capacity_human}  "
                f"|  {d.filesystem}  |  {tag}")

    def _start_investigation(self):
        manual = self.path_input.text().strip()
        idx = self.device_list.currentRow()
        import psutil

        if manual and os.path.exists(manual):
            dev = DeviceInfo(path=manual, name=manual, mount_point=manual)
            try:
                u = psutil.disk_usage(manual)
                dev.capacity_bytes = u.total
            except Exception:
                pass
        elif idx >= 0 and self._devices:
            dev = self._devices[idx]
        else:
            QMessageBox.warning(self, "No Target",
                                "Select a device or enter a valid path.")
            return

        mode_map = {0: "full_auto", 1: "hybrid", 2: "manual"}
        mode = mode_map.get(self.mode_combo.currentIndex(), "full_auto")
        inv = self.investigator_input.text() or "Investigator"

        self.inv_bar.setValue(0)
        self.inv_log.clear()
        self.inv_status.setText("Initializing…")
        self.inv_status.setStyleSheet(f"color: {CYAN}; background: transparent;")
        self.start_btn.setEnabled(False)
        self.start_btn.setText("⏳  Running…")

        self.worker = InvestigationWorker(dev, mode, inv)
        self.worker.progress.connect(self._inv_progress)
        self.worker.finished.connect(self._inv_done)
        self.worker.error.connect(self._inv_error)
        self.worker.start()

    def _inv_progress(self, pct, msg):
        self.inv_bar.setValue(pct)
        self.inv_status.setText(msg)
        ts = datetime.now().strftime("%H:%M:%S")
        self.inv_log.append(f"[{ts}] [{pct:3d}%]  {msg}")

    def _inv_done(self, case):
        self.current_case = case
        self.inv_status.setText("✅  Investigation complete!")
        self.inv_status.setStyleSheet(
            f"color: {GREEN}; font-weight: bold; background: transparent;")
        self.start_btn.setEnabled(True)
        self.start_btn.setText("🚀  Start Investigation")
        self.inv_log.append(
            f"\n✅  Case {case.id} — Report: {case.report_path}")

        # Toast notification
        toast = ToastNotification(
            f"Investigation {case.id} complete!",
            "success", parent=self)
        toast.show_toast()

        self._populate_results(case)
        self._nav_to(4)  # Show results

    def _inv_error(self, msg):
        self.inv_status.setText("❌  Error occurred")
        self.inv_status.setStyleSheet(
            f"color: {RED}; background: transparent;")
        self.inv_log.append(f"\n❌  {msg}")
        self.start_btn.setEnabled(True)
        self.start_btn.setText("🚀  Start Investigation")
        toast = ToastNotification("Investigation failed!", "error", parent=self)
        toast.show_toast()
        QMessageBox.critical(self, "Error", msg[:600])

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Page 2: Quick Scan
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def _build_scan(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(36, 32, 36, 32)
        lay.setSpacing(20)

        lay.addWidget(_label("⚡  Quick Scan", "title"))
        lay.addWidget(_label(
            "Fast file system and malware analysis on any directory",
            "subtitle"))

        g = QGroupBox("Target")
        gl = QHBoxLayout(g)
        self.scan_input = QLineEdit()
        self.scan_input.setPlaceholderText("Enter directory path…")
        gl.addWidget(self.scan_input, 1)
        br = QPushButton("Browse…")
        br.clicked.connect(lambda: self.scan_input.setText(
            QFileDialog.getExistingDirectory(self, "Select") or
            self.scan_input.text()))
        gl.addWidget(br)
        self.scan_btn = QPushButton("⚡  Scan Now")
        self.scan_btn.setProperty("cssClass", "primary")
        self.scan_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.scan_btn.clicked.connect(self._run_scan)
        gl.addWidget(self.scan_btn)
        lay.addWidget(g)

        # Scan status
        self.scan_status = _label("", "subtitle")
        lay.addWidget(self.scan_status)

        # Results tabs
        self.scan_tabs = QTabWidget()

        self.scan_overview = QPlainTextEdit()
        self.scan_overview.setReadOnly(True)
        self.scan_overview.setStyleSheet(
            f"font-family: 'Consolas', monospace; font-size: 12px; "
            f"background: {BG_PRIMARY}; color: {TEXT_SEC}; padding: 12px;")
        self.scan_tabs.addTab(self.scan_overview, "📊 Overview")

        self.scan_files_table = QTableWidget(0, 4)
        self.scan_files_table.setHorizontalHeaderLabels(
            ["File", "Reason", "Entropy", "Size"])
        self.scan_files_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch)
        self.scan_files_table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers)
        self.scan_files_table.setAlternatingRowColors(True)
        self.scan_tabs.addTab(self.scan_files_table, "⚠️ Suspicious")

        self.scan_malware_table = QTableWidget(0, 4)
        self.scan_malware_table.setHorizontalHeaderLabels(
            ["Severity", "Rule", "File", "Description"])
        self.scan_malware_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch)
        self.scan_malware_table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers)
        self.scan_malware_table.setAlternatingRowColors(True)
        self.scan_tabs.addTab(self.scan_malware_table, "🦠 Malware")

        lay.addWidget(self.scan_tabs, 1)
        lay.addStretch()
        scroll.setWidget(page)
        return scroll

    def _run_scan(self):
        path = self.scan_input.text().strip()
        if not path or not os.path.exists(path):
            QMessageBox.warning(self, "Invalid", "Enter a valid directory.")
            return

        self.scan_btn.setEnabled(False)
        self.scan_btn.setText("⏳  Scanning…")
        self.scan_status.setText(f"Scanning {path}…")
        self.scan_overview.clear()

        self._scan_w = ScanWorker(path)
        self._scan_w.progress.connect(
            lambda msg: self.scan_status.setText(msg))
        self._scan_w.finished.connect(self._scan_done)
        self._scan_w.error.connect(self._scan_err)
        self._scan_w.start()

    def _scan_done(self, analysis, malware):
        self.scan_btn.setEnabled(True)
        self.scan_btn.setText("⚡  Scan Now")
        self.scan_status.setText(
            f"✅ Done — {analysis.total_files} files, "
            f"Risk: {malware.risk_level}")

        # Overview
        txt = (
            f"FILES:         {analysis.total_files}\n"
            f"DIRECTORIES:   {analysis.total_dirs}\n"
            f"TOTAL SIZE:    {analysis.total_size_bytes:,} bytes\n"
            f"HIDDEN:        {analysis.hidden_files}\n"
            f"SUSPICIOUS:    {len(analysis.suspicious_files)}\n\n"
            f"RISK LEVEL:    {malware.risk_level}\n"
            f"SCANNED:       {malware.files_scanned}\n"
            f"INDICATORS:    {len(malware.indicators)}\n"
        )
        if analysis.file_type_counts:
            txt += "\nFILE TYPES:\n"
            for ext, cnt in list(analysis.file_type_counts.items())[:20]:
                txt += f"  {ext:15s} {cnt}\n"
        self.scan_overview.setPlainText(txt)

        # Suspicious files table
        sf = analysis.suspicious_files
        self.scan_files_table.setRowCount(min(len(sf), 100))
        for i, f in enumerate(sf[:100]):
            self.scan_files_table.setItem(i, 0, QTableWidgetItem(f.filename))
            self.scan_files_table.setItem(
                i, 1, QTableWidgetItem(f.suspicious_reason))
            self.scan_files_table.setItem(
                i, 2, QTableWidgetItem(f"{f.entropy:.2f}"))
            self.scan_files_table.setItem(
                i, 3, QTableWidgetItem(f"{f.file_size:,}"))
        self.scan_tabs.setTabText(1, f"⚠️ Suspicious ({len(sf)})")

        # Malware table
        inds = malware.indicators
        self.scan_malware_table.setRowCount(len(inds))
        for i, ind in enumerate(inds):
            sev = QTableWidgetItem(ind.severity.upper())
            sev.setForeground(QColor(
                RED if ind.severity in ("critical", "high")
                else ORANGE if ind.severity == "medium" else TEXT_SEC))
            self.scan_malware_table.setItem(i, 0, sev)
            self.scan_malware_table.setItem(
                i, 1, QTableWidgetItem(ind.rule_name))
            self.scan_malware_table.setItem(
                i, 2, QTableWidgetItem(os.path.basename(ind.file_path)))
            self.scan_malware_table.setItem(
                i, 3, QTableWidgetItem(ind.description))
        self.scan_tabs.setTabText(2, f"🦠 Malware ({len(inds)})")

    def _scan_err(self, msg):
        self.scan_btn.setEnabled(True)
        self.scan_btn.setText("⚡  Scan Now")
        self.scan_status.setText(f"❌ Error: {msg}")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Page 3: Case Management
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def _build_cases(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(36, 32, 36, 32)
        lay.setSpacing(20)

        lay.addWidget(_label("📁  Case Management", "title"))
        lay.addWidget(_label("Search, filter, and manage investigations",
                             "subtitle"))

        # Search
        search_row = QHBoxLayout()
        self.case_search = QLineEdit()
        self.case_search.setPlaceholderText("🔎  Search by Case ID…")
        self.case_search.textChanged.connect(self._filter_cases)
        search_row.addWidget(self.case_search, 1)

        self.case_filter = QComboBox()
        self.case_filter.addItems(["All", "Completed", "Active"])
        self.case_filter.currentIndexChanged.connect(
            lambda: self._filter_cases(self.case_search.text()))
        search_row.addWidget(self.case_filter)

        ref = QPushButton("🔄  Refresh")
        ref.clicked.connect(self._refresh_cases)
        search_row.addWidget(ref)
        lay.addLayout(search_row)

        self.cases_table = QTableWidget(0, 5)
        self.cases_table.setHorizontalHeaderLabels(
            ["Case ID", "Date", "Device", "Mode", "Status"])
        self.cases_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch)
        self.cases_table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers)
        self.cases_table.setAlternatingRowColors(True)
        self.cases_table.setMinimumHeight(300)
        self.cases_table.doubleClicked.connect(self._open_case_report)
        lay.addWidget(self.cases_table, 1)

        btns = QHBoxLayout()
        open_b = QPushButton("📄  Open Report")
        open_b.clicked.connect(self._open_case_report)
        btns.addWidget(open_b)
        btns.addStretch()
        lay.addLayout(btns)

        lay.addStretch()
        scroll.setWidget(page)
        return scroll

    def _refresh_cases(self):
        try:
            s = get_session()
            self._case_recs = s.query(CaseRecord).order_by(
                CaseRecord.created_at.desc()).limit(100).all()
            self._show_cases(self._case_recs)
            s.close()
        except Exception:
            pass

    def _show_cases(self, recs):
        self.cases_table.setRowCount(len(recs))
        for i, r in enumerate(recs):
            self.cases_table.setItem(i, 0, QTableWidgetItem(r.id))
            self.cases_table.setItem(i, 1, QTableWidgetItem(
                (r.created_at or "")[:19]))
            dev = json.loads(r.device_info_json) if r.device_info_json else {}
            self.cases_table.setItem(
                i, 2, QTableWidgetItem(dev.get("name", "—")))
            self.cases_table.setItem(i, 3, QTableWidgetItem(r.mode))
            si = QTableWidgetItem(r.status)
            si.setForeground(QColor(
                GREEN if r.status == "completed" else
                CYAN if r.status == "active" else YELLOW))
            self.cases_table.setItem(i, 4, si)

    def _filter_cases(self, text):
        if not hasattr(self, "_case_recs"):
            return
        recs = self._case_recs
        q = text.lower().strip()
        filt = self.case_filter.currentText()
        if filt == "Completed":
            recs = [r for r in recs if r.status == "completed"]
        elif filt == "Active":
            recs = [r for r in recs if r.status == "active"]
        if q:
            recs = [r for r in recs if q in r.id.lower()]
        self._show_cases(recs)

    def _open_case_report(self):
        row = self.cases_table.currentRow()
        if row < 0 or not hasattr(self, "_case_recs"):
            return
        r = self._case_recs[row]
        cfg = get_config()
        rd = cfg.get("reports_dir", "")
        for ext in ["pdf", "txt", "json"]:
            p = os.path.join(rd, f"{r.id}_report.{ext}")
            if os.path.exists(p):
                os.startfile(p)
                return
        if r.report_path and os.path.exists(r.report_path):
            os.startfile(r.report_path)
        else:
            QMessageBox.information(self, "No Report",
                                     f"No report found for {r.id}")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Page 4: Results  (populated after investigation)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def _build_results(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        self.results_page_w = QWidget()
        self.results_lay = QVBoxLayout(self.results_page_w)
        self.results_lay.setContentsMargins(36, 32, 36, 32)
        self.results_lay.setSpacing(16)
        scroll.setWidget(self.results_page_w)
        return scroll

    def _populate_results(self, case: Case):
        lay = self.results_lay
        while lay.count():
            w = lay.takeAt(0).widget()
            if w:
                w.deleteLater()

        lay.addWidget(_label(
            f"📋  Investigation Results — {case.id}", "title"))

        # Risk
        risk = "UNKNOWN"
        if case.interpretation:
            risk = case.interpretation.risk_assessment
        elif case.findings and case.findings.malware:
            risk = case.findings.malware.risk_level

        risk_map = {"LOW": "riskLow", "MEDIUM": "riskMedium",
                     "HIGH": "riskHigh", "CRITICAL": "riskCritical"}
        risk_lbl = QLabel(f"  RISK LEVEL:  {risk}  ")
        risk_lbl.setProperty("cssClass", risk_map.get(risk, "riskHigh"))
        risk_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        risk_lbl.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        lay.addWidget(risk_lbl)

        # Tabs
        tabs = QTabWidget()

        # Summary
        summary_w = QPlainTextEdit()
        summary_w.setReadOnly(True)
        summary_w.setStyleSheet(
            f"font-size: 13px; padding: 12px; background: {BG_PRIMARY};")
        txt = ""
        if case.interpretation:
            txt += f"AI SUMMARY:\n{case.interpretation.summary}\n\n"
            if case.interpretation.recommendations:
                txt += "RECOMMENDATIONS:\n"
                for r in case.interpretation.recommendations:
                    txt += f"  • {r}\n"
                txt += "\n"
        txt += (f"Case ID:       {case.id}\n"
                f"Date:          {case.created_at}\n"
                f"Investigator:  {case.investigator}\n"
                f"Mode:          {case.mode}\n"
                f"Status:        {case.status}\n")
        if case.device_info:
            txt += (f"\nDevice:        {case.device_info.name}\n"
                    f"Path:          {case.device_info.path}\n"
                    f"Capacity:      {case.device_info.capacity_human}\n")
        summary_w.setPlainText(txt)
        tabs.addTab(summary_w, "📊 Summary")

        # Suspicious files
        if case.findings and case.findings.file_system:
            fs = case.findings.file_system
            ft = QTableWidget(min(len(fs.suspicious_files), 100), 4)
            ft.setHorizontalHeaderLabels(
                ["File", "Reason", "Entropy", "Size"])
            ft.horizontalHeader().setSectionResizeMode(
                QHeaderView.ResizeMode.Stretch)
            ft.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
            ft.setAlternatingRowColors(True)
            for i, f in enumerate(fs.suspicious_files[:100]):
                ft.setItem(i, 0, QTableWidgetItem(f.filename))
                ft.setItem(i, 1, QTableWidgetItem(f.suspicious_reason))
                ft.setItem(i, 2, QTableWidgetItem(f"{f.entropy:.2f}"))
                ft.setItem(i, 3, QTableWidgetItem(f"{f.file_size:,}"))
            tabs.addTab(ft,
                        f"⚠️ Suspicious ({len(fs.suspicious_files)})")

        # Malware
        if case.findings and case.findings.malware:
            m = case.findings.malware
            mt = QTableWidget(len(m.indicators), 4)
            mt.setHorizontalHeaderLabels(
                ["Severity", "Rule", "File", "Description"])
            mt.horizontalHeader().setSectionResizeMode(
                QHeaderView.ResizeMode.Stretch)
            mt.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
            mt.setAlternatingRowColors(True)
            for i, ind in enumerate(m.indicators):
                sev = QTableWidgetItem(ind.severity.upper())
                sev.setForeground(QColor(
                    RED if ind.severity in ("critical", "high") else ORANGE))
                mt.setItem(i, 0, sev)
                mt.setItem(i, 1, QTableWidgetItem(ind.rule_name))
                mt.setItem(i, 2, QTableWidgetItem(
                    os.path.basename(ind.file_path)))
                mt.setItem(i, 3, QTableWidgetItem(ind.description))
            tabs.addTab(mt, f"🦠 Malware ({len(m.indicators)})")

        # Artifacts
        if case.findings and case.findings.artifacts:
            art = case.findings.artifacts
            all_a = art.all_artifacts()
            at = QTableWidget(min(len(all_a), 200), 4)
            at.setHorizontalHeaderLabels(
                ["Type", "Timestamp", "Description", "Score"])
            at.horizontalHeader().setSectionResizeMode(
                QHeaderView.ResizeMode.Stretch)
            at.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
            at.setAlternatingRowColors(True)
            for i, a in enumerate(all_a[:200]):
                at.setItem(i, 0, QTableWidgetItem(a.artifact_type))
                at.setItem(i, 1, QTableWidgetItem((a.timestamp or "")[:19]))
                at.setItem(i, 2, QTableWidgetItem(a.description[:120]))
                at.setItem(
                    i, 3, QTableWidgetItem(f"{a.suspicious_score:.2f}"))
            tabs.addTab(at, f"🔎 Artifacts ({art.total_artifacts})")

        # Timeline
        if case.findings and case.findings.timeline:
            tl = case.findings.timeline
            tl_w = QPlainTextEdit()
            tl_w.setReadOnly(True)
            tl_w.setStyleSheet(
                f"font-family: 'Consolas', monospace; font-size: 11px; "
                f"background: {BG_PRIMARY};")
            tl_w.setPlainText(
                TimelineBuilder().format_ascii_timeline(tl, max_events=80))
            tabs.addTab(tl_w, f"📅 Timeline ({len(tl.events)})")

        # Chain of Custody
        if case.backup:
            coc = QPlainTextEdit()
            coc.setReadOnly(True)
            coc.setStyleSheet(
                f"font-family: 'Consolas', monospace; font-size: 12px; "
                f"background: {BG_PRIMARY};")
            coc.setPlainText(
                f"CHAIN OF CUSTODY\n"
                f"{'═' * 50}\n"
                f"Backup Path:     {case.backup.backup_path}\n"
                f"Files Backed Up: {case.backup.files_backed_up}\n"
                f"Size:            {case.backup.size_bytes:,} bytes\n"
                f"Created:         {case.backup.created_at}\n"
                f"MD5:             {case.backup.hash_md5}\n"
                f"SHA-256:         {case.backup.hash_sha256}\n"
                f"{'═' * 50}")
            tabs.addTab(coc, "🔒 Chain of Custody")

        lay.addWidget(tabs, 1)

        # Buttons
        btn_row = QHBoxLayout()
        cfg = get_config()
        rd = cfg.get("reports_dir", "")
        for fmt, icon in [("pdf", "📕"), ("txt", "📝"), ("json", "📋")]:
            p = os.path.join(rd, f"{case.id}_report.{fmt}")
            if os.path.exists(p):
                b = QPushButton(f"{icon}  {fmt.upper()}")
                b.setCursor(Qt.CursorShape.PointingHandCursor)
                b.clicked.connect(
                    lambda _, pp=p: os.startfile(pp))
                btn_row.addWidget(b)

        back = QPushButton("← Dashboard")
        back.clicked.connect(lambda: self._nav_to(0))
        btn_row.addWidget(back)
        btn_row.addStretch()

        bw = QWidget()
        bw.setLayout(btn_row)
        lay.addWidget(bw)

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Page 5: Playbooks
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def _build_playbooks(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(36, 32, 36, 32)
        lay.setSpacing(20)

        lay.addWidget(_label("📋  Playbooks", "title"))
        lay.addWidget(_label(
            "Reusable forensic investigation workflows", "subtitle"))

        engine = PlaybookEngine()
        playbooks = engine.list_playbooks()

        if not playbooks:
            lay.addWidget(_label(
                "No playbooks found. Place YAML files in the "
                "playbooks/defaults directory.", "subtitle"))
        else:
            for pb in playbooks:
                g = QGroupBox(f"📋  {pb.name}")
                gl = QVBoxLayout(g)
                gl.addWidget(_label(pb.description or "", "subtitle",
                                    wrap=True))

                info_row = QHBoxLayout()
                info_row.addWidget(QLabel(
                    f"Steps: {len(pb.steps)}  |  "
                    f"Version: {pb.version}"))
                if pb.metadata:
                    md = pb.metadata
                    if md.get("difficulty"):
                        info_row.addWidget(QLabel(
                            f"Difficulty: {md['difficulty']}"))
                    if md.get("estimated_duration_minutes"):
                        info_row.addWidget(QLabel(
                            f"~{md['estimated_duration_minutes']} min"))
                info_row.addStretch()
                gl.addLayout(info_row)

                if pb.steps:
                    steps_w = QPlainTextEdit()
                    steps_w.setReadOnly(True)
                    steps_w.setMaximumHeight(150)
                    steps_w.setStyleSheet(
                        f"font-family: Consolas, monospace; font-size: 11px; "
                        f"background: {BG_PRIMARY}; padding: 8px;")
                    step_text = ""
                    for j, step in enumerate(pb.steps, 1):
                        actions = step.actions
                        module = (actions[0].get("type", "")
                                  if actions else "")
                        step_text += (
                            f"{j}. [{module}] {step.name}\n"
                            f"   {step.description}\n\n")
                    steps_w.setPlainText(step_text)
                    gl.addWidget(steps_w)

                lay.addWidget(g)

        lay.addStretch()
        scroll.setWidget(page)
        return scroll

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Page 6: Settings
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def _build_settings(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(36, 32, 36, 32)
        lay.setSpacing(20)

        lay.addWidget(_label("⚙️  Settings", "title"))
        lay.addWidget(_label("Configure Servos", "subtitle"))

        cfg = get_config()
        self._settings_inputs = {}

        groups = {
            "LLM Configuration": [
                ("llm_model", "Model name", "llama3.1:8b"),
                ("llm_base_url", "Ollama URL",
                 "http://localhost:11434"),
                ("llm_timeout", "Timeout (sec)", "30"),
            ],
            "Storage Paths": [
                ("backup_location", "Backup directory", ""),
                ("reports_dir", "Reports directory", ""),
                ("data_dir", "Data directory", ""),
            ],
            "Analysis": [
                ("entropy_threshold", "Entropy threshold", "7.5"),
                ("max_file_size_mb", "Max file size (MB)", "100"),
            ],
        }

        for group_name, fields in groups.items():
            g = QGroupBox(group_name)
            gl = QVBoxLayout(g)
            for key, label, default in fields:
                row = QHBoxLayout()
                row.addWidget(QLabel(label))
                inp = QLineEdit(str(cfg.get(key, default)))
                inp.setPlaceholderText(default)
                row.addWidget(inp, 1)
                gl.addLayout(row)
                self._settings_inputs[key] = inp

                # Add browse button for path fields
                if "dir" in key or "location" in key or "path" in key:
                    br = QPushButton("Browse…")
                    br.clicked.connect(
                        lambda _, inp_ref=inp: inp_ref.setText(
                            QFileDialog.getExistingDirectory(
                                self, "Select Directory") or inp_ref.text()))
                    row.addWidget(br)

            lay.addWidget(g)

        save_btn = QPushButton("💾  Save Settings")
        save_btn.setProperty("cssClass", "success")
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.clicked.connect(self._save_settings)
        lay.addWidget(save_btn)

        lay.addStretch()
        scroll.setWidget(page)
        return scroll

    def _save_settings(self):
        cfg = get_config()
        for key, inp in self._settings_inputs.items():
            val = inp.text().strip()
            if val:
                # Try numeric conversion
                try:
                    val = int(val)
                except ValueError:
                    try:
                        val = float(val)
                    except ValueError:
                        pass
                cfg[key] = val
        save_config(cfg)
        QMessageBox.information(self, "Saved", "Settings saved successfully.")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Page 7: Automate Task
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def _build_automate(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(36, 32, 36, 32)
        lay.setSpacing(20)

        lay.addWidget(_label("🤖  Automate Task", "title"))
        lay.addWidget(_label(
            "Enter commands in natural language to automate forensic "
            "and system tasks", "subtitle"))

        # ── Box 1: Command Input ──
        g1 = QGroupBox("Command Input")
        l1 = QVBoxLayout(g1)
        l1.addWidget(_label(
            "Describe what you want Servos to do. You can type natural "
            "language or use the supported commands below.",
            "subtitle", wrap=True))

        self.auto_cmd = QPlainTextEdit()
        self.auto_cmd.setPlaceholderText(
            "Type a command here…\n\n"
            "Examples:\n"
            "  • delete file C:\\Users\\me\\Desktop\\malware.exe\n"
            "  • eject device D:\\\n"
            "  • hash file C:\\evidence\\suspicious.pdf\n"
            "  • list devices\n"
            "  • scan directory C:\\Users\\me\\Downloads\n"
            "  • open folder C:\\Users\\me\\Desktop")
        self.auto_cmd.setMaximumHeight(140)
        self.auto_cmd.setStyleSheet(
            f"font-family: 'Consolas', 'JetBrains Mono', monospace; "
            f"font-size: 13px; background: {BG_INPUT}; "
            f"color: {TEXT}; border: 1px solid {BORDER}; "
            f"border-radius: 10px; padding: 14px;")
        l1.addWidget(self.auto_cmd)
        lay.addWidget(g1)

        # ── Box 2: Automate Task ──
        g2 = QGroupBox("Automate Task")
        l2 = QVBoxLayout(g2)
        l2.addWidget(_label(
            "Enter specific automation instructions such as "
            "\"delete a file\", \"disconnect the device\", "
            "\"hash a file\", or \"clear temp files\".",
            "subtitle", wrap=True))

        self.auto_task = QLineEdit()
        self.auto_task.setPlaceholderText(
            "e.g. delete file C:\\temp\\malware.exe")
        self.auto_task.setMinimumHeight(44)
        self.auto_task.returnPressed.connect(self._run_auto_from_task)
        l2.addWidget(self.auto_task)

        # Execute button
        exec_row = QHBoxLayout()
        self.auto_exec_btn = QPushButton("🚀  Execute Command")
        self.auto_exec_btn.setProperty("cssClass", "primary")
        self.auto_exec_btn.setMinimumHeight(48)
        self.auto_exec_btn.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        self.auto_exec_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.auto_exec_btn.clicked.connect(self._run_auto_from_cmd)
        exec_row.addWidget(self.auto_exec_btn)

        self.auto_task_btn = QPushButton("⚡  Automate")
        self.auto_task_btn.setProperty("cssClass", "primary")
        self.auto_task_btn.setMinimumHeight(48)
        self.auto_task_btn.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        self.auto_task_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.auto_task_btn.clicked.connect(self._run_auto_from_task)
        exec_row.addWidget(self.auto_task_btn)
        l2.addLayout(exec_row)
        lay.addWidget(g2)

        # ── Supported Commands Reference ──
        g3 = QGroupBox("Supported Commands")
        l3 = QVBoxLayout(g3)
        ref = QPlainTextEdit()
        ref.setReadOnly(True)
        ref.setMaximumHeight(160)
        ref.setStyleSheet(
            f"font-family: 'Consolas', monospace; font-size: 11px; "
            f"background: {BG_PRIMARY}; padding: 10px;")
        ref.setPlainText(
            "COMMAND                          DESCRIPTION\n"
            "─────────────────────────────────────────────────────────\n"
            "delete file <path>               Delete a specific file\n"
            "eject device <drive>             Safely eject a USB drive\n"
            "disconnect device <drive>        Same as eject\n"
            "open file <path>                 Open a file with default app\n"
            "open folder <path>               Open a folder in Explorer\n"
            "hash file <path>                 Compute MD5 + SHA-256\n"
            "list devices                     Show all connected devices\n"
            "scan directory <path>            Quick malware scan a folder\n"
            "clear temp files                 Delete Windows temp files\n"
            "system info                      Show system information\n"
            "help                             Show this command list\n")
        l3.addWidget(ref)
        lay.addWidget(g3)

        # ── Output Console ──
        g4 = QGroupBox("Output")
        l4 = QVBoxLayout(g4)
        self.auto_output = QPlainTextEdit()
        self.auto_output.setReadOnly(True)
        self.auto_output.setStyleSheet(
            f"font-family: 'Consolas', 'JetBrains Mono', monospace; "
            f"font-size: 12px; background: {BG_PRIMARY}; "
            f"color: {GREEN}; border: 1px solid {BORDER}; "
            f"border-radius: 10px; padding: 14px;")
        l4.addWidget(self.auto_output)
        lay.addWidget(g4, 1)

        lay.addStretch()
        scroll.setWidget(page)
        return scroll

    def _run_auto_from_cmd(self):
        cmd = self.auto_cmd.toPlainText().strip()
        if cmd:
            self._execute_auto(cmd)

    def _run_auto_from_task(self):
        cmd = self.auto_task.text().strip()
        if cmd:
            self._execute_auto(cmd)

    def _execute_auto(self, raw_cmd: str):
        """Parse and execute an automation command."""
        ts = datetime.now().strftime("%H:%M:%S")
        self.auto_output.appendPlainText(f"[{ts}] > {raw_cmd}")

        cmd = raw_cmd.lower().strip()
        try:
            if cmd in ("help", "?"):
                self._auto_log(
                    "Commands: delete file, eject device, open file, "
                    "open folder, hash file, list devices, scan directory, "
                    "clear temp files, system info")

            elif cmd.startswith("delete file ") or cmd.startswith("remove file "):
                path = raw_cmd.split(" ", 2)[2].strip().strip('"').strip("'")
                self._auto_delete_file(path)

            elif (cmd.startswith("eject device ") or
                  cmd.startswith("disconnect device ") or
                  cmd.startswith("eject ") or
                  cmd.startswith("disconnect ")):
                drive = raw_cmd.split()[-1].strip().strip('"')
                self._auto_eject(drive)

            elif cmd.startswith("open file "):
                path = raw_cmd.split(" ", 2)[2].strip().strip('"')
                self._auto_open(path)

            elif cmd.startswith("open folder ") or cmd.startswith("open dir "):
                path = raw_cmd.split(" ", 2)[2].strip().strip('"')
                self._auto_open_folder(path)

            elif cmd.startswith("hash file ") or cmd.startswith("hash "):
                parts = raw_cmd.split(" ", 2)
                path = parts[2].strip().strip('"') if len(parts) > 2 else parts[1].strip().strip('"')
                self._auto_hash(path)

            elif cmd == "list devices" or cmd == "devices":
                self._auto_list_devices()

            elif cmd.startswith("scan directory ") or cmd.startswith("scan dir ") or cmd.startswith("scan "):
                parts = raw_cmd.split(" ", 2)
                path = parts[-1].strip().strip('"')
                if path.startswith("directory ") or path.startswith("dir "):
                    path = path.split(" ", 1)[1].strip()
                self._auto_scan(path)

            elif cmd in ("clear temp files", "clear temp", "clean temp"):
                self._auto_clear_temp()

            elif cmd in ("system info", "sysinfo"):
                self._auto_sysinfo()

            else:
                self._auto_log(
                    f"⚠  Unrecognized command: '{raw_cmd}'\n"
                    f"   Type 'help' for a list of supported commands.")

        except Exception as e:
            self._auto_log(f"❌  Error: {e}")

    def _auto_log(self, msg):
        ts = datetime.now().strftime("%H:%M:%S")
        self.auto_output.appendPlainText(f"[{ts}]   {msg}")

    def _auto_delete_file(self, path):
        if not os.path.exists(path):
            self._auto_log(f"❌  File not found: {path}")
            return
        reply = QMessageBox.warning(
            self, "Confirm Delete",
            f"Are you sure you want to PERMANENTLY delete:\n{path}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            if os.path.isfile(path):
                os.remove(path)
            else:
                shutil.rmtree(path)
            self._auto_log(f"✅  Deleted: {path}")
        else:
            self._auto_log("⊘  Delete cancelled.")

    def _auto_eject(self, drive):
        """Safely eject a removable drive (Windows)."""
        drive = drive.rstrip("\\")
        if not drive.endswith(":"):
            drive += ":"
        self._auto_log(f"⏏  Ejecting {drive}…")
        try:
            result = subprocess.run(
                ["powershell", "-Command",
                 f"$vol = Get-WmiObject -Class Win32_Volume -Filter \""
                 f"DriveLetter='{drive}'\"; "
                 f"$vol.Dismount($false, $false)"],
                capture_output=True, text=True, timeout=15)
            if result.returncode == 0:
                self._auto_log(f"✅  {drive} ejected successfully. Safe to remove.")
            else:
                self._auto_log(
                    f"⚠  Eject returned code {result.returncode}. "
                    f"Drive may still be in use. {result.stderr.strip()}")
        except Exception as e:
            self._auto_log(f"❌  Eject failed: {e}")

    def _auto_open(self, path):
        if not os.path.exists(path):
            self._auto_log(f"❌  File not found: {path}")
            return
        os.startfile(path)
        self._auto_log(f"✅  Opened: {path}")

    def _auto_open_folder(self, path):
        if not os.path.isdir(path):
            self._auto_log(f"❌  Folder not found: {path}")
            return
        subprocess.Popen(["explorer", path])
        self._auto_log(f"✅  Opened folder: {path}")

    def _auto_hash(self, path):
        if not os.path.isfile(path):
            self._auto_log(f"❌  File not found: {path}")
            return
        self._auto_log(f"🔐  Hashing {os.path.basename(path)}…")
        md5 = hashlib.md5()
        sha = hashlib.sha256()
        with open(path, "rb") as f:
            while True:
                chunk = f.read(65536)
                if not chunk:
                    break
                md5.update(chunk)
                sha.update(chunk)
        size = os.path.getsize(path)
        self._auto_log(
            f"✅  {os.path.basename(path)}\n"
            f"     Size:    {size:,} bytes\n"
            f"     MD5:     {md5.hexdigest()}\n"
            f"     SHA-256: {sha.hexdigest()}")

    def _auto_list_devices(self):
        svc = USBDetectionService()
        devs = svc.detect_devices()
        if not devs:
            self._auto_log("No devices found.")
            return
        self._auto_log(f"Found {len(devs)} device(s):")
        for d in devs:
            tag = "REMOVABLE" if d.is_removable else "Fixed"
            self._auto_log(
                f"  {d.mount_point}  {d.name}  |  "
                f"{d.capacity_human}  |  {d.filesystem}  |  {tag}")

    def _auto_scan(self, path):
        if not os.path.isdir(path):
            self._auto_log(f"❌  Directory not found: {path}")
            return
        self._auto_log(f"⚡  Scanning {path}…")
        self.scan_input.setText(path)
        self._run_scan()
        self._nav_to(2)  # Switch to Quick Scan page

    def _auto_clear_temp(self):
        tmp = os.environ.get("TEMP", os.path.join(os.path.expanduser("~"), "AppData", "Local", "Temp"))
        reply = QMessageBox.warning(
            self, "Clear Temp Files",
            f"Delete all files in:\n{tmp}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply != QMessageBox.StandardButton.Yes:
            self._auto_log("⊘  Cancelled.")
            return
        count = 0
        for item in os.listdir(tmp):
            p = os.path.join(tmp, item)
            try:
                if os.path.isfile(p):
                    os.remove(p)
                    count += 1
                elif os.path.isdir(p):
                    shutil.rmtree(p)
                    count += 1
            except Exception:
                pass
        self._auto_log(f"✅  Cleared {count} items from temp folder.")

    def _auto_sysinfo(self):
        import platform
        import psutil
        self._auto_log(
            f"SYSTEM INFORMATION\n"
            f"  OS:       {platform.system()} {platform.release()}\n"
            f"  Machine:  {platform.machine()}\n"
            f"  CPU:      {psutil.cpu_count()} cores\n"
            f"  RAM:      {psutil.virtual_memory().total // (1024**3)} GB\n"
            f"  Disk C:   {psutil.disk_usage('C:/').free // (1024**3)} GB free")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Entry Point
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(STYLESHEET)

    # Dark palette
    pal = QPalette()
    pal.setColor(QPalette.ColorRole.Window, QColor(BG_PRIMARY))
    pal.setColor(QPalette.ColorRole.WindowText, QColor(TEXT))
    pal.setColor(QPalette.ColorRole.Base, QColor(BG_PRIMARY))
    pal.setColor(QPalette.ColorRole.AlternateBase, QColor(BG_SURFACE))
    pal.setColor(QPalette.ColorRole.Text, QColor(TEXT))
    pal.setColor(QPalette.ColorRole.Button, QColor(BG_CARD))
    pal.setColor(QPalette.ColorRole.ButtonText, QColor(TEXT))
    pal.setColor(QPalette.ColorRole.Highlight, QColor(CYAN))
    pal.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))
    app.setPalette(pal)

    win = ServosMainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

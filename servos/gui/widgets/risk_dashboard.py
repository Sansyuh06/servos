"""
Per-case risk dashboard widget used after an investigation completes.

Shows an overall risk badge, detection ratio, various metric cards, a table
of top threats, anomaly summaries, suggested IT Act sections, and a button to
export the full report.
"""

from __future__ import annotations

from typing import List, Optional, Dict, Any

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QGridLayout,
    QTableWidget, QTableWidgetItem, QListWidget, QPushButton, QFrame
)

from servos.forensics.multi_engine_scanner import MultiScanResult
from servos.forensics.log_analyzer import LogThreat
from servos.forensics.timeline import TimelineAnomaly
from servos.reference.it_act import ITActResult
from servos.forensics.duplicate_detector import DuplicateAlert
from servos.models.schema import ThreatVerdict, Case
from servos.gui.theme import BG_CARD, TEXT, GREEN, RED, YELLOW, ACCENT


class MetricCard(QFrame):
    def __init__(self, title: str, value: str, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setStyleSheet(f"background:{BG_CARD};border:1px solid {ACCENT};border-radius:8px;")
        lay = QVBoxLayout(self)
        lab_title = QLabel(title)
        lab_title.setStyleSheet(f"color:{TEXT};font-weight:600;font-size:11px;")
        lab_value = QLabel(value)
        lab_value.setStyleSheet(f"color:{TEXT};font-size:20px;font-weight:700;")
        lay.addWidget(lab_title)
        lay.addWidget(lab_value)
        lay.addStretch()

    def set_value(self, value: str) -> None:
        self.findChildren(QLabel)[1].setText(value)


class RiskDashboard(QWidget):
    export_requested = pyqtSignal()

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self) -> None:
        lay = QVBoxLayout(self)
        lay.setSpacing(12)
        lay.setContentsMargins(16, 16, 16, 16)

        self.badge = QLabel("RISK: UNKNOWN")
        self.badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.badge.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        lay.addWidget(self.badge)

        self.ratio_label = QLabel("")
        self.ratio_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.ratio_label.setFont(QFont("Segoe UI", 14))
        lay.addWidget(self.ratio_label)

        # metrics grid
        grid = QGridLayout()
        grid.setSpacing(8)
        self.cards: Dict[str, MetricCard] = {}
        metric_names = [
            "Total files scanned", "Suspicious files", "Malware families",
            "Browser domains flagged", "Log threats", "Deleted executables",
            "Timeline anomalies", "IT Act sections"
        ]
        for i, name in enumerate(metric_names):
            card = MetricCard(name, "0")
            self.cards[name] = card
            grid.addWidget(card, i // 4, i % 4)
        lay.addLayout(grid)

        # top threats table
        self.threat_table = QTableWidget(0, 4)
        self.threat_table.setHorizontalHeaderLabels(["Filename", "Score", "Family", "Engines"])  # engines count
        self.threat_table.horizontalHeader().setStretchLastSection(True)
        self.threat_table.verticalHeader().setVisible(False)
        lay.addWidget(self.threat_table)

        # anomalies list
        self.anomaly_list = QListWidget()
        lay.addWidget(self.anomaly_list)

        # IT Act suggestions
        self.itact_list = QListWidget()
        lay.addWidget(self.itact_list)

        # export button
        self.export_btn = QPushButton("Export Full Report")
        self.export_btn.setProperty("cssClass", "primary")
        self.export_btn.clicked.connect(lambda: self.export_requested.emit())
        lay.addWidget(self.export_btn)

    def update(self,
               case: Case,
               multi_scan: Optional[MultiScanResult] = None,
               top_threats: Optional[List[ThreatVerdict]] = None,
               anomalies: Optional[List[TimelineAnomaly]] = None,
               itact: Optional[List[ITActResult]] = None,
               log_threats: Optional[List[LogThreat]] = None,
               deleted_exes: Optional[List[Any]] = None) -> None:
        """Populate dashboard using provided datasets."""
        # risk badge
        self.badge.setText(f"RISK: {case.findings.file_system.risk_level if case and case.findings and case.findings.file_system else 'UNKNOWN'}")

        # ratio
        if multi_scan:
            self.ratio_label.setText(multi_scan.ratio)
        else:
            self.ratio_label.setText("")

        # metrics
        self.cards["Total files scanned"].set_value(str(len(case.findings.file_system.files) if case and case.findings and case.findings.file_system else 0))
        self.cards["Suspicious files"].set_value(str(len(case.findings.file_system.suspicious_files) if case and case.findings and case.findings.file_system else 0))
        self.cards["Malware families"].set_value(str(len(case.findings.file_system.suspicious_files)))
        self.cards["Browser domains flagged"].set_value(str(len([a for a in (case.findings.artifacts.browser_history if case and case.findings and case.findings.artifacts else []) if a.suspicious_score > 0.5])))
        self.cards["Log threats"].set_value(str(len(log_threats) if log_threats else 0))
        self.cards["Deleted executables"].set_value(str(len([d for d in (deleted_exes or []) if d.original_path.lower().endswith('.exe')])))
        self.cards["Timeline anomalies"].set_value(str(len(anomalies) if anomalies else 0))
        self.cards["IT Act sections"].set_value(str(len(itact) if itact else 0))

        # top threats table
        self.threat_table.setRowCount(0)
        if top_threats:
            for t in top_threats[:5]:
                row = self.threat_table.rowCount()
                self.threat_table.insertRow(row)
                self.threat_table.setItem(row, 0, QTableWidgetItem(t.filename))
                self.threat_table.setItem(row, 1, QTableWidgetItem(str(t.threat_score)))
                self.threat_table.setItem(row, 2, QTableWidgetItem(t.malware_family))
                self.threat_table.setItem(row, 3, QTableWidgetItem(str(t.signal_count)))

        # anomalies list
        self.anomaly_list.clear()
        if anomalies:
            for a in anomalies:
                self.anomaly_list.addItem(f"{a.anomaly_type}: {a.description} ({a.severity})")

        # it act suggestions
        self.itact_list.clear()
        if itact:
            for sec in itact:
                self.itact_list.addItem(f"{sec.section_id} - {sec.title}")

"""
PyQt6 widget wrapping the offline multi-engine scanner.

The UI allows the investigator to drag and drop a single file, click Scan,
view per-engine results with colour coding, see the detection ratio and
optionally export the verdict to the active case report.

The widget emits a ``verdict_exported`` signal when the user requests an
export; the surrounding application (main window or worker) should connect
and handle PDF merging or case updates.
"""

from __future__ import annotations

import os
import tempfile
from typing import Optional

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox,
)

from servos.forensics.multi_engine_scanner import MultiEngineScanner, MultiScanResult
from servos.gui.theme import BG_CARD, TEXT, GREEN, RED, YELLOW


class FileScannerWidget(QWidget):
    """Standalone widget to scan individual files using the multi-engine logic."""

    verdict_exported = pyqtSignal(MultiScanResult)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self._file: Optional[str] = None
        self._last_result: Optional[MultiScanResult] = None

        self._build_ui()

    def _build_ui(self) -> None:
        lay = QVBoxLayout(self)
        lay.setSpacing(8)
        lay.setContentsMargins(16, 16, 16, 16)

        self.drop_label = QLabel("Drag & drop file here")
        self.drop_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.drop_label.setStyleSheet(
            "border: 2px dashed #aaa; padding: 40px; background:%s" % BG_CARD)
        lay.addWidget(self.drop_label)

        self.scan_button = QPushButton("Scan")
        self.scan_button.setProperty("cssClass", "primary")
        self.scan_button.clicked.connect(self._on_scan)
        self.scan_button.setEnabled(False)
        lay.addWidget(self.scan_button)

        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Engine", "Verdict", "Detail"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(self.table.NoEditTriggers)
        lay.addWidget(self.table)

        self.ratio_label = QLabel("")
        self.ratio_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.ratio_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        lay.addWidget(self.ratio_label)

        self.export_button = QPushButton("Export Verdict")
        self.export_button.setEnabled(False)
        self.export_button.clicked.connect(self._on_export)
        lay.addWidget(self.export_button)

    # drag/drop -------------------------------------------------------------
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if len(urls) == 1 and urls[0].isLocalFile():
                event.acceptProposedAction()
                return
        event.ignore()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if urls and urls[0].isLocalFile():
            path = urls[0].toLocalFile()
            if os.path.isfile(path):
                self._set_file(path)

    def _set_file(self, path: str) -> None:
        self._file = path
        self.drop_label.setText(os.path.basename(path))
        self.scan_button.setEnabled(True)
        self._last_result = None
        self.export_button.setEnabled(False)
        self.table.setRowCount(0)
        self.ratio_label.setText("")

    # scan logic -----------------------------------------------------------
    def _on_scan(self) -> None:
        if not self._file:
            return
        self.scan_button.setEnabled(False)
        self.drop_label.setText(f"Scanning {os.path.basename(self._file)}...")
        QApplication = self.__class__.__module__  # to keep linter happy
        try:
            scanner = MultiEngineScanner()
            result = scanner.scan(self._file)
            self._last_result = result
            self._display_result(result)
            self.export_button.setEnabled(True)
        except Exception as e:
            QMessageBox.warning(self, "Scan Failed", str(e))
        finally:
            if self._file:
                self.drop_label.setText(os.path.basename(self._file))
            self.scan_button.setEnabled(True)

    def _display_result(self, result: MultiScanResult) -> None:
        self.table.setRowCount(0)
        for r in result.per_engine_results:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(r.get("engine", "")))
            verdict_item = QTableWidgetItem(r.get("verdict", ""))
            verdict = r.get("verdict", "").lower()
            if verdict == "malicious":
                clue = RED
            elif verdict == "suspicious":
                clue = YELLOW
            else:
                clue = GREEN
            verdict_item.setForeground(QColor(clue))
            self.table.setItem(row, 1, verdict_item)
            self.table.setItem(row, 2, QTableWidgetItem(r.get("detail", "")))
        self.ratio_label.setText(result.ratio)

    # export ----------------------------------------------------------------
    def _on_export(self) -> None:
        if not self._last_result:
            return
        # emit signal so outer context can handle updating the case/report
        self.verdict_exported.emit(self._last_result)
        QMessageBox.information(self, "Export", "Verdict ready for export.")

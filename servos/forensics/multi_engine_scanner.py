"""
Servos 1 Offline Multi-Engine File Scanner.

Aggregates file reputation signals from multiple internal engines in parallel
and produces a unified threat score such as a local, offline equivalent of
VirusTotal's "detection ratio".

This module is intentionally lightweight: it merely ties together existing
components (HashDatabase, PEAnalyzer, DeepMalwareScanner, FileAnalyzer,
ThreatScorer, etc.) and exposes a convenient high-level API for the GUI and
command-line workflows.
"""

import os
import threading
from dataclasses import dataclass
from typing import List, Dict, Any

from servos.forensics.hash_database import HashDatabase, HashLookupResult
from servos.forensics.pe_analyzer import PEAnalyzer, PEAnalysisResult
from servos.forensics.deep_malware_scanner import DeepMalwareScanner
from servos.forensics.file_analyzer import FileAnalyzer
from servos.forensics.hasher import FileHasher
from servos.forensics.threat_scorer import ThreatScorer, ThreatSignal, SIGNAL_WEIGHTS


@dataclass
class MultiScanResult:
    """Aggregate result returned by :class:`MultiEngineScanner`.

    Attributes:
        ratio: Human-friendly detection ratio ("3/5 engines flagged").
        score: Final 0-100 threat score from ``ThreatScorer``.
        threat_level: Corresponding level (CLEAN/LOW/MEDIUM/HIGH/CRITICAL).
        malware_family: Family name returned by hash lookup, if any.
        per_engine_results: List of individual engine verdict dicts.
    """
    ratio: str
    score: float
    threat_level: str
    malware_family: str
    per_engine_results: List[Dict[str, Any]]


class MultiEngineScanner:
    """Perform a unified, multi-engine scan of a single file.

    All five engines run in parallel threads and their outcomes are collected
    before a final ``ThreatScorer`` verdict is produced.  The scanners are kept
    simple; their weights and decision logic mirror the existing
    ``MalwareDetector`` code so that behaviour is consistent across the
    application.
    """

    def __init__(self):
        self.hash_db = HashDatabase()
        self.pe_analyzer = PEAnalyzer()
        self.deep_scanner = DeepMalwareScanner()
        self.file_analyzer = FileAnalyzer()
        self.hasher = FileHasher()
        self.scorer = ThreatScorer()

    def scan(self, filepath: str, yara_rules: str = None) -> MultiScanResult:
        """Scan *filepath* through all available engines and return a summary.

        ``yara_rules`` may be provided for the DeepMalwareScanner; if omitted the
        scanner will still run but only match against any built-in rules.
        """
        # pre-compute hash once (used by engine thread and final scoring)
        hash_info = self.hasher.hash_file(filepath)
        sha256 = hash_info.get("sha256", "")
        md5 = hash_info.get("md5", "")
        lookup: HashLookupResult = self.hash_db.lookup(sha256, md5, filepath)

        results: List[Dict[str, Any]] = []
        lock = threading.Lock()

        def _append(engine_result: Dict[str, Any]) -> None:
            with lock:
                results.append(engine_result)

        # Engine definitions --------------------------------------------------
        def run_hash():
            verdict = "clean"
            if lookup.verdict == "KNOWN_MALICIOUS":
                verdict = "malicious"
            elif lookup.verdict == "KNOWN_CLEAN":
                verdict = "clean"
            else:
                verdict = "clean"
            _append({
                "engine": "HashDatabase",
                "verdict": verdict,
                "detail": lookup.verdict,
                "lookup": lookup,
            })

        def run_pe():
            try:
                pe: PEAnalysisResult = self.pe_analyzer.analyze(filepath)
                verdict = "clean"
                details: List[str] = []
                if pe.is_packed:
                    verdict = "suspicious"
                    details.append(f"packed ({pe.packer_name})")
                if pe.suspicious_imports:
                    verdict = "suspicious"
                    details.append("suspicious imports: " + ",".join(pe.suspicious_imports))
                if pe.anomalies:
                    verdict = "suspicious"
                    details.append("anomalies: " + ",".join(pe.anomalies))
                if pe.suspicious_sections:
                    verdict = "suspicious"
                    details.append("suspicious sections: " + ",".join(pe.suspicious_sections))
                _append({
                    "engine": "PEAnalyzer",
                    "verdict": verdict,
                    "detail": "; ".join(details) or "no issues",
                    "pe_result": pe,
                })
            except Exception as e:
                _append({
                    "engine": "PEAnalyzer",
                    "verdict": "clean",
                    "detail": f"error: {e}",
                })

        def run_yara():
            verdict = "clean"
            detail = "no matches"
            matches: List[str] = []
            try:
                findings = self.deep_scanner.scan_path(os.path.dirname(filepath))
                for f in findings:
                    if f.get("file") == filepath:
                        matches = f.get("matches", [])
                        if matches:
                            verdict = "malicious"
                            detail = ";".join(matches)
                        break
            except Exception as e:
                detail = f"error: {e}"
            _append({
                "engine": "DeepMalwareScanner",
                "verdict": verdict,
                "detail": detail,
                "matches": matches,
            })

        def run_entropy():
            ent = self.file_analyzer._calculate_entropy(filepath)
            verdict = "suspicious" if ent > 7.0 else "clean"
            _append({
                "engine": "Entropy",
                "verdict": verdict,
                "detail": f"entropy {ent:.2f}",
                "entropy": ent,
            })

        def run_magic():
            verdict = "clean"
            detail = "extension matches magic"
            try:
                with open(filepath, "rb") as f:
                    header = f.read(32)
                ext = os.path.splitext(filepath)[1].lower()
                from servos.forensics.malware_detector import MAGIC_BYTES

                for magic, info in MAGIC_BYTES.items():
                    if header.startswith(magic):
                        valid_exts = info.get("extensions", set())
                        if ext and ext not in valid_exts and valid_exts != {""}:
                            verdict = "suspicious"
                            detail = f"{info['type']} masquerading as {ext}"
                        break
            except Exception as e:
                detail = f"error: {e}"
            _append({
                "engine": "MagicBytes",
                "verdict": verdict,
                "detail": detail,
            })

        # launch threads ------------------------------------------------------
        threads = []
        for fn in (run_hash, run_pe, run_yara, run_entropy, run_magic):
            t = threading.Thread(target=fn)
            t.daemon = True
            threads.append(t)
            t.start()
        for t in threads:
            t.join()

        # summarise -----------------------------------------------------------
        flagged = sum(1 for r in results if r["verdict"] in ("suspicious", "malicious"))
        ratio = f"{flagged}/{len(results)} engines flagged"

        # score using ThreatScorer ------------------------------------------------
        try:
            size = os.path.getsize(filepath)
        except OSError:
            size = 0

        verdict_obj = self.scorer.create_verdict(filepath, sha256=sha256,
                                                  md5=md5, file_size=size)

        # incorporate each engine's findings into the verdict
        for r in results:
            if r["engine"] == "HashDatabase":
                verdict_obj = self.scorer.add_hash_signal(verdict_obj, r.get("lookup"))
            elif r["engine"] == "PEAnalyzer":
                pe_res = r.get("pe_result")
                if isinstance(pe_res, PEAnalysisResult):
                    verdict_obj = self.scorer.add_pe_signal(verdict_obj, pe_res)
            elif r["engine"] == "Entropy":
                ent = r.get("entropy", 0.0)
                if ent > 7.0:
                    verdict_obj.signals.append(ThreatSignal(
                        signal_type="entropy_high",
                        description=f"High entropy ({ent:.2f})",
                        severity="medium",
                        weight=SIGNAL_WEIGHTS.get("high_entropy", 20.0),
                        source="MultiEngine",
                    ))
            elif r["engine"] == "MagicBytes":
                if "masquerading" in r.get("detail", ""):
                    verdict_obj.signals.append(ThreatSignal(
                        signal_type="extension_mismatch",
                        description=r.get("detail", ""),
                        severity="high",
                        weight=SIGNAL_WEIGHTS.get("extension_mismatch", 40.0),
                        source="MultiEngine",
                    ))
            elif r["engine"] == "DeepMalwareScanner":
                if r.get("verdict") == "malicious":
                    for m in r.get("matches", []):
                        verdict_obj.signals.append(ThreatSignal(
                            signal_type="yara_match",
                            description=f"YARA rule matched: {m}",
                            severity="high",
                            weight=SIGNAL_WEIGHTS.get("yara_high", 45.0),
                            source="MultiEngine",
                        ))

        verdict_obj = self.scorer.finalize(verdict_obj)

        return MultiScanResult(
            ratio=ratio,
            score=verdict_obj.threat_score,
            threat_level=verdict_obj.threat_level,
            malware_family=verdict_obj.malware_family,
            per_engine_results=results,
        )

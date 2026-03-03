"""
Servos – Unified Threat Scoring Engine.
Aggregates all detection signals into a single 0-100 threat score per file,
similar to VirusTotal's detection ratio.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional


@dataclass
class ThreatSignal:
    """A single detection signal contributing to the threat score."""
    signal_type: str      # hash_match, pe_anomaly, yara_match, entropy, extension, name, pe_import
    description: str
    severity: str = "low"  # low, medium, high, critical
    weight: float = 0.0    # Contribution to score
    source: str = ""       # Which engine detected this


@dataclass
class ThreatVerdict:
    """Per-file threat assessment — the final verdict."""
    filepath: str
    filename: str = ""
    sha256: str = ""
    md5: str = ""
    threat_score: float = 0.0         # 0-100
    threat_level: str = "CLEAN"       # CLEAN, LOW, MEDIUM, HIGH, CRITICAL
    signals: List[ThreatSignal] = field(default_factory=list)
    hash_verdict: str = "UNKNOWN"     # KNOWN_MALICIOUS, KNOWN_CLEAN, UNKNOWN
    malware_family: str = ""
    is_pe: bool = False
    is_packed: bool = False
    packer_name: str = ""
    file_size: int = 0
    entropy: float = 0.0

    @property
    def signal_count(self) -> int:
        return len(self.signals)

    @property
    def critical_signals(self) -> List[ThreatSignal]:
        return [s for s in self.signals if s.severity == "critical"]

    @property
    def high_signals(self) -> List[ThreatSignal]:
        return [s for s in self.signals if s.severity == "high"]

    def to_dict(self) -> dict:
        return {
            "filepath": self.filepath,
            "filename": self.filename,
            "sha256": self.sha256,
            "threat_score": round(self.threat_score, 1),
            "threat_level": self.threat_level,
            "signal_count": self.signal_count,
            "hash_verdict": self.hash_verdict,
            "malware_family": self.malware_family,
            "is_pe": self.is_pe,
            "is_packed": self.is_packed,
            "signals": [
                {"type": s.signal_type, "description": s.description,
                 "severity": s.severity, "weight": s.weight}
                for s in self.signals
            ],
        }


@dataclass
class ScanSummary:
    """Overall scan summary with risk distribution."""
    total_files: int = 0
    files_scanned: int = 0
    scan_errors: int = 0

    clean_count: int = 0
    low_count: int = 0
    medium_count: int = 0
    high_count: int = 0
    critical_count: int = 0

    known_malicious: int = 0
    known_clean: int = 0
    unknown: int = 0

    packed_files: int = 0
    pe_files: int = 0

    top_threats: List[ThreatVerdict] = field(default_factory=list)
    overall_risk: str = "LOW"       # LOW, MEDIUM, HIGH, CRITICAL

    malware_families_found: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "total_files": self.total_files,
            "files_scanned": self.files_scanned,
            "risk_distribution": {
                "clean": self.clean_count,
                "low": self.low_count,
                "medium": self.medium_count,
                "high": self.high_count,
                "critical": self.critical_count,
            },
            "hash_results": {
                "known_malicious": self.known_malicious,
                "known_clean": self.known_clean,
                "unknown": self.unknown,
            },
            "packed_files": self.packed_files,
            "pe_files": self.pe_files,
            "overall_risk": self.overall_risk,
            "malware_families": self.malware_families_found,
            "top_threats": [t.to_dict() for t in self.top_threats[:10]],
        }


# ── Signal Weights ───────────────────────────────────────────
# Higher weight = stronger indicator of malware

SIGNAL_WEIGHTS = {
    # Hash-based (strongest signal)
    "hash_malicious":       90.0,

    # PE analysis
    "pe_packed":            30.0,
    "pe_suspicious_import": 8.0,   # Per import, capped
    "pe_anomaly":           12.0,  # Per anomaly, capped
    "pe_suspicious_section": 10.0,

    # Pattern matching
    "yara_critical":        60.0,
    "yara_high":            45.0,
    "yara_medium":          25.0,
    "yara_low":             10.0,

    # File anomalies
    "extension_mismatch":   40.0,
    "double_extension":     35.0,
    "high_entropy":         20.0,
    "suspicious_name":      15.0,
    "ads_detected":         25.0,

    # Bonus: known clean reduces score
    "hash_clean":          -30.0,
}


class ThreatScorer:
    """
    Aggregate detection signals into a unified threat score.

    Usage:
        scorer = ThreatScorer()
        verdict = scorer.create_verdict("path/to/file.exe")

        # Add signals from different engines
        verdict = scorer.add_hash_signal(verdict, hash_result)
        verdict = scorer.add_pe_signal(verdict, pe_result)
        verdict = scorer.add_yara_signal(verdict, yara_indicators)

        # Finalize
        verdict = scorer.finalize(verdict)
    """

    def create_verdict(self, filepath: str, **kwargs) -> ThreatVerdict:
        """Create a new empty verdict for a file."""
        import os
        return ThreatVerdict(
            filepath=filepath,
            filename=os.path.basename(filepath),
            sha256=kwargs.get("sha256", ""),
            md5=kwargs.get("md5", ""),
            file_size=kwargs.get("file_size", 0),
        )

    def add_hash_signal(self, verdict: ThreatVerdict, hash_result) -> ThreatVerdict:
        """Add hash database lookup signal."""
        if hash_result.verdict == "KNOWN_MALICIOUS":
            verdict.hash_verdict = "KNOWN_MALICIOUS"
            verdict.malware_family = hash_result.malware_family
            verdict.signals.append(ThreatSignal(
                signal_type="hash_match",
                description=f"Known malware: {hash_result.malware_family} "
                            f"(source: {hash_result.source})",
                severity="critical",
                weight=SIGNAL_WEIGHTS["hash_malicious"],
                source="HashDatabase",
            ))
        elif hash_result.verdict == "KNOWN_CLEAN":
            verdict.hash_verdict = "KNOWN_CLEAN"
            verdict.signals.append(ThreatSignal(
                signal_type="hash_clean",
                description="Known clean file",
                severity="low",
                weight=SIGNAL_WEIGHTS["hash_clean"],
                source="HashDatabase",
            ))
        return verdict

    def add_pe_signal(self, verdict: ThreatVerdict, pe_result) -> ThreatVerdict:
        """Add PE analysis signals."""
        if not pe_result.is_valid_pe:
            return verdict

        verdict.is_pe = True

        # Packer detection
        if pe_result.is_packed:
            verdict.is_packed = True
            verdict.packer_name = pe_result.packer_name
            verdict.signals.append(ThreatSignal(
                signal_type="pe_packed",
                description=f"Packed with: {pe_result.packer_name}",
                severity="medium",
                weight=SIGNAL_WEIGHTS["pe_packed"],
                source="PEAnalyzer",
            ))

        # Suspicious imports (cap at 5 signals max)
        for i, imp_desc in enumerate(pe_result.suspicious_imports[:5]):
            verdict.signals.append(ThreatSignal(
                signal_type="pe_suspicious_import",
                description=imp_desc,
                severity="high",
                weight=SIGNAL_WEIGHTS["pe_suspicious_import"],
                source="PEAnalyzer",
            ))

        # Anomalies (cap at 3 signals max)
        for anomaly in pe_result.anomalies[:3]:
            verdict.signals.append(ThreatSignal(
                signal_type="pe_anomaly",
                description=anomaly,
                severity="medium",
                weight=SIGNAL_WEIGHTS["pe_anomaly"],
                source="PEAnalyzer",
            ))

        # Suspicious sections
        for sec_desc in pe_result.suspicious_sections[:3]:
            verdict.signals.append(ThreatSignal(
                signal_type="pe_suspicious_section",
                description=sec_desc,
                severity="medium",
                weight=SIGNAL_WEIGHTS["pe_suspicious_section"],
                source="PEAnalyzer",
            ))

        return verdict

    def add_yara_signal(self, verdict: ThreatVerdict, indicators: list) -> ThreatVerdict:
        """Add YARA-like pattern match signals."""
        for indicator in indicators:
            severity = getattr(indicator, "severity", "medium")
            weight_key = f"yara_{severity}"
            weight = SIGNAL_WEIGHTS.get(weight_key, SIGNAL_WEIGHTS["yara_medium"])

            verdict.signals.append(ThreatSignal(
                signal_type="yara_match",
                description=f"[{getattr(indicator, 'rule_name', 'Unknown')}] "
                            f"{getattr(indicator, 'description', '')}",
                severity=severity,
                weight=weight,
                source="YARAEngine",
            ))
        return verdict

    def add_file_signal(self, verdict: ThreatVerdict,
                        signal_type: str, description: str,
                        severity: str = "medium") -> ThreatVerdict:
        """Add a generic file-based signal (entropy, extension mismatch, etc.)."""
        weight = SIGNAL_WEIGHTS.get(signal_type, 10.0)
        verdict.signals.append(ThreatSignal(
            signal_type=signal_type,
            description=description,
            severity=severity,
            weight=weight,
            source="FileAnalyzer",
        ))
        return verdict

    def finalize(self, verdict: ThreatVerdict) -> ThreatVerdict:
        """Calculate final threat score and level from accumulated signals."""
        raw_score = sum(s.weight for s in verdict.signals)

        # Clamp to 0-100
        verdict.threat_score = max(0.0, min(100.0, raw_score))

        # Determine threat level
        if verdict.threat_score >= 80:
            verdict.threat_level = "CRITICAL"
        elif verdict.threat_score >= 55:
            verdict.threat_level = "HIGH"
        elif verdict.threat_score >= 30:
            verdict.threat_level = "MEDIUM"
        elif verdict.threat_score >= 10:
            verdict.threat_level = "LOW"
        else:
            verdict.threat_level = "CLEAN"

        # Override: hash match = always at least HIGH
        if verdict.hash_verdict == "KNOWN_MALICIOUS" and verdict.threat_level not in ("CRITICAL",):
            verdict.threat_level = "CRITICAL"
            verdict.threat_score = max(verdict.threat_score, 90.0)

        return verdict

    def create_summary(self, verdicts: List[ThreatVerdict]) -> ScanSummary:
        """Create an overall scan summary from a list of verdicts."""
        summary = ScanSummary()
        summary.total_files = len(verdicts)
        summary.files_scanned = len(verdicts)

        families = set()

        for v in verdicts:
            # Risk distribution
            if v.threat_level == "CLEAN":
                summary.clean_count += 1
            elif v.threat_level == "LOW":
                summary.low_count += 1
            elif v.threat_level == "MEDIUM":
                summary.medium_count += 1
            elif v.threat_level == "HIGH":
                summary.high_count += 1
            elif v.threat_level == "CRITICAL":
                summary.critical_count += 1

            # Hash status
            if v.hash_verdict == "KNOWN_MALICIOUS":
                summary.known_malicious += 1
            elif v.hash_verdict == "KNOWN_CLEAN":
                summary.known_clean += 1
            else:
                summary.unknown += 1

            # PE stats
            if v.is_pe:
                summary.pe_files += 1
            if v.is_packed:
                summary.packed_files += 1

            # Track families
            if v.malware_family:
                families.add(v.malware_family)

        summary.malware_families_found = sorted(families)

        # Top threats (sorted by score desc)
        summary.top_threats = sorted(verdicts, key=lambda v: v.threat_score, reverse=True)[:10]

        # Overall risk
        if summary.critical_count > 0:
            summary.overall_risk = "CRITICAL"
        elif summary.high_count > 0:
            summary.overall_risk = "HIGH"
        elif summary.medium_count > 0:
            summary.overall_risk = "MEDIUM"
        elif summary.low_count > 0:
            summary.overall_risk = "LOW"
        else:
            summary.overall_risk = "CLEAN"

        return summary

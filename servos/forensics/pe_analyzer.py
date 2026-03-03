"""
Servos – PE (Portable Executable) Analyzer.
Pure-Python PE header parsing for malware triage — no external dependencies.
Detects suspicious imports, packing, section anomalies, and embedded executables.
"""

import os
import struct
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple


# ── Data Models ──────────────────────────────────────────────

@dataclass
class PESection:
    """A single PE section."""
    name: str
    virtual_size: int = 0
    virtual_address: int = 0
    raw_size: int = 0
    raw_offset: int = 0
    characteristics: int = 0
    entropy: float = 0.0

    @property
    def is_executable(self) -> bool:
        return bool(self.characteristics & 0x20000000)

    @property
    def is_writable(self) -> bool:
        return bool(self.characteristics & 0x80000000)

    @property
    def is_readable(self) -> bool:
        return bool(self.characteristics & 0x40000000)


@dataclass
class PEImport:
    """An imported DLL and its functions."""
    dll_name: str
    functions: List[str] = field(default_factory=list)


@dataclass
class PEAnalysisResult:
    """Complete PE analysis result."""
    is_valid_pe: bool = False
    is_64bit: bool = False
    machine_type: str = "UNKNOWN"
    subsystem: str = "UNKNOWN"
    entry_point: int = 0
    image_base: int = 0
    file_size: int = 0
    compile_timestamp: int = 0
    compile_date: str = ""

    sections: List[PESection] = field(default_factory=list)
    imports: List[PEImport] = field(default_factory=list)

    # Detection flags
    is_packed: bool = False
    packer_name: str = ""
    suspicious_imports: List[str] = field(default_factory=list)
    suspicious_sections: List[str] = field(default_factory=list)
    anomalies: List[str] = field(default_factory=list)

    # Scoring
    risk_score: float = 0.0  # 0-100

    def to_dict(self) -> dict:
        return {
            "is_valid_pe": self.is_valid_pe,
            "is_64bit": self.is_64bit,
            "machine_type": self.machine_type,
            "subsystem": self.subsystem,
            "entry_point": hex(self.entry_point),
            "image_base": hex(self.image_base),
            "compile_date": self.compile_date,
            "sections": [s.name for s in self.sections],
            "imports_count": sum(len(i.functions) for i in self.imports),
            "is_packed": self.is_packed,
            "packer_name": self.packer_name,
            "suspicious_imports": self.suspicious_imports,
            "suspicious_sections": self.suspicious_sections,
            "anomalies": self.anomalies,
            "risk_score": self.risk_score,
        }


# ── Constants ────────────────────────────────────────────────

# Suspicious API imports commonly used by malware
DANGEROUS_IMPORTS = {
    # Process injection
    "createremotethread": "Process injection – creates thread in another process",
    "writeprocessmemory": "Process injection – writes to another process's memory",
    "virtualallocex": "Remote memory allocation in another process",
    "ntcreatethreadex": "Undocumented thread creation (evasion)",
    "rtlcreateuserthread": "Low-level thread creation (evasion)",
    "queueuserapc": "APC injection technique",
    "ntqueueapcthread": "Undocumented APC injection",
    "setthreadcontext": "Thread context manipulation (injection)",

    # Code execution
    "shellexecutea": "Execute arbitrary commands",
    "shellexecutew": "Execute arbitrary commands (wide)",
    "winexec": "Execute arbitrary commands",
    "createprocessa": "Launch new processes",
    "createprocessw": "Launch new processes (wide)",

    # Credential & memory access
    "lsaenumeratelogonsessions": "Enumerate logon sessions (credential theft)",
    "minidumpwritedump": "Create process memory dump (credential extraction)",
    "openprocesstoken": "Access process security token",
    "adjusttokenprivileges": "Elevate process privileges",
    "lookupprivilegevaluea": "Privilege escalation preparation",

    # Evasion & anti-analysis
    "isdebuggerpresent": "Anti-debugging check",
    "checkremotedebuggerpresent": "Anti-debugging check",
    "ntqueryinformationprocess": "Anti-debugging / anti-VM check",
    "gettickcount": "Timing-based anti-analysis",
    "sleep": "Potential sandbox evasion (delayed execution)",
    "virtualprotect": "Change memory page protection (code injection prep)",

    # Network
    "urldownloadtofilea": "Download file from URL",
    "urldownloadtofilew": "Download file from URL (wide)",
    "internetopena": "Open internet connection",
    "internetopenurla": "Fetch URL content",
    "httpopenrequesta": "HTTP request",
    "httpsendrequesta": "Send HTTP data",
    "wsastartup": "Initialize Winsock (network activity)",
    "connect": "Network socket connection",
    "send": "Send data over network",
    "recv": "Receive network data",

    # File system manipulation
    "deletefilea": "Delete files (evidence destruction)",
    "movefileexa": "Move/rename files",
    "findfirstfilea": "File enumeration / search",
    "findresourceexa": "Access embedded resources",

    # Registry manipulation
    "regopenkeyexa": "Open registry key",
    "regsetvalexa": "Set registry value (persistence)",
    "regcreatekeyexa": "Create registry key (persistence)",

    # Service manipulation
    "createservicea": "Create Windows service (persistence)",
    "openscmanagera": "Access Service Control Manager",
    "startservicea": "Start a Windows service",

    # Crypto
    "cryptencrypt": "Encryption (possible ransomware)",
    "cryptdecrypt": "Decryption operations",
    "cryptgenkey": "Generate encryption key",
    "cryptacquirecontexta": "Initialize crypto provider",
}

# Known packer section names
PACKER_SIGNATURES = {
    ".upx0":    "UPX",
    ".upx1":    "UPX",
    ".upx2":    "UPX",
    "upx0":     "UPX",
    "upx1":     "UPX",
    ".aspack":  "ASPack",
    ".adata":   "ASPack",
    ".nsp0":    "NsPack",
    ".nsp1":    "NsPack",
    ".nsp2":    "NsPack",
    ".mpress1": "MPRESS",
    ".mpress2": "MPRESS",
    ".themida": "Themida",
    ".vmp0":    "VMProtect",
    ".vmp1":    "VMProtect",
    ".vmp2":    "VMProtect",
    ".enigma1": "Enigma Protector",
    ".enigma2": "Enigma Protector",
    ".petite":  "Petite",
    ".yp":      "Y0da Protector",
    ".seau":    "SeauSFX",
    ".perplex": "Perplex PE Protector",
    ".pecompact2": "PECompact",
    ".pec2":    "PECompact",
    "pebundle":  "PEBundle",
    ".rsrc":    None,  # Not a packer, but skip
}

# Machine type constants
MACHINE_TYPES = {
    0x14c:  "i386 (32-bit)",
    0x8664: "AMD64 (64-bit)",
    0x1c0:  "ARM",
    0x1c4:  "ARMv7",
    0xaa64: "ARM64",
    0x200:  "IA-64",
}

SUBSYSTEM_NAMES = {
    0:  "Unknown",
    1:  "Native",
    2:  "Windows GUI",
    3:  "Windows Console",
    7:  "POSIX Console",
    9:  "Windows CE",
    10: "EFI Application",
    14: "Xbox",
}


# ── PE Analyzer ──────────────────────────────────────────────

class PEAnalyzer:
    """Analyze PE files for malware indicators using pure-Python struct parsing."""

    def analyze(self, filepath: str) -> PEAnalysisResult:
        """Perform full PE analysis on a file."""
        result = PEAnalysisResult()

        try:
            result.file_size = os.path.getsize(filepath)
        except OSError:
            return result

        try:
            with open(filepath, "rb") as f:
                data = f.read(min(result.file_size, 10 * 1024 * 1024))  # Cap at 10MB
        except (PermissionError, OSError):
            return result

        if len(data) < 64:
            return result

        # ── DOS Header ──
        if data[:2] != b"MZ":
            return result

        try:
            pe_offset = struct.unpack_from("<I", data, 0x3C)[0]
        except struct.error:
            return result

        if pe_offset + 24 > len(data):
            return result

        # ── PE Signature ──
        if data[pe_offset:pe_offset + 4] != b"PE\x00\x00":
            return result

        result.is_valid_pe = True

        # ── COFF Header ──
        coff_offset = pe_offset + 4
        try:
            machine = struct.unpack_from("<H", data, coff_offset)[0]
            num_sections = struct.unpack_from("<H", data, coff_offset + 2)[0]
            timestamp = struct.unpack_from("<I", data, coff_offset + 4)[0]
            optional_size = struct.unpack_from("<H", data, coff_offset + 16)[0]
        except struct.error:
            return result

        result.machine_type = MACHINE_TYPES.get(machine, f"Unknown (0x{machine:x})")
        result.is_64bit = machine == 0x8664
        result.compile_timestamp = timestamp

        # Convert timestamp to human-readable
        import datetime
        try:
            result.compile_date = datetime.datetime.utcfromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S UTC")
        except (OSError, ValueError, OverflowError):
            result.compile_date = "Invalid"

        # ── Optional Header ──
        opt_offset = coff_offset + 20
        if opt_offset + 2 > len(data):
            return result

        magic = struct.unpack_from("<H", data, opt_offset)[0]
        is_pe32_plus = magic == 0x20b  # PE32+ (64-bit)

        try:
            if is_pe32_plus:
                result.entry_point = struct.unpack_from("<I", data, opt_offset + 16)[0]
                result.image_base = struct.unpack_from("<Q", data, opt_offset + 24)[0]
                subsystem_off = opt_offset + 68
            else:
                result.entry_point = struct.unpack_from("<I", data, opt_offset + 16)[0]
                result.image_base = struct.unpack_from("<I", data, opt_offset + 28)[0]
                subsystem_off = opt_offset + 68

            if subsystem_off + 2 <= len(data):
                subsystem = struct.unpack_from("<H", data, subsystem_off)[0]
                result.subsystem = SUBSYSTEM_NAMES.get(subsystem, f"Unknown({subsystem})")
        except struct.error:
            pass

        # ── Sections ──
        section_offset = opt_offset + optional_size
        for i in range(min(num_sections, 96)):  # Cap sections
            s_off = section_offset + i * 40
            if s_off + 40 > len(data):
                break

            try:
                name_raw = data[s_off:s_off + 8].rstrip(b"\x00").decode("ascii", errors="replace")
                vsize = struct.unpack_from("<I", data, s_off + 8)[0]
                vaddr = struct.unpack_from("<I", data, s_off + 12)[0]
                raw_size = struct.unpack_from("<I", data, s_off + 16)[0]
                raw_offset = struct.unpack_from("<I", data, s_off + 20)[0]
                chars = struct.unpack_from("<I", data, s_off + 36)[0]
            except struct.error:
                continue

            section = PESection(
                name=name_raw,
                virtual_size=vsize,
                virtual_address=vaddr,
                raw_size=raw_size,
                raw_offset=raw_offset,
                characteristics=chars,
            )

            # Calculate section entropy
            if raw_offset + raw_size <= len(data) and raw_size > 0:
                section_data = data[raw_offset:raw_offset + raw_size]
                section.entropy = self._calculate_entropy(section_data)

            result.sections.append(section)

        # ── Import Directory ──
        self._parse_imports(data, result, opt_offset, is_pe32_plus)

        # ── Detection Checks ──
        self._check_packers(result)
        self._check_suspicious_imports(result)
        self._check_anomalies(result, data)
        self._calculate_risk_score(result)

        return result

    def _parse_imports(self, data: bytes, result: PEAnalysisResult,
                       opt_offset: int, is_pe32_plus: bool):
        """Parse the import directory table."""
        try:
            # Data directory offset for imports
            if is_pe32_plus:
                dd_offset = opt_offset + 120  # Import table RVA in PE32+
            else:
                dd_offset = opt_offset + 104  # Import table RVA in PE32

            if dd_offset + 8 > len(data):
                return

            import_rva = struct.unpack_from("<I", data, dd_offset)[0]
            import_size = struct.unpack_from("<I", data, dd_offset + 4)[0]

            if import_rva == 0 or import_size == 0:
                return

            # Convert RVA to file offset
            import_offset = self._rva_to_offset(import_rva, result.sections)
            if import_offset is None or import_offset >= len(data):
                return

            # Parse Import Directory entries (20 bytes each)
            idx = 0
            while True:
                entry_off = import_offset + idx * 20
                if entry_off + 20 > len(data):
                    break

                ilt_rva = struct.unpack_from("<I", data, entry_off)[0]
                name_rva = struct.unpack_from("<I", data, entry_off + 12)[0]

                if ilt_rva == 0 and name_rva == 0:
                    break

                # Read DLL name
                name_off = self._rva_to_offset(name_rva, result.sections)
                if name_off and name_off < len(data):
                    end = data.find(b"\x00", name_off, min(name_off + 256, len(data)))
                    if end == -1:
                        end = min(name_off + 256, len(data))
                    dll_name = data[name_off:end].decode("ascii", errors="replace")
                else:
                    dll_name = "UNKNOWN"

                pe_import = PEImport(dll_name=dll_name)

                # Parse imported functions from ILT
                ilt_off = self._rva_to_offset(ilt_rva, result.sections)
                if ilt_off and ilt_off < len(data):
                    func_idx = 0
                    entry_size = 8 if is_pe32_plus else 4
                    while func_idx < 500:  # Cap functions per DLL
                        f_off = ilt_off + func_idx * entry_size
                        if f_off + entry_size > len(data):
                            break

                        if is_pe32_plus:
                            thunk = struct.unpack_from("<Q", data, f_off)[0]
                            ordinal_flag = 1 << 63
                        else:
                            thunk = struct.unpack_from("<I", data, f_off)[0]
                            ordinal_flag = 1 << 31

                        if thunk == 0:
                            break

                        if thunk & ordinal_flag:
                            pe_import.functions.append(f"Ordinal_{thunk & 0xFFFF}")
                        else:
                            hint_off = self._rva_to_offset(thunk & 0x7FFFFFFF, result.sections)
                            if hint_off and hint_off + 2 < len(data):
                                fname_start = hint_off + 2
                                fname_end = data.find(b"\x00", fname_start, min(fname_start + 256, len(data)))
                                if fname_end == -1:
                                    fname_end = min(fname_start + 256, len(data))
                                func_name = data[fname_start:fname_end].decode("ascii", errors="replace")
                                pe_import.functions.append(func_name)

                        func_idx += 1

                result.imports.append(pe_import)
                idx += 1
                if idx > 200:  # Cap DLLs
                    break

        except (struct.error, Exception):
            pass

    def _rva_to_offset(self, rva: int, sections: List[PESection]) -> Optional[int]:
        """Convert RVA to file offset using section table."""
        for section in sections:
            if section.virtual_address <= rva < section.virtual_address + max(section.virtual_size, section.raw_size):
                return rva - section.virtual_address + section.raw_offset
        return None

    def _check_packers(self, result: PEAnalysisResult):
        """Detect known packers by section names."""
        for section in result.sections:
            name_lower = section.name.lower().strip()
            if name_lower in PACKER_SIGNATURES:
                packer = PACKER_SIGNATURES[name_lower]
                if packer:
                    result.is_packed = True
                    result.packer_name = packer
                    result.suspicious_sections.append(
                        f"Packer detected: {packer} (section: {section.name})")
                    break

        # Heuristic: very high entropy on code section suggests packing
        for section in result.sections:
            if section.is_executable and section.entropy > 7.0 and section.raw_size > 1024:
                if not result.is_packed:
                    result.is_packed = True
                    result.packer_name = "Unknown (high entropy)"
                result.suspicious_sections.append(
                    f"High entropy executable section: {section.name} ({section.entropy:.2f})")

    def _check_suspicious_imports(self, result: PEAnalysisResult):
        """Flag dangerous API imports."""
        for imp in result.imports:
            for func in imp.functions:
                func_lower = func.lower()
                if func_lower in DANGEROUS_IMPORTS:
                    result.suspicious_imports.append(
                        f"{imp.dll_name}:{func} — {DANGEROUS_IMPORTS[func_lower]}")

    def _check_anomalies(self, result: PEAnalysisResult, data: bytes):
        """Check for structural anomalies."""
        # Entry point outside any section
        ep = result.entry_point
        ep_in_section = False
        for section in result.sections:
            if section.virtual_address <= ep < section.virtual_address + section.virtual_size:
                ep_in_section = True
                # Entry in writable section is suspicious
                if section.is_writable and section.is_executable:
                    result.anomalies.append(
                        f"Entry point in writable+executable section: {section.name}")
                break

        if not ep_in_section and result.sections:
            result.anomalies.append("Entry point outside all defined sections")

        # Sections with zero raw size but non-zero virtual size
        for section in result.sections:
            if section.raw_size == 0 and section.virtual_size > 0 and section.name != ".bss":
                result.anomalies.append(
                    f"Section {section.name} has zero raw size but virtual size {section.virtual_size}")

        # Very old or future compile date
        import datetime
        if result.compile_timestamp > 0:
            try:
                compile_dt = datetime.datetime.utcfromtimestamp(result.compile_timestamp)
                now = datetime.datetime.utcnow()
                if compile_dt.year < 2000:
                    result.anomalies.append(f"Suspiciously old compile date: {result.compile_date}")
                if compile_dt > now:
                    result.anomalies.append(f"Future compile date: {result.compile_date}")
            except (OSError, ValueError, OverflowError):
                result.anomalies.append("Invalid/corrupt compile timestamp")

        # Executable with no imports (possibly packed or shellcode)
        total_funcs = sum(len(i.functions) for i in result.imports)
        if total_funcs == 0 and result.file_size > 4096:
            result.anomalies.append("No imported functions (possibly packed or shellcode)")

        # Check for embedded MZ headers (indicates embedded PE)
        mz_count = data.count(b"MZ")
        if mz_count > 2:
            result.anomalies.append(f"Multiple MZ headers found ({mz_count}) — possible embedded executables")

        # Double extension in the filename
        # (Caller should pass the filepath for this, but we check sections for TLS)
        for section in result.sections:
            if section.name.lower().strip() == ".tls":
                result.anomalies.append("TLS callback section present (anti-debugging / initialization hijack)")

    def _calculate_risk_score(self, result: PEAnalysisResult):
        """Calculate overall PE risk score (0-100)."""
        score = 0.0

        # Packer detection
        if result.is_packed:
            score += 25.0

        # Suspicious imports (capped at 40)
        import_score = min(len(result.suspicious_imports) * 5.0, 40.0)
        score += import_score

        # Anomalies (capped at 25)
        anomaly_score = min(len(result.anomalies) * 8.0, 25.0)
        score += anomaly_score

        # Suspicious sections
        if result.suspicious_sections:
            score += min(len(result.suspicious_sections) * 5.0, 10.0)

        result.risk_score = min(score, 100.0)

    @staticmethod
    def _calculate_entropy(data: bytes) -> float:
        """Calculate Shannon entropy of raw bytes."""
        import math
        if not data:
            return 0.0

        byte_counts = [0] * 256
        for b in data:
            byte_counts[b] += 1

        total = len(data)
        entropy = 0.0
        for count in byte_counts:
            if count == 0:
                continue
            p = count / total
            entropy -= p * math.log2(p)
        return round(entropy, 2)

    def is_pe_file(self, filepath: str) -> bool:
        """Quick check if a file is a PE executable."""
        try:
            with open(filepath, "rb") as f:
                header = f.read(2)
                if header != b"MZ":
                    return False
                f.seek(0x3C)
                pe_offset_bytes = f.read(4)
                if len(pe_offset_bytes) < 4:
                    return False
                pe_offset = struct.unpack("<I", pe_offset_bytes)[0]
                f.seek(pe_offset)
                sig = f.read(4)
                return sig == b"PE\x00\x00"
        except (PermissionError, OSError):
            return False

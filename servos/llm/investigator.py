"""
Servos – LLM-Powered Investigation Guidance.
Connects to Ollama for offline AI-driven forensic reasoning.
Falls back to rule-based suggestions if LLM is unavailable.
"""

import os
import json
from typing import List, Optional, Dict, Any

from servos.config import get_config


class LLMInvestigator:
    """Offline LLM-powered investigation assistant."""

    def __init__(self, model: Optional[str] = None, base_url: Optional[str] = None):
        cfg = get_config()
        self.model = model or cfg.get("llm_model", "llama3.1:8b")
        self.base_url = base_url or cfg.get("llm_base_url", "http://localhost:11434")
        self.timeout = cfg.get("llm_timeout", 30)
        self._client = None
        self._available = None

    # ------------------------------------------------------------------
    # Connection
    # ------------------------------------------------------------------

    def is_available(self) -> bool:
        """Check if the LLM backend is reachable."""
        if self._available is not None:
            return self._available
        try:
            import ollama
            self._client = ollama.Client(host=self.base_url)
            self._client.list()
            self._available = True
        except Exception:
            self._available = False
        return self._available

    def _generate(self, prompt: str) -> str:
        """Send a prompt to the LLM and return the response text."""
        if not self.is_available():
            return ""
        try:
            import ollama
            if self._client is None:
                self._client = ollama.Client(host=self.base_url)
            response = self._client.generate(model=self.model, prompt=prompt)
            return response.get("response", "")
        except Exception as e:
            return f"[LLM Error: {e}]"

    # ------------------------------------------------------------------
    # General-Purpose Conversational Chat
    # ------------------------------------------------------------------

    CHAT_SYSTEM_CONTEXT = (
        "You are Servos AI, a helpful, knowledgeable, and friendly AI assistant. "
        "You engage in natural, thoughtful conversations on any topic. "
        "You understand context from the ongoing conversation and respond appropriately. "
        "Be concise yet thorough. Use a warm, professional tone. "
        "If you don't know something, say so honestly. "
        "Format responses with markdown when it improves readability."
    )

    def chat(self, message: str, history: list = None, active_case: Optional[Case] = None) -> str:
        """General-purpose multi-turn conversational chat.

        If *active_case* is provided it will be prepended as system context so the
        model can answer questions about the investigator's current evidence.
        """
        # Build conversation context from history
        history_block = ""
        if history:
            for msg in history[-10:]:  # Last 10 messages for context window
                role = msg.get("role", "user").capitalize()
                content = msg.get("content", "")
                history_block += f"{role}: {content}\n"

        system_ctx = self.CHAT_SYSTEM_CONTEXT
        if active_case:
            top_files = []
            if active_case.findings and active_case.findings.file_system:
                for f in active_case.findings.file_system.suspicious_files[:3]:
                    top_files.append(os.path.basename(f.full_path))
            families = []
            if active_case.findings and active_case.findings.malware:
                for ind in active_case.findings.malware.indicators:
                    if ind.indicator_type == "hash_match":
                        families.append(ind.description)
            fam_txt = ", ".join(families[:3])
            system_ctx += (
                f"\nActive Case: {active_case.id} | Device: "
                f"{active_case.device_info.name if active_case.device_info else 'unknown'} | "
                f"Risk: {active_case.findings.malware.risk_level if active_case.findings and active_case.findings.malware else 'UNKNOWN'} | "
                f"Top threats: {', '.join(top_files)} | Families: {fam_txt}"
            )

        if self.is_available():
            prompt = f"""{system_ctx}

{"--- CONVERSATION HISTORY ---" + chr(10) + history_block + "--- END HISTORY ---" + chr(10) if history_block else ""}
User: {message}

Respond naturally and helpfully:"""
            response = self._generate(prompt)
            if response and not response.startswith("[LLM Error"):
                return response.strip()

        # Fallback: rule-based conversational responses
        return self._fallback_chat(message)

    @staticmethod
    def _fallback_chat(message: str) -> str:
        """Provide helpful responses when LLM is unavailable."""
        msg_lower = message.lower()

        # common greetings
        if any(w in msg_lower for w in ["hello", "hi", "hey", "greetings"]):
            return "Hello! I'm Servos AI running in offline mode. How can I help with your investigation today?"

        if any(w in msg_lower for w in ["help", "what can you do", "capabilities"]):
            return ("I can answer basic forensic questions even without a language model. "
                    "Ask me about entropy, packing, browser artifacts, logs, or general investigation workflow.")

        if "entropy" in msg_lower:
            return ("Entropy measures randomness in a file. Values near 8.0 often indicate packed, encrypted, or compressed data, which can be a sign of malware or hidden content.")
        if "packed" in msg_lower or "packing" in msg_lower:
            return ("Packing is a technique where an executable compresses or encrypts itself to evade detection. Unpacking it during analysis reveals the true code. High entropy is often associated with packers.")
        if "browser" in msg_lower:
            return ("Browser artifacts like history and cookies can show visited domains and potential data exfiltration vectors; they are crucial for timeline reconstruction.")
        if "malware" in msg_lower:
            return ("Malware is software designed to harm or exploit. Common indicators include unusual file hashes, high entropy, and suspicious network connections.")
        if "hash" in msg_lower:
            return ("A hash (MD5/SHA256) uniquely identifies a file's contents. Comparing hashes against known databases helps quickly flag known good or bad files.")
        if "timeline" in msg_lower:
            return ("A timeline orders system events chronologically, helping to identify suspicious bursts of activity or off-hours operations.")
        if "ransom" in msg_lower or "ransomware" in msg_lower:
            return ("Ransomware encrypts files and demands payment for the key. Look for file extensions like .locky or unusual mass file modifications.")
        if "log" in msg_lower:
            return ("Log files record system and application events. Parsing them for patterns like failed logins or encoded PowerShell helps detect intrusions.")
        if "registry" in msg_lower:
            return ("Windows registry artifacts record installed programs, USB history, and autoruns; they frequently reveal persistence mechanisms.")
        if "exfil" in msg_lower or "exfiltration" in msg_lower:
            return ("Data exfiltration refers to unauthorized transfer of data out of a system, often via HTTP uploads, FTP, or cloud services.")
        if "network" in msg_lower:
            return ("Network anomalies such as sudden spikes or communication with known bad domains can indicate C2 traffic or data theft.")

        # fallback generic
        return ("I'm running without a language model backend and can only provide basic forensic info. "
                "Try asking about entropy, packing, logs, or browser artifacts.")

    # ------------------------------------------------------------------
    # Investigation Guidance
    # ------------------------------------------------------------------

    SYSTEM_CONTEXT = (
        "You are Servos, an expert digital forensics assistant. "
        "You help investigators analyze evidence from storage devices. "
        "Be concise, specific, and actionable. "
        "Always prioritize evidence preservation and chain-of-custody."
    )

    def suggest_next_steps(self, findings: Dict[str, Any]) -> List[str]:
        """Suggest next investigation steps based on current findings."""
        ctx = self._build_rich_context(findings)
        if self.is_available():
            prompt = f"""{self.SYSTEM_CONTEXT}

{ctx}
Based on the above evidence, suggest 3-5 specific, actionable next steps for the investigator. Provide numbered recommendations:"""
            response = self._generate(prompt)
            if response and not response.startswith("[LLM Error"):
                return [line.strip() for line in response.strip().split("\n") if line.strip()]
        return self._rule_based_suggestions(findings)

    def ask_clarifying_question(self, finding_description: str) -> str:
        """Generate a clarifying question about a specific finding."""
        if self.is_available():
            prompt = f"""{self.SYSTEM_CONTEXT}

A forensic investigation has found the following:
"{finding_description}"

Ask ONE specific, helpful clarifying question to determine if this finding is malicious or benign. Be concise."""
            response = self._generate(prompt)
            if response and not response.startswith("[LLM Error"):
                return response.strip()

        # Fallback
        return f"Is this finding expected? Was '{finding_description}' present before the incident?"

    def interpret_artifacts(self, artifacts_summary: Dict[str, Any]) -> str:
        """Provide human-readable interpretation of extracted artifacts."""
        if self.is_available():
            prompt = f"""{self.SYSTEM_CONTEXT}

Interpret the following forensic artifacts. Provide a 2-3 sentence analysis of what they suggest about the device:

Artifacts:
{json.dumps(artifacts_summary, indent=2, default=str)[:3000]}

Interpretation:"""
            response = self._generate(prompt)
            if response and not response.startswith("[LLM Error"):
                return response.strip()

        # Fallback
        return self._rule_based_interpretation(artifacts_summary)

    def generate_summary(self, case_data: Dict[str, Any]) -> str:
        """Generate an executive summary for the investigation report."""
        ctx = self._build_rich_context(case_data.get("findings", {}))
        if self.is_available():
            prompt = f"""{self.SYSTEM_CONTEXT}

{ctx}
Write a professional executive summary (1 paragraph, 4-6 sentences) for a forensic investigation report based on the following case data:

{json.dumps(case_data, indent=2, default=str)[:4000]}

Executive Summary:"""
            response = self._generate(prompt)
            if response and not response.startswith("[LLM Error"):
                return response.strip()
        return self._rule_based_summary(case_data)

    # ------------------------------------------------------------------
    # Rule-based fallbacks
    # ------------------------------------------------------------------

    @staticmethod
    def _build_rich_context(self, findings: Dict[str, Any]) -> str:
        """Construct a rich context block summarizing key suspicious items."""
        parts: List[str] = []
        # top 5 suspicious files
        files = findings.get("file_system", {}).get("suspicious_files", [])
        if files:
            top = files[:5]
            entries = []
            for f in top:
                entries.append(f"{os.path.basename(f.get('full_path',''))} (entropy={f.get('entropy',0):.1f}, reason={f.get('suspicious_reason','')}, score={f.get('threat_score','N/A')})")
            parts.append("Top suspicious files:\n" + "\n".join(entries))
        # malware families
        malware = findings.get("malware", {}).get("indicators", [])
        families = {ind.get('description','') for ind in malware if ind.get('indicator_type') == 'hash_match'}
        if families:
            parts.append("Malware families detected: " + ", ".join(families))
        # browser domains
        browsers = findings.get("artifacts", {}).get("browser_history", [])
        bad_domains = [b.get('content', {}).get('url','') for b in browsers if b.get('suspicious_score',0) > 0.5]
        if bad_domains:
            parts.append("Suspicious domains: " + ", ".join(bad_domains[:10]))
        # timeline anomalies
        timeline = findings.get("timeline", {}).get("suspicious_windows", [])
        if timeline:
            parts.append("Timeline anomaly windows: " + ", ".join(f"{s}-{e}" for s,e in timeline))
        # risk level
        risk = findings.get("malware", {}).get("risk_level")
        if risk:
            parts.append(f"Current risk level: {risk}")
        return "\n\n".join(parts)

    def _rule_based_suggestions(findings: Dict) -> List[str]:
        suggestions = [
            "1. Review all suspicious files identified in the scan.",
            "2. Cross-reference file hashes with threat intelligence databases.",
            "3. Examine the activity timeline for unusual patterns.",
            "4. Check extracted artifacts for evidence of unauthorized access.",
            "5. Generate a comprehensive report and preserve evidence chain-of-custody.",
        ]

        # Add context-specific suggestions
        if findings.get("malware", {}).get("risk_level") in ("HIGH", "CRITICAL"):
            suggestions.insert(0, "⚠ CRITICAL: Malware indicators detected. Quarantine the device immediately.")
        if findings.get("artifacts", {}).get("browser_history"):
            suggestions.append("6. Review browser history for data exfiltration or suspicious domain access.")

        return suggestions

    @staticmethod
    def _rule_based_interpretation(artifacts: Dict) -> str:
        parts = []
        browser = artifacts.get("browser_history", [])
        recent = artifacts.get("recent_files", [])
        registry = artifacts.get("registry_items", [])

        if browser:
            parts.append(f"Browser history contains {len(browser)} entries; review for suspicious domains.")
        if recent:
            parts.append(f"{len(recent)} recently modified files found; check for unauthorized changes.")
        if registry:
            parts.append(f"Registry artifacts detected ({len(registry)} items); may indicate system-level modifications.")
        if not parts:
            parts.append("No significant artifacts extracted from this device.")

        return " ".join(parts)

    @staticmethod
    def _rule_based_summary(case_data: Dict) -> str:
        case_id = case_data.get("id", "UNKNOWN")
        device = case_data.get("device_info", {}).get("name", "Unknown device")
        status = case_data.get("status", "active")

        findings = case_data.get("findings", {})
        fs = findings.get("file_system", {})
        malware = findings.get("malware", {})

        total_files = fs.get("total_files", 0)
        suspicious = fs.get("suspicious_files", [])
        risk = malware.get("risk_level", "UNKNOWN")

        summary = (
            f"Investigation {case_id} examined a {device}. "
            f"A total of {total_files} files were analyzed. "
        )
        if suspicious:
            summary += f"{len(suspicious)} suspicious files were identified. "
        else:
            summary += "No immediately suspicious files were detected. "

        summary += f"Overall risk assessment: {risk}. "
        summary += "Evidence has been preserved with integrity hashes for chain-of-custody verification."

        return summary

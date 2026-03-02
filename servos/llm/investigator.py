"""
Servos – LLM-Powered Investigation Guidance.
Connects to Ollama for offline AI-driven forensic reasoning.
Falls back to rule-based suggestions if LLM is unavailable.
"""

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
        if self.is_available():
            prompt = f"""{self.SYSTEM_CONTEXT}

Based on the following forensic findings, suggest 3-5 specific, actionable next steps for the investigator:

Findings:
{json.dumps(findings, indent=2, default=str)[:3000]}

Provide numbered recommendations:"""
            response = self._generate(prompt)
            if response and not response.startswith("[LLM Error"):
                return [line.strip() for line in response.strip().split("\n") if line.strip()]

        # Fallback: rule-based suggestions
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
        if self.is_available():
            prompt = f"""{self.SYSTEM_CONTEXT}

Write a professional executive summary (1 paragraph, 4-6 sentences) for a forensic investigation report based on the following case data:

{json.dumps(case_data, indent=2, default=str)[:4000]}

Executive Summary:"""
            response = self._generate(prompt)
            if response and not response.startswith("[LLM Error"):
                return response.strip()

        # Fallback
        return self._rule_based_summary(case_data)

    # ------------------------------------------------------------------
    # Rule-based fallbacks
    # ------------------------------------------------------------------

    @staticmethod
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

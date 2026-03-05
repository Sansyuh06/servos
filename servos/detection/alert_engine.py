"""
Servos  Context-aware alert engine with rule set and LLM enrichment.

Replaces the old hardcoded risk_score function with a flexible RuleSet class
and stores recent alerts in memory.  Can optionally query an LLM for natural
language advice about whether an investigator should be concerned about a
particular event.  Responses are cached to avoid repeated calls.
"""

import time
from typing import Callable, Dict, Any, Optional, List


class Rule:
    """A single alert rule."""

    def __init__(self, event_type: str, condition_fn: Callable[[Dict[str, Any]], bool],
                 risk_level: str, message_template: str):
        self.event_type = event_type
        self.condition_fn = condition_fn
        self.risk_level = risk_level
        self.message_template = message_template


class RuleSet:
    """Collection of rules used to evaluate events."""

    def __init__(self):
        self.rules: List[Rule] = []

    def add_rule(self, event_type: str, condition_fn: Callable[[Dict[str, Any]], bool],
                 risk_level: str, message_template: str) -> None:
        self.rules.append(Rule(event_type, condition_fn, risk_level, message_template))

    def evaluate(self, event: Dict[str, Any]) -> Optional[Dict[str, str]]:
        """Return payload dict with risk/message or None if no rule matched."""
        for rule in self.rules:
            if event.get("event_type") == rule.event_type and rule.condition_fn(event):
                return {"risk": rule.risk_level, "message": rule.message_template.format(**event)}
        return None


class AlertEngine:
    def __init__(self, callback: Callable[[Dict], None]):
        self.callback = callback
        self.rule_set = RuleSet()
        self._setup_default_rules()
        self._llm_cache: Dict[str, str] = {}
        self.history: List[Dict[str, Any]] = []  # store last 100 alerts

    def _setup_default_rules(self) -> None:
        # USB_CONNECTED + large capacity (>64GB) → HIGH
        self.rule_set.add_rule(
            "USB_CONNECTED",
            lambda e: e.get("details", {}).get("capacity_gb", 0) > 64,
            "HIGH",
            "USB device with capacity >64GB connected."
        )
        # FILE_MODIFIED + path contains system32/etc → CRITICAL
        self.rule_set.add_rule(
            "FILE_MODIFIED",
            lambda e: any(x in e.get("path", "").lower() for x in ("\\system32\\", "/system32/", "\\windows\\")),
            "CRITICAL",
            "System file modified: {path}"
        )
        # PROCESS_NEW + path is temp/appdata → HIGH
        self.rule_set.add_rule(
            "PROCESS_NEW",
            lambda e: any(x in e.get("exe", "").lower() for x in ("\\temp\\", "appdata", "/temp/")),
            "HIGH",
            "Process started from suspicious location: {exe}"
        )
        # NETWORK_ANOMALY + multiple interfaces added → HIGH
        self.rule_set.add_rule(
            "NETWORK_ANOMALY",
            lambda e: len(e.get("details", {}).get("interfaces", [])) > 1,
            "HIGH",
            "Multiple network interfaces added."
        )

    def process_event(self, event: Dict[str, Any]) -> None:
        result = self.rule_set.evaluate(event)
        payload: Dict[str, Any] = {**event}
        if result:
            payload.update(result)
        else:
            payload["risk"] = "LOW"
            payload["message"] = "Event detected. Investigate?"

        # optionally enrich with LLM
        # note: llm object is not stored; enrich_with_llm can be called externally
        payload_id = f"{event.get('event_type')}|{str(event.get('details'))}"
        payload["enriched_message"] = self._llm_cache.get(payload_id, "")

        # store history (max 100)
        self.history.append({"timestamp": time.time(), **payload})
        if len(self.history) > 100:
            self.history.pop(0)

        try:
            self.callback(payload)
        except Exception:
            pass

    def enrich_with_llm(self, event: Dict[str, Any], llm: Any) -> str:
        """Ask an LLM for a one-sentence assessment of the event.

        Caches answers by event type + details string.
        """
        key = f"{event.get('event_type')}|{str(event.get('details'))}"
        if key in self._llm_cache:
            return self._llm_cache[key]

        if not llm:
            return ""
        try:
            prompt = (
                f"In one sentence, should an investigator be concerned about: {event}?"
            )
            answer = llm.chat(prompt)
            self._llm_cache[key] = answer
            return answer
        except Exception:
            return ""

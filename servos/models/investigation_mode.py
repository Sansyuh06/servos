"""
Servos – Investigation Mode Enum.
"""

from enum import Enum


class InvestigationMode(str, Enum):
    FULL = "full"
    HYBRID = "hybrid"
    MANUAL = "manual"

    @classmethod
    def from_str(cls, value: str) -> "InvestigationMode":
        """Convert string to InvestigationMode, default to HYBRID."""
        try:
            return cls(value.lower())
        except (ValueError, AttributeError):
            return cls.HYBRID

    @property
    def description(self) -> str:
        descriptions = {
            "full": "Fully automated: USB detected → auto-backup → auto-scan → auto-report",
            "hybrid": "Semi-automated: prompts for confirmation at each major step",
            "manual": "Manual: notification only, user controls every step",
        }
        return descriptions.get(self.value, "")

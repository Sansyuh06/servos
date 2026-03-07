"""
Servos – Legal Advisor Module.
Provides offline access to Indian IT Act sections, chain-of-custody checklists,
evidence handling guidelines, and admissibility tips.
"""

import os
import json
from typing import List, Dict, Any, Optional

_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "legal")
_cached_data: Optional[Dict] = None


def _load_data() -> Dict:
    """Load legal_summary.json (cached)."""
    global _cached_data
    if _cached_data:
        return _cached_data
    path = os.path.join(_DATA_DIR, "legal_summary.json")
    if not os.path.exists(path):
        return {"sections": {}, "chain_of_custody_checklist": [],
                "evidence_handling_guidelines": [], "admissibility_tips": [],
                "key_precedents": []}
    with open(path, "r", encoding="utf-8") as f:
        _cached_data = json.load(f)
    return _cached_data


def get_legal_checklist() -> List[str]:
    """Return chain-of-custody checklist items."""
    return _load_data().get("chain_of_custody_checklist", [])


def get_section_summary(section_id: str) -> Dict[str, str]:
    """Return summary for a specific IT Act section."""
    sections = _load_data().get("sections", {})
    # Normalize: accept "65B", "Section 65B", "s65B", etc.
    clean_id = section_id.upper().replace("SECTION", "").replace("S", "").strip()
    # Try direct match
    if clean_id in sections:
        return sections[clean_id]
    # Try case-insensitive
    for key, val in sections.items():
        if key.upper() == clean_id:
            return val
    return {"title": "Not Found", "summary": f"Section {section_id} not in database.",
            "punishment": "", "relevance": ""}


def get_all_sections() -> Dict[str, Dict]:
    """Return all IT Act sections."""
    return _load_data().get("sections", {})


def get_admissibility_tips() -> List[str]:
    """Return admissibility tips for digital evidence."""
    return _load_data().get("admissibility_tips", [])


def get_evidence_handling_guide() -> List[str]:
    """Return evidence handling do's and don'ts."""
    return _load_data().get("evidence_handling_guidelines", [])


def get_key_precedents() -> List[Dict[str, str]]:
    """Return key legal precedents/case law."""
    return _load_data().get("key_precedents", [])


def get_full_legal_reference() -> Dict[str, Any]:
    """Return the complete legal reference package."""
    data = _load_data()
    return {
        "sections": data.get("sections", {}),
        "checklist": data.get("chain_of_custody_checklist", []),
        "evidence_handling": data.get("evidence_handling_guidelines", []),
        "admissibility_tips": data.get("admissibility_tips", []),
        "precedents": data.get("key_precedents", []),
    }

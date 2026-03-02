"""
Servos – Playbook Engine.
Load, validate, and execute YAML-based investigation playbooks.
"""

import os
import yaml
from typing import List, Dict, Optional


class PlaybookStep:
    """A single step in a playbook."""
    def __init__(self, data: dict):
        self.id = data.get("id", "")
        self.name = data.get("name", "Unnamed Step")
        self.description = data.get("description", "")
        self.actions = data.get("actions", [])
        self.decision_point = data.get("decision_point", None)


class Playbook:
    """A parsed investigation playbook."""
    def __init__(self, data: dict):
        self.name = data.get("name", "Unnamed Playbook")
        self.description = data.get("description", "")
        self.version = data.get("version", "1.0")
        self.author = data.get("author", "Unknown")
        self.metadata = data.get("metadata", {})
        self.variables = data.get("variables", {})
        self.steps = [PlaybookStep(s) for s in data.get("steps", [])]

    def __repr__(self):
        return f"<Playbook: {self.name} ({len(self.steps)} steps)>"


class PlaybookEngine:
    """Load and manage investigation playbooks."""

    def __init__(self):
        self.playbooks_dir = os.path.join(
            os.path.dirname(__file__), "defaults"
        )

    def list_playbooks(self) -> List[Playbook]:
        """List all available playbooks."""
        playbooks = []
        if not os.path.exists(self.playbooks_dir):
            return playbooks

        for fname in os.listdir(self.playbooks_dir):
            if fname.endswith((".yaml", ".yml")):
                try:
                    pb = self.load(os.path.join(self.playbooks_dir, fname))
                    playbooks.append(pb)
                except Exception:
                    continue
        return playbooks

    def load(self, filepath: str) -> Playbook:
        """Load a playbook from a YAML file."""
        with open(filepath, "r") as f:
            data = yaml.safe_load(f)
        return Playbook(data)

    def get_default(self, name: str) -> Optional[Playbook]:
        """Get a default playbook by name."""
        for pb in self.list_playbooks():
            if name.lower() in pb.name.lower():
                return pb
        return None

    def print_checklist(self, playbook: Playbook) -> str:
        """Generate a printable checklist from a playbook."""
        lines = [
            f"{'=' * 50}",
            f"  PLAYBOOK: {playbook.name}",
            f"  {playbook.description}",
            f"{'=' * 50}",
            "",
        ]
        for i, step in enumerate(playbook.steps):
            lines.append(f"  [{' '}] Step {i+1}: {step.name}")
            lines.append(f"      {step.description}")
            for action in step.actions:
                lines.append(f"        → {action.get('type', 'unknown')}")
            lines.append("")

        return "\n".join(lines)

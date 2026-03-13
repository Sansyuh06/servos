"""
Servos – Memory Scanner Module.
Provides basic interface for RAM capture and Volatility analysis.
"""

import os
import subprocess
from typing import Dict, Any, List


class MemoryScanner:
    def capture_ram(self, output_path: str) -> bool:
        """Capture memory using winpmem or LiME (depending on platform).
        """
        if os.name == "nt":
            cmd = ["winpmem", "--output", output_path]
        else:
            # require LiME kernel module preloaded as `lime.ko`
            cmd = ["lime", "path=", output_path]  # this is placeholder
        try:
            subprocess.run(cmd, check=True, timeout=600)
            return True
        except Exception:
            return False

    def analyze_dump(self, dump_path: str, plugin: str = "pslist") -> List[str]:
        """Run a volatility3 plugin against the dump and return text output."""
        try:
            out = subprocess.check_output(["volatility3", "-f", dump_path, plugin], text=True)
            return out.splitlines()
        except Exception:
            return []

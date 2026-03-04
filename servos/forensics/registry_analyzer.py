"""
Servos – Registry Analyzer Module.
Uses python-registry/RegRipper patterns to examine hive files.
"""

from typing import Dict, Any

try:
    from Registry import Registry
except ImportError:
    Registry = None


class RegistryAnalyzer:
    def load_hive(self, path: str) -> Any:
        if not Registry:
            raise RuntimeError("python-registry not installed")
        return Registry.Registry(path)

    def list_keys(self, hive) -> Dict[str, Any]:
        result = {}
        for key in hive.root().subkeys():
            result[key.name()] = len(key.subkeys())
        return result

"""
Servos – USB / Storage Device Detection.
Monitors for new removable storage devices using psutil.
"""

import time
import threading
from typing import Callable, List, Optional, Set

import psutil

from servos.models.schema import DeviceInfo


class USBDetectionService:
    """Monitor the system for USB / removable storage device connections."""

    def __init__(self, callback: Optional[Callable[[DeviceInfo], None]] = None,
                 poll_interval: float = 2.0):
        self.callback = callback
        self.poll_interval = poll_interval
        self._known: Set[str] = set()
        self._running = False
        self._thread: Optional[threading.Thread] = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def detect_devices(self) -> List[DeviceInfo]:
        """Return a list of currently connected removable / fixed storage devices."""
        devices: List[DeviceInfo] = []
        for part in psutil.disk_partitions(all=False):
            # On Windows: removable drives typically have 'removable' in opts
            is_removable = "removable" in part.opts.lower() if part.opts else False
            try:
                usage = psutil.disk_usage(part.mountpoint)
                capacity = usage.total
            except Exception:
                capacity = 0

            dev = DeviceInfo(
                path=part.device,
                name=self._device_friendly_name(part),
                capacity_bytes=capacity,
                mount_point=part.mountpoint,
                is_removable=is_removable,
                filesystem=part.fstype or "Unknown",
            )
            devices.append(dev)
        return devices

    def detect_removable(self) -> List[DeviceInfo]:
        """Return only removable storage devices."""
        all_devs = self.detect_devices()
        removable = [d for d in all_devs if d.is_removable]
        # If no removable detected on Windows, also include non-C: fixed drives
        # as potential external drives
        if not removable:
            removable = [d for d in all_devs
                         if d.mount_point and not d.mount_point.upper().startswith("C")]
        return removable

    def start_monitoring(self):
        """Start background monitoring for new devices."""
        if self._running:
            return
        self._running = True
        # Snapshot current devices
        self._known = {d.path for d in self.detect_devices()}
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._thread.start()

    def stop_monitoring(self):
        """Stop background monitoring."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _monitor_loop(self):
        while self._running:
            time.sleep(self.poll_interval)
            current = self.detect_devices()
            current_paths = {d.path for d in current}
            new_paths = current_paths - self._known
            if new_paths and self.callback:
                for dev in current:
                    if dev.path in new_paths:
                        self.callback(dev)
            self._known = current_paths

    @staticmethod
    def _device_friendly_name(partition) -> str:
        """Build a human-friendly name for the device."""
        name_parts = []
        if partition.device:
            name_parts.append(partition.device)
        if partition.mountpoint:
            name_parts.append(f"({partition.mountpoint})")
        if partition.fstype:
            name_parts.append(f"[{partition.fstype}]")
        return " ".join(name_parts) if name_parts else "Unknown Device"

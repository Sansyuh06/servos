"""
Servos – Network Scanner Module.
Provides simple offline analysis of network interfaces, connections,
open ports, ARP table, and DNS cache. Designed for cross-platform use.
"""

import os
import platform
import subprocess
import socket
from typing import List, Dict, Any

import psutil


def _run_cmd(cmd: List[str]) -> str:
    try:
        return subprocess.check_output(cmd, stderr=subprocess.DEVNULL, text=True)
    except Exception:
        return ""


class NetworkScanner:
    def list_interfaces(self) -> List[Dict[str, Any]]:
        """Return basic info about network interfaces."""
        result = []
        for name, addrs in psutil.net_if_addrs().items():
            for addr in addrs:
                if addr.family == socket.AF_INET:
                    result.append({
                        "name": name,
                        "address": addr.address,
                        "netmask": addr.netmask,
                        "broadcast": addr.broadcast,
                    })
        return result

    def active_connections(self) -> List[Dict[str, Any]]:
        """List active TCP/UDP connections."""
        conns = []
        for c in psutil.net_connections(kind="inet"):
            conns.append({
                "fd": c.fd,
                "family": str(c.family),
                "type": str(c.type),
                "laddr": f"{c.laddr.ip}:{c.laddr.port}" if c.laddr else "",
                "raddr": f"{c.raddr.ip}:{c.raddr.port}" if c.raddr else "",
                "status": c.status,
                "pid": c.pid,
            })
        return conns

    def listening_ports(self) -> List[Dict[str, Any]]:
        """Return processes listening on ports."""
        ports = []
        for c in psutil.net_connections(kind="inet"):
            if c.status == "LISTEN":
                ports.append({
                    "laddr": f"{c.laddr.ip}:{c.laddr.port}" if c.laddr else "",
                    "pid": c.pid,
                    "process": psutil.Process(c.pid).name() if c.pid else "",
                })
        return ports

    def arp_table(self) -> List[Dict[str, str]]:
        """Return ARP table entries (platform-dependent)."""
        entries = []
        if platform.system() == "Windows":
            out = _run_cmd(["arp", "-a"]).splitlines()
            for line in out:
                parts = line.split()
                if len(parts) >= 3 and parts[0][0].isdigit():
                    entries.append({"ip": parts[0], "mac": parts[1], "type": parts[2]})
        else:
            out = _run_cmd(["arp", "-n"]).splitlines()
            for line in out[1:]:
                parts = line.split()
                if len(parts) >= 4:
                    entries.append({"ip": parts[0], "mac": parts[2], "iface": parts[5]})
        return entries

    def dns_cache(self) -> List[str]:
        """Attempt to read DNS cache entries (platform dependent)."""
        if platform.system() == "Windows":
            out = _run_cmd(["ipconfig", "/displaydns"]).splitlines()
            return [l for l in out if l.strip().startswith("Record Name")]
        else:
            # Linux: read /etc/hosts as placeholder
            try:
                with open("/etc/hosts") as f:
                    return [l.strip() for l in f if l and not l.startswith("#")]
            except Exception:
                return []

    def capture_pcap(self, interface: str, duration: int = 10, output: str = "capture.pcap") -> str:
        """Capture network traffic using tcpdump if available."""
        cmd = ["tcpdump", "-i", interface, "-w", output, "-c", str(1000)]
        try:
            subprocess.run(cmd, timeout=duration)
            return output
        except Exception:
            return ""

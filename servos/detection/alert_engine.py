"""
Servos – Smart Alert Engine.
Assigns risk scores and produces contextual alerts based on events.
"""

from enum import Enum
from typing import Dict, Any


def risk_score(event: Dict[str, Any]) -> str:
    # simplistic rules; real engine would be much smarter
    et = event.get('event_type')
    if et == 'USB_CONNECTED':
        return 'LOW'
    if et == 'NETWORK_ANOMALY':
        return 'MEDIUM'
    if et == 'FILE_MODIFIED':
        return 'HIGH'
    if et == 'PROCESS_NEW':
        return 'LOW'  # could increase if process is from suspicious path
    return 'LOW'


class AlertEngine:
    class Risk(Enum):
        LOW = 'LOW'
        MEDIUM = 'MEDIUM'
        HIGH = 'HIGH'
        CRITICAL = 'CRITICAL'

    def __init__(self, callback: Callable[[Dict], None]):
        self.callback = callback

    def process_event(self, event: Dict[str, Any]):
        score = risk_score(event)
        payload = {**event, 'risk': score}
        # alert text generation
        if event.get('event_type') == 'USB_CONNECTED':
            payload['message'] = "You connected a new storage device. Wanna scan for vulnerabilities?"
        elif event.get('event_type') == 'NETWORK_ANOMALY':
            payload['message'] = "Network traffic spike detected. Run network forensics?"
        elif event.get('event_type') == 'FILE_MODIFIED':
            payload['message'] = "Modified system files detected. Analyze for tampering?"
        else:
            payload['message'] = "Event detected. Investigate?"
        try:
            self.callback(payload)
        except Exception:
            pass

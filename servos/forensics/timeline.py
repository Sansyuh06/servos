"""
Servos – Timeline Reconstruction.
Build chronological event timelines from file metadata and artifacts.
"""

from datetime import datetime
from typing import List, Optional, Tuple

from dataclasses import dataclass, field

from servos.models.schema import (
    Timeline, TimelineEvent, FileSystemAnalysis, ArtifactResult
)


@dataclass
class TimelineAnomaly:
    anomaly_type: str
    start_time: str
    end_time: str
    description: str
    severity: str
    event_count: int

# add anomalies field to existing Timeline dataclass by monkeypatch at runtime (or we could modify model)
# we will simply add it in code where Timeline is constructed below


class TimelineBuilder:
    """Reconstruct an investigation timeline from collected data."""

    def build(self, fs_analysis: Optional[FileSystemAnalysis] = None,
              artifacts: Optional[ArtifactResult] = None) -> Timeline:
        """Build a unified timeline from all available data sources."""
        events: List[TimelineEvent] = []

        if fs_analysis:
            events.extend(self._events_from_filesystem(fs_analysis))

        if artifacts:
            events.extend(self._events_from_artifacts(artifacts))

        # Sort chronologically
        events.sort(key=lambda e: e.timestamp if e.timestamp else "")

        # Determine date range
        timestamps = [e.timestamp for e in events if e.timestamp]
        date_start = timestamps[0] if timestamps else ""
        date_end = timestamps[-1] if timestamps else ""

        # Find suspicious windows (clusters of high-severity events)
        suspicious_windows = self._find_suspicious_windows(events)

        timeline = Timeline(
            events=events,
            date_range_start=date_start,
            date_range_end=date_end,
            suspicious_windows=suspicious_windows,
        )
        # detect deeper anomalies and attach
        timeline.anomalies = self.detect_anomalies(timeline)
        return timeline

    def _events_from_filesystem(self, fs: FileSystemAnalysis) -> List[TimelineEvent]:
        """Create timeline events from file modifications."""
        events = []

        for f in fs.files:
            severity = "high" if f.suspicious else "info"

            if f.modified:
                events.append(TimelineEvent(
                    timestamp=f.modified,
                    description=f"File modified: {f.filename} ({f.file_size} bytes)",
                    event_type="file",
                    severity=severity,
                    source=f.full_path,
                ))

            if f.created and f.created != f.modified:
                events.append(TimelineEvent(
                    timestamp=f.created,
                    description=f"File created: {f.filename}",
                    event_type="file",
                    severity=severity,
                    source=f.full_path,
                ))

        return events

    def _events_from_artifacts(self, artifacts: ArtifactResult) -> List[TimelineEvent]:
        """Create timeline events from extracted artifacts."""
        events = []

        for art in artifacts.all_artifacts():
            severity = "info"
            if art.suspicious_score > 0.7:
                severity = "high"
            elif art.suspicious_score > 0.4:
                severity = "medium"
            elif art.suspicious_score > 0.1:
                severity = "low"

            events.append(TimelineEvent(
                timestamp=art.timestamp,
                description=art.description,
                event_type="artifact",
                severity=severity,
                source=art.source_path,
            ))

        return events

    def _find_suspicious_windows(self, events: List[TimelineEvent]) -> List[tuple]:
        """Identify time windows with suspicious activity clusters."""
        windows = []
        high_events = [e for e in events if e.severity in ("high", "medium") and e.timestamp]

        if not high_events:
            return windows

        # Cluster nearby events (within 1 hour)
        cluster_start = high_events[0].timestamp
        cluster_end = high_events[0].timestamp

        for i in range(1, len(high_events)):
            try:
                current = datetime.fromisoformat(high_events[i].timestamp)
                prev = datetime.fromisoformat(high_events[i - 1].timestamp)
                diff = abs((current - prev).total_seconds())

                if diff <= 3600:  # Within 1 hour
                    cluster_end = high_events[i].timestamp
                else:
                    windows.append((cluster_start, cluster_end))
                    cluster_start = high_events[i].timestamp
                    cluster_end = high_events[i].timestamp
            except (ValueError, TypeError):
                continue

        windows.append((cluster_start, cluster_end))
        return windows

    def detect_anomalies(self, timeline: Timeline) -> List[TimelineAnomaly]:
        """Scan a completed Timeline for higher-level anomaly patterns."""
        anomalies: List[TimelineAnomaly] = []
        events = timeline.events

        # OFF_HOURS: any events between 23:00-05:00
        off_events = [e for e in events if e.timestamp and 23 <= int(e.timestamp[11:13]) or (e.timestamp and int(e.timestamp[11:13]) < 5)]
        if off_events:
            anomalies.append(TimelineAnomaly(
                anomaly_type="OFF_HOURS_ACTIVITY",
                start_time=off_events[0].timestamp,
                end_time=off_events[-1].timestamp,
                description="Activity detected outside normal business hours (23:00-05:00)",
                severity="medium",
                event_count=len(off_events),
            ))
        # BURST: >20 file events in any 5-minute window
        for i in range(len(events)):
            try:
                t1 = datetime.fromisoformat(events[i].timestamp)
            except Exception:
                continue
            count = 1
            for j in range(i+1, len(events)):
                try:
                    t2 = datetime.fromisoformat(events[j].timestamp)
                except Exception:
                    continue
                if (t2 - t1).total_seconds() <= 300:
                    count += 1
                else:
                    break
            if count > 20:
                anomalies.append(TimelineAnomaly(
                    anomaly_type="BURST_ACTIVITY",
                    start_time=events[i].timestamp,
                    end_time=events[i+count-1].timestamp,
                    description=f"{count} events within 5 minutes",
                    severity="high",
                    event_count=count,
                ))
                break
        # WEEKEND_ACTIVITY: events on Saturday (5) or Sunday (6)
        weekend = [e for e in events if e.timestamp and datetime.fromisoformat(e.timestamp).weekday() >= 5]
        if weekend:
            anomalies.append(TimelineAnomaly(
                anomaly_type="WEEKEND_ACTIVITY",
                start_time=weekend[0].timestamp,
                end_time=weekend[-1].timestamp,
                description="High-volume activity during weekend",
                severity="medium",
                event_count=len(weekend),
            ))
        # RAPID_DELETION: >10 deletions within 10 minutes
        deletions = [e for e in events if "deleted" in e.description.lower()]
        for i in range(len(deletions)):
            try:
                t1 = datetime.fromisoformat(deletions[i].timestamp)
            except Exception:
                continue
            cnt = 1
            for j in range(i+1, len(deletions)):
                try:
                    t2 = datetime.fromisoformat(deletions[j].timestamp)
                except Exception:
                    continue
                if (t2 - t1).total_seconds() <= 600:
                    cnt += 1
                else:
                    break
            if cnt > 10:
                anomalies.append(TimelineAnomaly(
                    anomaly_type="RAPID_DELETION",
                    start_time=deletions[i].timestamp,
                    end_time=deletions[i+cnt-1].timestamp,
                    description=f"{cnt} deletion events within 10 minutes",
                    severity="high",
                    event_count=cnt,
                ))
                break
        # MASS_ENCRYPTION: >50 files modified with same timestamp
        timestamps = {}
        for e in events:
            if e.timestamp:
                timestamps.setdefault(e.timestamp, 0)
                timestamps[e.timestamp] += 1
        for ts, cnt in timestamps.items():
            if cnt > 50:
                anomalies.append(TimelineAnomaly(
                    anomaly_type="MASS_ENCRYPTION",
                    start_time=ts,
                    end_time=ts,
                    description=f"{cnt} files modified simultaneously",
                    severity="critical",
                    event_count=cnt,
                ))
                break
        # SEQUENTIAL_ACCESS: files accessed in alphabetical order
        accessed = [e for e in events if e.event_type == "file"]
        names = [e.description for e in accessed]
        if names == sorted(names) and len(names) > 10:
            anomalies.append(TimelineAnomaly(
                anomaly_type="SEQUENTIAL_ACCESS",
                start_time=accessed[0].timestamp if accessed else "",
                end_time=accessed[-1].timestamp if accessed else "",
                description="Files accessed in alphabetical sequence",
                severity="medium",
                event_count=len(accessed),
            ))
        return anomalies

    def format_ascii_timeline(self, timeline: Timeline, max_events: int = 30) -> str:
        """Create a human-readable ASCII timeline."""
        lines = []
        lines.append("═" * 60)
        lines.append("  INVESTIGATION TIMELINE")
        lines.append("═" * 60)

        if timeline.date_range_start and timeline.date_range_end:
            lines.append(f"  Period: {timeline.date_range_start[:19]} → {timeline.date_range_end[:19]}")
            lines.append("")

        severity_icons = {
            "info": "  ",
            "low": "⚬ ",
            "medium": "⚠ ",
            "high": "🔴",
        }

        shown = 0
        for event in timeline.events:
            if shown >= max_events:
                lines.append(f"  ... and {len(timeline.events) - max_events} more events")
                break

            icon = severity_icons.get(event.severity, "  ")
            ts = event.timestamp[:19] if event.timestamp else "Unknown time     "
            # annotate if this event falls within any detected anomaly window
            note = ""
            for a in timeline.anomalies:
                try:
                    if a.start_time <= (event.timestamp or "") <= a.end_time:
                        note = f" [{a.anomaly_type}]"
                        break
                except Exception:
                    continue
            lines.append(f"  {ts}  {icon}  {event.description}{note}")
            shown += 1

        if timeline.suspicious_windows:
            lines.append("")
            lines.append("  ⚠ SUSPICIOUS ACTIVITY WINDOWS:")
            for start, end in timeline.suspicious_windows:
                lines.append(f"    {start[:19]} → {end[:19]}")

        lines.append("═" * 60)
        return "\n".join(lines)

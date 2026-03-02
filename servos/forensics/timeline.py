"""
Servos – Timeline Reconstruction.
Build chronological event timelines from file metadata and artifacts.
"""

from datetime import datetime
from typing import List, Optional

from servos.models.schema import (
    Timeline, TimelineEvent, FileSystemAnalysis, ArtifactResult
)


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

        return Timeline(
            events=events,
            date_range_start=date_start,
            date_range_end=date_end,
            suspicious_windows=suspicious_windows,
        )

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
            lines.append(f"  {ts}  {icon}  {event.description}")
            shown += 1

        if timeline.suspicious_windows:
            lines.append("")
            lines.append("  ⚠ SUSPICIOUS ACTIVITY WINDOWS:")
            for start, end in timeline.suspicious_windows:
                lines.append(f"    {start[:19]} → {end[:19]}")

        lines.append("═" * 60)
        return "\n".join(lines)

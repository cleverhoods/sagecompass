"""Trace state reducers for event management.

Provides LangGraph-compatible reducer functions for TraceEvent lists.
"""

from __future__ import annotations

from app.platform.core.dto.events import TraceEvent


def add_events(
    existing: list[TraceEvent],
    new: list[TraceEvent],
) -> list[TraceEvent]:
    """Reducer to append trace events to the event list.

    This reducer follows LangGraph's reducer pattern:
    - Takes existing state and new values
    - Returns merged result (append-only for events)
    - Deduplicates by uid to handle subgraph state merges

    Args:
        existing: Current list of trace events.
        new: New events to append.

    Returns:
        Combined event list with new events appended, deduplicated by uid.
    """
    existing_uids = {e.uid for e in existing}
    unique_new = [e for e in new if e.uid not in existing_uids]
    return [*existing, *unique_new]

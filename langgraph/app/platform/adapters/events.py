"""Events adapter for trace event emission.

This adapter provides boundary translation between trace events and state updates,
with dual-sink logging for observability.
"""

from __future__ import annotations

from typing import Any

import structlog

from app.platform.core.dto.events import EventKind, TraceEvent

_logger = structlog.get_logger("trace.events")


def emit_event(
    *,
    owner: str,
    kind: EventKind,
    message: str,
    phase: str | None = None,
    data: dict[str, object] | None = None,
) -> dict[str, Any]:
    """Emit a trace event and return state update dict.

    Creates a TraceEvent and returns a state update dict suitable for
    LangGraph Command.update. Also logs the event via structlog for
    observability.

    Args:
        owner: Node or component generating the event.
        kind: Category of the event.
        message: Human-readable description.
        phase: Optional phase name.
        data: Optional structured data.

    Returns:
        Dict with "events" key containing list of the new TraceEvent.

    Example:
        ```python
        update = emit_event(
            owner="supervisor",
            kind="routing",
            message="Running safety checks.",
        )
        return Command(update=update, goto="guardrails_check")
        ```
    """
    event = TraceEvent.create(
        owner=owner,
        kind=kind,
        message=message,
        phase=phase,
        data=data,
    )

    # Dual-sink: log for observability
    _logger.info(
        "trace_event",
        owner=owner,
        kind=kind,
        message=message,
        phase=phase,
        data=data,
    )

    return {"events": [event]}


def merge_event_updates(*updates: dict[str, Any]) -> dict[str, Any]:
    """Merge multiple event updates into a single update dict.

    Combines events from multiple emit_event() calls.

    Args:
        *updates: Variable number of update dicts from emit_event.

    Returns:
        Single merged update dict with combined events list.
    """
    all_events: list[TraceEvent] = []

    for update in updates:
        if "events" in update:
            all_events.extend(update["events"])

    return {"events": all_events} if all_events else {}

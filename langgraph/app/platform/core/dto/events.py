"""Core DTOs for trace events."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Literal

EventKind = Literal["routing", "progress", "decision", "error"]
"""
Trace event kinds for operational observability:
- "routing": Node routing decisions (supervisor to next node)
- "progress": Progress updates within a node
- "decision": Internal decision points (not user-facing)
- "error": Error conditions or failures
"""


@dataclass(frozen=True)
class TraceEvent:
    """Immutable trace event for operational observability.

    TraceEvents capture operational details that should NOT be included
    in LLM conversation context. They serve debugging and observability
    purposes only.

    Attributes:
        uid: Unique identifier for deduplication during state merges.
        timestamp: UTC timestamp when the event occurred.
        owner: Node or component that generated the event.
        kind: Category of the event.
        message: Human-readable event description.
        phase: Optional phase name if event relates to a specific phase.
        data: Optional structured data for the event.
    """

    uid: str
    timestamp: datetime
    owner: str
    kind: EventKind
    message: str
    phase: str | None = None
    data: dict[str, object] = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        *,
        owner: str,
        kind: EventKind,
        message: str,
        phase: str | None = None,
        data: dict[str, object] | None = None,
    ) -> TraceEvent:
        """Factory method to create a TraceEvent with current timestamp.

        Args:
            owner: Node or component generating the event.
            kind: Category of the event.
            message: Human-readable description.
            phase: Optional phase name.
            data: Optional structured data.

        Returns:
            New TraceEvent with UTC timestamp.
        """
        return cls(
            uid=str(uuid.uuid4()),
            timestamp=datetime.now(UTC),
            owner=owner,
            kind=kind,
            message=message,
            phase=phase,
            data=data or {},
        )

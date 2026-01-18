"""Core data transfer objects for boundary translation."""

from app.platform.core.dto.errors import ErrorEntry, ErrorSeverity
from app.platform.core.dto.events import EventKind, TraceEvent
from app.platform.core.dto.phases import PhaseResult, PhaseStatus

__all__ = [
    "ErrorEntry",
    "ErrorSeverity",
    "EventKind",
    "PhaseResult",
    "PhaseStatus",
    "TraceEvent",
]

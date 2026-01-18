"""Core DTOs for structured error logging."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Literal

ErrorSeverity = Literal["warning", "error", "fatal"]
"""
Error severity levels:
- "warning": Non-blocking issue, operation continued
- "error": Operation failed but system can continue
- "fatal": Critical failure requiring intervention
"""


@dataclass(frozen=True)
class ErrorEntry:
    """Immutable structured error log entry.

    Provides queryable error information for debugging and observability.
    Replaces unstructured string errors with typed, filterable entries.

    Attributes:
        code: Machine-readable error code (e.g., "PHASE_TIMEOUT", "VALIDATION_FAILED").
        message: Human-readable error description.
        severity: Error severity level.
        phase: Phase name where error occurred (if applicable).
        owner: Node or component that generated the error.
        timestamp: UTC timestamp when error occurred.
        context: Optional structured context data for debugging.
    """

    code: str
    message: str
    severity: ErrorSeverity
    owner: str
    timestamp: datetime
    phase: str | None = None
    context: dict[str, object] = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        *,
        code: str,
        message: str,
        severity: ErrorSeverity,
        owner: str,
        phase: str | None = None,
        context: dict[str, object] | None = None,
    ) -> ErrorEntry:
        """Factory method to create an ErrorEntry with current timestamp.

        Args:
            code: Machine-readable error code.
            message: Human-readable description.
            severity: Error severity level.
            owner: Node or component generating the error.
            phase: Optional phase name.
            context: Optional structured context data.

        Returns:
            New ErrorEntry with UTC timestamp.
        """
        return cls(
            code=code,
            message=message,
            severity=severity,
            owner=owner,
            timestamp=datetime.now(UTC),
            phase=phase,
            context=context or {},
        )

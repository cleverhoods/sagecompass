"""Schema adapter for the ambiguity clarification agent output."""

from __future__ import annotations

from app.schemas.clarification import ClarificationResponse, ClarificationResponses

__all__ = [
    "ClarificationResponse",
    "ClarificationResponses",
    "OutputSchema",
]


# Generic loader convention.
OutputSchema = ClarificationResponses

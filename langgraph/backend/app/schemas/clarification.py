"""Shared schema for ambiguity clarification outputs."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ClarificationResponse(BaseModel):
    """Structured response emitted by the ambiguity clarification agent."""

    clarified_input: str | None = Field(
        default=None,
        description="Clarified version of the user's input, if updated.",
    )
    clarified_keys: list[str] = Field(
        default_factory=list,
        description=(
            "Clarified topic keys (non-empty). Allowed values are restricted to the prompt-provided "
            "list shown under 'Topics to clarify: {keys_to_clarify}'. Each item MUST exactly match an entry "
            "from the provided `keys_to_clarify` list (subset only; no additional keys). Return the set of "
            "keys that are now clarified, preferring the largest valid subset you can justify."
        ),
    )
    clarification_output: str | None = Field(
        default=None,
        description="Assistant output that should be sent back to the user.",
    )


class ClarificationResponses(BaseModel):
    """Batch of clarification replies produced in one agent invocation."""

    responses: list[ClarificationResponse] = Field(
        default_factory=list,
        description="Ordered list of clarification replies (most recent last).",
    )


__all__ = [
    "ClarificationResponse",
    "ClarificationResponses",
]

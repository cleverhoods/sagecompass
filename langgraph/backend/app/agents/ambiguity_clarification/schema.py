"""Schema for ambiguity clarification agent output."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ClarificationResponse(BaseModel):
    """Structured response from the Ambiguity Clarification agent.

    Invariants:
        clarified_keys are reported when the user addresses fields in this round.
    """
    clarified_input: str | None = Field(
        default=None,
        description="Clarified version of the user's input, if updated.",
    )
    clarified_keys: list[str] = Field(
        default_factory=list,
        description=(
            "Clarified topic keys (non-empty). Allowed values are restricted to the prompt-provided "
    "list shown under 'Topics to clarify: {keys_to_clarify}'. Each item MUST exactly match an entry from the provided "
            "`keys_to_clarify` list (subset only; no additional keys). Return the set of keys that are "
            "now clarified, preferring the largest valid subset you can justify.\n\n"
            "Example: keys_to_clarify=['budget | timeline | scope']; "
            "clarified_keys=['budget | timeline | scope'] is valid; "
            "clarified_keys=['scope'] is invalid; clarified_keys=[] is invalid."
        )

    )
    clarification_output: str | None = Field(
        default=None,
        description="Assistant output that should be sent back to the user.",
    )


class ClarificationResponses(BaseModel):
    """Batch of clarification replies emitted in one agent invocation."""

    responses: list[ClarificationResponse] = Field(
        default_factory=list,
        description="Ordered list of clarification replies (most recent last).",
    )


# Generic loader convention.
OutputSchema = ClarificationResponses

"""State invariants and ownership contract for SageState.

Contract meaning:
- Defines which top-level fields exist on SageState and forbids ad-hoc keys.
- Documents field ownership so nodes do not mutate data they do not own.
- Encodes invariants such as allowed PhaseEntry status values.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from pydantic import BaseModel, Field


SAGESTATE_TOP_LEVEL_FIELDS: tuple[str, ...] = (
    "gating",
    "ambiguity",
    "messages",
    "phases",
    "errors",
)

PHASE_STATUS_VALUES: tuple[str, ...] = ("pending", "complete", "stale")


class StateOwnershipRule(BaseModel):
    """Ownership rules for SageState top-level fields."""

    field: str = Field(
        ...,
        description="SageState top-level field name.",
    )
    owners: tuple[str, ...] = Field(
        ...,
        description="Nodes or subsystems that are allowed to mutate this field.",
    )
    invariant: str = Field(
        ...,
        description="Short invariant statement for the field.",
    )


STATE_OWNERSHIP_RULES: tuple[StateOwnershipRule, ...] = (
    StateOwnershipRule(
        field="gating",
        owners=("gating_guardrails",),
        invariant="GatingContext contains guardrail metadata only.",
    ),
    StateOwnershipRule(
        field="ambiguity",
        owners=("ambiguity_scan", "ambiguity_clarification", "ambiguity_supervisor"),
        invariant="AmbiguityContext contains ambiguity detection/clarification only.",
    ),
    StateOwnershipRule(
        field="messages",
        owners=("nodes", "middleware"),
        invariant="Messages append only; no raw prompt/system leakage.",
    ),
    StateOwnershipRule(
        field="phases",
        owners=("phase_nodes", "phase_supervisor"),
        invariant="PhaseEntry status must be pending|complete|stale.",
    ),
    StateOwnershipRule(
        field="errors",
        owners=("nodes",),
        invariant="Errors are append-only summaries; no sensitive raw content.",
    ),
)


def validate_state_update(update: Mapping[str, Any]) -> None:
    """Validate that a state update uses only known SageState top-level fields."""
    unknown = [key for key in update.keys() if key not in SAGESTATE_TOP_LEVEL_FIELDS]
    if unknown:
        raise ValueError(f"Unknown SageState fields in update: {unknown}")

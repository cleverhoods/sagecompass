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
        owners=(
            "ambiguity_scan",
            "ambiguity_clarification",
            "ambiguity_clarification_external",
            "ambiguity_supervisor",
            "supervisor",
        ),
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

OWNER_GROUPS: dict[str, set[str]] = {
    "nodes": {
        "ambiguity_clarification",
        "ambiguity_clarification_external",
        "ambiguity_scan",
        "ambiguity_supervisor",
        "gating_guardrails",
        "phase_supervisor",
        "problem_framing",
        "retrieve_context",
        "supervisor",
    },
    "phase_nodes": {
        "ambiguity_scan",
        "problem_framing",
        "retrieve_context",
    },
    "middleware": set(),
}


def _owner_allowed(owner: str | None, rule: StateOwnershipRule) -> bool:
    if owner is None:
        return True
    if owner in rule.owners:
        return True
    for group_name in ("nodes", "middleware", "phase_nodes"):
        if group_name in rule.owners and owner in OWNER_GROUPS.get(group_name, set()):
            return True
    return False


def _iter_phase_entries(phases: Any) -> list[Any]:
    if isinstance(phases, Mapping):
        return list(phases.values())
    return []


def validate_state_update(update: Mapping[str, Any], *, owner: str | None = None) -> None:
    """Validate that a state update uses only known SageState top-level fields."""
    unknown = [key for key in update if key not in SAGESTATE_TOP_LEVEL_FIELDS]
    if unknown:
        raise ValueError(f"Unknown SageState fields in update: {unknown}")

    if owner is not None:
        rules_by_field = {rule.field: rule for rule in STATE_OWNERSHIP_RULES}
        for field in update:
            rule = rules_by_field.get(field)
            if rule is None:
                raise ValueError(f"No ownership rule for SageState field: {field}")
            if not _owner_allowed(owner, rule):
                raise ValueError(
                    f"Owner {owner!r} is not allowed to update SageState.{field}"
                )

    phases = update.get("phases")
    if phases is not None:
        for entry in _iter_phase_entries(phases):
            status = getattr(entry, "status", None)
            if status is None and isinstance(entry, Mapping):
                status = entry.get("status")
            if status is not None and status not in PHASE_STATUS_VALUES:
                raise ValueError(f"Invalid PhaseEntry status: {status}")

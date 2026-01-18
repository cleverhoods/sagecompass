"""State invariants and ownership contract for SageState.

Contract meaning:
- Defines which top-level fields exist on SageState and forbids ad-hoc keys.
- Documents field ownership so nodes do not mutate data they do not own.
- Encodes invariants such as allowed PhaseEntry status values.
- Defines phase dependencies for invalidation when upstream phases change.
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
    "events",
)

PHASE_STATUS_VALUES: tuple[str, ...] = ("pending", "complete", "stale")

# Phase dependency graph: maps phase -> list of phases that depend on it
# When a phase changes, all downstream phases should be marked stale
PHASE_DEPENDENCIES: dict[str, tuple[str, ...]] = {
    "problem_framing": ("goals_kpis", "feasibility", "decision_synthesis"),
    "goals_kpis": ("feasibility", "decision_synthesis"),
    "feasibility": ("decision_synthesis",),
    "decision_synthesis": (),  # Terminal phase, no dependents
}


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
    StateOwnershipRule(
        field="events",
        owners=("nodes",),
        invariant="Events are append-only trace records; not for LLM context.",
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
                raise ValueError(f"Owner {owner!r} is not allowed to update SageState.{field}")

    phases = update.get("phases")
    if phases is not None:
        for entry in _iter_phase_entries(phases):
            status = getattr(entry, "status", None)
            if status is None and isinstance(entry, Mapping):
                status = entry.get("status")
            if status is not None and status not in PHASE_STATUS_VALUES:
                raise ValueError(f"Invalid PhaseEntry status: {status}")


def get_downstream_phases(phase_name: str) -> tuple[str, ...]:
    """Get all phases that depend on the given phase.

    Args:
        phase_name: Name of the upstream phase.

    Returns:
        Tuple of phase names that depend on this phase (directly or transitively).
    """
    return PHASE_DEPENDENCIES.get(phase_name, ())


def get_phases_to_invalidate(changed_phase: str) -> set[str]:
    """Get all phases that should be marked stale when a phase changes.

    Computes transitive closure of dependencies: if A → B → C,
    changing A invalidates both B and C.

    Args:
        changed_phase: Name of the phase that changed.

    Returns:
        Set of phase names to mark as stale.
    """
    to_invalidate: set[str] = set()
    queue = list(get_downstream_phases(changed_phase))

    while queue:
        phase = queue.pop(0)
        if phase not in to_invalidate:
            to_invalidate.add(phase)
            queue.extend(get_downstream_phases(phase))

    return to_invalidate


def invalidate_downstream_phases(
    phases: Mapping[str, Any],
    changed_phase: str,
) -> dict[str, Any]:
    """Mark downstream phases as stale when an upstream phase changes.

    Creates a new phases dict with downstream entries marked stale.
    Does not mutate the original.

    Args:
        phases: Current phases dict from state.
        changed_phase: Name of the phase that changed.

    Returns:
        New phases dict with downstream phases marked stale.
    """
    to_invalidate = get_phases_to_invalidate(changed_phase)
    if not to_invalidate:
        return dict(phases)

    updated = dict(phases)
    for phase_name in to_invalidate:
        if phase_name in updated:
            entry = updated[phase_name]
            # Handle both Pydantic models and dicts
            if hasattr(entry, "model_copy"):
                updated[phase_name] = entry.model_copy(update={"status": "stale"})
            elif isinstance(entry, Mapping):
                updated[phase_name] = {**entry, "status": "stale"}

    return updated

from __future__ import annotations

from typing import Any, Dict, Type, TypeVar
from pydantic import BaseModel
from app.state import PhaseEntry, PhaseStatus, SageState

T = TypeVar("T", bound=BaseModel)

# ---- WRITE HELPERS (return updates, do NOT mutate state) ----

def set_phase_data_update(
    state: SageState,
    key: str,
    value: BaseModel,
) -> Dict[str, Any]:
    """
    Return a state update that stores a phase's structured result
    in SageState.phases[key].data.
    """
    phases = state.phases.copy()
    existing = phases.get(key)

    entry = PhaseEntry(
        data=value.model_dump(),
        status=existing.status if existing else "pending",
        evidence=existing.evidence if existing else [],
        error=existing.error if existing else {},
    )

    phases[key] = entry
    return {"phases": phases}


def set_phase_status_update(
    state: SageState,
    key: str,
    status: PhaseStatus,
) -> Dict[str, Any]:
    """
    Return a state update that sets the lifecycle status for a given phase.
    """
    phases = state.phases.copy()
    existing = phases.get(key)

    entry = PhaseEntry(
        status=status,
        data=existing.data if existing else {},
        evidence=existing.evidence if existing else [],
        error=existing.error if existing else {},
    )

    phases[key] = entry
    return {"phases": phases}


# ---------- READ HELPERS (pure) ----------

def get_phase_data(
    state: SageState,
    key: str,
    model: Type[T],
) -> T | None:
    """
    Load and validate a phase's structured result from SageState.
    """
    entry = state.phases.get(key)
    if not entry or not entry.data:
        return None

    return model.model_validate(entry.data)


def get_phase_status(
    state: SageState,
    key: str,
) -> PhaseStatus:
    """
    Read lifecycle status for a phase; default to 'pending'.
    """
    entry = state.phases.get(key)
    return entry.status if entry else "pending"

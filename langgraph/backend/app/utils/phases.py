from __future__ import annotations

from typing import Any, Dict, Type, TypeVar

from pydantic import BaseModel

from app.state import PhaseEntry, PhaseStatus, SageState


T = TypeVar("T", bound=BaseModel)


# ---- WRITE HELPERS (return updates, do NOT mutate state) ----

def set_phase_data_update(state: SageState, key: str, value: BaseModel) -> Dict[str, Any]:
    """
    Return a state update that stores a phase's structured result
    in SageState['phases'][key]['data'].
    """
    # Copy phases so we don't mutate state in-place
    phases: Dict[str, PhaseEntry] = dict(state.get("phases") or {})
    existing = phases.get(key)

    # Start a fresh PhaseEntry, then optionally carry over status
    entry: PhaseEntry = {"data": value.model_dump()}
    if existing is not None and "status" in existing:
        entry["status"] = existing["status"]

    phases[key] = entry
    return {"phases": phases}


def set_phase_status_update(state: SageState, key: str, status: PhaseStatus) -> Dict[str, Any]:
    """
    Return a state update that sets the lifecycle status for a given phase.
    """
    phases: Dict[str, PhaseEntry] = dict(state.get("phases") or {})
    existing = phases.get(key)

    # Start a fresh PhaseEntry, then optionally carry over data
    entry: PhaseEntry = {"status": status}
    if existing is not None and "data" in existing:
        entry["data"] = existing["data"]

    phases[key] = entry
    return {"phases": phases}

# ---------- READ HELPERS (pure) ----------

def get_phase_data(state: SageState, key: str, model: Type[T]) -> T | None:
    """
    Load and validate a phase's structured result from SageState.
    """
    phases = state.get("phases") or {}
    entry = phases.get(key)
    if not entry or "data" not in entry:
        return None

    return model.model_validate(entry["data"])


def get_phase_status(state: SageState, key: str) -> PhaseStatus:
    """
    Read lifecycle status for a phase; default to 'pending'.
    """
    phases = state.get("phases") or {}
    entry = phases.get(key) or {}

    status = entry.get("status")
    if status in ("pending", "complete", "stale"):
        return status

    return "pending"
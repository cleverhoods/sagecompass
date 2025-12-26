from __future__ import annotations

from typing import Dict
from uuid import uuid4

from app.state import SageState


def init_state() -> SageState:
    return {
        "messages": [],
        "user_query": "",
        "phases": {},
        "errors": [],
    }


def init_ui_meta() -> Dict:
    return {
        "thread_id": None,
        "pending_interrupt": None,
        "pending_interrupt_id": None,
        "hilp_answers": {},
    }


def ensure_thread_id(ui_meta: Dict) -> str:
    if not ui_meta.get("thread_id"):
        ui_meta["thread_id"] = str(uuid4())
    return ui_meta["thread_id"]


def normalize_state(state: SageState | None) -> SageState:
    normalized: SageState = dict(state or init_state())
    normalized.setdefault("messages", [])
    normalized.setdefault("phases", {})
    normalized.setdefault("errors", [])
    normalized.setdefault("user_query", "")
    return normalized


def summarize_problem_frame(state: SageState) -> str:
    phases = state.get("phases") or {}
    pf_entry = phases.get("problem_framing") or {}
    pf = pf_entry.get("data")
    if not pf:
        return "I’ve stored an updated problem framing for your request."

    try:
        pf_dict = pf.model_dump() if hasattr(pf, "model_dump") else pf
        domain = getattr(pf, "business_domain", None) or pf_dict.get("business_domain")
        outcome = getattr(pf, "primary_outcome", None) or pf_dict.get("primary_outcome")
        return (
            "I’ve framed your problem.\n\n"
            f"- Business domain: {domain}\n"
            f"- Primary outcome: {outcome}"
        )
    except Exception:
        return "I’ve stored an updated problem framing for your request."

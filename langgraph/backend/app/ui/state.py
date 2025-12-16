from __future__ import annotations

from typing import Any, Dict, Optional

from app.state import SageState


def init_state() -> SageState:
    return {
        "messages": [],
        "user_query": "",
        "phases": {},
        "user_lang": "en",  # UI fallback; graph may overwrite
        "hilp": {
            "hilp_request": None,
            "hilp_round": 0,
            "hilp_answers": {},
            "proceed_anyway": None,
        },
        "errors": [],
    }


def get_hilp_block(state: SageState) -> Dict[str, Any]:
    return state.get("hilp") or {}


def get_hilp_request(state: SageState) -> Optional[Dict[str, Any]]:
    hilp = get_hilp_block(state)
    req = hilp.get("hilp_request")
    return req or None


def is_hilp_active(state: SageState) -> bool:
    req = get_hilp_request(state)
    questions = (req or {}).get("questions") or []
    return bool(req and questions)


def summarize_problem_frame(state: SageState) -> str:
    pf = state.get("problem_frame")
    if not pf:
        return "I’ve stored an updated problem framing for your request."

    try:
        domain = getattr(pf, "business_domain", None) or pf.get("business_domain")
        outcome = getattr(pf, "primary_outcome", None) or pf.get("primary_outcome")
        return (
            "I’ve framed your problem.\n\n"
            f"- Business domain: {domain}\n"
            f"- Primary outcome: {outcome}"
        )
    except Exception:
        return "I’ve stored an updated problem framing for your request."

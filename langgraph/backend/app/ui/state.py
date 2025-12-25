from __future__ import annotations

from app.state import SageState


def init_state() -> SageState:
    return {
        "messages": [],
        "user_query": "",
        "phases": {},
        "user_lang": "en",  # UI fallback; graph may overwrite
        "errors": [],
    }


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

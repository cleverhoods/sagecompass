from __future__ import annotations

from typing import Callable, Literal

from langgraph.graph import END
from langgraph.types import Command

from app.state import SageState
from app.utils.logger import log


def make_node_supervisor(
    *,
    pf_phase: str = "problem_framing",
    detect_lang_phase: str = "detect_language",
) -> Callable[[SageState], Command[str]]:
    def node_supervisor(state: SageState) -> Command[Literal["problem_framing", "translator", "detect_language", END]]:
        # Detect language.
        if (state.get("user_query") or state.get("messages")) and not state.get("user_lang"):
            return Command(goto=detect_lang_phase)

        phases = state.get("phases") or {}
        pf_entry = phases.get(pf_phase) or {}
        pf_status = pf_entry.get("status")
        pf_data = pf_entry.get("data")

        log("SUPERVISOR: pf status", {"status": pf_status, "has_data": pf_data is not None})

        if pf_status != "complete" or pf_data is None:
            return Command(goto=pf_phase)

        return Command(goto="translator")

    return node_supervisor

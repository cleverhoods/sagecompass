from __future__ import annotations

from typing import Callable, Literal

from langgraph.graph import END
from langgraph.types import Command

from app.state import SageState, Hilp, HilpRequest
from app.utils.logger import log


def make_node_supervisor(
    *,
    pf_phase: str = "problem_framing",
    hilp_node: str = "hilp",
    detect_lang_phase: str = "detect_language",
) -> Callable[[SageState], Command[str]]:
    def node_supervisor(state: SageState) -> Command[Literal["hilp", "problem_framing", "translator", "detect_language", END]]:
        # Detect language.
        if (state.get("user_query") or state.get("messages")) and not state.get("user_lang"):
            return Command(goto=detect_lang_phase)

        hilp_block: Hilp | None = state.get("hilp")  # type: ignore[assignment]
        hilp_block = hilp_block or {}

        req: HilpRequest | None = hilp_block.get("hilp_request")  # type: ignore[assignment]
        log("SUPERVISOR: hilp_request", {"hilp_request": req})

        if isinstance(req, dict) and req:
            hilp_round = int(hilp_block.get("hilp_round", 0) or 0)
            max_rounds = int(req.get("max_rounds", 3) or 3)

            if hilp_round < max_rounds:
                return Command(goto=hilp_node)

            errors = list(state.get("errors") or [])
            errors.append("HILP max rounds reached")

            hilp_block["hilp_request"] = None
            hilp_block["hilp_round"] = hilp_round

            return Command(
                update={"hilp": hilp_block, "errors": errors},
                goto=END,
            )

        phases = state.get("phases") or {}
        pf_entry = phases.get(pf_phase) or {}
        pf_status = pf_entry.get("status")
        pf_data = pf_entry.get("data")

        if pf_status != "complete" or pf_data is None:
            return Command(goto=pf_phase)

        return Command(goto="translator")

    return node_supervisor

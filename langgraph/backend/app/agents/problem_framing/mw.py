from __future__ import annotations

from typing import Any

from langchain.agents import AgentState
from langchain.agents.middleware import after_agent
from langgraph.runtime import Runtime

from app.utils.logger import log

from .schema import ProblemFrame
from .hilp_policy import compute_hilp_meta

PHASE_KEY = "problem_framing"

@after_agent
def problem_framing_hilp(state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
    pf = state.get("structured_response")

    if pf is None:
        log.warning(
            "HILP middleware: missing structured_response",
            extra={"phase": PHASE_KEY},
        )
        return None

    if not isinstance(pf, ProblemFrame):
        try:
            pf = ProblemFrame.model_validate(pf)
        except Exception as e:
            log.exception(
                "HILP middleware: invalid structured_response",
                extra={"phase": PHASE_KEY, "error": str(e)},
            )
            return None

    hilp_meta = compute_hilp_meta(pf)

    log(
        "HILP policy evaluated",
        {"phase": PHASE_KEY, "hilp_meta": hilp_meta},
    )

    # IMPORTANT:
    # - This returns metadata in the agent result (for observability).
    # - Nodes still must persist routing signals into SageState explicitly.
    return {"hilp_meta": hilp_meta}

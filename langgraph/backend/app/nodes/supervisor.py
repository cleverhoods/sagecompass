from __future__ import annotations

from typing import Callable, Literal

from langgraph.graph import END
from langgraph.types import Command, Runtime

from app.state import SageState
from app.runtime import SageRuntimeContext
from app.utils.logger import log


def make_node_supervisor(
    *,
    pf_phase: str = "problem_framing",
) -> Callable[[SageState], Command[str]]:
    def node_supervisor(
        state: SageState, runtime: Runtime[SageRuntimeContext] | None = None
    ) -> Command[Literal["problem_framing", END]]:

        phases = state.get("phases") or {}
        pf_entry = phases.get(pf_phase) or {}
        pf_status = pf_entry.get("status")
        pf_data = pf_entry.get("data")

        log("SUPERVISOR: pf status", {"status": pf_status, "has_data": pf_data is not None})

        if pf_status != "complete" or pf_data is None:
            return Command(goto=pf_phase)

        return Command(goto=END)

    return node_supervisor

"""Problem framing phase subgraph wiring."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, cast

from langgraph.graph import StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.runtime import Runtime

from app.agents.problem_framing.agent import build_agent as build_problem_framing_agent
from app.nodes import (
    make_node_phase_supervisor,
    make_node_problem_framing,
)
from app.runtime import SageRuntimeContext
from app.state import SageState


def build_problem_framing_subgraph(
    *,
    problem_framing_agent: Any | None = None,
) -> CompiledStateGraph[SageState, SageRuntimeContext, SageState, SageState]:
    """Phase Subgraph: problem_framing.

    Purpose:
        Wire the problem framing node and phase supervisor.

    Side effects/state writes:
        None (graph wiring only).

    Returns:
        A compiled phase subgraph for problem framing.
    """
    graph = StateGraph(SageState, context_schema=SageRuntimeContext)
    phase = "problem_framing"

    def _as_runtime_node(node):
        return cast(Callable[[SageState, Runtime[SageRuntimeContext]], Any], node)

    # Inject all nodes
    resolved_problem_framing_agent = (
        problem_framing_agent or build_problem_framing_agent()
    )

    graph.add_node(
        "problem_framing",
        _as_runtime_node(
            make_node_problem_framing(
                agent=resolved_problem_framing_agent,
                phase=phase,
                goto="phase_supervisor",
            )
        ),
    )

    # Supervisor reused across all phases
    graph.add_node(
        "phase_supervisor",
        _as_runtime_node(
            make_node_phase_supervisor(
                phase=phase,
            )
        ),
    )

    # Control flow (loop + termination)
    graph.set_entry_point("phase_supervisor")

    return cast(
        CompiledStateGraph[SageState, SageRuntimeContext, SageState, SageState],
        graph.compile(),
    )

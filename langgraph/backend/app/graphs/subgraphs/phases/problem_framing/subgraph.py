"""Problem framing phase subgraph wiring."""

from __future__ import annotations

from typing import Any, Literal

from langgraph.graph import StateGraph
from langgraph.runtime import Runtime
from langgraph.types import Command

from app.nodes.phase_supervisor import make_node_phase_supervisor
from app.nodes.problem_framing import make_node_problem_framing
from app.runtime import SageRuntimeContext
from app.state import SageState


def build_problem_framing_subgraph(  # type: ignore[no-untyped-def]
    *,
    problem_framing_agent: Any | None = None,
):
    """Phase Subgraph: problem_framing.

    Note: Return type omitted due to LangGraph's use of generic TypeVars in CompiledStateGraph.

    Purpose:
        Wire the problem framing node and phase supervisor.

    Side effects/state writes:
        None (graph wiring only).

    Returns:
        A compiled phase subgraph for problem framing.
    """
    graph = StateGraph(SageState, context_schema=SageRuntimeContext)
    phase = "problem_framing"

    # Inject all nodes
    resolved_problem_framing_agent = problem_framing_agent
    if resolved_problem_framing_agent is None:
        from app.agents.problem_framing.agent import (
            build_agent as build_problem_framing_agent,
        )

        resolved_problem_framing_agent = build_problem_framing_agent()

    problem_framing_node = make_node_problem_framing(
        agent=resolved_problem_framing_agent,
        phase=phase,
        goto="phase_supervisor",
    )
    phase_supervisor_node = make_node_phase_supervisor(phase=phase)

    def _phase_supervisor(
        state: SageState,
        *,
        runtime: Runtime[SageRuntimeContext],
    ) -> Command[Literal["problem_framing", "__end__"]]:
        cmd = phase_supervisor_node(state, runtime=runtime)
        if cmd.goto == "problem_framing":
            return Command(update=cmd.update, goto="problem_framing")
        return Command(update=cmd.update, goto="__end__")

    # Add nodes - problem_framing matches protocol directly
    graph.add_node("problem_framing", problem_framing_node)

    # Supervisor has goto transformation logic so needs wrapper
    graph.add_node("phase_supervisor", _phase_supervisor)

    # Control flow (loop + termination)
    graph.set_entry_point("phase_supervisor")

    return graph.compile()

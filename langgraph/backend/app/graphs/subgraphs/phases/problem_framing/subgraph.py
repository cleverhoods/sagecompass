"""Problem framing phase subgraph wiring."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, Literal, TypeVar

from langgraph.graph import StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.runtime import Runtime
from langgraph.types import Command

from app.nodes.phase_supervisor import make_node_phase_supervisor
from app.nodes.problem_framing import make_node_problem_framing
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
    T = TypeVar("T")

    def _as_runtime_node(node: Callable[[SageState, Runtime[SageRuntimeContext] | None], T]) -> Callable[[SageState, Runtime[SageRuntimeContext]], T]:
        def runtime_node(state: SageState, runtime: Runtime[SageRuntimeContext]) -> T:
            return node(state, runtime)

        return runtime_node

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

    def _problem_framing(
        state: SageState,
        runtime: Runtime[SageRuntimeContext] | None = None,
    ) -> Command[Literal["phase_supervisor"]]:
        return problem_framing_node(state, runtime)

    def _phase_supervisor(
        state: SageState,
        runtime: Runtime[SageRuntimeContext] | None = None,
    ) -> Command[Literal["problem_framing", "__end__"]]:
        cmd = phase_supervisor_node(state, runtime)
        if cmd.goto == "problem_framing":
            return cmd
        return Command(update=cmd.update, goto="__end__")

    graph.add_node("problem_framing", _as_runtime_node(_problem_framing))

    # Supervisor reused across all phases
    graph.add_node("phase_supervisor", _as_runtime_node(_phase_supervisor))

    # Control flow (loop + termination)
    graph.set_entry_point("phase_supervisor")

    compiled_graph: CompiledStateGraph[SageState, SageRuntimeContext, SageState, SageState] = graph.compile()
    return compiled_graph

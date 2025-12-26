from __future__ import annotations

from collections.abc import Callable

from langgraph.graph import StateGraph, START
from langgraph.graph.state import CompiledStateGraph
from app.state import SageState


# Type alias for node callables operating on SageState.
NodeFn = Callable[[SageState], object]


def build_main_app(
    *,
    supervisor_node: NodeFn,
    problem_framing_node: NodeFn,
) -> CompiledStateGraph:
    """
    Graph factory for the main SageCompass graph.

    Contracts:
    - No import-time construction (factory only).
    - Receives fully dependency-injected node callables.
    - Only static edge is START -> entry node ("supervisor").
    """
    graph = StateGraph(SageState)

    graph.add_node("supervisor", supervisor_node)

    graph.add_node("problem_framing", problem_framing_node)

    graph.add_edge(START, "supervisor")

    return graph.compile()

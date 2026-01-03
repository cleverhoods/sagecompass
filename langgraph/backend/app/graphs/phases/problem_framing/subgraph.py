"""Problem framing phase subgraph wiring."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, cast

from langgraph.graph import StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.runtime import Runtime

from app.agents.ambiguity.agent import build_agent as build_ambiguity_agent
from app.agents.ambiguity_detector.agent import build_agent as build_ambiguity_detector_agent
from app.agents.problem_framing.agent import build_agent as build_problem_framing_agent
from app.nodes import (
    make_node_ambiguity_detection,
    make_node_clarify_ambiguity,
    make_node_guardrails_check,
    make_node_phase_supervisor,
    make_node_problem_framing,
    make_node_retrieve_context,
)
from app.runtime import SageRuntimeContext
from app.state import SageState
from app.tools.context_lookup import context_lookup


def build_problem_framing_subgraph(
    *,
    ambiguity_detector_agent: Any | None = None,
    ambiguity_agent: Any | None = None,
    problem_framing_agent: Any | None = None,
    retrieval_tool: Any | None = None,
) -> CompiledStateGraph[SageState, SageRuntimeContext, SageState, SageState]:
    """Phase Subgraph: problem_framing.

    Purpose:
        Wire retrieval, ambiguity detection, clarification, and framing nodes.

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
    resolved_retrieval_tool = retrieval_tool or context_lookup
    resolved_ambiguity_detector = ambiguity_detector_agent or build_ambiguity_detector_agent()
    resolved_ambiguity_agent = ambiguity_agent or build_ambiguity_agent()
    resolved_problem_framing_agent = problem_framing_agent or build_problem_framing_agent()

    graph.add_node(
        "retrieve_context",
        _as_runtime_node(
            make_node_retrieve_context(
                tool=resolved_retrieval_tool,
                phase=phase,
                goto="phase_supervisor",
            )
        ),
    )

    graph.add_node(
        "ambiguity_detection",
        _as_runtime_node(
            make_node_ambiguity_detection(
                node_agent=resolved_ambiguity_detector,
                phase=phase,
                goto="phase_supervisor",
            )
        ),
    )

    graph.add_node(
        "clarify_ambiguity",
        _as_runtime_node(
            make_node_clarify_ambiguity(
                node_agent=resolved_ambiguity_agent,
                phase=phase,
                goto="phase_supervisor",
            )
        ),
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


    graph.add_node(
        "guardrails_check",
        _as_runtime_node(make_node_guardrails_check(goto_if_safe="phase_supervisor")),
    )

    # Supervisor reused across all phases
    graph.add_node(
        "phase_supervisor",
        _as_runtime_node(
            make_node_phase_supervisor(
                phase=phase,
                retrieve_node="retrieve_context",
                ambiguity_node="ambiguity_detection",
                clarify_node="clarify_ambiguity",
                retrieval_enabled=True,
                requires_evidence=True,
                clarification_enabled=True,
            )
        ),
    )

    # Control flow (loop + termination)
    graph.set_entry_point("phase_supervisor")

    return cast(
        CompiledStateGraph[SageState, SageRuntimeContext, SageState, SageState],
        graph.compile(),
    )

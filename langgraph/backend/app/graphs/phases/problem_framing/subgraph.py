from __future__ import annotations

from langgraph.graph import StateGraph
from langgraph.graph.state import CompiledStateGraph

from app.state import SageState
from app.agents.problem_framing.agent import build_agent as build_problem_framing_agent
from app.agents.ambiguity_detector.agent import build_agent as build_ambiguity_detector_agent
from app.agents.ambiguity.agent import build_agent as build_ambiguity_agent

from app.nodes import (
    make_node_retrieve_context,
    make_node_ambiguity_detection,
    make_node_problem_framing,
    make_node_clarify_ambiguity,
    make_node_phase_supervisor,
    make_node_guardrails_check,
)
from app.tools.context_lookup import context_lookup


def build_problem_framing_subgraph() -> CompiledStateGraph[SageState]:
    """
    Phase Subgraph: problem_framing

    Purpose:
        Wire retrieval, ambiguity detection, clarification, and framing nodes.

    Side effects/state writes:
        None (graph wiring only).

    Returns:
        A compiled phase subgraph for problem framing.
    """
    graph = StateGraph(SageState)
    phase = "problem_framing"

    # Inject all nodes
    graph.add_node("retrieve_context", make_node_retrieve_context(
        tool=context_lookup,
        phase=phase,
    ))

    graph.add_node("ambiguity_detection", make_node_ambiguity_detection(
        node_agent=build_ambiguity_detector_agent(),
        phase=phase,
    ))

    graph.add_node("clarify_ambiguity", make_node_clarify_ambiguity(
        node_agent=build_ambiguity_agent(),
        phase=phase,
    ))

    graph.add_node("problem_framing", make_node_problem_framing(
        agent=build_problem_framing_agent(),
        phase=phase,
    ))


    graph.add_node("guardrails_check", make_node_guardrails_check())

    # 🧠 Supervisor reused across all phases
    graph.add_node("phase_supervisor", make_node_phase_supervisor(
        phase=phase,
        retrieve_node="retrieve_context"
    ))

    # Control flow (loop + termination)
    graph.set_entry_point("retrieve_context")
    graph.set_finish_point("problem_framing")

    return graph.compile()

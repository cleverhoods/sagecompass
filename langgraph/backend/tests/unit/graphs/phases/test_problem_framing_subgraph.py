from __future__ import annotations

from types import SimpleNamespace

from app.graphs.phases.problem_framing.subgraph import build_problem_framing_subgraph


def test_problem_framing_subgraph_routes_via_phase_supervisor() -> None:
    dummy = SimpleNamespace(invoke=lambda *args, **kwargs: {})

    graph = build_problem_framing_subgraph(
        ambiguity_scan_agent=dummy,
        ambiguity_clarification_agent=dummy,
        problem_framing_agent=dummy,
        retrieval_tool=dummy,
    )

    graph_view = graph.get_graph()
    node_names = set(graph_view.nodes.keys())

    assert "phase_supervisor" in node_names
    assert "supervisor" not in node_names
    assert "__start__" in node_names
    assert "__end__" in node_names

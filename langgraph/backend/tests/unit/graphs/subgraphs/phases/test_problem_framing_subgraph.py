from __future__ import annotations

from types import SimpleNamespace

from app.graphs.subgraphs.phases.problem_framing.subgraph import (
    build_problem_framing_subgraph,
)


def test_problem_framing_subgraph_routes_via_phase_supervisor() -> None:
    dummy = SimpleNamespace(invoke=lambda *args, **kwargs: {})

    graph = build_problem_framing_subgraph(
        problem_framing_agent=dummy,
    )

    graph_view = graph.get_graph()
    node_names = set(graph_view.nodes.keys())

    assert "phase_supervisor" in node_names
    assert "supervisor" not in node_names
    assert "__start__" in node_names
    assert "__end__" in node_names

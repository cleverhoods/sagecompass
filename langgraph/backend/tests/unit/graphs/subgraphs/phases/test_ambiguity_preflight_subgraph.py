from __future__ import annotations

from types import SimpleNamespace

from app.graphs.subgraphs.ambiguity_preflight.subgraph import (
    build_ambiguity_preflight_subgraph,
)


def test_ambiguity_preflight_subgraph_wires_nodes() -> None:
    dummy = SimpleNamespace(invoke=lambda *args, **kwargs: {})

    graph = build_ambiguity_preflight_subgraph(
        ambiguity_scan_agent=dummy,
        ambiguity_clarification_agent=dummy,
        retrieve_tool=dummy,
    )

    graph_view = graph.get_graph()
    node_names = set(graph_view.nodes.keys())

    assert "ambiguity_supervisor" in node_names
    assert "ambiguity_scan" in node_names
    assert "retrieve_context" in node_names
    assert "ambiguity_clarification" in node_names
    assert "ambiguity_clarification_external" in node_names
    assert "__start__" in node_names
    assert "__end__" in node_names

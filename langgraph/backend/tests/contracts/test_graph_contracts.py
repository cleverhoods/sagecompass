from __future__ import annotations

import app.graphs.graph as graphs
from app.graphs.graph import build_main_app
from app.runtime import SageRuntimeContext
from langgraph.types import Runtime


class _FakeCompiledGraph(dict):
    pass


class _FakeStateGraph:
    def __init__(self, state_type, context_schema=None):
        self.state_type = state_type
        self.context_schema = context_schema
        self.nodes: list[tuple[str, object]] = []
        self.edges: list[tuple[str, str]] = []

    def add_node(self, name: str, fn: object) -> None:
        self.nodes.append((name, fn))

    def add_edge(self, start: str, end: str) -> None:
        self.edges.append((start, end))

    def compile(self) -> _FakeCompiledGraph:
        return _FakeCompiledGraph(
            {
                "state_type": self.state_type,
                "context_schema": self.context_schema,
                "nodes": self.nodes,
                "edges": self.edges,
            }
        )


def test_build_main_app_wires_nodes_and_edges(monkeypatch):
    fake_graph = _FakeStateGraph
    fake_start = "START"
    monkeypatch.setattr(graphs, "StateGraph", fake_graph)
    monkeypatch.setattr(graphs, "START", fake_start)

    supervisor = lambda state: "supervisor-called"
    problem_framing = lambda state: "problem-framing-called"

    compiled = build_main_app(supervisor_node=supervisor, problem_framing_node=problem_framing)

    assert isinstance(compiled, _FakeCompiledGraph)
    assert compiled["state_type"] is graphs.SageState
    assert compiled["context_schema"] is SageRuntimeContext
    assert ("supervisor", supervisor) in compiled["nodes"]
    assert ("problem_framing", problem_framing) in compiled["nodes"]
    assert (fake_start, "supervisor") in compiled["edges"]

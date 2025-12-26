from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Iterable, List, TypeVar

from .state import CompiledStateGraph

T = TypeVar("T")

# Simple END sentinel to mimic langgraph.graph.END
END: str = "END"
START: str = "START"


def add_messages(messages: Iterable[T]) -> List[T]:
    """Identity helper used for Annotated typings."""
    return list(messages)


class StateGraph:
    def __init__(self, state_type: type) -> None:
        self.state_type = state_type
        self.nodes: list[tuple[str, Callable]] = []
        self.edges: list[tuple[str, str]] = []

    def add_node(self, name: str, fn: Callable) -> None:
        self.nodes.append((name, fn))

    def add_edge(self, start: str, end: str) -> None:
        self.edges.append((start, end))

    def compile(self) -> CompiledStateGraph:
        return CompiledStateGraph({"state_type": self.state_type, "nodes": self.nodes, "edges": self.edges})

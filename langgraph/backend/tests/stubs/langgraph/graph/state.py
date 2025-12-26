from __future__ import annotations

from typing import Any, Callable


class CompiledStateGraph(dict):
    """
    Minimal stub to mirror langgraph.graph.state.CompiledStateGraph.
    Stores provided metadata for assertions in tests.
    """

    def __init__(self, payload: dict[str, Any] | None = None) -> None:
        super().__init__(payload or {})

    def invoke(self, *args: Any, **kwargs: Any) -> Any:  # pragma: no cover - convenience stub
        return kwargs.get("state") if "state" in kwargs else None

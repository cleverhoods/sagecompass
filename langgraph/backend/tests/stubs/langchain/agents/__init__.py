from __future__ import annotations

from typing import Any, Callable, Dict

from .middleware import AgentMiddleware

AgentState = Dict[str, Any]


def create_agent(*args, **kwargs) -> Callable[..., Any]:  # pragma: no cover - unused helper
    def _agent(*_args, **_kwargs):
        return {}

    return _agent


__all__ = ["AgentMiddleware", "AgentState", "create_agent"]

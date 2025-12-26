from __future__ import annotations

from typing import Any, Callable, Protocol, TypeVar

from langchain_core.messages import BaseMessage

ModelRequest = TypeVar("ModelRequest")
T = TypeVar("T")


class AgentMiddleware(Protocol[T]):
    """Callable middleware protocol stub."""

    def __call__(self, *args: Any, **kwargs: Any) -> Any: ...


def after_agent(fn: Callable[..., T]) -> Callable[..., T]:
    """Decorator that returns a callable with an `after_agent` attribute."""

    class _Middleware:
        def __init__(self, func: Callable[..., T]) -> None:
            self.after_agent = func

        def __call__(self, *args: Any, **kwargs: Any) -> Any:
            return self.after_agent(*args, **kwargs)

    return _Middleware(fn)


def dynamic_prompt(fn: Callable[..., BaseMessage | str]) -> Callable[..., BaseMessage | str]:
    """Decorator passthrough used for dynamic prompts."""

    return fn

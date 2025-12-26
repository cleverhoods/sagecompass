from __future__ import annotations

from typing import Callable, TypeVar

T = TypeVar("T", bound=Callable[..., object])


class BaseTool:
    """Minimal tool stub."""

    def __init__(self, name: str, func: Callable[..., object]) -> None:
        self.name = name
        self.func = func

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)


def tool(name: str) -> Callable[[T], T]:
    """Decorator that tags a callable with a tool name."""

    def decorator(fn: T) -> T:
        setattr(fn, "name", name)
        return fn

    return decorator

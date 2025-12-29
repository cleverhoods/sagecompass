from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Generic, TypeVar

T = TypeVar("T")


@dataclass
class Command(Generic[T]):
    update: dict[str, Any] | None = None
    goto: T | None = None


@dataclass
class Runtime(Generic[T]):
    context: T | None = None
    checkpointer: Any | None = None
    config: dict[str, Any] = field(default_factory=dict)


def interrupt(value: Any | None = None) -> Any:
    """Stub interrupt that simply returns the provided value."""
    return value

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, List, TypeVar

T = TypeVar("T")

# Simple END sentinel to mimic langgraph.graph.END
END: str = "END"


def add_messages(messages: Iterable[T]) -> List[T]:
    """Identity helper used for Annotated typings."""
    return list(messages)

from __future__ import annotations

from typing import Iterable

from . import AnyMessage, BaseMessage, HumanMessage


def get_buffer_string(messages: Iterable[BaseMessage]) -> str:
    """Render a simple buffer string for the provided messages."""
    rendered: list[str] = []
    for msg in messages:
        prefix = "Human: " if isinstance(msg, HumanMessage) else "Message: "
        rendered.append(prefix + str(msg.content))
    return "\n".join(rendered)

__all__ = ["AnyMessage", "BaseMessage", "HumanMessage", "get_buffer_string"]

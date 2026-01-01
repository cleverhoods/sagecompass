from __future__ import annotations

from typing import Optional
from langchain_core.messages import HumanMessage
from langchain_core.messages.utils import AnyMessage

def get_latest_user_input(messages: list[AnyMessage]) -> Optional[str]:
    """
    Finds the most recent HumanMessage in the message stream.

    Returns:
        The content of the most recent user message, or None if not found.
    """
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage):
            return msg.content
    return None

"""Prompting utilities for LLM context assembly.

Provides canonical functions for building LLM message context,
ensuring separation between conversation messages and trace events.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import TYPE_CHECKING, Any

from langchain_core.messages import (
    AIMessage,
    AnyMessage,
    BaseMessage,
    HumanMessage,
    SystemMessage,
)

if TYPE_CHECKING:
    from app.state import SageState


def build_llm_messages(
    state: SageState,
    *,
    max_messages: int | None = None,
    exclude_patterns: Sequence[str] | None = None,
    include_types: tuple[type[BaseMessage], ...] | None = None,
    filter_fn: Callable[[AnyMessage], bool] | None = None,
) -> list[AnyMessage]:
    """Build LLM conversation context from state messages.

    This is the canonical function for assembling messages to send to an LLM.
    It filters state.messages to include only conversation-relevant content,
    explicitly excluding trace events (which are stored in state.events).

    Args:
        state: SageState containing messages.
        max_messages: Optional limit on number of messages to return (most recent).
        exclude_patterns: Optional list of content patterns to exclude.
        include_types: Optional tuple of message types to include.
            Defaults to (HumanMessage, AIMessage, SystemMessage).
        filter_fn: Optional custom filter function. If provided, takes precedence
            over include_types and exclude_patterns.

    Returns:
        List of messages suitable for LLM context.

    Example:
        ```python
        # Get last 10 conversation messages
        messages = build_llm_messages(state, max_messages=10)

        # Get only user and AI messages
        messages = build_llm_messages(
            state,
            include_types=(HumanMessage, AIMessage),
        )
        ```
    """
    # Default message types for conversation
    if include_types is None:
        include_types = (HumanMessage, AIMessage, SystemMessage)

    messages = state.messages

    # Apply filter
    if filter_fn is not None:
        filtered = [msg for msg in messages if filter_fn(msg)]
    else:
        filtered = []
        for msg in messages:
            # Type filter
            if not isinstance(msg, include_types):
                continue

            # Pattern exclusion
            if exclude_patterns:
                content = _get_message_content(msg)
                if any(pattern in content for pattern in exclude_patterns):
                    continue

            filtered.append(msg)

    # Apply max_messages limit (take most recent)
    if max_messages is not None and len(filtered) > max_messages:
        filtered = filtered[-max_messages:]

    return filtered


def get_user_messages(state: SageState) -> list[HumanMessage]:
    """Extract only user messages from state.

    Args:
        state: SageState containing messages.

    Returns:
        List of HumanMessage instances only.
    """
    return [msg for msg in state.messages if isinstance(msg, HumanMessage)]


def get_ai_messages(state: SageState) -> list[AIMessage]:
    """Extract only AI messages from state.

    Args:
        state: SageState containing messages.

    Returns:
        List of AIMessage instances only.
    """
    return [msg for msg in state.messages if isinstance(msg, AIMessage)]


def get_last_user_message(state: SageState) -> HumanMessage | None:
    """Get the most recent user message.

    Args:
        state: SageState containing messages.

    Returns:
        Most recent HumanMessage or None if no user messages exist.
    """
    for msg in reversed(state.messages):
        if isinstance(msg, HumanMessage):
            return msg
    return None


def _get_message_content(msg: AnyMessage) -> str:
    """Extract string content from a message.

    Args:
        msg: Message to extract content from.

    Returns:
        String content or empty string if not extractable.
    """
    content: Any = msg.content
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        # Handle multi-part messages
        parts = []
        for part in content:
            if isinstance(part, str):
                parts.append(part)
            elif isinstance(part, dict) and "text" in part:
                parts.append(str(part["text"]))
        return " ".join(parts)
    return str(content)

"""Tests for prompting utilities."""

from __future__ import annotations

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from app.platform.runtime.prompting import (
    build_llm_messages,
    get_ai_messages,
    get_last_user_message,
    get_user_messages,
)
from app.state import SageState


def _create_state_with_messages(messages: list) -> SageState:
    """Helper to create a state with messages."""
    state = SageState()
    # Direct assignment for testing (bypasses reducer)
    object.__setattr__(state, "messages", messages)
    return state


def test_build_llm_messages_returns_empty_for_empty_state():
    """Test that empty state returns empty message list."""
    state = SageState()
    messages = build_llm_messages(state)
    assert messages == []


def test_build_llm_messages_includes_conversation_types():
    """Test that build_llm_messages includes Human, AI, and System messages."""
    messages = [
        SystemMessage(content="System instruction"),
        HumanMessage(content="User question"),
        AIMessage(content="AI response"),
    ]
    state = _create_state_with_messages(messages)

    result = build_llm_messages(state)

    assert len(result) == 3
    assert isinstance(result[0], SystemMessage)
    assert isinstance(result[1], HumanMessage)
    assert isinstance(result[2], AIMessage)


def test_build_llm_messages_respects_max_messages():
    """Test that max_messages limits output."""
    messages = [
        HumanMessage(content="Message 1"),
        AIMessage(content="Response 1"),
        HumanMessage(content="Message 2"),
        AIMessage(content="Response 2"),
        HumanMessage(content="Message 3"),
    ]
    state = _create_state_with_messages(messages)

    result = build_llm_messages(state, max_messages=2)

    assert len(result) == 2
    # Should be most recent messages
    assert result[0].content == "Response 2"
    assert result[1].content == "Message 3"


def test_build_llm_messages_excludes_patterns():
    """Test that exclude_patterns filters messages."""
    messages = [
        HumanMessage(content="Real question"),
        AIMessage(content="Running safety checks."),  # Should be excluded
        AIMessage(content="Real response"),
    ]
    state = _create_state_with_messages(messages)

    result = build_llm_messages(state, exclude_patterns=["Running safety"])

    assert len(result) == 2
    assert result[0].content == "Real question"
    assert result[1].content == "Real response"


def test_build_llm_messages_with_include_types():
    """Test filtering by message type."""
    messages = [
        SystemMessage(content="System"),
        HumanMessage(content="User"),
        AIMessage(content="AI"),
    ]
    state = _create_state_with_messages(messages)

    result = build_llm_messages(state, include_types=(HumanMessage, AIMessage))

    assert len(result) == 2
    assert isinstance(result[0], HumanMessage)
    assert isinstance(result[1], AIMessage)


def test_build_llm_messages_with_custom_filter():
    """Test custom filter function."""
    messages = [
        HumanMessage(content="Short"),
        AIMessage(content="This is a longer message"),
        HumanMessage(content="Tiny"),
    ]
    state = _create_state_with_messages(messages)

    # Filter for messages longer than 10 chars
    result = build_llm_messages(state, filter_fn=lambda m: len(str(m.content)) > 10)

    assert len(result) == 1
    assert result[0].content == "This is a longer message"


def test_get_user_messages_extracts_human_only():
    """Test that get_user_messages returns only HumanMessage."""
    messages = [
        SystemMessage(content="System"),
        HumanMessage(content="User 1"),
        AIMessage(content="AI"),
        HumanMessage(content="User 2"),
    ]
    state = _create_state_with_messages(messages)

    result = get_user_messages(state)

    assert len(result) == 2
    assert all(isinstance(m, HumanMessage) for m in result)
    assert result[0].content == "User 1"
    assert result[1].content == "User 2"


def test_get_ai_messages_extracts_ai_only():
    """Test that get_ai_messages returns only AIMessage."""
    messages = [
        HumanMessage(content="User"),
        AIMessage(content="AI 1"),
        HumanMessage(content="User 2"),
        AIMessage(content="AI 2"),
    ]
    state = _create_state_with_messages(messages)

    result = get_ai_messages(state)

    assert len(result) == 2
    assert all(isinstance(m, AIMessage) for m in result)


def test_get_last_user_message_returns_most_recent():
    """Test that get_last_user_message returns the most recent HumanMessage."""
    messages = [
        HumanMessage(content="First"),
        AIMessage(content="Response"),
        HumanMessage(content="Last"),
        AIMessage(content="Final response"),
    ]
    state = _create_state_with_messages(messages)

    result = get_last_user_message(state)

    assert result is not None
    assert result.content == "Last"


def test_get_last_user_message_returns_none_if_empty():
    """Test that get_last_user_message returns None if no HumanMessage exists."""
    messages = [AIMessage(content="AI only")]
    state = _create_state_with_messages(messages)

    result = get_last_user_message(state)

    assert result is None


def test_build_llm_messages_does_not_access_events():
    """Test that build_llm_messages only uses state.messages, not state.events.

    This is a critical contract test - LLM context must come from messages only.
    """
    from app.platform.core.dto.events import TraceEvent

    state = SageState()

    # Add some messages
    messages = [HumanMessage(content="User question")]
    object.__setattr__(state, "messages", messages)

    # Add some events (these should NOT appear in LLM context)
    events = [
        TraceEvent.create(owner="test", kind="routing", message="Should not appear"),
    ]
    object.__setattr__(state, "events", events)

    result = build_llm_messages(state)

    # Only the message should be included
    assert len(result) == 1
    assert result[0].content == "User question"

"""Tests for TraceEvent DTO."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from app.platform.core.dto.events import EventKind, TraceEvent


def test_trace_event_is_frozen():
    """Test that TraceEvent is immutable."""
    event = TraceEvent.create(
        owner="test_node",
        kind="routing",
        message="Test message",
    )

    with pytest.raises(AttributeError):
        event.message = "Changed"  # type: ignore[misc]


def test_trace_event_create_sets_timestamp():
    """Test that create() factory sets current timestamp."""
    before = datetime.now(UTC)

    event = TraceEvent.create(
        owner="test_node",
        kind="routing",
        message="Test message",
    )

    after = datetime.now(UTC)

    assert before <= event.timestamp <= after
    assert event.timestamp.tzinfo is not None, "Timestamp should be timezone-aware"


def test_trace_event_create_with_all_fields():
    """Test create() with all optional fields."""
    event = TraceEvent.create(
        owner="supervisor",
        kind="progress",
        message="Processing phase",
        phase="problem_framing",
        data={"detail": "value"},
    )

    assert event.owner == "supervisor"
    assert event.kind == "progress"
    assert event.message == "Processing phase"
    assert event.phase == "problem_framing"
    assert event.data == {"detail": "value"}


def test_trace_event_kind_type():
    """Test that EventKind accepts valid values."""
    valid_kinds: list[EventKind] = ["routing", "progress", "decision", "error"]

    for kind in valid_kinds:
        event = TraceEvent.create(
            owner="test",
            kind=kind,
            message=f"Test {kind}",
        )
        assert event.kind == kind


def test_trace_event_defaults():
    """Test default values for optional fields."""
    event = TraceEvent.create(
        owner="test",
        kind="routing",
        message="Test",
    )

    assert event.phase is None
    assert event.data == {}


def test_trace_event_data_is_not_mutable():
    """Test that data dict default factory creates new dicts."""
    event1 = TraceEvent.create(owner="test", kind="routing", message="Test 1")
    event2 = TraceEvent.create(owner="test", kind="routing", message="Test 2")

    # Each event should have its own data dict
    assert event1.data is not event2.data


def test_trace_event_uid_is_unique():
    """Test that each event gets a unique uid."""
    event1 = TraceEvent.create(owner="test", kind="routing", message="Test 1")
    event2 = TraceEvent.create(owner="test", kind="routing", message="Test 1")

    assert event1.uid != event2.uid
    assert len(event1.uid) > 0


def test_trace_event_uid_is_set_by_create():
    """Test that create() factory generates a uid."""
    event = TraceEvent.create(
        owner="test",
        kind="routing",
        message="Test",
    )

    assert event.uid is not None
    assert isinstance(event.uid, str)
    assert len(event.uid) == 36  # UUID4 format: 8-4-4-4-12

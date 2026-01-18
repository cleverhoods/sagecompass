"""Tests for trace state reducers."""

from __future__ import annotations

from app.platform.core.dto.events import TraceEvent
from app.state.trace import add_events


def _make_event(message: str) -> TraceEvent:
    """Helper to create a TraceEvent."""
    return TraceEvent.create(
        owner="test",
        kind="routing",
        message=message,
    )


def test_add_events_appends_to_empty():
    """Test adding events to empty list."""
    existing: list[TraceEvent] = []
    new = [_make_event("Event 1"), _make_event("Event 2")]

    result = add_events(existing, new)

    assert len(result) == 2
    assert result[0].message == "Event 1"
    assert result[1].message == "Event 2"


def test_add_events_appends_to_existing():
    """Test adding events to existing list."""
    existing = [_make_event("Existing")]
    new = [_make_event("New")]

    result = add_events(existing, new)

    assert len(result) == 2
    assert result[0].message == "Existing"
    assert result[1].message == "New"


def test_add_events_does_not_mutate_original():
    """Test that add_events doesn't mutate the original list."""
    existing = [_make_event("Existing")]
    original_len = len(existing)
    new = [_make_event("New")]

    add_events(existing, new)

    assert len(existing) == original_len


def test_add_events_with_empty_new():
    """Test adding empty list of events."""
    existing = [_make_event("Existing")]
    new: list[TraceEvent] = []

    result = add_events(existing, new)

    assert len(result) == 1
    assert result[0].message == "Existing"


def test_add_events_deduplicates_by_uid():
    """Test that add_events deduplicates events with the same uid.

    This is critical for subgraph state merges where inherited events
    would otherwise be duplicated.
    """
    event1 = _make_event("Event 1")
    event2 = _make_event("Event 2")
    existing = [event1, event2]

    # Try to add the same events again (simulating subgraph merge)
    new = [event1, event2, _make_event("Event 3")]

    result = add_events(existing, new)

    # Should only have 3 unique events, not 5
    assert len(result) == 3
    assert result[0].message == "Event 1"
    assert result[1].message == "Event 2"
    assert result[2].message == "Event 3"

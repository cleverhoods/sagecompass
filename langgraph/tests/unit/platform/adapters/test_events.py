"""Tests for events adapter layer."""

from __future__ import annotations

from app.platform.adapters.events import emit_event, merge_event_updates
from app.platform.core.dto.events import TraceEvent


def test_emit_event_returns_events_dict():
    """Test that emit_event returns proper state update dict."""
    update = emit_event(
        owner="supervisor",
        kind="routing",
        message="Test message",
    )

    assert "events" in update
    assert isinstance(update["events"], list)
    assert len(update["events"]) == 1
    assert isinstance(update["events"][0], TraceEvent)


def test_emit_event_creates_correct_event():
    """Test that emit_event creates TraceEvent with correct values."""
    update = emit_event(
        owner="test_node",
        kind="progress",
        message="Processing",
        phase="problem_framing",
        data={"step": 1},
    )

    event = update["events"][0]
    assert event.owner == "test_node"
    assert event.kind == "progress"
    assert event.message == "Processing"
    assert event.phase == "problem_framing"
    assert event.data == {"step": 1}


def test_merge_event_updates_combines_events():
    """Test merging multiple event updates."""
    update1 = emit_event(owner="node1", kind="routing", message="Message 1")
    update2 = emit_event(owner="node2", kind="progress", message="Message 2")

    merged = merge_event_updates(update1, update2)

    assert "events" in merged
    assert len(merged["events"]) == 2


def test_merge_event_updates_handles_empty():
    """Test merging with empty updates."""
    update1 = emit_event(owner="node", kind="routing", message="Message")

    merged = merge_event_updates(update1, {})

    assert "events" in merged
    assert len(merged["events"]) == 1


def test_merge_event_updates_all_empty():
    """Test merging only empty updates."""
    merged = merge_event_updates({}, {})

    assert merged == {}

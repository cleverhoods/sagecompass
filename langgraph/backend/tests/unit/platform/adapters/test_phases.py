"""Tests for phase adapter layer."""

from __future__ import annotations

from app.platform.adapters.phases import (
    extract_phase_summary,
    merge_phase_results,
    phase_entry_to_result,
    phase_result_to_entry,
)
from app.platform.core.dto.phases import PhaseResult
from app.state import EvidenceItem, PhaseEntry


def test_phase_result_to_entry_converts_dto_to_state():
    """Test converting PhaseResult DTO to PhaseEntry state model."""
    result = PhaseResult(
        phase_name="test_phase",
        data={"key": "value"},
        error=None,
        status="complete",
        evidence=[{"namespace": ["drupal", "context"], "key": "test-1", "score": 0.95}],
    )

    entry = phase_result_to_entry(result)

    assert isinstance(entry, PhaseEntry)
    assert entry.data == {"key": "value"}
    assert entry.status == "complete"
    assert entry.error == {}
    assert len(entry.evidence) == 1
    assert isinstance(entry.evidence[0], EvidenceItem)


def test_phase_entry_to_result_converts_state_to_dto():
    """Test converting PhaseEntry state model to PhaseResult DTO."""
    entry = PhaseEntry(
        data={"key": "value"},
        error={},
        status="complete",
        evidence=[EvidenceItem(namespace=["drupal", "context"], key="test-1", score=0.95)],
    )

    result = phase_entry_to_result(entry, "test_phase")

    assert isinstance(result, PhaseResult)
    assert result.phase_name == "test_phase"
    assert result.data == {"key": "value"}
    assert result.status == "complete"
    assert len(result.evidence) == 1
    assert result.evidence[0]["key"] == "test-1"


def test_merge_phase_results_combines_data():
    """Test merging phase result into existing entry."""
    existing = PhaseEntry(
        data={"old_key": "old_value"},
        error={},
        status="pending",
        evidence=[],
    )

    result = PhaseResult(
        phase_name="test_phase",
        data={"new_key": "new_value"},
        error=None,
        status="complete",
        evidence=None,
    )

    merged = merge_phase_results(existing, result)

    assert merged.data == {"old_key": "old_value", "new_key": "new_value"}
    assert merged.status == "complete"
    assert merged.evidence == []


def test_extract_phase_summary_returns_structured_data():
    """Test extracting phase summary for logging."""
    entry = PhaseEntry(
        data={"result": "value"},
        error={},
        status="complete",
        evidence=[EvidenceItem(namespace=["drupal", "context"], key="test-1", score=0.95)],
    )

    summary = extract_phase_summary(entry, "test_phase")

    assert summary["phase"] == "test_phase"
    assert summary["status"] == "complete"
    assert summary["has_data"] is True
    assert summary["has_error"] is False
    assert summary["evidence_count"] == 1

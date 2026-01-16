"""Tests for evidence adapter layer."""

from __future__ import annotations

from langchain_core.documents import Document

from app.platform.adapters.evidence import (
    evidence_to_items,
    items_to_evidence_dicts,
    update_phase_evidence,
)
from app.platform.core.dto.evidence import EvidenceBundle
from app.state import EvidenceItem, PhaseEntry


def test_evidence_to_items_converts_dicts_to_models():
    """Test converting evidence dicts from DTO to EvidenceItem models."""
    bundle = EvidenceBundle(
        evidence=[
            {"namespace": ["drupal", "context"], "key": "test-1", "score": 0.95},
            {"namespace": ["drupal", "context"], "key": "test-2", "score": 0.85},
        ],
        context_docs=[],
    )

    items = evidence_to_items(bundle)

    assert len(items) == 2
    assert all(isinstance(item, EvidenceItem) for item in items)
    assert items[0].namespace == ["drupal", "context"]
    assert items[0].key == "test-1"
    assert items[0].score == 0.95


def test_items_to_evidence_dicts_converts_models_to_dicts():
    """Test converting EvidenceItem models to dicts for DTO."""
    items = [
        EvidenceItem(namespace=["drupal", "context"], key="test-1", score=0.95),
        EvidenceItem(namespace=["drupal", "context"], key="test-2", score=0.85),
    ]

    dicts = items_to_evidence_dicts(items)

    assert len(dicts) == 2
    assert all(isinstance(d, dict) for d in dicts)
    assert dicts[0]["namespace"] == ["drupal", "context"]
    assert dicts[0]["key"] == "test-1"
    assert dicts[0]["score"] == 0.95


def test_update_phase_evidence_preserves_phase_data():
    """Test updating phase entry with new evidence preserves existing data."""
    existing = PhaseEntry(
        data={"result": "value"},
        error={},
        status="complete",
        evidence=[],
    )

    bundle = EvidenceBundle(
        evidence=[{"namespace": ["drupal", "context"], "key": "test-1", "score": 0.95}],
        context_docs=[Document(page_content="test")],
    )

    updated = update_phase_evidence(existing, bundle)

    assert updated.data == {"result": "value"}
    assert updated.status == "complete"
    assert len(updated.evidence) == 1
    assert updated.evidence[0].key == "test-1"

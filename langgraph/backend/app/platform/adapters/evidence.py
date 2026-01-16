"""Evidence adapter layer for translating between core DTOs and state models.

This adapter provides boundary translation functions that convert between:
- Core DTOs (pure, extractable): EvidenceBundle
- State models (LangGraph-specific): PhaseEntry with evidence field
"""

from __future__ import annotations

from app.platform.core.dto.evidence import EvidenceBundle
from app.state import EvidenceItem, PhaseEntry


def evidence_to_items(evidence_bundle: EvidenceBundle) -> list[EvidenceItem]:
    """Convert evidence dicts from EvidenceBundle DTO to EvidenceItem models.

    Args:
        evidence_bundle: Core DTO containing evidence as dicts.

    Returns:
        List of EvidenceItem models ready for state persistence.
    """
    return [
        item if isinstance(item, EvidenceItem) else EvidenceItem.model_validate(item)
        for item in evidence_bundle.evidence
    ]


def items_to_evidence_dicts(items: list[EvidenceItem]) -> list[dict]:
    """Convert EvidenceItem models to plain dicts for EvidenceBundle DTO.

    Args:
        items: List of EvidenceItem models from state.

    Returns:
        List of evidence dicts for use in core DTO.
    """
    return [{"namespace": item.namespace, "key": item.key, "score": item.score} for item in items]


def update_phase_evidence(
    phase_entry: PhaseEntry,
    evidence_bundle: EvidenceBundle,
) -> PhaseEntry:
    """Update phase entry with evidence from bundle, preserving other fields.

    Args:
        phase_entry: Existing phase entry to update.
        evidence_bundle: Core DTO with new evidence data.

    Returns:
        New PhaseEntry instance with updated evidence.
    """
    normalized_evidence = evidence_to_items(evidence_bundle)
    return PhaseEntry(
        data=phase_entry.data,
        error=phase_entry.error,
        status=phase_entry.status,
        evidence=normalized_evidence,
    )

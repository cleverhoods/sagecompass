"""Evidence adapter layer for translating between core DTOs and state models.

This adapter provides boundary translation functions that convert between:
- Core DTOs (pure, extractable): EvidenceBundle
- State models (LangGraph-specific): PhaseEntry with evidence field

This adapter also provides runtime wrappers that coordinate evidence collection
with logging and other wiring concerns.
"""

from __future__ import annotations

from app.platform.core.dto.evidence import EvidenceBundle
from app.platform.observability.logger import get_logger
from app.platform.runtime.evidence import collect_phase_evidence as _collect_phase_evidence
from app.state import EvidenceItem, PhaseEntry, SageState


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


def collect_phase_evidence(
    state: SageState,
    *,
    phase: str,
    max_items: int = 8,
) -> EvidenceBundle:
    """Collect evidence for a phase with logging (adapter wrapper).

    This is a runtime wrapper that coordinates evidence collection with logging.
    It accepts SageState and returns pure EvidenceBundle DTO.

    Args:
        state: Current graph state.
        phase: Phase name to collect evidence for.
        max_items: Maximum number of evidence items to collect.

    Returns:
        EvidenceBundle DTO with collected evidence.
    """
    bundle = _collect_phase_evidence(state, phase=phase, max_items=max_items)
    if bundle.missing_store and bundle.evidence:
        logger = get_logger("adapter.evidence")
        logger.warning(
            "adapter.evidence.missing_store",
            phase=phase,
            evidence_count=len(bundle.evidence),
        )
    return bundle

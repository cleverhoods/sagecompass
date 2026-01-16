"""Phase adapter layer for translating between core DTOs and state models.

This adapter provides boundary translation functions that convert between:
- Core DTOs (pure, extractable): PhaseResult
- State models (LangGraph-specific): PhaseEntry
"""

from __future__ import annotations

from app.platform.core.dto.phases import PhaseResult
from app.state import EvidenceItem, PhaseEntry


def phase_result_to_entry(result: PhaseResult) -> PhaseEntry:
    """Convert PhaseResult DTO to PhaseEntry state model.

    Args:
        result: Core DTO with phase execution results.

    Returns:
        PhaseEntry ready for state persistence.
    """
    # Convert evidence dicts to EvidenceItem models if present
    evidence: list[EvidenceItem] = []
    if result.evidence:
        evidence = [EvidenceItem.model_validate(item) for item in result.evidence]

    return PhaseEntry(
        data=result.data,
        error=result.error or {},
        status=result.status,
        evidence=evidence,
    )


def phase_entry_to_result(
    entry: PhaseEntry,
    phase_name: str,
) -> PhaseResult:
    """Convert PhaseEntry state model to PhaseResult DTO.

    Args:
        entry: Phase entry from state.
        phase_name: Name of the phase.

    Returns:
        Core DTO with phase data.
    """
    # Convert EvidenceItem models to dicts
    evidence_dicts = [{"namespace": item.namespace, "key": item.key, "score": item.score} for item in entry.evidence]

    return PhaseResult(
        phase_name=phase_name,
        data=entry.data,
        error=entry.error if entry.error else None,
        status=entry.status,
        evidence=evidence_dicts if evidence_dicts else None,
    )


def merge_phase_results(
    existing: PhaseEntry,
    result: PhaseResult,
) -> PhaseEntry:
    """Merge PhaseResult into existing PhaseEntry.

    Args:
        existing: Existing phase entry from state.
        result: New phase result to merge.

    Returns:
        Updated PhaseEntry with merged data.
    """
    # Convert evidence from result if present, otherwise keep existing
    evidence = existing.evidence
    if result.evidence:
        evidence = [EvidenceItem.model_validate(item) for item in result.evidence]

    return PhaseEntry(
        data={**existing.data, **result.data},
        error=result.error or existing.error,
        status=result.status,
        evidence=evidence,
    )


def extract_phase_summary(entry: PhaseEntry, phase_name: str) -> dict[str, object]:
    """Extract phase summary for logging or display.

    Args:
        entry: Phase entry to summarize.
        phase_name: Name of the phase.

    Returns:
        Dict with phase summary suitable for structured logging.
    """
    return {
        "phase": phase_name,
        "status": entry.status,
        "has_data": bool(entry.data),
        "has_error": bool(entry.error),
        "evidence_count": len(entry.evidence),
    }

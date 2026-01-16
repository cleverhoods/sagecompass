"""Evidence hydration contract."""

from __future__ import annotations

from app.platform.core.contract.logging import get_logger
from app.platform.core.dto.evidence import EvidenceBundle
from app.platform.runtime.evidence import collect_phase_evidence as _collect_phase_evidence
from app.state import SageState


def collect_phase_evidence(
    state: SageState,
    *,
    phase: str,
    max_items: int = 8,
) -> EvidenceBundle:
    """Collect evidence for a phase while enforcing the evidence contract."""
    bundle = _collect_phase_evidence(state, phase=phase, max_items=max_items)
    if bundle.missing_store and bundle.evidence:
        logger = get_logger("contract.evidence")
        logger.warning(
            "contract.evidence.missing_store",
            phase=phase,
            evidence_count=len(bundle.evidence),
        )
    return bundle

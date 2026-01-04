"""Runtime helper utilities for SageCompass."""

from __future__ import annotations

from app.platform.runtime.evidence import collect_phase_evidence, hydrate_evidence_docs
from app.platform.runtime.phases import get_phase_names
from app.platform.runtime.state_helpers import (
    format_ambiguity_key,
    get_clarified_keys,
    get_current_clarifying_question,
    get_latest_user_input,
    get_pending_ambiguity_keys,
    get_pending_ambiguity_questions,
    phase_to_node,
    reset_clarification_context,
)

__all__ = [
    "get_phase_names",
    "collect_phase_evidence",
    "hydrate_evidence_docs",
    "get_latest_user_input",
    "phase_to_node",
    "reset_clarification_context",
    "format_ambiguity_key",
    "get_pending_ambiguity_keys",
    "get_pending_ambiguity_questions",
    "get_current_clarifying_question",
    "get_clarified_keys",
]

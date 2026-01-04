"""Guardrails policy contract.

Contract meaning:
- Guardrail decisions come from app.platform.policy.guardrails.
- Both the gating node and middleware must call the same policy logic.
"""

from __future__ import annotations

from collections.abc import Mapping

from app.platform.policy.guardrails import build_guardrails_config, evaluate_guardrails
from app.state.gating import GuardrailResult

GUARDRAILS_ENTRYPOINT = "app.platform.policy.guardrails.evaluate_guardrails"


def evaluate_guardrails_contract(
    text: str,
    raw_config: Mapping[str, object] | None,
) -> GuardrailResult:
    """Evaluate guardrails using the canonical policy entrypoint."""
    config = build_guardrails_config(raw_config or {})
    return evaluate_guardrails(text, config)

"""Guardrails adapter layer for translating between core DTOs and state models.

This adapter provides boundary translation functions that convert between:
- Core DTOs (pure, extractable): GuardrailResult
- State models (LangGraph-specific): GatingContext
"""

from __future__ import annotations

from app.platform.core.dto.guardrails import GuardrailResult
from app.state.gating import GatingContext, GatingDecision


def guardrail_to_gating(
    guardrail: GuardrailResult,
    original_input: str,
) -> GatingContext:
    """Create GatingContext from GuardrailResult DTO.

    Args:
        guardrail: Core DTO with guardrail evaluation results.
        original_input: User's original input text.

    Returns:
        GatingContext with populated guardrail field and derived decision.
    """
    # Determine gating decision based on guardrail results
    decision: GatingDecision = "no-go" if not guardrail.is_safe or not guardrail.is_in_scope else "go"

    return GatingContext(
        original_input=original_input,
        guardrail=guardrail,
        decision=decision,
        rationale=guardrail.reasons.copy(),
    )


def update_gating_guardrail(
    gating_context: GatingContext,
    guardrail: GuardrailResult,
) -> GatingContext:
    """Update GatingContext with new guardrail result, preserving other fields.

    Args:
        gating_context: Existing gating context to update.
        guardrail: New guardrail evaluation result.

    Returns:
        New GatingContext instance with updated guardrail.
    """
    # Update decision based on new guardrail result
    decision: GatingDecision = gating_context.decision or "go"
    if not guardrail.is_safe or not guardrail.is_in_scope:
        decision = "no-go"

    return GatingContext(
        original_input=gating_context.original_input,
        guardrail=guardrail,
        confidence=gating_context.confidence,
        rationale=gating_context.rationale + guardrail.reasons,
        decision=decision,
    )


def extract_guardrail_summary(gating_context: GatingContext) -> dict[str, object]:
    """Extract guardrail summary for logging or display.

    Args:
        gating_context: Gating context containing guardrail results.

    Returns:
        Dict with guardrail summary suitable for structured logging.
    """
    if gating_context.guardrail is None:
        return {"checked": False}

    return {
        "checked": True,
        "is_safe": gating_context.guardrail.is_safe,
        "is_in_scope": gating_context.guardrail.is_in_scope,
        "reasons": gating_context.guardrail.reasons,
        "decision": gating_context.decision,
    }

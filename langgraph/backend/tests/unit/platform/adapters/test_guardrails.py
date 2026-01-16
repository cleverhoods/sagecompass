"""Tests for guardrails adapter layer."""

from __future__ import annotations

from app.platform.adapters.guardrails import (
    extract_guardrail_summary,
    guardrail_to_gating,
    update_gating_guardrail,
)
from app.platform.core.dto.guardrails import GuardrailResult
from app.state.gating import GatingContext


def test_guardrail_to_gating_creates_context_with_go_decision():
    """Test creating GatingContext from safe guardrail result."""
    guardrail = GuardrailResult(
        is_safe=True,
        is_in_scope=True,
        reasons=["Input is safe and in scope"],
    )

    context = guardrail_to_gating(guardrail, "test input")

    assert context.original_input == "test input"
    assert context.guardrail == guardrail
    assert context.decision == "go"
    assert context.rationale == ["Input is safe and in scope"]


def test_guardrail_to_gating_creates_context_with_no_go_decision():
    """Test creating GatingContext from unsafe guardrail result."""
    guardrail = GuardrailResult(
        is_safe=False,
        is_in_scope=True,
        reasons=["Input contains unsafe content"],
    )

    context = guardrail_to_gating(guardrail, "test input")

    assert context.decision == "no-go"
    assert "Input contains unsafe content" in context.rationale


def test_update_gating_guardrail_preserves_existing_data():
    """Test updating gating context preserves existing fields."""
    existing = GatingContext(
        original_input="test",
        guardrail=None,
        decision="go",
    )

    new_guardrail = GuardrailResult(
        is_safe=True,
        is_in_scope=True,
        reasons=["All checks passed"],
    )

    updated = update_gating_guardrail(existing, new_guardrail)

    assert updated.original_input == "test"
    assert updated.guardrail == new_guardrail
    assert "All checks passed" in updated.rationale


def test_extract_guardrail_summary_returns_checked_false_when_none():
    """Test summary extraction when no guardrail has been run."""
    context = GatingContext(original_input="test")

    summary = extract_guardrail_summary(context)

    assert summary["checked"] is False


def test_extract_guardrail_summary_returns_full_data_when_present():
    """Test summary extraction when guardrail result exists."""
    guardrail = GuardrailResult(
        is_safe=True,
        is_in_scope=True,
        reasons=["Safe"],
    )
    context = GatingContext(
        original_input="test",
        guardrail=guardrail,
        decision="go",
    )

    summary = extract_guardrail_summary(context)

    assert summary["checked"] is True
    assert summary["is_safe"] is True
    assert summary["is_in_scope"] is True
    assert summary["decision"] == "go"

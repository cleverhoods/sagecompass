from __future__ import annotations

import pytest

from app.platform.policy.guardrails import build_guardrails_config, evaluate_guardrails

pytestmark = pytest.mark.compliance


def test_evaluate_guardrails_allows_in_scope() -> None:
    config = build_guardrails_config(
        {
            "allowed_topics": ["automation"],
            "blocked_keywords": ["hack"],
        }
    )

    result = evaluate_guardrails("automation planning", config)

    assert result.is_safe is True
    assert result.is_in_scope is True


def test_evaluate_guardrails_denies_unsafe_or_out_of_scope() -> None:
    config = build_guardrails_config(
        {
            "allowed_topics": ["automation"],
            "blocked_keywords": ["hack"],
        }
    )

    result = evaluate_guardrails("hack the system", config)

    assert result.is_safe is False
    assert result.is_in_scope is False

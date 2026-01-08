"""Guardrails policy evaluation helpers."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass

from app.state.gating import GuardrailResult


@dataclass(frozen=True)
class GuardrailsConfig:
    """Normalized guardrails configuration used by policy checks."""

    allowed_topics: tuple[str, ...]
    blocked_keywords: tuple[str, ...]


def _normalize_terms(values: Iterable[object] | None) -> tuple[str, ...]:
    """Normalize topic/keyword inputs into lower-cased tuples."""
    if not values:
        return tuple()
    normalized: list[str] = []
    for value in values:
        text = str(value).strip().lower()
        if text:
            normalized.append(text)
    return tuple(normalized)


def build_guardrails_config(raw: Mapping[str, object] | None) -> GuardrailsConfig:
    """Build a normalized guardrails config from raw YAML/JSON data."""
    data = raw or {}
    allowed_raw = data.get("allowed_topics")
    blocked_raw = data.get("blocked_keywords")
    allowed_values = (
        allowed_raw if isinstance(allowed_raw, Iterable) and not isinstance(allowed_raw, (str, bytes)) else None
    )
    blocked_values = (
        blocked_raw if isinstance(blocked_raw, Iterable) and not isinstance(blocked_raw, (str, bytes)) else None
    )
    allowed = _normalize_terms(allowed_values)
    blocked = _normalize_terms(blocked_values)
    return GuardrailsConfig(allowed_topics=allowed, blocked_keywords=blocked)


def evaluate_guardrails(text: str, config: GuardrailsConfig) -> GuardrailResult:
    """Evaluate safety and scope against normalized guardrail config."""
    normalized = (text or "").lower()

    is_safe = not any(keyword in normalized for keyword in config.blocked_keywords)
    is_in_scope = any(topic in normalized for topic in config.allowed_topics)

    reasons: list[str] = []
    if not is_safe:
        reasons.append("Contains blocked or unsafe terms.")
    if not is_in_scope:
        reasons.append("Outside supported business / AI domains.")

    return GuardrailResult(
        is_safe=is_safe,
        is_in_scope=is_in_scope,
        reasons=reasons or ["Passed all checks."],
    )

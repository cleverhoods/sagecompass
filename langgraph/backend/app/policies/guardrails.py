from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping

from app.state.gating import GuardrailResult


@dataclass(frozen=True)
class GuardrailsConfig:
    allowed_topics: tuple[str, ...]
    blocked_keywords: tuple[str, ...]


def _normalize_terms(values: Iterable[object] | None) -> tuple[str, ...]:
    if not values:
        return tuple()
    normalized: list[str] = []
    for value in values:
        text = str(value).strip().lower()
        if text:
            normalized.append(text)
    return tuple(normalized)


def build_guardrails_config(raw: Mapping[str, object] | None) -> GuardrailsConfig:
    data = raw or {}
    allowed = _normalize_terms(data.get("allowed_topics"))
    blocked = _normalize_terms(data.get("blocked_keywords"))
    return GuardrailsConfig(allowed_topics=allowed, blocked_keywords=blocked)


def evaluate_guardrails(text: str, config: GuardrailsConfig) -> GuardrailResult:
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

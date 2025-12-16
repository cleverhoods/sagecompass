from __future__ import annotations

from typing import Any, Callable, Literal, Sequence, TypedDict


class HilpQuestion(TypedDict):
    id: str
    text: str
    type: Literal["boolean"]


class HilpMeta(TypedDict, total=False):
    needs_hilp: bool
    reason: str
    confidence: float
    ambiguities: list[Any]
    questions: list[HilpQuestion]
    max_rounds: int


def _score_ambiguity(
    item: Any,
    *,
    importance_fn: Callable[[Any], float],
    confidence_fn: Callable[[Any], float],
) -> float:
    return float(importance_fn(item)) * float(confidence_fn(item))


def compute_hilp_meta_from_ambiguities(
    ambiguities: Sequence[Any],
    *,
    base_confidence: float,
    importance_fn: Callable[[Any], float],
    confidence_fn: Callable[[Any], float],
    id_fn: Callable[[Any], str],
    text_fn: Callable[[Any], str],
    max_items: int = 3,
    max_rounds: int = 1,
) -> HilpMeta:
    if not ambiguities:
        return {
            "needs_hilp": False,
            "reason": "no_ambiguities",
            "confidence": base_confidence,
        }

    sorted_items = sorted(
        ambiguities,
        key=lambda a: _score_ambiguity(a, importance_fn=importance_fn, confidence_fn=confidence_fn),
        reverse=True,
    )
    top = list(sorted_items[:max_items])

    questions: list[HilpQuestion] = [
        {"id": id_fn(a), "text": text_fn(a), "type": "boolean"}
        for a in top
    ]

    return {
        "needs_hilp": True,
        "reason": "critical_ambiguities",
        "confidence": base_confidence,
        "ambiguities": top,
        "questions": questions,
        "max_rounds": max_rounds,
    }

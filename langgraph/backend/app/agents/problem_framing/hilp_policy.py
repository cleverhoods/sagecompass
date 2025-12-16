from __future__ import annotations

from app.agents.problem_framing.schema import ProblemFrame, AmbiguityItem
from app.utils.hilp_core import (
    HilpMeta,
    compute_hilp_meta_from_ambiguities,
)

def compute_hilp_meta(pf: ProblemFrame) -> HilpMeta:
    return compute_hilp_meta_from_ambiguities(
        pf.ambiguities,
        base_confidence=pf.confidence,
        importance_fn=lambda a: float(a.importance),
        confidence_fn=lambda a: float(a.confidence),
        id_fn=lambda a: a.key,
        text_fn=lambda a: a.clarifying_question,
        max_items=3,
        max_rounds=1,
    )

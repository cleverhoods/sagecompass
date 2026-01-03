"""Ambiguity preflight phase contract definition."""

from __future__ import annotations

from app.graphs.subgraphs.ambiguity_preflight.subgraph import (
    build_ambiguity_preflight_subgraph,
)
from app.graphs.subgraphs.phases.contract import PhaseContract
from app.state.ambiguity import AmbiguityContext

ambiguity_preflight_contract = PhaseContract(
    name="ambiguity_preflight",
    build_graph=build_ambiguity_preflight_subgraph,
    output_schema=AmbiguityContext,
    description=(
        "Runs ambiguity scan, optional retrieval + rescan, and clarification loop "
        "for a target phase."
    ),
    requires_evidence=False,
    retrieval_enabled=False,
    clarification_enabled=True,
)

from __future__ import annotations

from app.graphs.phases.contract import PhaseContract
from app.graphs.phases.problem_framing.subgraph import build_problem_framing_subgraph
from app.agents.problem_framing.schema import ProblemFrame


problem_framing_contract = PhaseContract(
    name="problem_framing",
    build_graph=build_problem_framing_subgraph,
    output_schema=ProblemFrame,
    description=(
        "Frames the problem before committing to AI. "
        "Ensures scope, ambiguity, and relevance are addressed."
    ),
    requires_evidence=True,
    retrieval_enabled=True,
    clarification_enabled=True,
)

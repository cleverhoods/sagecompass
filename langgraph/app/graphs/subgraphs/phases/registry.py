"""Phase contract registry for SageCompass graphs."""

from __future__ import annotations

from app.graphs.subgraphs.phases.problem_framing import problem_framing_contract

PHASES = {
    problem_framing_contract.name: problem_framing_contract,
}

__all__ = ["PHASES"]

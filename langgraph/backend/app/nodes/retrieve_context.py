from __future__ import annotations

from typing import Callable, List
from typing_extensions import Literal

from langgraph.types import Command
from langgraph.runtime import Runtime

from app.state import SageState, EvidenceItem, PhaseEntry
from app.tools.context_lookup import context_lookup


def make_node_retrieve_context(
    *,
    phase: str = "problem_framing",       # where evidence is stored
    collection: str = "problem_framing",  # lookup namespace segment
) -> Callable[[SageState], Command[Literal["supervisor"]]]:
    def node_retrieve_context(
        state: SageState, runtime: Runtime | None = None
    ) -> Command[Literal["problem_framing"]]:
        user_query = state.get("user_query", "") or ""

        docs = context_lookup.invoke({"query": user_query, "collection": collection}) or []

        evidence: List[EvidenceItem] = []
        for d in docs:
            md = d.metadata or {}
            ns = md.get("store_namespace")
            key = md.get("store_key")
            score = md.get("score")
            if ns and key:
                e: EvidenceItem = {"namespace": ns, "key": key}
                if isinstance(score, (int, float)):
                    e["score"] = float(score)
                evidence.append(e)

        phases = dict(state.get("phases") or {})
        entry: PhaseEntry = dict(phases.get(phase) or {})
        entry["evidence"] = evidence  # IMPORTANT: set even if empty list
        phases[phase] = entry

        return Command(update={"phases": phases}, goto="supervisor")

    return node_retrieve_context

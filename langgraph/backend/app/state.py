from __future__ import annotations

from typing import Annotated, Dict, Literal, TypedDict, Type, Any, Optional

from langchain_core.messages import AnyMessage
from langgraph.graph import add_messages
from pydantic import BaseModel

from app.utils.hilp_core import HilpQuestion
from app.agents.problem_framing.schema import ProblemFrame
from app.agents.translator.schema import TranslationResult


PhaseStatus = Literal["pending", "complete", "stale", "error"]


# Mapping phase key -> Pydantic schema for that phase's output
PHASE_SCHEMAS: dict[str, Type[BaseModel]] = {
    "problem_framing": ProblemFrame,
    "translation":     TranslationResult,
    # "business_goals": BusinessGoals,
}


class PhaseEntry(TypedDict, total=False):
    # Pydantic .model_dump() of the phase's output schema
    data: Dict[str, Any]

    # Lifecycle of this phase's result.
    # - "pending"  – never run or invalidated
    # - "complete" – last run is considered valid
    # - "stale"    – upstream changes mean this phase should be re-run
    status: PhaseStatus

class HilpRequest(TypedDict, total=False):
    phase: str
    prompt: str
    goto_after: str
    max_rounds: int
    questions: list[HilpQuestion]

class Hilp(TypedDict, total=False):
    hilp_request: Optional[HilpRequest]
    hilp_round: int
    hilp_answers: dict[str, Literal["yes", "no", "unknown"]]
    proceed_anyway: Optional[bool]

class SageState(TypedDict, total=False):
    """
    Shared state for the 'agent' graph.

    - `messages`: canonical conversation timeline (UI + agents).
    - `user_query`: current main question for the active phase.
    - `phases`: per-phase structured results, keyed by phase/agent name.
    """
    messages: Annotated[list[AnyMessage], add_messages]
    user_query: str
    # e.g. phases["problem_framing"] = {...}, phases["business_goals"] = {...}
    phases: Dict[str, PhaseEntry]
    hilp: Hilp | None
    user_lang: str
    errors: list[str]

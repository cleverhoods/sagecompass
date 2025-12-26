from __future__ import annotations

from typing import Annotated, Dict, Literal, TypedDict, Type, Any

from langchain_core.messages import AnyMessage
from langgraph.graph import add_messages
from pydantic import BaseModel

from app.agents.problem_framing.schema import ProblemFrame

PhaseStatus = Literal["pending", "complete", "stale"]


# Mapping phase key -> Pydantic schema for that phase's output
PHASE_SCHEMAS: dict[str, Type[BaseModel]] = {
    "problem_framing": ProblemFrame,
    # "business_goals": BusinessGoals,
}


class PhaseEntry(TypedDict, total=False):
    # Pydantic .model_dump() of the phase's output schema
    data: Dict[str, Any]
    hilp_meta: Dict[str, Any]
    hilp_clarifications: list[Dict[str, Any]]
    error: Dict[str, Any]

    # Lifecycle of this phase's result.
    # - "pending"  – never run or invalidated
    # - "complete" – last run is considered valid
    # - "stale"    – upstream changes mean this phase should be re-run
    status: PhaseStatus

class SageState(TypedDict, total=False):
    """
    Shared state for the 'agent' graph.

    - `messages`: canonical conversation timeline (UI + agents).
    - `user_query`: current main question for the active phase.
    - `phases`: per-phase structured results, keyed by phase/agent name.
    - `errors`: error summaries for failed phase executions.
    """
    messages: Annotated[list[AnyMessage], add_messages]
    user_query: str
    # e.g. phases["problem_framing"] = {...}, phases["business_goals"] = {...}
    phases: Dict[str, PhaseEntry]
    errors: list[str]

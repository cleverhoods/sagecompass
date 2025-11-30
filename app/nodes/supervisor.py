from __future__ import annotations

from typing import Literal

from langgraph.types import Command

from app.state import PipelineState
from app.models import EligibilityResult
from app.utils.logger import log

NodeReturn = PipelineState | Command[
    Literal[
        "problem_framing",
        "rag",               # <--- NEW
        "business_goals",
        "eligibility",
        "kpi",
        "solution_design",
        "cost_estimation",
        "output_formatter",
    ]
]


def node_supervisor(state: PipelineState) -> NodeReturn:
    """
    Deterministic supervisor node.

    It decides which agent node should run next, based on what is already
    present in the PipelineState.

    Routing logic (v5 + RAG):

    1) Always run in this order the first time:
       - Problem Framing
       - RAG for business goals context
       - Business Goals
       - Eligibility

    2) After Eligibility:
       - If category = 'not_really_ai'
         OR (category = 'unclear_need_more_info' AND confidence < 0.85):
           → go to output_formatter (non-AI path, no KPI/SDA/CEA)

       - Else (core_ai_problem, ai_useful_but_not_core,
              or unclear_need_more_info with sufficient confidence):
           → AI path:
              KPI → Solution Design → Cost Estimation → Output Formatter
    """

    log("supervisor.node.start", {"keys": list(state.keys())})

    # --- 1) Discovery / definition phases in fixed order -----------------

    # 1a) Problem framing
    if state.get("problem_frame") is None:
        log("supervisor.route", {"next": "problem_framing"})
        return Command(goto="problem_framing")

    # 1b) After PF, ensure we have RAG context for business goals
    rag_contexts = state.get("rag_contexts") or {}
    if not state.get("business_goals"):
        # If no phase-specific RAG context yet, run RAG first
        if "business_goals" not in rag_contexts:
            log(
                "supervisor.route",
                {"next": "rag", "reason": "no_business_goals_rag_context"},
            )
            return Command(goto="rag")

    # 1c) Then business goals
    if not state.get("business_goals"):
        log("supervisor.route", {"next": "business_goals"})
        return Command(goto="business_goals")

    # 1d) Eligibility
    if state.get("eligibility") is None:
        log("supervisor.route", {"next": "eligibility"})
        return Command(goto="eligibility")

    # --- 2) After eligibility, decide AI vs non-AI path ------------------

    elig: EligibilityResult = state["eligibility"]
    category = elig.category
    confidence = elig.confidence

    non_ai = (
        category == "not_really_ai"
        or (category == "unclear_need_more_info" and confidence < 0.85)
    )
    ai_path = not non_ai  # kept for readability / logging if needed

    if non_ai:
        # Non-AI / unclear-low-confidence: skip KPI/SDA/CEA
        log(
            "supervisor.route",
            {
                "next": "output_formatter",
                "path": "non_ai",
                "category": category,
                "confidence": confidence,
            },
        )
        return Command(goto="output_formatter")

    # --- 3) AI path: KPI → SDA → CEA → Output formatter ------------------

    if not state.get("kpis"):
        log(
            "supervisor.route",
            {"next": "kpi", "path": "ai", "category": category, "confidence": confidence},
        )
        return Command(goto="kpi")

    if state.get("solution_design") is None:
        log(
            "supervisor.route",
            {"next": "solution_design", "path": "ai"},
        )
        return Command(goto="solution_design")

    if not state.get("cost_estimates"):
        log(
            "supervisor.route",
            {"next": "cost_estimation", "path": "ai"},
        )
        return Command(goto="cost_estimation")

    # 4) Everything is present → final HTML
    log(
        "supervisor.route",
        {"next": "output_formatter", "path": "ai"},
    )
    return Command(goto="output_formatter")

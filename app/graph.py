from __future__ import annotations

from copy import deepcopy
from typing import List, Optional

from langgraph.graph import StateGraph, END

from app.state import PipelineState
from app.models import (
    AtomicBusinessGoal,
    EligibilityResult,
    SolutionDesign,
    SolutionOption,
    CostEstimate,
)
from app.agents.problem_framing import node_pf
from app.agents.business_goals import node_bg
from app.agents.eligibility import node_eligibility
from app.agents.kpi import node_kpi
from app.agents.solution_design import node_sd
from app.agents.cost_estimation import node_ce
from app.agents.output_formatter.agent import node_output_formatter

# later:
# from app.agents.supervisor import node_supervisor
# from app.agents.output import node_output


def route_from_eligibility(state: PipelineState) -> str:
    """
    Decide where to go after Eligibility Agent.

    Returns one of the keys of the conditional edges mapping:
    - "NonAI" → go to Non-AI recommendation node
    - "KPI"   → continue with KPI agent and full AI pipeline
    """
    elig: EligibilityResult = state["eligibility"]
    category = elig.category
    confidence = elig.confidence

    # Hard "not AI" path
    if category == "not_really_ai":
        return "NonAI"

    # Low-confidence or unclear: for v1, treat as Non-AI path.
    # Later you can route this to a Human Review node instead.
    if category == "unclear_need_more_info" and confidence < 0.85:
        return "NonAI"

    # core_ai_problem or ai_useful_but_not_core with sufficient confidence
    return "KPI"


def node_non_ai(state: PipelineState) -> PipelineState:
    """
    Fallback node for 'not_really_ai' or low-confidence 'unclear_need_more_info'.

    Produces a business-friendly non-AI recommendation based on
    the problem frame and atomic business goals.
    """
    new_state = deepcopy(state)

    pf = state.get("problem_frame")
    goals: List[AtomicBusinessGoal] = state.get("business_goals", [])
    elig: Optional[EligibilityResult] = state.get("eligibility")

    lines: List[str] = []
    lines.append("Non-AI recommendation")
    lines.append("")

    if pf:
        lines.append(f"Domain: {pf.business_domain}")
        lines.append(f"Primary outcome: {pf.primary_outcome}")
        lines.append("")
        lines.append(
            "Based on the current information, this problem appears better suited to "
            "process, data, or BI improvements rather than AI/ML as the primary lever."
        )
        lines.append(
            "You can still create significant value by focusing on the following goals via "
            "workflow, data, and reporting changes:"
        )
        lines.append("")

    if goals:
        lines.append("Key business goals to address (without AI-first):")
        for g in goals:
            lines.append(f"- {g.direction.upper()} {g.subject} (weight {g.weight:.2f})")
        lines.append("")

    if elig:
        if elig.reasons:
            lines.append("Why this is not treated as an AI-first problem:")
            for r in elig.reasons:
                lines.append(f"- {r}")
            lines.append("")
        if elig.missing_info:
            lines.append("Questions worth clarifying before revisiting AI options:")
            for q in elig.missing_info:
                lines.append(f"- {q}")

    recommendation = "\n".join(lines)
    new_state["final_recommendation"] = recommendation
    return new_state


def node_final_reco(state: PipelineState) -> PipelineState:
    """
    Summarize SolutionDesign + CostEstimates into a final, human-readable recommendation.

    This keeps all detailed objects in state, but also adds a single
    'final_recommendation' string for UI / reporting.
    """
    new_state = deepcopy(state)

    pf = state.get("problem_frame")
    sd: Optional[SolutionDesign] = state.get("solution_design")
    costs: List[CostEstimate] = state.get("cost_estimates", [])

    lines: List[str] = []
    lines.append("Strategic AI recommendation")
    lines.append("")

    if pf:
        lines.append(f"Primary outcome: {pf.primary_outcome}")
        lines.append("")

    if not sd or not sd.options:
        lines.append("No structured solution options available.")
        new_state["final_recommendation"] = "\n".join(lines)
        return new_state

    # Find recommended option (if any)
    rec_id = sd.recommended_option_id
    rec_option: Optional[SolutionOption] = None
    if rec_id:
        for opt in sd.options:
            if opt.id == rec_id:
                rec_option = opt
                break

    # Fallback: if no recommended id, pick highest fit_score
    if not rec_option:
        rec_option = max(sd.options, key=lambda o: o.fit_score)

    lines.append(f"Recommended option: {rec_option.id} ({rec_option.kind})")
    lines.append(f"Summary: {rec_option.summary}")
    lines.append("")

    if rec_option.how_it_uses_ai:
        lines.append("How it uses AI/ML:")
        lines.append(rec_option.how_it_uses_ai)
        lines.append("")

    # Attach cost range for the recommended option, if available
    rec_cost: Optional[CostEstimate] = None
    for ce in costs:
        if ce.option_id == rec_option.id:
            rec_cost = ce
            break

    if rec_cost:
        lines.append("Effort and cost (ballpark):")
        lines.append(
            f"- Effort: ~{rec_cost.effort_person_months.min:.1f}–"
            f"{rec_cost.effort_person_months.max:.1f} person-months"
        )
        lines.append(
            f"- Calendar time: ~{rec_cost.calendar_time_months.min:.1f}–"
            f"{rec_cost.calendar_time_months.max:.1f} months"
        )
        lines.append(
            f"- Build CAPEX (ballpark): {int(rec_cost.capex_ballpark.min)}–"
            f"{int(rec_cost.capex_ballpark.max)}"
        )
        lines.append(
            f"- Ongoing OPEX (ballpark): {int(rec_cost.opex_ballpark.min)}–"
            f"{int(rec_cost.opex_ballpark.max)} per period"
        )
        lines.append(f"- Estimate uncertainty: {rec_cost.uncertainty:.2f}")
        lines.append("")

    # Add rationale from SolutionDesign, if present
    if sd.rationale:
        lines.append("Rationale and key trade-offs:")
        for r in sd.rationale:
            lines.append(f"- {r}")
        lines.append("")

    # List alternative options
    if len(sd.options) > 1:
        lines.append("Alternative options considered:")
        for opt in sd.options:
            label = " (recommended)" if opt.id == rec_option.id else ""
            lines.append(f"- {opt.id} ({opt.kind}){label}: {opt.summary}")
        lines.append("")

    new_state["final_recommendation"] = "\n".join(lines)
    return new_state


# --- Build the graph ---

graph = StateGraph(PipelineState)

# Nodes
graph.add_node("PF", node_pf)
graph.add_node("ABG", node_bg)
graph.add_node("EA", node_eligibility)
graph.add_node("KPI", node_kpi)
graph.add_node("SDA", node_sd)
graph.add_node("CEA", node_ce)
graph.add_node("NonAI", node_non_ai)
#graph.add_node("FinalReco", node_final_reco)
graph.add_node("HTML", node_output_formatter)

# Entry point: PF reads raw_text and writes problem_frame
graph.set_entry_point("PF")

# Linear part: PF → ABG → EA
graph.add_edge("PF", "ABG")
graph.add_edge("ABG", "EA")

# Branch from Eligibility:
# - Either NonAI (terminal non-AI recommendation)
# - Or KPI (continue AI path)
graph.add_conditional_edges(
    "EA",
    route_from_eligibility,
    {
        "NonAI": "NonAI",
        "KPI": "KPI",
    },
)

# AI path: KPI → SDA → CEA → FinalReco
graph.add_edge("KPI", "SDA")
graph.add_edge("SDA", "CEA")
graph.add_edge("CEA", "HTML")

# Terminal nodes
graph.add_edge("NonAI", END)
#graph.add_edge("FinalReco")
graph.add_edge("HTML", END)

graph.set_finish_point("HTML")

# Compiled app
app = graph.compile()


def run_pipeline(raw_text: str) -> PipelineState:
    """
    Convenience helper to run the full graph on a single user query.
    """
    initial_state: PipelineState = {"raw_text": raw_text}
    final_state: PipelineState = app.invoke(initial_state)
    return final_state


__all__ = ["app", "run_pipeline"]

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any, Dict

from app.agents.base import LLMAgent
from app.models import HtmlReport
from app.state import PipelineState
from app.utils.logger import log

AGENT_DIR = Path(__file__).resolve().parent
PROMPT_PATH = AGENT_DIR / "system.prompt"


def _to_json_like(value: Any) -> str:
    """
    Best-effort JSON-ish serialization for Pydantic models and lists.
    This is only for feeding structured context into the LLM, not for strict parsing.
    """
    if value is None:
        return "null"

    # Pydantic v2 style
    if hasattr(value, "model_dump_json"):
        return value.model_dump_json(indent=2, ensure_ascii=False)
    if hasattr(value, "model_dump"):
        import json

        return json.dumps(value.model_dump(), indent=2, ensure_ascii=False)

    # List/tuple of models or primitives
    if isinstance(value, (list, tuple)):
        import json

        items = []
        for x in value:
            if hasattr(x, "model_dump"):
                items.append(x.model_dump())
            else:
                items.append(x)
        return json.dumps(items, indent=2, ensure_ascii=False)

    # Plain dict or primitive
    import json

    try:
        return json.dumps(value, indent=2, ensure_ascii=False)
    except TypeError:
        return repr(value)


class OutputFormatterAgent(LLMAgent[HtmlReport]):
    def __init__(self) -> None:
        super().__init__(
            name="output_formatter",
            output_model=HtmlReport,
            prompt_path=PROMPT_PATH,
        )

    def run_on_state(self, state: PipelineState) -> HtmlReport:
        # Extract pieces from state
        problem_frame = state.get("problem_frame")
        business_goals = state.get("business_goals")
        eligibility = state.get("eligibility")
        kpis = state.get("kpis")
        solution_design = state.get("solution_design")
        cost_estimates = state.get("cost_estimates")
        user_question = state.get("raw_text")

        pf_json = _to_json_like(problem_frame)
        goals_json = _to_json_like(business_goals)
        elig_json = _to_json_like(eligibility)
        kpis_json = _to_json_like(kpis)
        sd_json = _to_json_like(solution_design)
        ce_json = _to_json_like(cost_estimates)

        human_instructions = (
            "UserQuestion (plain text):\n"
            f"{user_question or ''}\n\n"
            "ProblemFrame (JSON):\n"
            f"{pf_json}\n\n"
            "BusinessGoals (JSON array):\n"
            f"{goals_json}\n\n"
            "EligibilityResult (JSON):\n"
            f"{elig_json}\n\n"
            "KPIs (JSON array):\n"
            f"{kpis_json}\n\n"
            "SolutionDesign (JSON):\n"
            f"{sd_json}\n\n"
            "CostEstimates (JSON array):\n"
            f"{ce_json}\n"
        )

        log(
            "agent.output_formatter.run_on_state",
            {
                "has_problem_frame": problem_frame is not None,
                "goals_count": len(business_goals) if business_goals else 0,
                "has_eligibility": eligibility is not None,
                "kpis_count": len(kpis) if kpis else 0,
                "has_solution_design": solution_design is not None,
                "estimates_count": len(cost_estimates) if cost_estimates else 0,
            },
            agent="output_formatter",
        )

        return self.run(human_instructions=human_instructions)


_formatter_agent = OutputFormatterAgent()


def node_output_formatter(state: PipelineState) -> PipelineState:
    """
    LangGraph node wrapper for the OutputFormatterAgent.
    Produces a HtmlReport and stores the raw HTML string under 'html_report'.
    """
    new_state = deepcopy(state)
    report: HtmlReport = _formatter_agent.run_on_state(state)
    new_state["html_report"] = report.html

    log(
        "agent.node.done",
        {"agent": "output_formatter", "html_length": len(report.html or "")},
    )

    return new_state

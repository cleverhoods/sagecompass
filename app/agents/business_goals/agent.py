from __future__ import annotations

from copy import deepcopy
from pathlib import Path

from app.utils.logger import log
from app.agents.base import LLMAgent
from app.models import ProblemFrame, BusinessGoalsOutput
from app.state import PipelineState
from app.utils.retriever import get_context_for_query

AGENT_DIR = Path(__file__).resolve().parent
PROMPT_PATH = AGENT_DIR / "system.prompt"


class BusinessGoalsLLMAgent(LLMAgent[BusinessGoalsOutput]):
    def __init__(self) -> None:
        super().__init__(
            name="business_goals",
            output_model=BusinessGoalsOutput,
            prompt_path=PROMPT_PATH,
        )

    def run_on_state(self, state: PipelineState) -> BusinessGoalsOutput:
        raw_text = state["raw_text"]
        pf: ProblemFrame = state["problem_frame"]

        context = get_context_for_query(raw_text)

        pf_json = pf.model_dump_json(indent=2)

        human_instructions = (
            f"ProblemFrame (JSON):\n{pf_json}\n\n"
            f"User question:\n{raw_text}\n\n"
            f"Context (may be empty):\n{context}"
        )

        return self.run(human_instructions=human_instructions)


_bg_agent = BusinessGoalsLLMAgent()


def node_bg(state: PipelineState) -> PipelineState:
    log("agent.node.start", {"agent": "business_goals"})
    new_state = deepcopy(state)
    bg_output = _bg_agent.run_on_state(state)
    log(
        "agent.node.done",
        {
            "agent": "business_goals",
            "goals_count": len(bg_output.business_goals),
        },
    )

    new_state["business_goals"] = bg_output.business_goals
    return new_state

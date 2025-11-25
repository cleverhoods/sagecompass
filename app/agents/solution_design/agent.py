from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from app.utils.logger import log
from app.agents.base import LLMAgent
from app.models import SolutionDesign
from app.state import PipelineState
from app.utils.retriever import get_context_for_query

AGENT_DIR = Path(__file__).resolve().parent
PROMPT_PATH = AGENT_DIR / "system.prompt"


class SolutionDesignLLMAgent(LLMAgent[SolutionDesign]):
    def __init__(self) -> None:
        super().__init__(
            name="solution_design",
            output_model=SolutionDesign,
            prompt_path=PROMPT_PATH,
        )

    def run_on_state(self, state: PipelineState) -> SolutionDesign:
        raw_text = state["raw_text"]
        context = get_context_for_query(raw_text)

        human_instructions = (
            f"User question:\n{raw_text}\n\n"
            f"Context (may be empty):\n{context}"
        )

        return self.run(human_instructions=human_instructions)


_sd_agent = SolutionDesignLLMAgent()


def node_sd(state: PipelineState) -> PipelineState:
    """
    LangGraph node wrapper for the ProblemFraming LLMAgent.
    """
    log("agent.node.start", {"agent": "solution_design"})
    new_state = deepcopy(state)

    sd: SolutionDesign = _sd_agent.run_on_state(state)

    log(
        "agent.node.done",
        {
            "agent": "solution_design",
            "options_count": len(sd.options),
            "recommended_option_id": sd.recommended_option_id,
        },
    )

    new_state["solution_design"] = sd
    return new_state

from __future__ import annotations

from copy import deepcopy
from pathlib import Path

from app.utils.logger import log
from app.agents.base import LLMAgent
from app.models import EligibilityResult
from app.state import PipelineState
from app.utils.retriever import get_context_for_query

AGENT_DIR = Path(__file__).resolve().parent
PROMPT_PATH = AGENT_DIR / "system.prompt"


class EligibilityLLMAgent(LLMAgent[EligibilityResult]):
    def __init__(self) -> None:
        super().__init__(
            name="eligibility",
            output_model=EligibilityResult,
            prompt_path=PROMPT_PATH,
        )

    def run_on_state(self, state: PipelineState) -> EligibilityResult:
        raw_text = state["raw_text"]
        context = get_context_for_query(raw_text)

        human_instructions = (
            f"User question:\n{raw_text}\n\n"
            f"Context (may be empty):\n{context}"
        )

        return self.run(human_instructions=human_instructions)


_eligibility_agent = EligibilityLLMAgent()


def node_eligibility(state: PipelineState) -> PipelineState:
    """
    LangGraph node wrapper for the ProblemFraming LLMAgent.
    """
    log("agent.node.start", {"agent": "eligibility"})
    new_state = deepcopy(state)

    elig = _eligibility_agent.run_on_state(state)

    log(
        "agent.node.done",
        {
            "agent": "eligibility",
            "category": elig.category,
            "confidence": elig.confidence,
        },
    )

    new_state["eligibility"] = elig
    return new_state

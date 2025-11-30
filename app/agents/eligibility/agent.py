from __future__ import annotations

from pathlib import Path
from typing import List

from app.utils.logger import log
from app.agents.base import LLMAgent

from app.models import ProblemFrame, BusinessGoal, EligibilityResult
from app.state import PipelineState

AGENT_DIR = Path(__file__).resolve().parent
PROMPT_PATH = AGENT_DIR / "system.prompt"

class EligibilityLLMAgent(LLMAgent[EligibilityResult]):
    """
    Eligibility agent built on top of the shared LLMAgent base.

    Responsibilities:
    - Load its own system.prompt.
    - Build a structured payload from PipelineState:
      - original_input
      - problem_frame
      - business_goals
      - optional RAG context
    - Return an EligibilityResult model.
    """

    def __init__(self) -> None:
        super().__init__(
            name="eligibility",
            output_model=EligibilityResult,
            prompt_path=PROMPT_PATH,
        )

    def build_payload(self, state: PipelineState) -> dict:
        raw_text = state.get("raw_text", "") or ""

        pf: ProblemFrame | None = state.get("problem_frame")
        goals: List[BusinessGoal] = state.get("business_goals") or []

        return {
            "original_input": raw_text or None,
            "problem_frame": pf.model_dump() if pf is not None else None,
            "business_goals": [g.model_dump() for g in goals] if goals else [],
            "retrieved_context": None,
        }

    def run_on_state(self, state: PipelineState) -> EligibilityResult:
        payload = self.build_payload(state)
        log(
            "agent.eligibility.payload",
            {"keys": list(payload.keys())},
        )
        return self.run_with_payload(payload)

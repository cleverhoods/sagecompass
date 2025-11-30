from __future__ import annotations

from pathlib import Path

from app.agents.base import LLMAgent
from app.models import ProblemFrame, BusinessGoalsOutput
from app.state import PipelineState

AGENT_DIR = Path(__file__).resolve().parent
PROMPT_PATH = AGENT_DIR / "system.prompt"

class BusinessGoalsLLMAgent(LLMAgent[BusinessGoalsOutput]):
    """
    Business Goals agent built on top of the shared LLMAgent base.

    Responsibilities:
    - Load its own system.prompt.
    - Build human_instructions from PipelineState:
      - raw_text
      - current ProblemFrame (if available)
      - optional RAG context (via RAGAgent)
    - Return a BusinessGoalsOutput model.
    """

    def __init__(self) -> None:
        super().__init__(
            name="business_goals",
            output_model=BusinessGoalsOutput,
            prompt_path=PROMPT_PATH,
        )

    def build_payload(self, state: PipelineState) -> dict:
        raw_text = state.get("raw_text", "") or ""
        pf: ProblemFrame | None = state.get("problem_frame")

        rag_contexts = state.get("rag_contexts") or {}
        bg_context = rag_contexts.get("business_goals") or rag_contexts.get("general") or ""

        return {
            "original_input": raw_text,
            "problem_frame": pf.model_dump() if pf is not None else None,
            "retrieved_context": bg_context or None,
        }

    def run_on_state(self, state: PipelineState) -> BusinessGoalsOutput:
        payload = self.build_payload(state)
        return self.run_with_payload(payload)

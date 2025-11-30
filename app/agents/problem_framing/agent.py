from __future__ import annotations

from pathlib import Path

from app.utils.logger import log
from app.agents.base import LLMAgent

from app.models import ProblemFrame
from app.state import PipelineState

AGENT_DIR = Path(__file__).resolve().parent
PROMPT_PATH = AGENT_DIR / "system.prompt"

class ProblemFramingLLMAgent(LLMAgent[ProblemFrame]):
    """
    Problem Framing agent built on top of the shared LLMAgent base.

    Responsibilities:
    - Load its own system.prompt.
    - Build a structured payload from PipelineState (original_input + optional RAG context).
    - Return a structured ProblemFrame model.
    """

    def __init__(self) -> None:
        super().__init__(
            name="problem_framing",
            output_model=ProblemFrame,
            prompt_path=PROMPT_PATH,
        )

    def build_payload(self, state: PipelineState) -> dict:
        raw_text = state.get("raw_text", "") or ""

        return {
            "original_input": raw_text or None,
            "retrieved_context": None,
        }

    def run_on_state(self, state: PipelineState) -> ProblemFrame:
        payload = self.build_payload(state)
        log(
            "agent.problem_framing.payload",
            {"keys": list(payload.keys())},
        )
        return self.run_with_payload(payload)


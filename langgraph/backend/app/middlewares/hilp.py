from __future__ import annotations

from typing import Any, Callable, Literal

from langchain.agents import AgentState
from langchain.agents.middleware import after_agent
from pydantic import BaseModel, Field, ValidationError

from app.utils.hilp_core import HilpMeta
from app.utils.logger import get_logger


class HilpBooleanPrompt(BaseModel):
    """
    Schema for a single boolean HILP clarification prompt.
    """

    phase: str = Field(..., description="Phase that raised this clarification.")
    question_id: str = Field(..., description="Stable identifier for the ambiguity.")
    question: str = Field(..., description="Yes/No/Unknown question to ask the user.")


class HilpBooleanAnswer(BaseModel):
    """
    Schema for yes/no/unknown HILP answers collected from the user.
    """

    question_id: str
    answer: Literal["yes", "no", "unknown"]


def make_boolean_hilp_middleware(
    *,
    phase: str,
    output_schema: type[BaseModel],
    compute_meta: Callable[[Any], HilpMeta],
):
    """
    Build a LangGraph agent middleware that manages boolean HILP clarifications.

    - Validates the agent's structured output using `output_schema`.
    - Computes HILP metadata via `compute_meta`.
    - If boolean questions are present and the runtime exposes `human(...)`,
      prompts for yes/no/unknown answers using `HilpBooleanPrompt` / `HilpBooleanAnswer`.
    - Returns a dict merged into the agent result with:
        - `structured_response`: validated model
        - `hilp_meta`: metadata + (optional) `clarifications`
        - `hilp_clarifications`: collected answers (list of dicts)
    """

    logger = get_logger("hilp_middleware")

    @after_agent
    def middleware(state: AgentState, runtime: Any) -> dict[str, Any] | None:
        raw = state.get("structured_response")
        if raw is None:
            logger.warning("HILP middleware: missing structured_response", phase=phase)
            return None

        try:
            structured = raw if isinstance(raw, output_schema) else output_schema.model_validate(raw)
        except Exception as exc:
            logger.warning(
                "HILP middleware: invalid structured_response",
                phase=phase,
                error=str(exc),
            )
            return None

        meta = compute_meta(structured)
        questions = [
            q for q in (meta.get("questions") or []) if isinstance(q, dict) and q.get("type") == "boolean"
        ]

        clarifications: list[HilpBooleanAnswer] = []

        if questions and hasattr(runtime, "human"):
            for q in questions:
                prompt = HilpBooleanPrompt(
                    phase=phase,
                    question_id=str(q.get("id")),
                    question=q.get("text") or "",
                )
                try:
                    raw_answer = runtime.human(prompt, schema=HilpBooleanAnswer)
                    clarifications.append(HilpBooleanAnswer.model_validate(raw_answer))
                except ValidationError as exc:
                    logger.warning(
                        "HILP middleware: invalid human response",
                        phase=phase,
                        error=str(exc),
                        question_id=prompt.question_id,
                    )
                except Exception as exc:
                    logger.warning(
                        "HILP middleware: runtime.human failed",
                        phase=phase,
                        error=str(exc),
                        question_id=prompt.question_id,
                    )
        elif questions:
            logger.warning(
                "HILP middleware: runtime lacks human(); skipping clarifications",
                phase=phase,
                question_count=len(questions),
            )

        meta_out: dict[str, Any] = dict(meta)
        if clarifications:
            meta_out["clarifications"] = [c.model_dump() for c in clarifications]

        return {
            "structured_response": structured,
            "hilp_meta": meta_out,
            "hilp_clarifications": [c.model_dump() for c in clarifications],
        }

    return middleware

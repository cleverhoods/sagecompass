from __future__ import annotations

from typing import Any, Callable, Literal, TypedDict

from langchain.agents import AgentState
from langchain.agents.middleware import after_agent, AgentMiddleware
from langgraph.types import interrupt
from pydantic import BaseModel, ValidationError

from app.utils.hilp_core import HilpMeta
from app.utils.logger import get_logger


class HilpBooleanQuestion(TypedDict):
    id: str
    text: str
    type: Literal["boolean"]


class HilpBooleanAnswer(BaseModel):
    """Schema for yes/no/unknown HILP answers collected from the user."""

    question_id: str
    answer: Literal["yes", "no", "unknown"]


class HilpClarificationRequest(TypedDict, total=False):
    phase: str
    questions: list[HilpBooleanQuestion]
    reason: str
    confidence: float


class HilpClarificationResponse(TypedDict):
    answers: list[dict[str, str]]


def make_boolean_hilp_middleware(
    *,
    phase: str,
    output_schema: type[BaseModel],
    compute_meta: Callable[[Any], HilpMeta],
) -> AgentMiddleware[AgentState, Any]:
    """
    Build a LangGraph agent middleware that manages boolean HILP clarifications.

    - Validates the agent's structured output using `output_schema`.
    - Computes HILP metadata via `compute_meta`.
    - If boolean questions are present, interrupts execution to collect
      yes/no/unknown answers using `langgraph.types.interrupt`.
    - Returns a dict merged into the agent result with:
        - `structured_response`: validated model
        - `hilp_meta`: metadata + (optional) `clarifications`
        - `hilp_clarifications`: collected answers (list of dicts)
    """

    logger = get_logger("hilp_middleware")

    @after_agent
    def middleware(
            state: AgentState,
            runtime: dict[str, Any] | None = None,
    ) -> dict[str, Any] | None:
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

        if questions:
            request: HilpClarificationRequest = {
                "phase": phase,
                "questions": questions,  # type: ignore[list-item]
            }
            if reason := meta.get("reason"):
                request["reason"] = reason
            if (confidence := meta.get("confidence")) is not None:
                try:
                    request["confidence"] = float(confidence)
                except Exception:
                    pass

            response_raw = interrupt(request)

            try:
                response = HilpClarificationResponse(**response_raw)  # type: ignore[arg-type]
            except Exception as exc:
                logger.warning(
                    "HILP middleware: invalid interrupt response",
                    phase=phase,
                    error=str(exc),
                )
                response = {"answers": []}

            for ans in response.get("answers", []):
                answer_val = ans.get("answer") if isinstance(ans, dict) else None
                qid = ans.get("question_id") if isinstance(ans, dict) else None
                if answer_val not in {"yes", "no", "unknown"} or not qid:
                    logger.warning(
                        "HILP middleware: invalid answer",
                        phase=phase,
                        error="invalid_choice",
                    )
                    continue
                try:
                    clarifications.append(HilpBooleanAnswer.model_validate(ans))
                except ValidationError as exc:
                    logger.warning(
                        "HILP middleware: invalid answer",
                        phase=phase,
                        error=str(exc),
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

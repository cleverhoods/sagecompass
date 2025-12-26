from __future__ import annotations

import app.middlewares.hilp as hilp
from app.agents.problem_framing.schema import ProblemFrame


def _sample_problem_frame() -> ProblemFrame:
    return ProblemFrame(
        business_domain="Retail",
        primary_outcome="Reduce churn",
        actors=["Customer"],
        current_pain=["High churn"],
        constraints=["Limited budget"],
        ambiguities=[],
        confidence=0.7,
    )


def test_boolean_hilp_middleware_collects_answers(monkeypatch):
    captured_requests: list[dict] = []

    def _interrupt_stub(request):
        captured_requests.append(request)
        return {
            "answers": [
                {
                    "question_id": request["questions"][0]["id"],
                    "answer": "yes",
                }
            ]
        }

    monkeypatch.setattr(hilp, "interrupt", _interrupt_stub)

    middleware = hilp.make_boolean_hilp_middleware(
        phase="problem_framing",
        output_schema=ProblemFrame,
        compute_meta=lambda pf: {
            "questions": [
                {"id": "q1", "text": "Is retention critical?", "type": "boolean"},
            ],
            "confidence": 0.6,
            "reason": "Ambiguities detected",
        },
    )

    result = middleware({"structured_response": _sample_problem_frame()})  # type: ignore[arg-type]

    assert captured_requests, "interrupt should be called with a question payload"
    assert result is not None
    assert isinstance(result["structured_response"], ProblemFrame)
    assert result["hilp_clarifications"][0]["question_id"] == "q1"
    assert result["hilp_clarifications"][0]["answer"] == "yes"
    assert result["hilp_meta"]["clarifications"][0]["answer"] == "yes"

from __future__ import annotations

from types import SimpleNamespace

import pytest
from langgraph.types import Runtime

from app.agents.problem_framing.schema import ProblemFrame
from app.middlewares.hilp import make_boolean_hilp_middleware
from app.runtime import SageRuntimeContext, build_runtime_context
from app.nodes.problem_framing import make_node_problem_framing
from app.utils.hilp_core import HilpMeta


def _runtime(ctx: SageRuntimeContext | None = None) -> Runtime[SageRuntimeContext]:
    return Runtime(context=build_runtime_context(ctx))


@pytest.mark.unit
def test_hilp_runtime_flag_disables_interrupts():
    frame = ProblemFrame(business_domain="retail", primary_outcome="conversion", confidence=0.5)

    def compute_meta(_structured: ProblemFrame) -> HilpMeta:
        return {"needs_hilp": True, "questions": [{"id": "q1", "text": "bool?", "type": "boolean"}]}

    middleware = make_boolean_hilp_middleware(
        phase="problem_framing",
        output_schema=ProblemFrame,
        compute_meta=compute_meta,
    )

    result = middleware.after_agent(
        {"structured_response": frame},
        runtime=_runtime({"hilp_enabled": False}),
    )

    assert result is None, "hilp_enabled=False should short-circuit interrupt handling"


@pytest.mark.unit
def test_runtime_context_prevents_state_pollution():
    pf_agent = SimpleNamespace(
        invoke=lambda _inputs: {
            "structured_response": ProblemFrame(
                business_domain="retail",
                primary_outcome="conversion",
                confidence=0.5,
            ),
            "hilp_meta": {"needs_hilp": True},
            "hilp_clarifications": [{"answer": "yes"}],
        }
    )
    node = make_node_problem_framing(pf_agent=pf_agent)

    cmd = node({}, runtime=_runtime({"hilp_audit_mode": False}))

    entry = cmd.update["phases"]["problem_framing"]
    assert "hilp_meta" not in entry
    assert "hilp_clarifications" not in entry

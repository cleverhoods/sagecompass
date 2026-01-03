from __future__ import annotations

from app.nodes.supervisor import make_node_supervisor
from app.state import SageState
from app.state.gating import GatingContext, GuardrailResult


def test_supervisor_routes_to_phase_subgraph_supervisor() -> None:
    guardrail = GuardrailResult(is_safe=True, is_in_scope=True, reasons=["ok"])
    state = SageState(gating=GatingContext(original_input="hi", guardrail=guardrail))
    node = make_node_supervisor()

    result = node(state, None)

    assert result.goto == "problem_framing_supervisor"
    assert result.update is not None
    assert result.update["messages"]

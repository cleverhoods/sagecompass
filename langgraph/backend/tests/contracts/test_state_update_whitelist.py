from __future__ import annotations

from types import SimpleNamespace

import pytest
from langgraph.types import Command
from langgraph.runtime import Runtime

from app.agents.problem_framing.schema import ProblemFrame
from app.nodes.problem_framing import make_node_problem_framing
from app.nodes.supervisor import make_node_supervisor
from app.runtime import build_runtime_context, SageRuntimeContext
from app.state import SAGESTATE_KEYS


def _runtime(ctx: SageRuntimeContext | None = None) -> Runtime[SageRuntimeContext]:
    return Runtime(context=build_runtime_context(ctx))


def _assert_allowed_updates(cmd: Command, msg: str = "") -> None:
    updates = cmd.update or {}
    unexpected = set(updates.keys()) - SAGESTATE_KEYS
    assert not unexpected, f"{msg} unexpected keys: {unexpected}"


@pytest.mark.unit
def test_problem_framing_node_updates_are_whitelisted():
    pf = ProblemFrame(
        business_domain="retail",
        primary_outcome="conversion",
        confidence=0.5,
    )
    pf_agent = SimpleNamespace(invoke=lambda _inputs: {"structured_response": pf})
    node = make_node_problem_framing(pf_agent=pf_agent)

    cmd = node({}, runtime=_runtime())

    _assert_allowed_updates(cmd, "problem_framing")
    phases = cmd.update["phases"]
    assert "problem_framing" in phases


@pytest.mark.unit
def test_supervisor_node_updates_are_whitelisted():
    node = make_node_supervisor()

    cmd = node({}, runtime=_runtime())

    _assert_allowed_updates(cmd, "supervisor")

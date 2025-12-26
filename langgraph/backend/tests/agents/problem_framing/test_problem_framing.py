import pytest

from app.agents.problem_framing.schema import (
    AmbiguityItem,
    AmbiguityResolution,
    AmbiguityResolutionAssumption,
    ProblemFrame,
)
from app.nodes.problem_framing import make_node_problem_framing


class StubAgentNeedsHilp:
    def invoke(self, _):
        resolution = AmbiguityResolution(
            yes=AmbiguityResolutionAssumption(impact_direction="+", impact_value=0.8, assumption="Proceed"),
            no=AmbiguityResolutionAssumption(impact_direction="-", impact_value=0.4, assumption="Hold"),
            unknown=AmbiguityResolutionAssumption(impact_direction="0", impact_value=0.5, assumption="Re-evaluate"),
        )
        return {
            "structured_response": ProblemFrame(
                business_domain="test",
                primary_outcome="test",
                confidence=0.5,
                ambiguities=[
                    AmbiguityItem(
                        key="criteria_for_tool_selection",
                        description="Missing criteria for tool selection.",
                        clarifying_question="?",
                        resolution=resolution,
                        importance=0.9,
                        confidence=0.9,
                    )
                ],
            ),
            "hilp_meta": {"needs_hilp": True},
            "hilp_clarifications": [{"question_id": "criteria_for_tool_selection", "answer": "yes"}],
        }


class StubAgentNoHilp:
    def invoke(self, _):
        return {
            "structured_response": ProblemFrame(
                business_domain="test",
                primary_outcome="test",
                confidence=0.95,
                ambiguities=[],
            )
        }


def test_pf_persists_hilp_metadata_when_present():
    node = make_node_problem_framing(StubAgentNeedsHilp(), goto_after="supervisor")
    cmd = node({"user_query": "hi", "messages": [], "phases": {}})

    assert cmd.goto == "supervisor"
    phase_entry = cmd.update["phases"]["problem_framing"]
    assert phase_entry["status"] == "complete"
    assert phase_entry["hilp_meta"]["needs_hilp"] is True
    assert phase_entry["hilp_clarifications"][0]["answer"] == "yes"


def test_pf_completes_when_hilp_not_needed():
    node = make_node_problem_framing(StubAgentNoHilp(), goto_after="supervisor")
    cmd = node({"user_query": "hi", "messages": [], "phases": {}})

    assert cmd.goto == "supervisor"
    phase_entry = cmd.update["phases"]["problem_framing"]
    assert phase_entry["status"] == "complete"
    assert "hilp_meta" not in phase_entry


def test_agent_config_can_toggle_few_shots():
    pytest.importorskip("langchain_core.output_parsers")

    from app.agents.utils import compose_agent_prompt

    prompt_without = compose_agent_prompt(
        agent_name="problem_framing",
        prompt_names=["system"],
        include_global=True,
        include_format_instructions=True,
        output_schema=ProblemFrame,
    )

    prompt_with = compose_agent_prompt(
        agent_name="problem_framing",
        prompt_names=["system", "few-shots"],
        include_global=True,
        include_format_instructions=True,
        output_schema=ProblemFrame,
    )

    assert "Input:" not in prompt_without
    assert "{user_query}" not in prompt_without
    assert "Input:" in prompt_with
    assert "reduce customer churn" in prompt_with
    assert "{user_query}" in prompt_with
    assert prompt_with.strip().endswith("Output:")

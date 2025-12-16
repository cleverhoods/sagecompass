from app.agents.problem_framing.schema import AmbiguityItem, ProblemFrame
from app.nodes.problem_framing import make_node_problem_framing


class StubAgentNeedsHilp:
    def invoke(self, _):
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
                        resolution=None,
                        importance=0.9,
                        confidence=0.9,
                    )
                ],
            )
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


def test_pf_sets_hilp_request_when_needed():
    node = make_node_problem_framing(StubAgentNeedsHilp(), goto_after="supervisor")
    cmd = node({"user_query": "hi", "messages": [], "phases": {}, "hilp": {"hilp_round": 0}})

    assert cmd.goto == "supervisor"
    hilp_block = cmd.update["hilp"]
    assert isinstance(hilp_block["hilp_request"], dict)
    assert hilp_block["hilp_request"]["phase"] == "problem_framing"
    assert hilp_block["hilp_request"]["goto_after"] == "supervisor"
    assert hilp_block["hilp_round"] == 0
    assert hilp_block["hilp_answers"] == {}


def test_pf_completes_when_hilp_not_needed():
    node = make_node_problem_framing(StubAgentNoHilp(), goto_after="supervisor")
    cmd = node({"user_query": "hi", "messages": [], "phases": {}, "hilp": {"hilp_round": 2}})

    assert cmd.goto == "supervisor"
    hilp_block = cmd.update["hilp"]
    assert hilp_block["hilp_request"] is None
    assert hilp_block["hilp_round"] == 2

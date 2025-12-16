from app.nodes.problem_framing import make_node_problem_framing


class StubAgent:
    def invoke(self, _):
        return {
            "structured_response": {
                "business_domain": "test",
                "primary_outcome": "test",
                "confidence": 0.5,
                "ambiguities": [
                    {
                        "key": "criteria_for_tool_selection",
                        "description": "Missing criteria for tool selection.",
                        "importance": 0.9,
                        "confidence": 0.9,
                    }
                ],
            }
        }


def test_pf_sets_hilp_request_when_needed():
    node = make_node_problem_framing(StubAgent(), goto_after="supervisor")
    cmd = node({"user_query": "hi", "messages": []})

    assert cmd.goto == "supervisor"
    assert cmd.update["hilp_request"] is not None

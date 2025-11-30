from __future__ import annotations

from typing import Union

from langgraph.types import Command

from app.state import PipelineState
from app.utils.logger import log
from app.agents.problem_framing.agent import ProblemFramingLLMAgent
from app.models import ProblemFrame

NodeReturn = Union[PipelineState, Command]

# Shared agent instance for this node
_pf_agent = ProblemFramingLLMAgent()


def node_pf(state: PipelineState) -> NodeReturn:
    """
    LangGraph node for Problem Framing.

    - Calls ProblemFramingLLMAgent on the current state.
    - Writes the resulting ProblemFrame to state["problem_frame"].
    - May interrupt if confidence is low or ambiguities are high.
    """
    log("agent.node.start", {"agent": "problem_framing"})

    pf: ProblemFrame = _pf_agent.run_on_state(state)
    state["problem_frame"] = pf

    # HITL / interrupt logic stays in the node layer,
    # so the agent stays "pure LLM".
    confidence = getattr(pf, "confidence", 1.0)
    ambiguities = getattr(pf, "ambiguity_flags", []) or []

    low_confidence = confidence < 0.7
    has_ambiguities = len(ambiguities) > 3

    if low_confidence or has_ambiguities:
        message_lines = [
            "The problem framing is uncertain.",
            f"- Confidence: {confidence:.2f}",
            f"- Ambiguities: {len(ambiguities)} item(s)",
        ]
        for a in ambiguities[:5]:
            message_lines.append(
                f"  • {a.item} (importance={a.importance:.2f}, conf={a.confidence:.2f})"
            )
        message_lines.append("")
        message_lines.append("Please clarify or add missing context.")

        from langgraph.types import interrupt

        return interrupt(
            value={
                "type": "problem_framing_low_confidence",
                "message": "\n".join(message_lines),
                "problem_frame": pf.model_dump(),
            }
        )

    log("agent.node.done", {"agent": "problem_framing"})
    return state

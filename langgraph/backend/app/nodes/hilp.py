from __future__ import annotations

from typing import Any, Callable

from langchain_core.messages import HumanMessage
from langgraph.types import Command, interrupt

from app.state import SageState, Hilp, HilpRequest
from app.utils.logger import log


def make_node_hilp(*, default_goto: str = "supervisor") -> Callable[[SageState], Command[str]]:
    def node_hilp(state: SageState) -> Command[str]:
        hilp_block: Hilp | None = state.get("hilp")  # type: ignore[assignment]
        hilp_block = hilp_block or {}

        req: HilpRequest | None = hilp_block.get("hilp_request")  # type: ignore[assignment]
        if not isinstance(req, dict):
            log("HILP: missing/invalid hilp_request; skipping", {"hilp_request": req})
            return Command(goto=default_goto)

        current_round = int(hilp_block.get("hilp_round", 0) or 0)
        max_rounds = int(req.get("max_rounds") or 0)

        if max_rounds and current_round >= max_rounds:
            log(
                "HILP: max_rounds reached; clearing request",
                {"current_round": current_round, "max_rounds": max_rounds},
            )
            new_hilp: Hilp = {
                "hilp_request": None,
                "hilp_round": current_round,
                "hilp_answers": hilp_block.get("hilp_answers") or [],
            }
            return Command(update={"hilp": new_hilp}, goto=req.get("goto_after") or default_goto)

        ## Add the translation here?

        answer = interrupt(req)

        messages = list(state.get("messages") or [])
        messages.append(HumanMessage(content=str(answer)))

        answers = list(hilp_block.get("hilp_answers") or [])
        answers.append(answer)

        new_hilp: Hilp = {
            "hilp_request": None,
            "hilp_round": current_round + 1,
            "hilp_answers": answers,
        }

        goto_after = req.get("goto_after") or default_goto

        log(
            "HILP: answer recorded",
            {"phase": req.get("phase"), "goto_after": goto_after, "hilp_round": new_hilp["hilp_round"]},
        )

        return Command(update={"messages": messages, "hilp": new_hilp}, goto=goto_after)

    return node_hilp

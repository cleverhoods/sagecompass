from __future__ import annotations

from typing import Callable
from typing_extensions import Literal

from langgraph.types import Command
from langgraph.runtime import Runtime
from langgraph.graph import END

from app.runtime import SageRuntimeContext
from app.state import SageState
from app.state.gating import GuardrailResult
from app.utils.file_loader import FileLoader
from app.utils.logger import get_logger


def make_node_guardrails_check(
    *,
    goto_if_safe: str = "supervisor",
) -> Callable[[SageState, Runtime | None], Command[Literal["supervisor", "__end__"]]]:
    """
    Node: guardrails_check

    Purpose:
    - Perform deterministic safety & scope validation on raw user input.
    - Update: state.gating.guardrail
    - Routing:
        - Safe + in-scope → supervisor
        - Unsafe / out-of-scope → END
    """

    logger = get_logger("nodes.guardrails_check")

    # Load config once at node construction
    config = FileLoader.load_guardrails_config()
    allowed_topics = [t.lower() for t in config.get("allowed_topics", [])]
    blocked_keywords = [k.lower() for k in config.get("blocked_keywords", [])]

    def node_guardrails_check(
        state: SageState,
        runtime: Runtime[SageRuntimeContext] | None = None,
    ) -> Command[Literal["supervisor", "__end__"]]:

        original_input = state.gating.original_input.lower()

        is_safe = not any(k in original_input for k in blocked_keywords)
        is_in_scope = any(t in original_input for t in allowed_topics)

        reasons: list[str] = []
        if not is_safe:
            reasons.append("Contains blocked or unsafe terms.")
        if not is_in_scope:
            reasons.append("Outside supported business / AI domains.")

        guardrail = GuardrailResult(
            is_safe=is_safe,
            is_in_scope=is_in_scope,
            reasons=reasons or ["Passed all checks."]
        )

        logger.info(
            "guardrails.result",
            is_safe=is_safe,
            is_in_scope=is_in_scope,
            reasons=guardrail.reasons,
        )

        # Always update gating state
        update = {
            "gating": state.gating.model_copy(update={"guardrail": guardrail})
        }

        # Stop only if unsafe
        if not (is_safe and is_in_scope):
            logger.warning("guardrails.blocked")
            return Command(update=update, goto=END)

        return Command(update=update, goto=goto_if_safe)

    return node_guardrails_check

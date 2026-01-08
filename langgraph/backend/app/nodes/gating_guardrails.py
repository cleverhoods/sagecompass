"""Node for guardrails gating."""

from __future__ import annotations

from collections.abc import Callable
from typing import Literal

from langgraph.graph import END
from langgraph.runtime import Runtime
from langgraph.types import Command

from app.platform.config.file_loader import FileLoader
from app.platform.contract.guardrails import evaluate_guardrails_contract
from app.platform.contract.state import validate_state_update
from app.platform.observability.logger import get_logger
from app.platform.runtime.state_helpers import get_latest_user_input
from app.runtime import SageRuntimeContext
from app.state import SageState

GuardrailsRoute = Literal["__end__", "supervisor"]


def make_node_guardrails_check(
    *,
    goto_if_safe: Literal["supervisor"] = "supervisor",
) -> Callable[
    [SageState, Runtime[SageRuntimeContext] | None],
    Command[GuardrailsRoute],
]:
    """Node: guardrails_check.

    Purpose:
        Perform deterministic safety & scope validation on raw user input.

    Args:
        goto_if_safe: Node name to route to when input is safe and in-scope.

    Side effects/state writes:
        Updates `state.gating.guardrail` with the guardrail decision.

    Returns:
        A Command routing to `goto_if_safe` on success or END on failure.
    """
    logger = get_logger("nodes.guardrails_check")

    def node_guardrails_check(
        state: SageState,
        runtime: Runtime[SageRuntimeContext] | None = None,
    ) -> Command[GuardrailsRoute]:
        original_input = state.gating.original_input or (get_latest_user_input(state.messages) or "")
        guardrail = evaluate_guardrails_contract(
            original_input,
            FileLoader.load_guardrails_config(),
        )

        logger.info(
            "guardrails.result",
            is_safe=guardrail.is_safe,
            is_in_scope=guardrail.is_in_scope,
            reasons=guardrail.reasons,
        )

        # Always update gating state
        update = {"gating": state.gating.model_copy(update={"guardrail": guardrail, "original_input": original_input})}
        validate_state_update(update, owner="gating_guardrails")

        # Stop only if unsafe
        if not (guardrail.is_safe and guardrail.is_in_scope):
            logger.warning("guardrails.blocked")
            return Command(update=update, goto=END)

        return Command(update=update, goto=goto_if_safe)

    return node_guardrails_check

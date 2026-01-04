"""Node for ambiguity clarification loop orchestration."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, Literal, cast

from langchain_core.messages import AIMessage
from langchain_core.runnables import Runnable
from langgraph.runtime import Runtime
from langgraph.types import Command

from app.agents.ambiguity_clarification.schema import (
    ClarificationResponse,
    OutputSchema,
)
from app.platform.contract.state import validate_state_update
from app.platform.contract.structured_output import (
    extract_structured_response,
    validate_structured_response,
)
from app.platform.observability.logger import get_logger
from app.platform.runtime.state_helpers import (
    format_ambiguity_key,
    get_latest_user_input,
    get_pending_ambiguity_keys,
    reset_clarification_context,
)
from app.runtime import SageRuntimeContext
from app.state import SageState

logger = get_logger("nodes.ambiguity_clarification")


AmbiguityClarificationRoute = Literal["ambiguity_supervisor"]


def make_node_ambiguity_clarification(
    node_agent: Runnable | None = None,
    *,
    phase: str | None = None,
    max_context_items: int = 3,
    max_rounds: int = 3,
    goto: AmbiguityClarificationRoute = "ambiguity_supervisor",
) -> Callable[
    [SageState, Runtime[SageRuntimeContext] | None],
    Command[AmbiguityClarificationRoute],
]:
    """Node: ambiguity_clarification.

    Purpose:
        Refine user input via the internal ambiguity clarification agent and manage
        clarification context state.

    Args:
        node_agent: Optional injected clarification agent runnable.
        phase: Optional phase key for clarification tracking.
        max_context_items: Max evidence items to hydrate into context.
            (Clarification prompts do not consume context documents.)
        max_rounds: Max clarification rounds before ending.
        goto: Node name to route to after clarification updates.

    Side effects/state writes:
        Updates `state.ambiguity` with the active clarification session.
        When phase is not provided, uses `state.ambiguity.target_step`.

    Returns:
        A Command routing to `goto` or END when max rounds exceeded.
    """
    agent = node_agent
    if agent is None:
        from app.agents.ambiguity_clarification.agent import build_agent

        agent = build_agent()

    def node_ambiguity_clarification(
        state: SageState,
        runtime: Runtime[SageRuntimeContext] | None = None,
    ) -> Command[AmbiguityClarificationRoute]:
        update: dict[str, Any]
        user_input = get_latest_user_input(state.messages)
        if not user_input:
            logger.warning("ambiguity_clarification.empty_user_input", phase=phase)
            update = {
                "messages": [AIMessage(content="Waiting for more details.")]
            }
            validate_state_update(update, owner="ambiguity_clarification")
            return Command(
                update=update,
                goto=goto,
            )

        ambiguity_context = state.ambiguity
        target_phase = phase or ambiguity_context.target_step
        if not target_phase:
            logger.warning("ambiguity_clarification.missing_target_step")
            update = {
                "messages": [AIMessage(content="Unable to determine clarification target.")]
            }
            validate_state_update(update, owner="ambiguity_clarification")
            return Command(
                update=update,
                goto=goto,
            )

        if ambiguity_context.target_step != target_phase:
            ambiguity_context = reset_clarification_context(
                state,
                target_step=target_phase,
            )

        pending_keys = get_pending_ambiguity_keys(ambiguity_context)
        if not pending_keys:
            updated_context = ambiguity_context.model_copy(
                update={
                    "target_step": target_phase,
                    "checked": True,
                    "eligible": True,
                    "exhausted": False,
                }
            )
            update = {
                "ambiguity": updated_context,
                "messages": [AIMessage(content="Clarification complete. Continuing.")],
            }
            validate_state_update(update, owner="ambiguity_clarification")
            return Command(update=update, goto=goto)

        detected_items = ambiguity_context.detected
        labeled_items = [
            (format_ambiguity_key(item.key), item)
            for item in detected_items
        ]
        question_map = {
            label: (
                item.clarifying_question
                or item.description
                or label
            )
            for label, item in labeled_items
        }
        pending_items = [
            item for label, item in labeled_items if label in pending_keys
        ]
        pending_questions = [
            question_map.get(format_ambiguity_key(item.key), format_ambiguity_key(item.key))
            for item in pending_items
        ]
        if not pending_questions:
            pending_questions = list(pending_keys)
        current_question = pending_questions[0] if pending_questions else None

        rounds_attempted = len(ambiguity_context.resolved)
        if rounds_attempted >= max_rounds:
            exhausted_context = ambiguity_context.model_copy(
                update={
                    "target_step": target_phase,
                    "eligible": False,
                    "exhausted": True,
                }
            )
            logger.warning("ambiguity_clarification.max_rounds_exceeded", phase=phase)
            update = {
                "ambiguity": exhausted_context,
                "messages": [AIMessage(content="Unable to clarify the request.")],
            }
            validate_state_update(update, owner="ambiguity_clarification")
            return Command(update=update, goto=goto)

        selected_keys = [label for label, _ in labeled_items]
        ambiguous_items_text = (
            "\n".join(
                (
                    f"- {format_ambiguity_key(item.key)}: "
                    f"{question_map.get(format_ambiguity_key(item.key), format_ambiguity_key(item.key))}"
                    f" (assumption: {item.resolution_assumption})"
                )
                for item in pending_items
            )
            if pending_items
            else "None."
        )
        keys_to_clarify = list(pending_keys)

        result = agent.invoke(
            {
                "user_input": user_input,
                "ambiguous_items": ambiguous_items_text,
                "keys_to_clarify": keys_to_clarify,
                "phase": target_phase,
                "messages": state.messages,
            }
        )
        structured = extract_structured_response(result)
        if structured is None and isinstance(result, OutputSchema):
            structured = result

        if structured is None:
            logger.warning(
                "ambiguity_clarification.missing_structured_response",
                phase=target_phase,
            )
            update = {
                "messages": [AIMessage(content="Clarification failed. Please try again.")],
                "ambiguity": ambiguity_context.model_copy(update={"eligible": False}),
            }
            validate_state_update(update, owner="ambiguity_clarification")
            return Command(
                update=update,
                goto=goto,
            )

        structured = cast(OutputSchema, validate_structured_response(structured, OutputSchema))

        responses = structured.responses
        if not responses:
            logger.warning(
                "ambiguity_clarification.empty_response",
                phase=target_phase,
            )
            update = {
                "messages": [AIMessage(content="Clarification failed. Please try again.")],
                "ambiguity": ambiguity_context.model_copy(update={"eligible": False}),
            }
            validate_state_update(update, owner="ambiguity_clarification")
            return Command(
                update=update,
                goto=goto,
            )

        valid_keys = {format_ambiguity_key(item.key) for item in ambiguity_context.detected}
        fallback_keys = list(dict.fromkeys(pending_keys))
        normalized_responses: list[ClarificationResponse] = []
        for response in responses:
            raw_clarified_input = response.clarified_input
            clarified_input = raw_clarified_input or user_input
            cleaned_keys = [
                key.strip() for key in response.clarified_keys if isinstance(key, str)
            ]
            filtered_keys = [key for key in cleaned_keys if key in valid_keys]
            unique_keys = list(dict.fromkeys(filtered_keys))
            if not unique_keys and raw_clarified_input is not None and fallback_keys:
                logger.warning(
                    "ambiguity_clarification.empty_clarified_keys",
                    phase=target_phase,
                )
                unique_keys = fallback_keys
            normalized_responses.append(
                response.model_copy(
                    update={
                        "clarified_input": clarified_input,
                        "clarified_keys": unique_keys,
                    }
                )
            )
        latest_response = normalized_responses[-1]
        updated_resolved = [*ambiguity_context.resolved, *normalized_responses]
        updated_resolved_keys = {
            key for response in updated_resolved for key in response.clarified_keys
        }
        next_pending_keys = [
            key for key in selected_keys if key not in updated_resolved_keys
        ]
        next_questions = [
            question_map.get(key, key) for key in next_pending_keys
        ]
        clarification_output = latest_response.clarification_output or ""

        updated_context = ambiguity_context.model_copy(
            update={
                "target_step": target_phase,
                "checked": True,
                "eligible": not next_pending_keys,
                "detected": ambiguity_context.detected,
                "resolved": updated_resolved,
                "exhausted": False,
            }
        )

        clarification_ai_message = (
            AIMessage(content=clarification_output)
            if clarification_output
            else AIMessage(content="Clarification needed to proceed.")
        )
        clarification_progress_message = (
            AIMessage(content=f"Clarifying question: {current_question}")
            if current_question
            else None
        )

        def _clarification_messages() -> list[AIMessage]:
            messages = [clarification_ai_message]
            if clarification_progress_message:
                messages.append(clarification_progress_message)
            return messages

        if next_pending_keys:
            logger.info(
                "ambiguity_clarification.continue",
                items=next_questions,
            )
            update = {
                "ambiguity": updated_context,
                "messages": _clarification_messages(),
            }
            validate_state_update(update, owner="ambiguity_clarification")
            return Command(
                update=update,
                goto=goto,
            )

        logger.info("ambiguity_clarification.resolved")
        update = {
            "ambiguity": updated_context,
            "messages": [AIMessage(content="Clarification complete. Continuing.")],
        }
        validate_state_update(update, owner="ambiguity_clarification")
        return Command(update=update, goto=goto)

    return node_ambiguity_clarification

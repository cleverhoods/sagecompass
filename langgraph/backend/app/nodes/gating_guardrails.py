from __future__ import annotations

from typing import Callable, Literal
from langgraph.graph import END
from langgraph.types import Command
from langgraph.runtime import Runtime

from app.state.gating import GatingContext, GuardrailResult
from app.utils.logger import get_logger
from app.utils.file_loader import FileLoader


def make_node_guardrails_check() -> Callable[[GatingContext, Runtime | None], Command[Literal[END]]]:
    logger = get_logger("nodes.guardrails_check")

    # Load config once when the node is instantiated
    config = FileLoader.load_guardrails_config()  # Expects allowed_topics and blocked_keywords

    allowed_topics = [topic.lower() for topic in config.get("allowed_topics", [])]
    blocked_keywords = [kw.lower() for kw in config.get("blocked_keywords", [])]

    def node_guardrails_check(
        state: GatingContext,
        runtime: Runtime | None = None
    ) -> Command[Literal[END]]:
        input_text = state.original_input.lower()
        is_safe = not any(kw in input_text for kw in blocked_keywords)
        is_in_scope = any(topic in input_text for topic in allowed_topics)

        reasons = []
        if not is_safe:
            reasons.append("Contains unsafe or prohibited terms.")
        if not is_in_scope:
            reasons.append("Does not appear to relate to supported business/AI topics.")

        state.guardrail = GuardrailResult(
            is_safe=is_safe,
            is_in_scope=is_in_scope,
            reasons=reasons or ["Passed all checks."]
        )

        logger.info("guardrails_check.result", safe=is_safe, in_scope=is_in_scope, reasons=reasons)
        return Command(goto=END)

    return node_guardrails_check

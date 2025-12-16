from __future__ import annotations

from typing import Any, Callable

from langgraph.graph import END
from typing_extensions import Literal

from langgraph.types import Command
from langchain_core.runnables import Runnable

from app.state import SageState
from app.agents.translator.schema import TranslationResult
from app.utils.state_helpers import get_primary_user_query


def make_node_translation(
    translation_agent: Runnable,
    *,
    goto_after: Literal[END] = END,
) -> Callable[[SageState], Command[Literal[END]]]:
    def node_translation(state: SageState) -> Command[Literal[END]]:
        user_lang = (state.get("user_lang") or "en").lower()
        # If user language is English, skip translation entirely.
        if user_lang.startswith("en"):
            return Command(goto=goto_after)

        source_text = get_primary_user_query(state)
        if not source_text.strip():
            return Command(goto=goto_after)

        raw = translation_agent.invoke(
            {
                "user_language": user_lang,
                "message": source_text,
            }
        )

        if isinstance(raw, TranslationResult):
            tr = raw
        elif isinstance(raw, dict):
            tr = TranslationResult.model_validate(raw)
        else:
            tr = TranslationResult(
                translated_text=str(raw),
                source_language=None,
                target_language=user_lang,
                style_notes=None,
            )

        updates: dict[str, Any] = {
            "translated_text": tr.translated_text,
            "translation_result": tr,
        }
        return Command(update=updates, goto=goto_after)

    return node_translation

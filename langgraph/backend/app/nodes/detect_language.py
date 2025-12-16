from __future__ import annotations

from typing import Callable
from typing_extensions import Literal
from langgraph.types import Command

from app.state import SageState
from app.utils.lang import detect_user_lang
from app.utils.logger import log
from app.utils.state_helpers import get_primary_user_query

def make_node_detect_language(
    *,
    goto_after: str = "supervisor",
) -> Callable[[SageState], Command[Literal["supervisor"]]]:
    """
    Runs once at the beginning of the graph, sets state['user_lang'],
    then hands off to the supervisor.
    """

    def node_detect_language(state: SageState) -> Command[Literal["supervisor"]]:
        # Derive “best available” user text (user_query or latest Human message)
        text = get_primary_user_query(state)
        if not text.strip():
            # No usable text yet → just continue without changing state
            return Command(goto=goto_after)

        current_lang = state.get("user_lang")
        lang = detect_user_lang(current_lang, text)
        log("Language detected: {}".format(lang))
        return Command(update={"user_lang": lang}, goto=goto_after)

    return node_detect_language

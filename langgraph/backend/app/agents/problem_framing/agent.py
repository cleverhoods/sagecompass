from __future__ import annotations

import logging
from typing import Sequence

from langchain.agents import create_agent
from langchain.agents.middleware import AgentMiddleware, TodoListMiddleware
from langchain_core.language_models import BaseChatModel
from langchain_core.runnables import Runnable
from langchain_core.tools import BaseTool

from app.tools import get_tools
from app.agents.utils import build_agent_prompt
from app.middlewares.dynamic_prompts import make_dynamic_prompt_middleware
from app.middlewares.tool_errors import make_tool_error_middleware
from app.utils.model_factory import get_model_for_agent

from .mw import problem_framing_hilp
from .schema import ProblemFrame

AGENT_NAME = "problem_framing"

def build_agent(
    model: BaseChatModel | None = None,
    *,
    tool_names: Sequence[str] | None = None,
    extra_middleware: Sequence[AgentMiddleware] | None = None,
) -> Runnable:
    if model is None:
        model = get_model_for_agent(AGENT_NAME)
    logging.info(f"Model used:: {model}")
    tools: Sequence[BaseTool] = get_tools(["nothingizer_tool"])

    logging.info(f"Building agent: {tools}")
    agent_prompt = build_agent_prompt(AGENT_NAME, ["system"])

    prompt_mw = make_dynamic_prompt_middleware(
        prompt=agent_prompt,
        placeholders=[
            "user_query",
            "history",  # to feed MessagesPlaceholder("history"), if you add it
            "format_instructions",  # to expand {format_instructions}
        ],
        output_schema=ProblemFrame,
    )

    middlewares: list[AgentMiddleware] = [
        make_tool_error_middleware("Problem framing tool error:"),
        prompt_mw,
        problem_framing_hilp,
        TodoListMiddleware()
    ]

    if extra_middleware:
        middlewares.extend(extra_middleware)

    agent = create_agent(
        model=model,
        tools=tools,
        middleware=middlewares,
        response_format=ProblemFrame,  # optional, for structured output
    )
    return agent

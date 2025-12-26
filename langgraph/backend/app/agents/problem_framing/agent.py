from __future__ import annotations

import logging
from typing import Sequence, Any

from langchain.agents import create_agent, AgentState
from langchain.agents.middleware import AgentMiddleware, TodoListMiddleware
from langchain_core.language_models import BaseChatModel
from langchain_core.runnables import Runnable
from langchain_core.tools import BaseTool
from pydantic import BaseModel

from app.tools import get_tools
from app.agents.utils import compose_agent_prompt
from app.utils.model_factory import get_model_for_agent

from .mw import problem_framing_hilp
from .schema import ProblemFrame

AGENT_NAME = "problem_framing"


class ProblemFramingAgentConfig(BaseModel):
    model: BaseChatModel | None = None
    tool_names: Sequence[str] = ["nothingizer_tool"]
    include_few_shots: bool = True
    extra_middleware: Sequence[AgentMiddleware] = []


def build_agent(config: ProblemFramingAgentConfig | None = None) -> Runnable:
    """
    Builds a LangChain agent runnable for use in LangGraph or standalone.

    Args:
        config: Configuration for this agent run. If None, defaults will be used.

    Returns:
        Runnable agent ready for invocation.
    """
    if config is None:
        config = ProblemFramingAgentConfig()

    model = config.model or get_model_for_agent(AGENT_NAME)
    tools: Sequence[BaseTool] = get_tools(config.tool_names)

    logging.info(f"[{AGENT_NAME}] Using model: {model}")
    logging.info(f"[{AGENT_NAME}] Tools: {tools}")

    # Build the system+few-shot prompt
    agent_prompt = compose_agent_prompt(
        agent_name=AGENT_NAME,
        prompt_names=["system", "few-shots"],
        include_global=True,
        include_format_instructions=True,
        output_schema=ProblemFrame
    )

    middlewares: list[AgentMiddleware[AgentState, Any]] = [
        TodoListMiddleware(),
        problem_framing_hilp,
    ]

    if config.extra_middleware:
        middlewares.extend(config.extra_middleware)

    return create_agent(
        model=model,
        tools=tools,
        system_prompt=agent_prompt,
        middleware=middlewares,
        response_format=ProblemFrame,
    )

from __future__ import annotations

from typing import Sequence, Any

from langchain.agents import create_agent, AgentState
from langchain.agents.middleware import AgentMiddleware
from langchain_core.language_models import BaseChatModel
from langchain_core.runnables import Runnable
from langchain_core.tools import BaseTool
from pydantic import BaseModel, PrivateAttr

from app.tools import nothingizer_tool
from app.agents.utils import build_tool_allowlist, compose_agent_prompt
from app.middlewares.guardrails import make_guardrails_middleware
from app.middlewares.dynamic_prompt import make_dynamic_prompt_middleware
from app.utils.model_factory import get_model_for_agent
from app.utils.logger import get_logger

from .schema import ProblemFrame

AGENT_NAME = "problem_framing"


def _logger():
    return get_logger(f"agents.{AGENT_NAME}")


class ProblemFramingAgentConfig(BaseModel):
    """Configuration for the Problem Framing agent build.

    Assumptions:
        If model is not provided, ProviderFactory supplies a default instance.
    """
    model: BaseChatModel | None = None

    _extra_middleware: list[AgentMiddleware] = PrivateAttr(default_factory=list)

    def get_extra_middleware(self) -> tuple[AgentMiddleware, ...]:
        return tuple(self._extra_middleware)


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

    # Tool wiring is explicit and configurable
    tools: list[BaseTool] = [nothingizer_tool]

    _logger().info(
        "agent.build",
        agent=AGENT_NAME,
        model=str(model),
        tools=[tool.name for tool in tools],
    )

    agent_prompt = compose_agent_prompt(
        agent_name=AGENT_NAME,
        prompt_names=["system", "few-shots"],
        include_global=True,
        include_format_instructions=False,
    )

    allowed_tools = build_tool_allowlist(tools, ProblemFrame)

    middlewares: list[AgentMiddleware[AgentState, Any]] = [
        make_guardrails_middleware(allowed_tools=allowed_tools),
        make_dynamic_prompt_middleware(
            agent_prompt,
            placeholders=("user_query"),
            output_schema=ProblemFrame,
        )
    ]

    if config.get_extra_middleware():
        middlewares.extend(config.get_extra_middleware())

    return create_agent(
        model=model,
        tools=tools,
        system_prompt=agent_prompt,
        middleware=middlewares,
        response_format=ProblemFrame,
    )

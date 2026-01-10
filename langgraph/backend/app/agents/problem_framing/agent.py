"""Problem framing agent builder."""

from __future__ import annotations

from typing import Any

from langchain.agents import AgentState, create_agent
from langchain.agents.middleware import AgentMiddleware
from langchain_core.language_models import BaseChatModel
from langchain_core.runnables import Runnable
from langchain_core.tools import BaseTool
from pydantic import BaseModel, PrivateAttr

from app.middlewares.context_docs import make_context_docs_middleware
from app.middlewares.dynamic_prompt import make_dynamic_prompt_middleware
from app.middlewares.guardrails import make_guardrails_middleware
from app.platform.contract.agents import validate_agent_schema
from app.platform.contract.tools import (
    build_allowlist_contract,
    validate_allowlist_contains_schema,
)
from app.platform.contract.logging import get_logger
from app.platform.utils.agent_utils import compose_agent_prompt
from app.platform.utils.model_factory import get_model_for_agent

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
        """Return extra middleware registered for this agent."""
        return tuple(self._extra_middleware)


def build_agent(config: ProblemFramingAgentConfig | None = None) -> Runnable:
    """Builds a LangChain agent runnable for use in LangGraph or standalone.

    Args:
        config: Configuration for this agent run. If None, defaults will be used.

    Returns:
        Runnable agent ready for invocation.
    """
    if config is None:
        config = ProblemFramingAgentConfig()

    validate_agent_schema(AGENT_NAME)

    model = config.model or get_model_for_agent(AGENT_NAME)

    # Tool wiring is explicit and configurable
    tools: list[BaseTool] = []

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

    allowed_tools = build_allowlist_contract(tools, ProblemFrame)
    validate_allowlist_contains_schema(allowed_tools, ProblemFrame)

    context_middlewares = make_context_docs_middleware()
    middlewares: list[AgentMiddleware[AgentState, Any]] = [
        make_guardrails_middleware(allowed_tools=allowed_tools),
        *context_middlewares,
        make_dynamic_prompt_middleware(
            agent_prompt,
            placeholders=["task_input"],
            output_schema=ProblemFrame,
        ),
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

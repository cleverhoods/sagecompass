"""Ambiguity clarification agent builder."""

from __future__ import annotations

from typing import Any

from langchain.agents import AgentState, create_agent
from langchain.agents.middleware import AgentMiddleware
from langchain_core.language_models import BaseChatModel
from langchain_core.runnables import Runnable
from langchain_core.tools import BaseTool

from app.middlewares.dynamic_prompt import make_dynamic_prompt_middleware
from app.middlewares.guardrails import make_guardrails_middleware
from app.platform.observability.logger import get_logger
from app.platform.utils.agent_utils import build_tool_allowlist, compose_agent_prompt
from app.platform.utils.model_factory import get_model_for_agent

from .schema import OutputSchema

AGENT_NAME = "ambiguity_clarification"


def _logger():
    return get_logger(f"agents.{AGENT_NAME}")


class AmbiguityClarificationAgentConfig:
    """Configuration for the Ambiguity Clarification agent."""

    def __init__(
        self,
        model: BaseChatModel | None = None,
        extra_middleware: list[AgentMiddleware] | None = None,
    ) -> None:
        """Initialize config with optional model and middleware overrides."""
        self.model = model
        self._extra_middleware = extra_middleware or []

    def get_model(self) -> BaseChatModel:
        """Return the configured model or a default provider model."""
        return self.model or get_model_for_agent(AGENT_NAME)

    def get_extra_middleware(self) -> list[AgentMiddleware]:
        """Return extra middleware to append during agent construction."""
        return self._extra_middleware


def build_agent(config: AmbiguityClarificationAgentConfig | None = None) -> Runnable:
    """Construct an ambiguity clarification agent to refine ambiguous user input.

    Returns:
        A Runnable agent that outputs a structured ClarificationResponse.
    """
    if config is None:
        config = AmbiguityClarificationAgentConfig()

    model = config.get_model()

    tools: list[BaseTool] = []  # No tools for this agent; clarification is model-only

    _logger().info(
        "agent.build",
        agent=AGENT_NAME,
        model=str(model),
        tools=[tool.name for tool in tools],
    )

    # Compose system + prompt using Jinja template
    agent_prompt = compose_agent_prompt(
        agent_name=AGENT_NAME,
        prompt_names=["system", "clarification_autonomous"],
        include_global=True,
        include_format_instructions=False,
    )

    allowed_tools = build_tool_allowlist(tools, OutputSchema)

    middlewares: list[AgentMiddleware[AgentState, Any]] = [
        make_guardrails_middleware(allowed_tools=allowed_tools),
        make_dynamic_prompt_middleware(
            agent_prompt,
            placeholders=[
                "user_input",
                "ambiguous_items",
                "keys_to_clarify",
                "phase",
            ],
            output_schema=OutputSchema,
        ),
    ]

    middlewares.extend(config.get_extra_middleware())

    return create_agent(
        model=model,
        tools=tools,
        system_prompt=agent_prompt,
        middleware=middlewares,
        response_format=OutputSchema,
    )

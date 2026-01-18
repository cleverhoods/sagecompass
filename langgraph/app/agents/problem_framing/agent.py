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
from app.platform.adapters.agents import validate_agent_schema
from app.platform.adapters.logging import get_logger
from app.platform.adapters.tools import build_allowlist_contract
from app.platform.core.contract.tools import validate_allowlist_contains_schema
from app.platform.utils.agent_utils import compose_agent_prompt
from app.platform.utils.model_factory import get_model_for_agent

from .schema import ProblemFrame

AGENT_NAME = "problem_framing"


def _logger():
    return get_logger(f"agents.{AGENT_NAME}")


class ProblemFramingAgentConfig(BaseModel):
    """Configuration for the Problem Framing agent build.

    Attributes:
        model: Optional LLM to use. If None, ProviderFactory supplies default.

    Private Attributes:
        _extra_middleware: Additional middleware to append after standard stack.

    Example:
        >>> from langchain_anthropic import ChatAnthropic
        >>> config = ProblemFramingAgentConfig(model=ChatAnthropic(model="claude-3-haiku"))
        >>> agent = build_agent(config)
    """

    model: BaseChatModel | None = None

    _extra_middleware: list[AgentMiddleware] = PrivateAttr(default_factory=list)

    def get_extra_middleware(self) -> tuple[AgentMiddleware, ...]:
        """Return extra middleware registered for this agent."""
        return tuple(self._extra_middleware)


def build_agent(config: ProblemFramingAgentConfig | None = None) -> Runnable:
    """Build the Problem Framing agent for structured business idea analysis.

    Purpose:
        Analyzes user input to extract a structured problem frame containing
        domain, stakeholders, pain points, and success criteria. This is the
        first analytical phase in the SageCompass decision pipeline.

    Args:
        config: Agent configuration with optional model and middleware overrides.
            If None, uses default provider model from ProviderFactory.

    Middleware stack (applied in order):
        1. GuardrailsMiddleware - Enforces tool allowlist and safety policies
        2. ContextDocsMiddleware - Injects retrieved evidence into agent context
        3. DynamicPromptMiddleware - Renders system prompt with placeholders

    Returns:
        Runnable agent that accepts {"task_input", "messages", "context_docs"}
        and returns a validated ProblemFrame structured output.

    Raises:
        ValidationError: If agent schema validation fails during build.

    See Also:
        - Schema: app/agents/problem_framing/schema.py (ProblemFrame)
        - Node: app/nodes/problem_framing.py (orchestration wrapper)
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

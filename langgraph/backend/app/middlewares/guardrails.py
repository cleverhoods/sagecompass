"""Guardrails middleware enforcing policy at model/tool boundaries."""

from __future__ import annotations

from collections.abc import Iterable, Sequence

from langchain.agents.middleware import AgentMiddleware, ModelRequest, ModelResponse
from langchain.agents.middleware.types import ToolCallRequest
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from app.platform.config.file_loader import FileLoader
from app.platform.contract.guardrails import evaluate_guardrails_contract
from app.platform.contract.logging import get_logger
from app.platform.policy.guardrails import GuardrailsConfig, build_guardrails_config

logger = get_logger("middlewares.guardrails")


def _latest_user_text(messages: Iterable[object]) -> str:
    for message in reversed(list(messages)):
        if isinstance(message, HumanMessage) and message.content:
            return str(message.content)
    return ""


class GuardrailsMiddleware(AgentMiddleware):
    """Enforce guardrails and tool allowlists at model/tool boundaries."""

    def __init__(
        self,
        config: GuardrailsConfig,
        allowed_tools: Sequence[str] | None = None,
    ) -> None:
        """Initialize middleware with a guardrails config and tool allowlist."""
        self._config = config
        self._allowed_tools = set(allowed_tools or [])

    def _check_guardrails(self, request: ModelRequest) -> ModelResponse | None:
        user_text = _latest_user_text(request.messages)
        if not user_text:
            return None

        result = evaluate_guardrails_contract(
            user_text,
            {"allowed_topics": self._config.allowed_topics, "blocked_keywords": self._config.blocked_keywords},
        )
        if result.is_safe and result.is_in_scope:
            return None

        logger.warning("guardrails.blocked", reasons=result.reasons)
        return ModelResponse(result=[AIMessage(content="Request rejected by guardrails.")])

    def wrap_model_call(
        self,
        request: ModelRequest,
        handler,
    ) -> ModelResponse:
        """Apply guardrails before executing the model call."""
        rejected = self._check_guardrails(request)
        if rejected is not None:
            return rejected
        return handler(request)

    async def awrap_model_call(
        self,
        request: ModelRequest,
        handler,
    ) -> ModelResponse:
        """Apply guardrails before executing the async model call."""
        rejected = self._check_guardrails(request)
        if rejected is not None:
            return rejected
        return await handler(request)

    def wrap_tool_call(self, request: ToolCallRequest, handler):
        """Enforce tool allowlist before executing tool calls."""
        tool_name = request.tool_call.get("name") if request.tool_call else None
        if self._allowed_tools and tool_name not in self._allowed_tools:
            logger.warning("tool.blocked", tool=tool_name)
            return ToolMessage(
                content="Tool not allowed by policy.",
                name=tool_name,
                tool_call_id=request.tool_call.get("id", ""),
                status="error",
            )
        return handler(request)

    async def awrap_tool_call(self, request: ToolCallRequest, handler):
        """Enforce tool allowlist before executing async tool calls."""
        tool_name = request.tool_call.get("name") if request.tool_call else None
        if self._allowed_tools and tool_name not in self._allowed_tools:
            logger.warning("tool.blocked", tool=tool_name)
            return ToolMessage(
                content="Tool not allowed by policy.",
                name=tool_name,
                tool_call_id=request.tool_call.get("id", ""),
                status="error",
            )
        return await handler(request)


def make_guardrails_middleware(
    *,
    allowed_tools: Sequence[str] | None = None,
    config: GuardrailsConfig | None = None,
) -> GuardrailsMiddleware:
    """Build guardrails middleware with a normalized config and tool allowlist."""
    # Expectation: config is loaded once at middleware construction to keep runtime deterministic.
    if config is None:
        raw = FileLoader.load_guardrails_config() or {}
        config = build_guardrails_config(raw)
    # Invariant: allowlist must include structured output tool names when response_format is used.
    return GuardrailsMiddleware(config=config, allowed_tools=allowed_tools)

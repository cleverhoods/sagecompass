from __future__ import annotations

from collections.abc import Sequence
from typing import Iterable

from langchain.agents.middleware import AgentMiddleware, ModelRequest, ModelResponse
from langchain.agents.middleware.types import ToolCallRequest
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from app.policies.guardrails import GuardrailsConfig, build_guardrails_config, evaluate_guardrails
from app.utils.file_loader import FileLoader
from app.utils.logger import get_logger

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
        self._config = config
        self._allowed_tools = set(allowed_tools or [])

    def _check_guardrails(self, request: ModelRequest) -> ModelResponse | None:
        user_text = _latest_user_text(request.messages)
        if not user_text:
            return None

        result = evaluate_guardrails(user_text, self._config)
        if result.is_safe and result.is_in_scope:
            return None

        logger.warning("guardrails.blocked", reasons=result.reasons)
        return ModelResponse(result=[AIMessage(content="Request rejected by guardrails.")])

    def wrap_model_call(
        self,
        request: ModelRequest,
        handler,
    ) -> ModelResponse:
        rejected = self._check_guardrails(request)
        if rejected is not None:
            return rejected
        return handler(request)

    async def awrap_model_call(
        self,
        request: ModelRequest,
        handler,
    ) -> ModelResponse:
        rejected = self._check_guardrails(request)
        if rejected is not None:
            return rejected
        return await handler(request)

    def wrap_tool_call(self, request: ToolCallRequest, handler):
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
    # Invariant: allowlist must include any structured output tool name when response_format is used.
    return GuardrailsMiddleware(config=config, allowed_tools=allowed_tools)

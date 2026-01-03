"""Dynamic prompt middleware for runtime placeholder injection."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from typing import Any

from langchain.agents.middleware import AgentMiddleware, ModelRequest, dynamic_prompt
from langchain_core.messages import BaseMessage, SystemMessage
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import (
    BasePromptTemplate,
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
)
from pydantic import BaseModel

PromptLike = str | ChatPromptTemplate | SystemMessagePromptTemplate | BasePromptTemplate
PromptSource = PromptLike | Callable[[ModelRequest], PromptLike]


def _as_mapping(value: Any) -> Mapping[str, Any]:
    if isinstance(value, Mapping):
        return value
    return {}


def _apply_placeholders_to_string(
    template: str,
    values: Mapping[str, Any],
    keys: Sequence[str],
) -> str:
    """Replace only the requested placeholder keys in a string template."""
    rendered = template
    for key in keys:
        placeholder = "{" + key + "}"
        replacement = "" if values.get(key) is None else str(values.get(key))
        rendered = rendered.replace(placeholder, replacement)
    return rendered


def make_dynamic_prompt_middleware(
    prompt: PromptSource,
    placeholders: Sequence[str],
    output_schema: type[BaseModel] | None = None,
) -> AgentMiddleware:
    """Return an AgentMiddleware that renders the prompt from SageState at runtime."""
    # Invariant: placeholders are injected at runtime so prompt suffix ordering stays intact.
    if isinstance(placeholders, str):
        placeholders = [placeholders]

    parser = (
        PydanticOutputParser(pydantic_object=output_schema)
        if output_schema is not None
        else None
    )

    def _values_from_request(request: ModelRequest) -> Mapping[str, Any]:
        state = _as_mapping(getattr(request, "state", None) or {})
        inputs = _as_mapping(
            getattr(request, "inputs", None) or getattr(request, "input", None) or {}
        )
        nested_input = _as_mapping(inputs.get("input", {})) if inputs else {}
        values: dict[str, Any] = {}

        for key in placeholders:
            if key == "format_instructions" and parser is not None:
                values["format_instructions"] = parser.get_format_instructions()
            else:
                values[key] = inputs.get(key, nested_input.get(key, state.get(key)))

        return values

    def _resolve_prompt_source(request: ModelRequest) -> PromptLike:
        if callable(prompt) and not isinstance(
            prompt,
            (str, ChatPromptTemplate, SystemMessagePromptTemplate, BasePromptTemplate),
        ):
            return prompt(request)
        return prompt

    def _render_to_system_message(prompt_obj: PromptLike, request: ModelRequest) -> SystemMessage:
        values = _values_from_request(request)

        if isinstance(prompt_obj, str):
            text = _apply_placeholders_to_string(prompt_obj, values, placeholders)
            return SystemMessage(content=text)

        if isinstance(prompt_obj, ChatPromptTemplate):
            messages: list[BaseMessage] = prompt_obj.format_messages(**values)
            system_contents = [
                str(m.content) for m in messages if isinstance(m, SystemMessage)
            ]
            text = "\n\n".join(system_contents)
            return SystemMessage(content=text)

        if isinstance(prompt_obj, SystemMessagePromptTemplate):
            msg = prompt_obj.format(**values)
            assert isinstance(msg, SystemMessage)
            return msg

        if isinstance(prompt_obj, BasePromptTemplate):
            text = prompt_obj.format(**values)
            return SystemMessage(content=text)

        return SystemMessage(content=str(prompt_obj))

    @dynamic_prompt
    def _dynamic_prompt(request: ModelRequest) -> SystemMessage | str:
        resolved_prompt = _resolve_prompt_source(request)
        return _render_to_system_message(resolved_prompt, request)

    return _dynamic_prompt

from __future__ import annotations

from typing import Any, Mapping, Sequence, Type, Union

from langchain.agents.middleware import AgentMiddleware, ModelRequest, dynamic_prompt
from langchain_core.messages import BaseMessage, SystemMessage
from langchain_core.prompts import (
    BasePromptTemplate,
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel

PromptLike = Union[str, ChatPromptTemplate, SystemMessagePromptTemplate, BasePromptTemplate]


def _apply_placeholders_to_string(template: str, values: Mapping[str, Any], keys: Sequence[str]) -> str:
    """Replace only the requested placeholder keys in a string template."""
    rendered = template
    for key in keys:
        placeholder = "{" + key + "}"
        rendered = rendered.replace(placeholder, "" if values.get(key) is None else str(values.get(key)))
    return rendered


def make_dynamic_prompt_middleware(
    prompt: PromptLike,
    placeholders: Sequence[str],
    output_schema: Type[BaseModel] | None = None,
) -> AgentMiddleware:
    """Return an AgentMiddleware that renders the prompt from SageState at runtime."""

    parser = PydanticOutputParser(pydantic_object=output_schema) if output_schema is not None else None

    def _values_from_request(request: ModelRequest) -> Mapping[str, Any]:
        state = request.state or {}
        values: dict[str, Any] = {}

        for key in placeholders:
            if key == "format_instructions" and parser is not None:
                values["format_instructions"] = parser.get_format_instructions()
            else:
                values[key] = state.get(key)

        return values

    def _render_to_system_message(prompt_obj: PromptLike, request: ModelRequest) -> SystemMessage:
        values = _values_from_request(request)

        if isinstance(prompt_obj, str):
            text = _apply_placeholders_to_string(prompt_obj, values, placeholders)
            return SystemMessage(content=text)

        if isinstance(prompt_obj, ChatPromptTemplate):
            messages: list[BaseMessage] = prompt_obj.format_messages(**values)
            system_contents = [m.content for m in messages if isinstance(m, SystemMessage)]
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
        return _render_to_system_message(prompt, request)

    return _dynamic_prompt

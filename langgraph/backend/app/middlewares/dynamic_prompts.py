from typing import Any, Mapping, Union, Sequence, Type

from langchain_core.messages import BaseMessage, SystemMessage
from langchain_core.prompts import (
    BasePromptTemplate,
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain.agents.middleware import AgentMiddleware, dynamic_prompt, ModelRequest

from pydantic import BaseModel
from langchain_core.output_parsers import PydanticOutputParser

PromptLike = Union[str, ChatPromptTemplate, SystemMessagePromptTemplate, BasePromptTemplate]

def make_dynamic_prompt_middleware(
    prompt: PromptLike,
    placeholders: Sequence[str],
    output_schema: Type[BaseModel] | None = None,
) -> AgentMiddleware:
    """Return an AgentMiddleware that uses the given prompt object."""

    parser = (
        PydanticOutputParser(pydantic_object=output_schema)
        if output_schema is not None
        else None
    )

    def _values_from_request(request: ModelRequest) -> Mapping[str, Any]:
        state = request.state or {}
        values: dict[str, Any] = {}

        # pull placeholders from state
        for key in placeholders:
            if key == "format_instructions" and parser is not None:
                values["format_instructions"] = parser.get_format_instructions()
            else:
                # by convention your state carries these keys: user_query, history, tool outputs, etc.
                values[key] = state.get(key)

        return values

    def _render_to_system_message(prompt: PromptLike, request: ModelRequest) -> SystemMessage:
        values = _values_from_request(request)

        # 1) Already a plain string
        if isinstance(prompt, str):
            return SystemMessage(content=prompt)

        # 2) ChatPromptTemplate
        if isinstance(prompt, ChatPromptTemplate):
            messages: list[BaseMessage] = prompt.format_messages(**values)
            system_contents = [m.content for m in messages if isinstance(m, SystemMessage)]
            text = "\n\n".join(system_contents)
            return SystemMessage(content=text)

        # 3) SystemMessagePromptTemplate
        if isinstance(prompt, SystemMessagePromptTemplate):
            msg = prompt.format(**values)
            assert isinstance(msg, SystemMessage)
            return msg

        # 4) Generic BasePromptTemplate → string
        if isinstance(prompt, BasePromptTemplate):
            text = prompt.format(**values)
            return SystemMessage(content=text)

        # Fallback
        return SystemMessage(content=str(prompt))

    @dynamic_prompt
    def _dynamic_prompt(request: ModelRequest) -> SystemMessage | str:
        # dynamic_prompt expects str | SystemMessage
        return _render_to_system_message(prompt, request)

    return _dynamic_prompt

from __future__ import annotations

import importlib
from functools import lru_cache
from typing import Any, Callable, Sequence, Type

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import FewShotPromptWithTemplates
from pydantic import BaseModel

from app.utils.file_loader import FileLoader


def _render_few_shots(agent_name: str) -> str:
    """Load and render few-shot examples via LangChain templates.

    Enforces that both the template and examples file exist and produce
    at least one formatted message.
    """

    template_file = FileLoader.resolve_agent_prompt_path("few-shots", agent_name)
    examples_file = template_file.with_name("examples.json")
    if not examples_file.exists():
        raise FileNotFoundError(examples_file)

    prompt_template = FewShotPromptWithTemplates.from_files(
        template_file=str(template_file),
        examples_file=str(examples_file),
    )

    formatted_messages = prompt_template.format_messages()
    if not formatted_messages:
        raise ValueError(f"No few-shot examples produced for agent '{agent_name}'")

    return "\n".join([m.content for m in formatted_messages])

def compose_agent_prompt(
    agent_name: str,
    prompt_names: Sequence[str],
    *,
    include_global: bool = True,
    include_format_instructions: bool = False,
    output_schema: Type[BaseModel] | None = None,
    include_few_shots: bool = True,
) -> str:
    """
    Compose a full agent prompt from global + agent-specific prompt files.
    Optionally appends format_instructions if a schema is provided.
    """

    parts = []

    if include_global:
        parts.append(FileLoader.load_prompt("global_system").strip())

    for name in prompt_names:
        if name == "few-shots":
            if not include_few_shots:
                continue

            parts.append(_render_few_shots(agent_name))
            continue

        else:
            parts.append(FileLoader.load_prompt(name, agent_name).strip())

    if include_format_instructions and output_schema is not None:
        parser = PydanticOutputParser(pydantic_object=output_schema)
        parts.append(parser.get_format_instructions().strip())

    return "\n\n".join(parts)


@lru_cache(maxsize=None)
def load_agent_schema(agent_name: str) -> Type[BaseModel]:
    """
    Convention: each agent exposes `OutputSchema` in
    app/agents/{agent_name}/schema.py.
    """
    try:
        module = importlib.import_module(f"app.agents.{agent_name}.schema")
    except ModuleNotFoundError as exc:
        raise RuntimeError(f"Schema module not found for agent: {agent_name!r}") from exc

    try:
        schema_cls = getattr(module, "OutputSchema")
    except AttributeError as exc:
        raise RuntimeError(
            f"Schema module for agent {agent_name!r} does not define OutputSchema"
        ) from exc

    if not issubclass(schema_cls, BaseModel):
        raise TypeError(
            f"OutputSchema for agent {agent_name!r} must be a Pydantic BaseModel subclass"
        )
    return schema_cls


@lru_cache(maxsize=None)
def load_agent_builder(agent_name: str) -> Callable[..., Any]:
    """
    Convention: each agent exposes `build_agent` in
    app/agents/{agent_name}/agent.py.
    """
    try:
        module = importlib.import_module(f"app.agents.{agent_name}.agent")
    except ModuleNotFoundError as exc:
        raise RuntimeError(f"Agent module not found for agent: {agent_name!r}") from exc

    try:
        builder = getattr(module, "build_agent")
    except AttributeError as exc:
        raise RuntimeError(
            f"Agent module for {agent_name!r} does not define build_agent(...)"
        ) from exc

    if not callable(builder):
        raise TypeError(f"build_agent for agent {agent_name!r} must be callable")
    return builder

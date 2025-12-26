from __future__ import annotations

import importlib
import json
from functools import lru_cache
from typing import Any, Callable, Sequence, Type

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate, FewShotPromptWithTemplates

from pydantic import BaseModel

from app.utils.file_loader import FileLoader


def _render_few_shots(agent_name: str, *, user_placeholder: str = "{user_query}") -> str:
    """Load and render few-shot examples via LangChain templates.

    Contract:
    - `few-shots.prompt` must exist and be non-empty.
    - `examples.json` must exist and contain a list.
    - The list must include:
        - at least one *real* example, and
        - a trailing user stub example that ends with an empty `output`
          and uses `original_input == user_placeholder` (default: `{user_query}`).

    The implementation uses `FewShotPromptWithTemplates` to keep the formatting
    behavior consistent with LangChain prompt-template semantics.
    """

    template_file = FileLoader.resolve_agent_prompt_path("few-shots", agent_name)
    template_str = template_file.read_text(encoding="utf-8").strip()
    if not template_str:
        raise ValueError(f"few-shots.prompt is empty for agent '{agent_name}'")

    examples_file = template_file.with_name("examples.json")
    if not examples_file.exists():
        raise FileNotFoundError(examples_file)

    raw = json.loads(examples_file.read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        raise ValueError(f"examples.json must contain a list for agent '{agent_name}'")
    if len(raw) < 2:
        raise ValueError(
            f"examples.json must include at least one example + one trailing stub for agent '{agent_name}'"
        )

    examples: list[dict[str, Any]] = []
    for idx, ex in enumerate(raw):
        if not isinstance(ex, dict):
            raise ValueError(f"Invalid example payload at index {idx} for agent '{agent_name}': {ex!r}")
        examples.append(ex)

    example_prompt = PromptTemplate.from_template(template_str)

    prefix = PromptTemplate.from_template(
        "Frame the following problems:",
    )
    suffix = PromptTemplate.from_template(
        "Input: { input }\nOutput:",
    )

    few_shot = FewShotPromptWithTemplates(
        examples=examples,
        example_prompt=example_prompt,
        prefix=prefix,
        suffix=suffix,
        input_variables=["input"],
    )

    # Keep `{user_query}` as a *literal placeholder* in the final prompt so it can
    # be substituted later at runtime (not during prompt assembly).
    return few_shot.format(user_query=user_placeholder)


def compose_agent_prompt(
    agent_name: str,
    prompt_names: Sequence[str],
    *,
    include_global: bool = True,
    include_format_instructions: bool = False,
    output_schema: Type[BaseModel] | None = None,
) -> str:
    parts: list[str] = []

    # Treat "few-shots" as a directive, not a prompt file.
    want_few_shots = ("few-shots" in prompt_names)
    normal_prompt_names = [n for n in prompt_names if n != "few-shots"]

    if include_global:
        parts.append(FileLoader.load_prompt("global_system").strip())

    # Render normal prompts in the order the caller gave.
    for name in normal_prompt_names:
        parts.append(FileLoader.load_prompt(name, agent_name).strip())

    # Compute format instructions once; place them BEFORE few-shots so "Output:" remains last.
    if include_format_instructions and output_schema is not None:
        parser = PydanticOutputParser(pydantic_object=output_schema)
        parts.append(parser.get_format_instructions().strip())

    # Append few-shots last, so the prompt ends with "Output:".
    if want_few_shots:
        parts.append(_render_few_shots(agent_name))

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
"""Agent prompt and schema utilities."""

from __future__ import annotations

import importlib
import json
from collections.abc import Callable, Sequence
from functools import cache
from typing import Any

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.tools import BaseTool
from pydantic import BaseModel

from app.platform.config.file_loader import FileLoader
from app.platform.core.contract.prompts import validate_prompt_suffix_order


def _render_few_shots(agent_name: str, *, user_placeholder: str = "{task_input}") -> str:
    """Load and render few-shot examples via LangChain templates.

    Contract:
    - `few-shots.prompt` must exist and contain placeholders.
    - `examples.json` must include:
        - ≥1 real example
        - 1 stub example that ends with an empty output and uses `task_input == user_placeholder`
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

    def _is_empty(value: Any) -> bool:
        return value in (None, "", {}, [])

    examples: list[dict[str, Any]] = list(raw)

    stub = examples[-1]
    real_examples = examples[:-1]

    if stub.get("task_input") != user_placeholder:
        raise ValueError(f"Trailing stub must use placeholder {user_placeholder!r} for agent '{agent_name}'")
    if not _is_empty(stub.get("output", "")):
        raise ValueError(f"Trailing stub output must be empty for agent '{agent_name}'")

    for idx, ex in enumerate(real_examples):
        if "task_input" not in ex or "output" not in ex:
            raise ValueError(f"Missing keys in example {idx} for agent '{agent_name}': {ex!r}")
        if not str(ex["task_input"]).strip():
            raise ValueError(f"Example {idx} for agent '{agent_name}' must include a task_input")
        if _is_empty(ex["output"]):
            raise ValueError(f"Example {idx} for agent '{agent_name}' must include a non-empty output")

    def _render_example(task_input: str, output: Any) -> str:
        rendered_output = output if isinstance(output, str) else json.dumps(output, indent=2)
        rendered = template_str.replace("{task_input}", task_input)
        rendered = rendered.replace("{output}", rendered_output)
        return rendered

    prefix = "Frame the following problems:"
    rendered_examples = [_render_example(ex["task_input"], ex["output"]) for ex in real_examples]

    prompt_parts = [prefix, *rendered_examples, _render_example(user_placeholder, "")]
    return "\n\n".join(prompt_parts)


def compose_agent_prompt(
    agent_name: str,
    prompt_names: Sequence[str],
    *,
    include_global: bool = True,
    include_format_instructions: bool = False,
    output_schema: type[BaseModel] | None = None,
) -> str:
    """Compose an agent system prompt from prompt files and optional few-shots.

    Prompt contracts:
    - `system.prompt` is required for each agent.
    - `few-shots` is a directive that requires `few-shots.prompt` + `examples.json`.
    - `examples.json` must include >=1 real example and a trailing stub with
      `task_input == "{task_input}"` and empty output.
    """
    parts: list[str] = []

    # Treat "few-shots" as a directive, not a prompt file.
    want_few_shots = "few-shots" in prompt_names
    normal_prompt_names = [n for n in prompt_names if n != "few-shots"]

    if include_global:
        parts.append(FileLoader.load_prompt("global_system").strip())

    # Render normal prompts in the order the caller gave.
    parts.extend(FileLoader.load_prompt(name, agent_name).strip() for name in normal_prompt_names)

    # Compute format instructions once; place them BEFORE few-shots so "Output:" remains last.
    if include_format_instructions and output_schema is not None:
        parser = PydanticOutputParser(pydantic_object=output_schema)
        parts.append(parser.get_format_instructions().strip())

    # Append few-shots last, so the prompt ends with "Output:".
    if want_few_shots:
        parts.append(_render_few_shots(agent_name))

    full_sequence = [*normal_prompt_names]
    if want_few_shots:
        full_sequence.append("few-shots")
        validate_prompt_suffix_order(full_sequence, ("few-shots",))

    return "\n\n".join(parts)


@cache
def load_agent_schema(agent_name: str) -> type[BaseModel]:
    """Load an agent's OutputSchema from its schema module.

    Convention: each agent exposes `OutputSchema` in
    app/agents/{agent_name}/schema.py.
    """
    try:
        module = importlib.import_module(f"app.agents.{agent_name}.schema")
    except ModuleNotFoundError as exc:
        raise RuntimeError(f"Schema module not found for agent: {agent_name!r}") from exc

    try:
        schema_cls = module.OutputSchema
    except AttributeError as exc:
        raise RuntimeError(f"Schema module for agent {agent_name!r} does not define OutputSchema") from exc

    if not issubclass(schema_cls, BaseModel):
        raise TypeError(f"OutputSchema for agent {agent_name!r} must be a Pydantic BaseModel subclass")
    return schema_cls


@cache
def load_agent_builder(agent_name: str) -> Callable[..., Any]:
    """Load an agent's build_agent factory from its module.

    Convention: each agent exposes `build_agent` in
    app/agents/{agent_name}/agent.py.
    """
    try:
        module = importlib.import_module(f"app.agents.{agent_name}.agent")
    except ModuleNotFoundError as exc:
        raise RuntimeError(f"Agent module not found for agent: {agent_name!r}") from exc

    try:
        builder = module.build_agent
    except AttributeError as exc:
        raise RuntimeError(f"Agent module for {agent_name!r} does not define build_agent(...)") from exc

    if not callable(builder):
        raise TypeError(f"build_agent for agent {agent_name!r} must be callable")
    return builder


def build_tool_allowlist(
    tools: Sequence[BaseTool],
    response_schema: type[BaseModel] | None = None,
) -> list[str]:
    """Return allowed tool names, including the structured output tool name if present."""
    allowlist = [tool.name for tool in tools]
    if response_schema is not None:
        allowlist.append(response_schema.__name__)
    return allowlist

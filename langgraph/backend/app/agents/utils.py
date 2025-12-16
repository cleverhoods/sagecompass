from __future__ import annotations

import importlib
import logging
from functools import lru_cache
from typing import Any, Callable, Sequence, Type, Mapping

from docling_ibm_models.tableformer.models.common.base_model import LOG_LEVEL
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel

from app.utils.file_loader import FileLoader

from typing import Any, Mapping, Sequence
import logging
from app.utils.file_loader import FileLoader

def build_hilp_clarifications(
    hilp_meta: Mapping[str, Any] | None,
    hilp_answers: Sequence[Any],
    *,
    max_items: int = 3,
) -> str:
    """Build human-readable ambiguity → clarification list."""
    if not hilp_meta or not hilp_meta.get("ambiguities") or not hilp_answers:
        return ""

    ambiguities = list(hilp_meta.get("ambiguities") or [])

    def _importance(a: Any) -> float:
        if isinstance(a, dict):
            return float(a.get("importance") or 0)
        return float(getattr(a, "importance", 0) or 0)

    ambiguities.sort(key=_importance, reverse=True)
    lines: list[str] = []

    for amb, ans in zip(ambiguities[:max_items], hilp_answers):
        if isinstance(amb, dict):
            desc = amb.get("description") or amb.get("key") or str(amb)
        else:
            desc = getattr(amb, "description", None) or getattr(amb, "key", None) or str(amb)
        lines.append(f"Ambiguity: {desc}")
        lines.append(f"Clarification: {ans}")
        lines.append("")

    return "\n".join(lines).strip()

def render_hilp_prompt(
    agent_name: str,
    *,
    context: Mapping[str, Any],
) -> str:
    template = FileLoader.load_prompt("hilp", agent_name)
    try:
        return template.format(**context)
    except Exception:
        logging.warning("HILP prompt formatting failed", exc_info=True)
        return template

def build_hilp_questions(
    hilp_meta: Mapping[str, Any] | None,
    *,
    max_items: int = 3,
) -> str:
    if not hilp_meta or not hilp_meta.get("ambiguities"):
        return ""
    ambiguities = list(hilp_meta["ambiguities"])

    def importance(a: Any) -> float:
        if isinstance(a, dict):
            return float(a.get("importance") or 0)
        return float(getattr(a, "importance", 0) or 0)

    ambiguities.sort(key=importance, reverse=True)
    lines: list[str] = []
    for amb in ambiguities[:max_items]:
        desc = amb.get("description") if isinstance(amb, dict) else getattr(amb, "description", str(amb))
        lines.append(f"- {desc}")
    return "\n".join(lines)

def build_agent_prompt(agent_name: str, prompt_names: Sequence[str], include_global: bool = True) -> ChatPromptTemplate:
    """
    Build a chat prompt template from a variety of message formats.
    :param agent_name:
    :param prompt_names: file base names without extension e.g.: ["system", "few-shots"]
    :param include_global:
    :return:
    """
    messages = []

    if include_global:
        messages.append(
            ("system", FileLoader.load_prompt("global_system"))
        )

    for prompt_name in prompt_names:
        logging.log(logging.INFO, f"Building prompt for | '{agent_name}' | '{prompt_name}' |")
        messages.append(
            ("system", FileLoader.load_prompt(prompt_name, agent_name))
        )

    # Final user input
    #messages.append(("human", "{user_query}"))

    return ChatPromptTemplate.from_messages(messages)

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

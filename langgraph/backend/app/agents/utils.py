from __future__ import annotations

import importlib
import logging
from functools import lru_cache
from typing import Any, Callable, Sequence, Type

from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel

from app.utils.file_loader import FileLoader


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

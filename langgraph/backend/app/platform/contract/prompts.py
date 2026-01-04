"""Prompt contract validators."""

from __future__ import annotations

from collections.abc import Sequence

from pydantic import BaseModel, Field


class PromptContract(BaseModel):
    """Defines required prompt placeholders and suffix ordering."""

    placeholders: tuple[str, ...] = Field(
        default_factory=tuple,
        description="Placeholders that must appear in the prompt.",
    )
    suffix_order: tuple[str, ...] = Field(
        default_factory=tuple,
        description="Ordered suffix identifiers that must appear last.",
    )


def validate_prompt_placeholders(prompt_text: str, placeholders: Sequence[str]) -> None:
    """Validate that required placeholders are present in the prompt."""
    missing = [
        placeholder
        for placeholder in placeholders
        if "{" + placeholder + "}" not in prompt_text
    ]
    if missing:
        raise ValueError(f"Missing prompt placeholders: {missing}")


def validate_prompt_variables(
    variables: Sequence[str],
    placeholders: Sequence[str],
) -> None:
    """Validate that required placeholders are declared as template variables."""
    missing = [placeholder for placeholder in placeholders if placeholder not in variables]
    if missing:
        raise ValueError(f"Missing prompt variables: {missing}")


def validate_prompt_suffix_order(
    suffixes: Sequence[str],
    required_order: Sequence[str],
) -> None:
    """Validate that suffixes end with the required ordered list."""
    if not required_order:
        return
    if len(suffixes) < len(required_order):
        raise ValueError("Prompt suffixes shorter than required order.")
    if list(suffixes[-len(required_order):]) != list(required_order):
        raise ValueError("Prompt suffix order does not match required order.")

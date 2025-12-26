from __future__ import annotations

from typing import Any, Type

from pydantic import BaseModel


class PydanticOutputParser:
    """Very small stub to mimic LangChain's output parser contract."""

    def __init__(self, *, pydantic_object: Type[BaseModel]) -> None:
        self.pydantic_object = pydantic_object

    def get_format_instructions(self) -> str:
        return f"Respond with JSON matching {self.pydantic_object.__name__}"

    def parse(self, data: Any) -> BaseModel:  # pragma: no cover - unused helper
        return self.pydantic_object.model_validate(data)

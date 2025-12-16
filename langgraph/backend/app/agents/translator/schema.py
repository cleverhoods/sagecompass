from __future__ import annotations

from pydantic import BaseModel, Field


class TranslationResult(BaseModel):
    translated_text: str = Field(
        ...,
        description="The fully translated text."
    )
    source_language: str | None = Field(
        default=None,
        description="Detected source language code or name, if known."
    )
    target_language: str = Field(
        ...,
        description="Target language code or name."
    )
    style_notes: str | None = Field(
        default=None,
        description="Optional notes on tone, terminology, or ambiguity."
    )


# Graph convention
OutputSchema = TranslationResult

"""Core DTOs for evidence and context handling."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from langchain_core.documents import Document


@dataclass(frozen=True)
class EvidenceBundle:
    """Evidence items and hydrated docs for a phase.

    This is a pure data transfer object that carries evidence data
    without knowledge of state management or LangGraph runtime details.
    """

    evidence: Sequence[dict]  # Raw evidence items (namespace, key, score)
    context_docs: list[Document]  # Hydrated LangChain documents
    missing_store: bool = False  # Whether store was unavailable during hydration

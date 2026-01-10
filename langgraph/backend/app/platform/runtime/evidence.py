"""Evidence hydration helpers for runtime use."""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass

from langchain_core.documents import Document
from langgraph.config import get_store

from app.platform.contract.logging import get_logger
from app.state import EvidenceItem, PhaseEntry, SageState

logger = get_logger("runtime.evidence")


@dataclass(frozen=True)
class EvidenceBundle:
    """Evidence items and hydrated docs for a phase."""

    phase_entry: PhaseEntry
    evidence: Sequence[EvidenceItem | dict]
    context_docs: list[Document]
    missing_store: bool = False


def _extract_evidence_fields(item: EvidenceItem | dict) -> tuple[list[str] | None, str | None, float | None]:
    if isinstance(item, EvidenceItem):
        return item.namespace, item.key, item.score
    namespace = item.get("namespace")
    key = item.get("key")
    score = item.get("score")
    return namespace, key, score


def _get_runtime_store(phase: str):
    try:
        store = get_store()
    except RuntimeError:
        logger.warning("evidence.missing_runtime_store", phase=phase)
        return None
    if store is None:
        logger.warning("evidence.missing_runtime_store", phase=phase)
        return None
    return store


def hydrate_evidence_docs(
    evidence: Iterable[EvidenceItem | dict],
    *,
    phase: str,
    max_items: int = 8,
    store=None,
) -> list[Document]:
    """Hydrate evidence items into LangChain Documents for downstream use."""
    evidence_items = list(evidence or [])
    if not evidence_items:
        return []

    if store is None:
        store = _get_runtime_store(phase)
        if store is None:
            return []

    context_docs: list[Document] = []
    for evidence_item in evidence_items[:max_items]:
        namespace, key, score = _extract_evidence_fields(evidence_item)
        if not namespace or not key:
            continue
        ns_tuple = tuple(namespace) if isinstance(namespace, (list, tuple)) else None
        if ns_tuple is None:
            continue

        stored = store.get(ns_tuple, key)
        if not stored or not getattr(stored, "value", None):
            continue
        value = stored.value or {}
        metadata = {
            "title": value.get("title", ""),
            "tags": value.get("tags", []),
            "agents": value.get("agents", []),
            "changed": value.get("changed", 0),
            "store_namespace": list(getattr(stored, "namespace", namespace)),
            "store_key": getattr(stored, "key", key),
            "score": score if score is None else float(score),
        }
        context_docs.append(
            Document(
                page_content=value.get("text", ""),
                metadata=metadata,
            )
        )

    return context_docs


def collect_phase_evidence(
    state: SageState,
    *,
    phase: str,
    max_items: int = 8,
) -> EvidenceBundle:
    """Return evidence items and hydrated docs for a phase."""
    phase_entry = state.phases.get(phase) or PhaseEntry()
    evidence = list(phase_entry.evidence or [])
    store = _get_runtime_store(phase)
    missing_store = store is None and bool(evidence)
    context_docs = hydrate_evidence_docs(
        evidence,
        phase=phase,
        max_items=max_items,
        store=store,
    )
    return EvidenceBundle(
        phase_entry=phase_entry,
        evidence=evidence,
        context_docs=context_docs,
        missing_store=missing_store,
    )

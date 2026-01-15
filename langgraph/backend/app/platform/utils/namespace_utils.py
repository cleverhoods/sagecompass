"""Namespace construction utilities for store operations.

Provides helpers for building consistent, standardized namespaces
used across tools and nodes when interacting with the LangGraph Store.
"""

from __future__ import annotations

from app.platform.core.contract.namespaces import NamespaceParts, build_namespace


def build_agent_namespace(collection: str) -> tuple[str, ...]:
    """Build a standard agent-scoped namespace for store operations.

    Args:
        collection: Agent machine name (e.g., "problem_framing").

    Returns:
        Namespace tuple for store operations.
    """
    return build_namespace(
        NamespaceParts(
            app="drupal",
            tenant=None,
            thread="context",
            phase="agent",
            artifact_type=collection,
        )
    )

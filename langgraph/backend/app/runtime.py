from __future__ import annotations

from typing import TypedDict


class SageRuntimeContext(TypedDict, total=False):
    """
    Runtime-only configuration for LangGraph execution.

    This data MUST NOT be persisted into SageState. It is supplied via
    `context=` when invoking a compiled graph or running nodes directly
    through LangGraph runtime hooks.
    """

    hilp_enabled: bool
    hilp_max_questions: int
    hilp_audit_mode: bool


DEFAULT_RUNTIME_CONTEXT: SageRuntimeContext = {
    "hilp_enabled": True,
    "hilp_audit_mode": True,
}


def build_runtime_context(overrides: SageRuntimeContext | None = None) -> SageRuntimeContext:
    """Return a runtime context dict merged with defaults."""
    base = dict(DEFAULT_RUNTIME_CONTEXT)
    if overrides:
        base.update(overrides)
    return base

from __future__ import annotations

from typing_extensions import TypedDict


class SageRuntimeContext(TypedDict, total=False):
    """
    Runtime-only configuration for LangGraph execution.

    This data MUST NOT be persisted into SageState. It is supplied via
    `context=` when invoking a compiled graph or running nodes directly.
    """
    pass


def build_runtime_context(
    overrides: SageRuntimeContext | None = None,
) -> SageRuntimeContext:
    """
    Return a runtime context dict merged with defaults.

    Context is intentionally empty for now; keep this function to preserve
    call sites and allow future runtime knobs without refactors.
    """
    return overrides if overrides is not None else {}

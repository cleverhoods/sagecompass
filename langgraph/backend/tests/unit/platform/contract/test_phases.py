from __future__ import annotations

from collections.abc import Callable

import pytest
from langchain_core.runnables import Runnable, RunnableLambda
from pydantic import BaseModel, ValidationError

from app.platform.core.contract.phases import PhaseContract
from app.platform.core.contract.registry import validate_phase_registry

pytestmark = pytest.mark.platform


class DummyOutput(BaseModel):
    """Dummy output schema for phase contract tests."""

    value: str


def _build_graph() -> Callable[[], Runnable[object, object]]:
    return lambda: RunnableLambda(lambda value: value)


def test_validate_phase_registry_accepts_matching_key() -> None:
    contract = PhaseContract(
        name="dummy",
        build_graph=_build_graph(),
        output_schema=DummyOutput,
        description="dummy phase",
    )

    validate_phase_registry({"dummy": contract})


def test_validate_phase_registry_rejects_mismatched_key() -> None:
    contract = PhaseContract(
        name="dummy",
        build_graph=_build_graph(),
        output_schema=DummyOutput,
        description="dummy phase",
    )

    with pytest.raises(ValueError):
        validate_phase_registry({"wrong": contract})


def test_validate_phase_registry_rejects_non_model_schema() -> None:
    class NotAModel:
        pass

    with pytest.raises(ValidationError):
        PhaseContract(
            name="dummy",
            build_graph=_build_graph(),
            output_schema=NotAModel,  # type: ignore[arg-type]
            description="dummy phase",
        )

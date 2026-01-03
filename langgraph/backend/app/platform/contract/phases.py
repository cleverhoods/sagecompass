"""Phase registry contract for PhaseContract entries.

Contract meaning:
- Every phase is defined via PhaseContract and registered under its name.
- The registry key must match PhaseContract.name.
- Each PhaseContract declares output_schema and flags required by routing.
"""

from __future__ import annotations

from collections.abc import Mapping

from pydantic import BaseModel

from app.graphs.subgraphs.phases.contract import PhaseContract


def validate_phase_registry(phases: Mapping[str, PhaseContract]) -> None:
    """Validate that the phase registry keys match contract names and schemas."""
    for key, contract in phases.items():
        if key != contract.name:
            raise ValueError(
                f"Phase registry key {key!r} does not match contract name {contract.name!r}."
            )
        if not issubclass(contract.output_schema, BaseModel):
            raise TypeError(
                f"Phase contract {contract.name!r} output_schema must be a BaseModel."
            )

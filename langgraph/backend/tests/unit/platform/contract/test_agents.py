from __future__ import annotations

import pytest

from app.agents.problem_framing.schema import ProblemFrame
from app.platform.adapters.agents import validate_agent_schema

pytestmark = pytest.mark.compliance


def test_validate_agent_schema_returns_model() -> None:
    schema = validate_agent_schema("problem_framing")
    assert schema is ProblemFrame

from __future__ import annotations

import pytest
from langchain_tests.unit_tests.tools import ToolsUnitTests

from app.tools.nothingizer import nothingizer_tool

# https://reference.langchain.com/python/langchain_tests/unit_tests/tools/
pytestmark = pytest.mark.real_deps


class TestNothingizerTool(ToolsUnitTests):
    @property
    def tool_constructor(self):
        return nothingizer_tool

    @property
    def tool_invoke_params_example(self) -> dict[str, object]:
        return {}

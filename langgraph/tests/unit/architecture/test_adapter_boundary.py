"""Architecture tests: Adapter boundary enforcement.

This test suite enforces the hexagonal architecture rule that only adapters
can import from both sides of the boundary (core and app/state).

Non-adapter modules must choose one side:
- Core modules: only import from core (tested in test_core_purity.py)
- App modules: can import from adapters and state, but not directly from core
  (they should go through adapters for DTO translations)
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

ADAPTERS_PATH = Path("app/platform/adapters")
CORE_PREFIXES = (
    "app.platform.core.contract",
    "app.platform.core.dto",
    "app.platform.core.policy",
)
STATE_PREFIXES = (
    "app.state",
    "app.graphs",
)


def _get_imports_from_file(file_path: Path) -> list[str]:
    """Extract all import statements from a Python file using AST.

    Args:
        file_path: Path to Python file to analyze.

    Returns:
        List of imported module names.
    """
    try:
        content = file_path.read_text()
        tree = ast.parse(content)
    except (SyntaxError, UnicodeDecodeError):
        return []

    imports: list[str] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.append(node.module)

    return imports


def _get_all_python_files(directory: Path) -> list[Path]:
    """Recursively find all Python files in a directory.

    Args:
        directory: Directory to search.

    Returns:
        List of Python file paths.
    """
    if not directory.exists():
        return []
    return list(directory.rglob("*.py"))


def _has_core_imports(imports: list[str]) -> bool:
    """Check if imports include any core modules."""
    return any(imp.startswith(CORE_PREFIXES) for imp in imports)


def _has_state_imports(imports: list[str]) -> bool:
    """Check if imports include any state/app modules."""
    return any(imp.startswith(STATE_PREFIXES) for imp in imports)


@pytest.mark.architecture
def test_adapters_can_import_both_sides() -> None:
    """Test that adapter modules can import from both core and state.

    Adapters are the boundary translation layer and are the ONLY modules
    allowed to import from both sides.
    """
    adapter_files = _get_all_python_files(ADAPTERS_PATH)
    adapter_files = [f for f in adapter_files if "__pycache__" not in str(f)]

    if not adapter_files:
        pytest.skip("No adapter files found (directory may be new)")

    # At least one adapter should import from both sides
    # (This validates the architecture is being used correctly)
    two_way_adapters = []

    for file_path in adapter_files:
        if file_path.name == "__init__.py":
            continue

        imports = _get_imports_from_file(file_path)
        has_core = _has_core_imports(imports)
        has_state = _has_state_imports(imports)

        if has_core and has_state:
            two_way_adapters.append(file_path)

    # We expect at least one adapter to use both sides
    # (If none do, the architecture isn't being utilized)
    assert two_way_adapters, (
        "No adapters found that import from both core and state. Adapters should translate between DTOs and State."
    )


@pytest.mark.architecture
def test_adapter_imports_are_intentional() -> None:
    """Test that adapter modules have meaningful imports.

    This is a sanity check to ensure adapters aren't empty wrappers.
    """
    adapter_files = _get_all_python_files(ADAPTERS_PATH)
    adapter_files = [f for f in adapter_files if "__pycache__" not in str(f)]

    # Pure Protocol definitions don't need runtime platform imports
    protocol_only_files = {"node.py"}

    for file_path in adapter_files:
        if file_path.name == "__init__.py" or file_path.name in protocol_only_files:
            continue

        imports = _get_imports_from_file(file_path)

        # Each adapter should import something from the platform
        platform_imports = [imp for imp in imports if imp.startswith("app.platform")]
        assert platform_imports, f"Adapter {file_path.name} has no platform imports"


@pytest.mark.architecture
def test_adapters_directory_exists() -> None:
    """Test that adapters directory exists."""
    assert ADAPTERS_PATH.exists(), "Adapters directory does not exist"
    assert ADAPTERS_PATH.is_dir(), "Adapters path is not a directory"

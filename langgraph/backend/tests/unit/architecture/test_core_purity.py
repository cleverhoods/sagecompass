"""Architecture tests: Core layer purity enforcement.

This test suite enforces the hexagonal architecture rule that the core layer
must not import from forbidden zones:
- app.state, app.graphs, app.nodes, app.agents, app.tools (app orchestration)
- app.platform.adapters (boundary layer)
- app.platform.config, app.platform.providers, app.platform.observability,
  app.platform.runtime (wiring/infrastructure)

Contract types and validators in core/ must remain pure and extractable.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

# Forbidden import prefixes for core/ modules
FORBIDDEN_PREFIXES = (
    "app.state",
    "app.graphs",
    "app.nodes",
    "app.agents",
    "app.tools",
    "app.platform.adapters",
    "app.platform.config",
    "app.platform.observability",
    "app.platform.runtime",
    "app.platform.utils",
)

# Core directories that must remain pure
CORE_PATHS = [
    Path("app/platform/core/contract"),
    Path("app/platform/core/dto"),
    Path("app/platform/core/policy"),
]


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


@pytest.mark.architecture
def test_core_has_no_forbidden_imports() -> None:
    """Test that core/ modules do not import from forbidden zones.

    This enforces the hexagonal architecture rule that core must remain pure
    and not depend on app orchestration or wiring infrastructure.
    """
    violations: list[tuple[Path, str]] = []

    for core_path in CORE_PATHS:
        python_files = _get_all_python_files(core_path)

        for file_path in python_files:
            # Skip __pycache__ and other non-source files
            if "__pycache__" in str(file_path):
                continue

            imports = _get_imports_from_file(file_path)

            violations.extend(
                (file_path, import_name)
                for import_name in imports
                for forbidden_prefix in FORBIDDEN_PREFIXES
                if import_name.startswith(forbidden_prefix)
            )

    if violations:
        error_lines = ["Core layer imports from forbidden zones:"]
        error_lines.extend(
            f"  {file_path.relative_to(Path.cwd())}: imports {import_name}" for file_path, import_name in violations
        )
        error_lines.append("")
        error_lines.append("Core must not import from:")
        error_lines.extend(f"  - {prefix}" for prefix in FORBIDDEN_PREFIXES)

        pytest.fail("\n".join(error_lines))


@pytest.mark.architecture
def test_core_directories_exist() -> None:
    """Test that core directories exist as expected."""
    for core_path in CORE_PATHS:
        assert core_path.exists(), f"Core directory {core_path} does not exist"
        assert core_path.is_dir(), f"Core path {core_path} is not a directory"


@pytest.mark.architecture
def test_core_has_pure_modules() -> None:
    """Test that core directories contain Python modules."""
    for core_path in CORE_PATHS:
        python_files = _get_all_python_files(core_path)
        # Allow empty directories but warn
        if not python_files:
            pytest.skip(f"No Python files found in {core_path} (directory may be new)")
        # At least one non-__init__ file should exist
        non_init_files = [f for f in python_files if f.name != "__init__.py"]
        assert non_init_files, f"Core directory {core_path} has no non-__init__ modules"

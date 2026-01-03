from __future__ import annotations

from pathlib import Path


def test_platform_domain_contracts() -> None:
    platform_root = Path("app/platform")
    if not platform_root.exists():
        return

    domain_dirs = [
        path
        for path in platform_root.iterdir()
        if path.is_dir() and not path.name.startswith("__")
    ]

    for domain in domain_dirs:
        readme = domain / "README.md"
        init = domain / "__init__.py"
        assert readme.exists(), f"Missing README.md for platform domain {domain.name}"
        assert init.exists(), f"Missing __init__.py for platform domain {domain.name}"

        tests_root = Path("tests/unit/platform") / domain.name
        assert tests_root.exists(), f"Missing tests folder for platform domain {domain.name}"
        has_tests = any(t.name.startswith("test_") for t in tests_root.rglob("*.py"))
        assert has_tests, f"Missing test_*.py in {tests_root}"

from __future__ import annotations

import ast
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[2]
APP = ROOT / "app"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def top_level_call_names(py: Path) -> list[tuple[int, str]]:
    src = read_text(py)
    tree = ast.parse(src)
    out: list[tuple[int, str]] = []
    for node in tree.body:
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Call):
            fn = node.value.func
            if isinstance(fn, ast.Name):
                out.append((node.lineno, fn.id))
            elif isinstance(fn, ast.Attribute):
                out.append((node.lineno, fn.attr))
    return out


def collect_import_modules(py: Path) -> set[str]:
    src = read_text(py)
    tree = ast.parse(src)
    imports: set[str] = set()
    for node in tree.body:
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module)
    return imports


def iter_python_files(base: Path) -> Iterable[Path]:
    return (
        py
        for py in base.rglob("*.py")
        if py.is_file() and py.name != "__init__.py"
    )

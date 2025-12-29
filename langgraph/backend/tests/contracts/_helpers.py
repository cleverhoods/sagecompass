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
    calls: list[tuple[int, str]] = []

    class _TopLevelCallVisitor(ast.NodeVisitor):
        def visit_FunctionDef(self, node):
            # Do not traverse into functions/classes; only import-time effects matter.
            return

        visit_AsyncFunctionDef = visit_FunctionDef
        visit_ClassDef = visit_FunctionDef

        def visit_Call(self, node: ast.Call):
            func = node.func
            name = None
            if isinstance(func, ast.Name):
                name = func.id
            elif isinstance(func, ast.Attribute):
                name = func.attr
            if name:
                calls.append((node.lineno, name))
            # Traverse arguments to catch nested calls at top-level expressions.
            for child in ast.iter_child_nodes(node):
                if not isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda)):
                    self.visit(child)

    visitor = _TopLevelCallVisitor()
    for node in tree.body:
        visitor.visit(node)

    return calls


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

from __future__ import annotations

import ast
from pathlib import Path

from app.state import HilpRequest

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "app"

def _read(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="replace")

def _top_level_call_names(py: Path) -> list[tuple[int, str]]:
    src = _read(py)
    tree = ast.parse(src)
    out = []
    for node in tree.body:
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Call):
            fn = node.value.func
            if isinstance(fn, ast.Name):
                out.append((node.lineno, fn.id))
            elif isinstance(fn, ast.Attribute):
                out.append((node.lineno, fn.attr))
    return out

def test_readmes_present_and_scoped():
    expected = [
        APP / "README.md",
        APP / "agents" / "README.md",
        APP / "nodes" / "README.md",
        APP / "graphs" / "README.md",
        APP / "tools" / "README.md",
        APP / "middlewares" / "README.md",
    ]
    for p in expected:
        assert p.exists(), f"Missing README: {p}"

    # scope/title sanity checks
    assert _read(APP / "middlewares" / "README.md").lstrip().startswith("# Middlewares")

def test_no_import_time_agent_construction_in_nodes():
    banned_calls = {"build_agent", "create_agent", "get_model_for_agent"}
    for py in (APP / "nodes").glob("*.py"):
        for lineno, name in _top_level_call_names(py):
            assert name not in banned_calls, f"{py}: import-time call {name} at line {lineno}"

def test_interrupt_only_in_hilp_node():
    for py in APP.rglob("*.py"):
        if py.name == "hilp.py":
            continue
        assert "interrupt(" not in _read(py), f"interrupt() used outside hilp node: {py}"

def test_agent_folder_minimum_contract():
    agents_dir = APP / "agents"
    for agent in agents_dir.iterdir():
        if not agent.is_dir():
            continue
        if agent.name.startswith("_"):
            continue
        if not (agent / "agent.py").exists():
            continue  # not an agent folder by your own definition

        assert (agent / "schema.py").exists(), f"{agent.name}: missing schema.py"
        assert (agent / "mw.py").exists(), f"{agent.name}: missing mw.py"
        assert (agent / "prompts" / "system.prompt").exists(), f"{agent.name}: missing prompts/system.prompt"

        system_prompt = _read(agent / "prompts" / "system.prompt")
        assert "{format_instructions}" in system_prompt, f"{agent.name}: system.prompt missing {{format_instructions}}"

        has_cfg = (agent / "config.yml").exists() or (agent / "config.yaml").exists()
        assert has_cfg, f"{agent.name}: missing config.yml/config.yaml"

def test_hilp_request_minimum_schema_is_used():
    ann = HilpRequest.__annotations__
    assert "phase" in ann
    assert "prompt" in ann
    assert "goto_after" in ann

from __future__ import annotations

import ast
from pathlib import Path

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
def test_hilp_middleware_factory_exists():
    import importlib

    mw = importlib.import_module("app.middlewares.hilp")
    assert hasattr(mw, "make_boolean_hilp_middleware"), "Missing HILP middleware factory"


def test_prompt_contracts():
    """Ensure agents wire system + few-shot prompts via templated files."""

    # Verify Problem Framing few-shot assets exist and are non-empty
    pf_prompts = APP / "agents" / "problem_framing" / "prompts"
    template = (pf_prompts / "few-shots.prompt").read_text().strip()
    examples_path = pf_prompts / "examples.json"
    examples = examples_path.read_text().strip()

    assert template, "problem_framing few-shots.prompt is empty"
    assert examples, "problem_framing examples.json is empty"

    # Ensure examples file is valid JSON
    import json

    with examples_path.open() as f:
        data = json.load(f)
    assert isinstance(data, list), "examples.json must contain a list of examples"
    assert len(data) >= 1, "examples.json must include at least one example"

    # Render few-shots to ensure template/examples compatibility and trailing stub
    import pytest

    pytest.importorskip("langchain_core.output_parsers")
    from app.agents.utils import compose_agent_prompt
    rendered = compose_agent_prompt(
        agent_name="problem_framing",
        prompt_names=["few-shots"],
        include_global=False,
        include_format_instructions=False,
        include_few_shots=True,
    )
    assert "Input:" in rendered
    assert "{user_query}" in rendered, "Few-shot stub must include user placeholder for final turn"
    assert rendered.strip().endswith("Output:"), "Few-shot rendering must end with empty output stub"

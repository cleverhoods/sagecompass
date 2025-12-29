from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.agents.utils import compose_agent_prompt
from ._helpers import APP, ROOT, read_text


def test_readmes_present_and_scoped():
    expected = [
        APP / "README.md",
        APP / "agents" / "README.md",
        APP / "nodes" / "README.md",
        APP / "graphs" / "README.md",
        APP / "tools" / "README.md",
        APP / "middlewares" / "README.md",
    ]
    for path in expected:
        assert path.exists(), f"Missing README: {path}"

    assert read_text(APP / "middlewares" / "README.md").lstrip().startswith("# Middlewares")


def test_agent_folder_minimum_contract():
    agents_dir = APP / "agents"
    for agent in agents_dir.iterdir():
        if not agent.is_dir() or agent.name.startswith("_"):
            continue
        if not (agent / "agent.py").exists():
            continue

        assert (agent / "schema.py").exists(), f"{agent.name}: missing schema.py"
        assert (agent / "mw.py").exists(), f"{agent.name}: missing mw.py"
        assert (agent / "prompts" / "system.prompt").exists(), f"{agent.name}: missing prompts/system.prompt"

        has_cfg = (agent / "config.yml").exists() or (agent / "config.yaml").exists()
        assert has_cfg, f"{agent.name}: missing config.yml/config.yaml"


def test_prompt_contracts():
    """Ensure agents wire system + few-shot prompts via templated files."""

    pf_prompts = APP / "agents" / "problem_framing" / "prompts"
    template = (pf_prompts / "few-shots.prompt").read_text().strip()
    examples_path = pf_prompts / "examples.json"
    examples = examples_path.read_text().strip()

    assert template, "problem_framing few-shots.prompt is empty"
    assert examples, "problem_framing examples.json is empty"

    with examples_path.open() as f:
        data = json.load(f)
    assert isinstance(data, list), "examples.json must contain a list of examples"
    assert len(data) >= 2, "examples.json must include examples plus a trailing stub"

    stub = data[-1]
    assert stub["user_query"] == "{user_query}", "Trailing stub must preserve the user placeholder"
    assert stub.get("output") in ("", None, {}, []), "Trailing stub output must remain empty"
    assert all(ex.get("output") for ex in data[:-1]), "Non-stub examples must include outputs"

    pytest.importorskip("langchain_core.output_parsers")
    rendered = compose_agent_prompt(
        agent_name="problem_framing",
        prompt_names=["few-shots"],
        include_global=False,
        include_format_instructions=False,
    )
    assert "Input:" in rendered
    assert "{user_query}" in rendered, "Few-shot stub must include the user placeholder for final turn"
    assert "reduce customer churn" in rendered, "Few-shot rendering must expand real examples"
    assert rendered.strip().endswith("Output:"), "Few-shot rendering must end with empty output stub"


def test_tests_mirror_component_layout():
    """tests/ should mirror app component layout for clarity."""

    root = ROOT / "tests"
    expected_dirs = [
        root / "agents" / "problem_framing",
        root / "graphs",
        root / "middlewares" / "hilp",
        root / "nodes",
        root / "tools",
        root / "utils",
    ]
    for directory in expected_dirs:
        assert directory.exists(), f"Expected tests directory missing: {directory}"

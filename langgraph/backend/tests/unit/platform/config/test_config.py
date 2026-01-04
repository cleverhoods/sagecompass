from __future__ import annotations

from pathlib import Path

import pytest

from app.platform.config import CONFIG_DIR, FileLoader, load_project_env

pytestmark = pytest.mark.structural


def test_config_paths_resolve() -> None:
    assert CONFIG_DIR.exists()
    assert CONFIG_DIR.is_dir()


def test_file_loader_resolves_agent_prompt() -> None:
    prompt_path = FileLoader.resolve_agent_prompt_path("system", "problem_framing")
    assert isinstance(prompt_path, Path)
    assert prompt_path.exists()


def test_env_loader_is_idempotent() -> None:
    load_project_env()
    load_project_env()

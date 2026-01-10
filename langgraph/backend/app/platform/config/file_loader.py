"""File loading utilities for prompts and configs."""

from __future__ import annotations

import json
import os
from functools import cache
from pathlib import Path

import yaml  # type: ignore[import-untyped]

from app.platform.config.paths import AGENTS_DIR, APP_ROOT, CONFIG_DIR

class FileLoader:
    """Load prompts, configs, and schemas from the filesystem."""

    DEV_MODE = os.getenv("SAGECOMPASS_ENV", "prod").lower() == "dev"

    @staticmethod
    def _logger():
        from app.platform.contract.logging import get_logger

        return get_logger("utils.file_loader")

    @classmethod
    def _read_file(
        cls,
        file_path: str,
        mode: str = "r",
        loader=None,
        category: str = "file",
    ):
        """Read a file and optionally parse it via a loader.

        Args:
            file_path: Absolute path to the file.
            mode: File open mode.
            loader: Optional callable to parse the file handle.
            category: Log category for observability.

        Side effects/state writes:
            Performs filesystem reads and emits structured logs.

        Returns:
            Parsed data if successful, otherwise False.
        """
        logger = cls._logger()
        try:
            with open(file_path, mode, encoding="utf-8") as f:
                data = loader(f) if loader else f.read()
                if cls.DEV_MODE:
                    logger.info(f"{category}.load.success", path=file_path)
                return data
        except FileNotFoundError:
            logger.warning(f"{category}.load.missing", path=file_path)
        except PermissionError as exc:
            logger.error(f"{category}.load.denied", path=file_path, error=str(exc))
        except Exception as e:
            logger.error(f"{category}.load.error", path=file_path, error=str(e))

        return False

    # --- Generic helpers -------------------------------------------------

    @classmethod
    @cache
    def load_yaml(cls, relative_path: str, category: str = "config"):
        """Load a YAML file relative to APP_ROOT (app/).

        Example: load_yaml("agents/problem_framing/config.yaml")

        Returns:
            Parsed YAML data or False if missing/invalid.
        """
        file_path = os.path.join(APP_ROOT, relative_path)
        return cls._read_file(file_path, loader=yaml.safe_load, category=category)

    # --- Legacy prompt/schema loaders (still relative to app/agents) -----

    @classmethod
    @cache
    def load_prompt(cls, prompt_name: str, agent_name: str | None = None):
        """Load a .prompt file for a given agent.

        Prompt contracts:
        - `system.prompt` is required for every agent.
        - few-shots require `few-shots.prompt` + `examples.json` in the agent prompts folder.
        """
        if agent_name is None:
            file_path = os.path.join(AGENTS_DIR, f"{prompt_name}.prompt")
        else:
            file_path = os.path.join(AGENTS_DIR, agent_name, "prompts", f"{prompt_name}.prompt")
        return cls._read_file(file_path, category="prompt")

    @classmethod
    def resolve_agent_prompt_path(cls, prompt_name: str, agent_name: str) -> Path:
        """Resolve the path to an agent prompt and ensure it exists.

        Args:
            prompt_name: Prompt filename without extension.
            agent_name: Agent folder name.

        Returns:
            Path to the prompt file.
        """
        prompt_path = AGENTS_DIR / agent_name / "prompts" / f"{prompt_name}.prompt"
        if not prompt_path.exists():
            raise FileNotFoundError(prompt_path)
        return prompt_path

    @classmethod
    @cache
    def load_schema(cls, agent_name: str, schema_name: str):
        """Load a JSON schema file for an agent."""
        file_path = os.path.join(APP_ROOT, "agents", agent_name, f"{schema_name}.json")
        return cls._read_file(file_path, loader=json.load, category="schema")

    # --- Specialized shortcuts -------------------------------------------

    @classmethod
    @cache
    def load_agent_config(cls, agent_name: str):
        """Loads agents/<agent_name>/config.yaml from app/.

        Returns:
            Parsed YAML data or False if missing/invalid.
        """
        path = os.path.join(APP_ROOT, "agents", agent_name, "config.yaml")
        return cls._read_file(path, loader=yaml.safe_load, category="agent.config")

    @classmethod
    @cache
    def load_provider_config(cls, provider: str):
        """Loads config/provider/<provider>.yaml from the top-level config/ dir.

        This no longer assumes config lives under app/; it uses CONFIG_DIR.

        Returns:
            Parsed YAML data or False if missing/invalid.
        """
        category = "provider"
        provider_dir = CONFIG_DIR / category
        file_path = provider_dir / f"{provider}.yaml"
        return cls._read_file(str(file_path), loader=yaml.safe_load, category=category)

    @classmethod
    @cache
    def load_guardrails_config(cls):
        """Loads guardrails.yaml from the top-level config/ dir.

        Returns:
            Parsed YAML data or False if missing/invalid.
        """
        file_path = CONFIG_DIR / "guardrails.yaml"
        return cls._read_file(str(file_path), loader=yaml.safe_load, category="config")

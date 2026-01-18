"""File loading utilities for prompts and configs."""

from __future__ import annotations

import json
import os
from functools import cache
from pathlib import Path
from typing import Any

import yaml  # type: ignore[import-untyped]

from app.platform.config.paths import AGENTS_DIR, APP_ROOT, CONFIG_DIR, PROVIDER_CONFIG_DIR


class FileLoader:
    """Load prompts, configs, and schemas from the filesystem."""

    _dev_mode: bool | None = None

    @staticmethod
    def _logger():
        from app.platform.adapters.logging import get_logger

        return get_logger("utils.file_loader")

    @classmethod
    def _is_dev_mode(cls) -> bool:
        if cls._dev_mode is None:
            cls._dev_mode = os.getenv("SAGECOMPASS_ENV", "prod").lower() == "dev"
        return cls._dev_mode

    @classmethod
    def _read_text(cls, path: Path | str, category: str = "file") -> str:
        """Read text file.

        Raises:
            FileNotFoundError: File does not exist
            PermissionError: No permission to read file
            IOError: Other I/O errors
        """
        path = Path(path)
        logger = cls._logger()
        try:
            content = path.read_text(encoding="utf-8")
            if cls._is_dev_mode():
                logger.info(f"{category}.load.success", path=str(path))
            return content
        except FileNotFoundError:
            logger.warning(f"{category}.load.missing", path=str(path))
            raise
        except PermissionError as exc:
            logger.error(f"{category}.load.denied", path=str(path), error=str(exc))
            raise
        except Exception as e:
            logger.error(f"{category}.load.error", path=str(path), error=str(e))
            raise

    @classmethod
    def _read_yaml(cls, path: Path | str, category: str = "config") -> dict[str, Any]:
        """Read YAML file.

        Raises:
            FileNotFoundError: File does not exist
            yaml.YAMLError: Invalid YAML syntax
            PermissionError: No permission to read file
        """
        content = cls._read_text(path, category)
        return yaml.safe_load(content)

    @classmethod
    def _read_json(cls, path: Path | str, category: str = "schema") -> dict[str, Any] | list[Any]:
        """Read JSON file.

        Raises:
            FileNotFoundError: File does not exist
            json.JSONDecodeError: Invalid JSON syntax
            PermissionError: No permission to read file
        """
        content = cls._read_text(path, category)
        return json.loads(content)

    @classmethod
    def _auto_load(cls, path: Path | str, category: str = "file") -> str | dict[str, Any] | list[Any]:
        """Auto-detect file type by extension and load appropriately.

        Supported extensions:
        - .yaml, .yml -> YAML
        - .json -> JSON
        - .prompt, .txt, .md -> Text
        - Others -> Text (default)

        Raises:
            FileNotFoundError: File does not exist
            yaml.YAMLError: Invalid YAML (for .yaml files)
            json.JSONDecodeError: Invalid JSON (for .json files)
        """
        path = Path(path)
        ext = path.suffix.lower()

        if ext in (".yaml", ".yml"):
            return cls._read_yaml(path, category)
        elif ext == ".json":
            return cls._read_json(path, category)
        else:
            # Default to text for .prompt, .txt, .md, and unknown extensions
            return cls._read_text(path, category)

    # --- Generic helpers -------------------------------------------------

    @classmethod
    @cache
    def load_yaml(cls, relative_path: str, category: str = "config") -> dict[str, Any]:
        """Load a YAML file relative to APP_ROOT (app/).

        Example: load_yaml("agents/problem_framing/config.yaml")

        Raises:
            FileNotFoundError: File does not exist
            yaml.YAMLError: Invalid YAML syntax
        """
        file_path = APP_ROOT / relative_path
        return cls._read_yaml(file_path, category)

    # --- Legacy prompt/schema loaders (still relative to app/agents) -----

    @classmethod
    @cache
    def load_prompt(cls, prompt_name: str, agent_name: str | None = None) -> str:
        """Load a .prompt file for a given agent.

        Prompt contracts:
        - `system.prompt` is required for every agent.
        - few-shots require `few-shots.prompt` + `examples.json` in the agent prompts folder.

        Raises:
            FileNotFoundError: Prompt file does not exist
        """
        if agent_name is None:
            file_path = AGENTS_DIR / f"{prompt_name}.prompt"
        else:
            file_path = AGENTS_DIR / agent_name / "prompts" / f"{prompt_name}.prompt"
        return cls._read_text(file_path, category="prompt")

    @classmethod
    def resolve_agent_prompt_path(cls, prompt_name: str, agent_name: str) -> Path:
        """Resolve the path to an agent prompt and ensure it exists.

        Args:
            prompt_name: Prompt filename without extension.
            agent_name: Agent folder name.

        Returns:
            Path to the prompt file.

        Raises:
            FileNotFoundError: Prompt file does not exist
        """
        prompt_path = AGENTS_DIR / agent_name / "prompts" / f"{prompt_name}.prompt"
        if not prompt_path.exists():
            raise FileNotFoundError(prompt_path)
        return prompt_path

    @classmethod
    @cache
    def load_schema(cls, agent_name: str, schema_name: str) -> dict[str, Any] | list[Any]:
        """Load a JSON schema file for an agent.

        Raises:
            FileNotFoundError: Schema file does not exist
            json.JSONDecodeError: Invalid JSON syntax
        """
        file_path = APP_ROOT / "agents" / agent_name / f"{schema_name}.json"
        return cls._read_json(file_path, category="schema")

    # --- Specialized shortcuts -------------------------------------------

    @classmethod
    @cache
    def load_agent_config(cls, agent_name: str) -> dict[str, Any]:
        """Loads agents/<agent_name>/config.yaml from app/.

        Raises:
            FileNotFoundError: Config file does not exist
            yaml.YAMLError: Invalid YAML syntax
        """
        path = APP_ROOT / "agents" / agent_name / "config.yaml"
        return cls._read_yaml(path, category="agent.config")

    @classmethod
    @cache
    def load_provider_config(cls, provider: str) -> dict[str, Any]:
        """Loads config/provider/<provider>.yaml from the top-level config/ dir.

        This no longer assumes config lives under app/; it uses CONFIG_DIR.

        Raises:
            FileNotFoundError: Provider config does not exist
            yaml.YAMLError: Invalid YAML syntax
        """
        category = "provider"
        file_path = PROVIDER_CONFIG_DIR / f"{provider}.yaml"
        return cls._read_yaml(file_path, category=category)

    @classmethod
    @cache
    def load_guardrails_config(cls) -> dict[str, Any]:
        """Loads guardrails.yaml from the top-level config/ dir.

        Raises:
            FileNotFoundError: Guardrails config does not exist
            yaml.YAMLError: Invalid YAML syntax
        """
        file_path = CONFIG_DIR / "guardrails.yaml"
        return cls._read_yaml(file_path, category="config")

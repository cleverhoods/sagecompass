# app/utils/file_loader.py
from __future__ import annotations

import os, json, yaml
from functools import lru_cache
from pathlib import Path

from app.utils.logger import get_logger
from app.utils.paths import APP_ROOT, AGENTS_DIR, CONFIG_DIR


class FileLoader:
    DEV_MODE = os.getenv("SAGECOMPASS_ENV", "prod").lower() == "dev"

    @staticmethod
    def _logger():
        return get_logger("utils.file_loader")

    @classmethod
    def _read_file(
        cls,
        file_path: str,
        mode: str = "r",
        loader=None,
        category: str = "file",
    ):
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
    @lru_cache(maxsize=None)
    def load_yaml(cls, relative_path: str, category: str = "config"):
        """
        Load a YAML file relative to APP_ROOT (app/).

        Example: load_yaml("agents/problem_framing/config.yaml")
        """
        file_path = os.path.join(APP_ROOT, relative_path)
        return cls._read_file(file_path, loader=yaml.safe_load, category=category)

    # --- Legacy prompt/schema loaders (still relative to app/agents) -----

    @classmethod
    @lru_cache(maxsize=None)
    def load_prompt(cls, prompt_name: str, agent_name: str | None = None):
        """Loads a specific .prompt file for a given agent (legacy)."""
        if agent_name is None:
            file_path = os.path.join(
                AGENTS_DIR, f"{prompt_name}.prompt"
            )
        else:
            file_path = os.path.join(
                AGENTS_DIR, agent_name, "prompts", f"{prompt_name}.prompt"
            )
        return cls._read_file(file_path, category="prompt")

    @classmethod
    def resolve_agent_prompt_path(cls, prompt_name: str, agent_name: str) -> Path:
        """Resolve the path to an agent prompt and ensure it exists."""

        prompt_path = AGENTS_DIR / agent_name / "prompts" / f"{prompt_name}.prompt"
        if not prompt_path.exists():
            raise FileNotFoundError(prompt_path)
        return prompt_path

    @classmethod
    @lru_cache(maxsize=None)
    def load_schema(cls, agent_name: str, schema_name: str):
        file_path = os.path.join(
            APP_ROOT, "agents", agent_name, f"{schema_name}.json"
        )
        return cls._read_file(file_path, loader=json.load, category="schema")

    # --- Specialized shortcuts -------------------------------------------

    @classmethod
    @lru_cache(maxsize=None)
    def load_agent_config(cls, agent_name: str):
        """
        Loads agents/<agent_name>/config.yaml from app/.
        """
        path = os.path.join(APP_ROOT, "agents", agent_name, "config.yaml")
        return cls._read_file(path, loader=yaml.safe_load, category="agent.config")

    @classmethod
    @lru_cache(maxsize=None)
    def load_provider_config(cls, provider: str):
        """
        Loads config/provider/<provider>.yaml from the top-level config/ dir.

        This no longer assumes config lives under app/; it uses CONFIG_DIR.
        """
        category = "provider"
        provider_dir = CONFIG_DIR / category
        file_path = provider_dir / f"{provider}.yaml"
        return cls._read_file(
            str(file_path), loader=yaml.safe_load, category=category
        )

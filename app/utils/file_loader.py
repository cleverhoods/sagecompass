# app/utils/file_loader.py
import os, json, yaml
from functools import lru_cache
from app.utils.logger import log


class FileLoader:
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    DEV_MODE = os.getenv("SAGECOMPASS_ENV", "prod").lower() == "dev"

    @classmethod
    def _read_file(cls, file_path: str, mode: str = "r", loader=None, category: str = "file"):
        try:
            with open(file_path, mode, encoding="utf-8") as f:
                data = loader(f) if loader else f.read()
                if cls.DEV_MODE:
                    log(f"{category}.load.success", {"path": file_path})
                return data
        except FileNotFoundError:
            log(f"{category}.load.missing", {"path": file_path})
        except PermissionError:
            log(f"{category}.load.denied", {"path": file_path})
        except Exception as e:
            log(f"{category}.load.error", {"path": file_path, "error": str(e)})

        log(f"{category}.load.error", {"path": file_path, "error": "unknown error"})
        return False

    @classmethod
    @lru_cache(maxsize=None)
    def load_yaml(cls, relative_path: str, category: str = "config"):
        full_path = os.path.join(cls.BASE_DIR, relative_path)
        return cls._read_file(full_path, loader=yaml.safe_load, category=category)

    @classmethod
    @lru_cache(maxsize=None)
    def load_prompt(cls, name: str):
        file_path = os.path.join(cls.BASE_DIR, "prompts", f"{name}.prompt")
        return cls._read_file(file_path, category="prompt")

    @classmethod
    @lru_cache(maxsize=None)
    def load_schema(cls, name: str):
        file_path = os.path.join(cls.BASE_DIR, "schemas", f"{name}.json")
        return cls._read_file(file_path, loader=json.load, category="schema")

    # --- Specialized shortcuts ---
    @classmethod
    @lru_cache(maxsize=None)
    def load_agent_config(cls, agent_name: str):
        category = "agent"
        return cls.load_yaml(f"config/{category}/{agent_name}.yaml", category=category)

    @classmethod
    @lru_cache(maxsize=None)
    def load_provider_config(cls, provider: str):
        category = "provider"
        return cls.load_yaml(f"config/{category}/{provider}.yaml", category=category)
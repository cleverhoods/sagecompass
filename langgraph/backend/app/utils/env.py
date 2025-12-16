from __future__ import annotations

from pathlib import Path

from dotenv import load_dotenv

from app.utils.paths import BACKEND_ROOT
from app.utils.logger import log

_ENV_LOADED = False


def load_project_env() -> None:
    """
    Load environment variables from the backend .env file exactly once.

    Safe to call from:
    - `uv run langgraph dev` (no-op if already loaded by LangGraph)
    - `uv run python -m app.main`
    - tests
    """
    global _ENV_LOADED
    if _ENV_LOADED:
        return

    env_path: Path = BACKEND_ROOT / ".env"

    try:
        if not env_path.exists():
            log(
                "env.load.missing",
                {"path": str(env_path)},
            )
        else:
            loaded = load_dotenv(dotenv_path=env_path)
            if not loaded:
                # File existed but dotenv did not load anything
                log(
                    "env.load.warning",
                    {"path": str(env_path), "reason": "no variables loaded"},
                )
            else:
                log(
                    "env.load.success",
                    {"path": str(env_path)},
                )
    except PermissionError as e:
        log(
            "env.load.permission_error",
            {"path": str(env_path), "error": str(e)},
        )
    except Exception as e:
        # Catch-all for weird FS or dotenv errors
        log(
            "env.load.error",
            {"path": str(env_path), "error": str(e)},
        )
    finally:
        # Mark as done so we don't keep re-checking on every import
        _ENV_LOADED = True

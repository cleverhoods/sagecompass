"""Environment loading utilities."""

from __future__ import annotations

from pathlib import Path

from dotenv import load_dotenv

from app.platform.config.paths import BACKEND_ROOT
_ENV_LOADED = False


def load_project_env() -> None:
    """Load environment variables from the backend .env file exactly once.

    Safe to call from:
    - `uv run langgraph dev` (no-op if already loaded by LangGraph)
    - `uv run python -m app.main`
    - tests
    """
    global _ENV_LOADED
    if _ENV_LOADED:
        return

    env_path: Path = BACKEND_ROOT / ".env"

    from app.platform.contract.logging import get_logger

    logger = get_logger("utils.env")
    try:
        if not env_path.exists():
            logger.warning("env.load.missing", path=str(env_path))
        else:
            loaded = load_dotenv(dotenv_path=env_path)
            if not loaded:
                # File existed but dotenv did not load anything
                logger.warning(
                    "env.load.warning",
                    path=str(env_path),
                    reason="no variables loaded",
                )
            else:
                logger.info("env.load.success", path=str(env_path))
    except PermissionError as e:
        logger.error("env.load.permission_error", path=str(env_path), error=str(e))
    except Exception as e:
        # Catch-all for weird FS or dotenv errors
        logger.error("env.load.error", path=str(env_path), error=str(e))
    finally:
        # Mark as done so we don't keep re-checking on every import
        _ENV_LOADED = True

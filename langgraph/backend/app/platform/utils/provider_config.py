"""Provider configuration loader for model factories."""

import importlib
import os

from app.platform.config.env import load_project_env
from app.platform.config.file_loader import FileLoader
from app.platform.observability.logger import get_logger
from app.platform.config.paths import CONFIG_DIR

PROVIDER_CONFIG_DIR = CONFIG_DIR / "provider"


class ProviderFactory:
    """Instantiate an LLM provider for a given agent.

    Sources:
        - agent.yaml (specific overrides)
        - config/provider/{provider}.yaml (global defaults)
    """

    @staticmethod
    def for_agent(agent_name: str | None = None):
        """Instantiate a provider model for an agent using config + env.

        Args:
            agent_name: Optional agent name for per-agent overrides.

        Side effects/state writes:
            Loads environment variables and reads provider config files.

        Returns:
            Tuple of (provider instance, merged params).
        """
        logger = get_logger("utils.provider_config")
        try:
            load_project_env()
            # --- Load configurations ---
            agent_cfg = {} if agent_name is None else FileLoader.load_agent_config(agent_name) or {}

            provider_name_value = agent_cfg.get("provider") or os.getenv(
                "DEFAULT_PROVIDER",
                "openai",
            )
            provider_name = str(provider_name_value).lower()
            prov_cfg = FileLoader.load_provider_config(provider_name)
            if not prov_cfg:
                raise FileNotFoundError(f"Provider config missing for '{provider_name}'")

            logger.info("provider.load.start", agent=agent_name, provider=provider_name)

            # --- Merge parameters (provider.defaults <- agent.yaml) ---
            provider_defaults = prov_cfg.get("defaults", {}) or {}
            agent_params = agent_cfg.get("params", {})

            params = {**provider_defaults, **agent_params}

            # --- Required provider keys ---
            for key in ("module", "class", "key_env"):
                if key not in prov_cfg:
                    raise KeyError(f"Missing '{key}' in provider config '{provider_name}'")

            # --- Resolve API key ---
            api_key = os.getenv(prov_cfg["key_env"])
            if not api_key:
                raise OSError(f"Missing environment variable: {prov_cfg['key_env']}")

            # --- Dynamic import and instantiation ---
            module = importlib.import_module(prov_cfg["module"])
            provider_class = getattr(module, prov_cfg["class"])

            # Detect constructor signature for LangChain v1 providers
            # ChatOpenAI → api_key=..., model=..., temperature=...
            instance = provider_class(api_key=api_key, **params)

            logger.info(
                "provider.load.success",
                agent=agent_name,
                provider=provider_name,
                params=list(params.keys()),
            )

            return instance, params

        except Exception as e:
            logger.error("provider.load.error", agent=agent_name, error=str(e))
            raise

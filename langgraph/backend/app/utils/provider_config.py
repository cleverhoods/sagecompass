import importlib
import os

from app.utils.file_loader import FileLoader
from app.utils.env import load_project_env
from app.utils.logger import get_logger
from app.utils.paths import CONFIG_DIR

PROVIDER_CONFIG_DIR = CONFIG_DIR / "provider"


class ProviderFactory:
    """
    Instantiates an LLM provider for a given agent based on:
      - agent.yaml (specific overrides)
      - config/provider/{provider}.yaml (global defaults)
    Supports any provider module in LangChain ecosystem.
    """

    @staticmethod
    def for_agent(agent_name: str = None):
        logger = get_logger("utils.provider_config")
        try:
            load_project_env()
            # --- Load configurations ---
            if agent_name is None:
                agent_cfg = {}
            else:
                agent_cfg = FileLoader.load_agent_config(agent_name) or {}

            provider_name = (agent_cfg.get("provider") or os.getenv("DEFAULT_PROVIDER", "openai")).lower()
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
                raise EnvironmentError(f"Missing environment variable: {prov_cfg['key_env']}")

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

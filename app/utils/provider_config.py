import os, importlib
from app.utils.file_loader import FileLoader
from app.utils.logger import log


class ProviderFactory:
    """
    Loads provider and agent configurations,
    merges parameters, validates environment,
    and returns an instantiated provider client.
    """

    @staticmethod
    def for_agent(agent_name: str):
        try:
            # --- Load agent config ---
            agent_cfg = FileLoader.load_agent_config(agent_name)
            provider_name = (agent_cfg.get("provider") or os.getenv("DEFAULT_PROVIDER", "openai")).lower()
            log("provider.load.start", {"agent": agent_name, "provider": provider_name})

            # --- Load provider config ---
            prov_cfg = FileLoader.load_provider_config(provider_name)
            if not prov_cfg:
                raise FileNotFoundError(f"Provider config missing for '{provider_name}'")

            # --- Merge params (provider.defaults ← agent.params) ---
            provider_defaults = prov_cfg.get("defaults", {}) or {}
            agent_overrides = agent_cfg.get("params", {}) or {}
            params = {**provider_defaults, **agent_overrides}

            # --- Validate required provider keys ---
            for key in ("module", "class", "key_env"):
                if key not in prov_cfg:
                    raise KeyError(f"Missing '{key}' in provider config '{provider_name}'")

            # --- Resolve API key ---
            api_key = os.getenv(prov_cfg["key_env"])
            if not api_key:
                raise EnvironmentError(f"Missing environment variable: {prov_cfg['key_env']}")

            # --- Dynamic import and instantiation ---
            module = importlib.import_module(prov_cfg["module"])
            cls = getattr(module, prov_cfg["class"])
            llm_instance = cls(api_key=api_key, **params)

            log("provider.load.success", {
                "agent": agent_name,
                "provider": provider_name,
                "params": list(params.keys())
            })

            return llm_instance, params

        except Exception as e:
            log("provider.load.error", {"agent": agent_name, "error": str(e)})
            raise

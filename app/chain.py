import os, importlib
from pathlib import Path
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableSequence

from utils.config_loader import load_config
from utils.prompt_loader import load_prompts


class SageCompass:
    """Encapsulates the LLM logic and system initialization."""

    def __init__(self):
        base = Path(__file__).resolve().parent
        load_dotenv(dotenv_path=base.parent / ".env")

        # --- Load configuration and prompts ---
        self.config = load_config(base / "config")
        self.prompts = load_prompts(base / "prompts")

        # Active provider
        llm_cfg = self.config.get("llm", {})
        provider_name = llm_cfg.get("active_provider")
        if not provider_name:
            raise ValueError("Missing 'active_provider' in llm.yaml")

        self.provider_cfg = load_config(base / "providers").get(provider_name, {})
        self._validate_config(llm_cfg)

        # --- Initialize LLM and chain ---
        self.llm = self._init_llm(llm_cfg)
        self.chain = self._init_chain()

    # ---------------- Internal methods ---------------- #

    def _validate_config(self, llm_cfg):
        key_name = self.provider_cfg.get("key_env")
        if not key_name or not os.getenv(key_name):
            raise EnvironmentError(f"Missing environment variable: {key_name}")
        if not llm_cfg.get("model"):
            raise ValueError("Model name missing from llm.yaml")

    def _init_llm(self, llm_cfg):
        """Dynamically load the provider module and initialize the LLM."""
        module = importlib.import_module(self.provider_cfg["module"])
        cls = getattr(module, self.provider_cfg["class"])
        api_key = os.getenv(self.provider_cfg["key_env"])

        return cls(
            model=llm_cfg["model"],
            temperature=llm_cfg.get("temperature", 0.2),
            max_tokens=llm_cfg.get("max_tokens", 1000),
            api_key=api_key
        )

    def _init_chain(self):
        """Initialize the reasoning chain using loaded prompts."""
        system_msg = self.prompts.get("system", "You are SageCompass, an ML strategy advisor.")
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_msg),
            ("human", "{question}")
        ])
        return RunnableSequence(prompt | self.llm)

    # ---------------- Public interface ---------------- #

    def ask(self, question: str) -> str:
        """Entry point for UI or CLI."""
        result = self.chain.invoke({"question": question})
        print(result)
        return result.content if hasattr(result, "content") else str(result)

# app/agents/base.py
import os, json, time
from typing import Any, Dict, Optional
from app.utils.config_loader import load_llm_config, load_provider_config
from app.utils.prompt_loader import load_prompt
from app.agents.llm_client import LLMClient  # assume existing
from app.utils.event_logger import log_event
from app.utils.validation import ValidationService

from abc import ABC, abstractmethod

class BaseAgent(ABC):
    """
     Abstract base class for all SageCompass agents.
     Provides:
           - PRAL cycle (Perceive > Reason > Act > Learn) (See README.md)
           - Default system prompt loading
           - Validation and event logging
    """

    stage: str = "global"
    name: str = "base"
    version: str = "1.0"

    def __init__(self, prompt_file: str, schema_file: Optional[str] = None):
        # --- Load config ---
        llm_cfg = load_llm_config()
        prv = load_provider_config(llm_cfg["provider"])
        api_key = os.getenv(prv.get("api_key_env", "OPENAI_API_KEY"), "")

        self.client = LLMClient(
            api_base=prv["api_base"],
            api_key=api_key,
            model=llm_cfg["model"],
            timeout=prv.get("timeout", 60),
            temperature=llm_cfg.get("temperature", 0.2),
            max_tokens=llm_cfg.get("max_tokens", 800),
        )

        # --- Load services ---
        self.validator = ValidationService()

        # --- Compose prompt ---
        system_prompt = load_prompt("system")
        agent_prompt = load_prompt(prompt_file)
        self.system_prompt = f"{system_prompt}\n\n{agent_prompt}"
        self.schema_file = schema_file

    # ---------- PRAL CYCLE ----------
    @abstractmethod
    def perceive(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Collects user input and context into a structured perception."""
        perception = {"input": user_input, "context": context or {}, "timestamp": time.time()}
        log_event("perceive", perception, agent=self.name, stage=self.stage, version=self.version)
        return perception

    @abstractmethod
    def reason(self, perception: Dict[str, Any]) -> str:
        """Plan reasoning or prepare LLM message."""
        plan = f"Input:\n{perception['input']}\n\nReturn JSON per schema."
        log_event("reason", {"plan": plan}, agent=self.name, stage=self.stage, version=self.version)
        return plan

    @abstractmethod
    def act(self, plan: str) -> str:
        """Execute the LLM call or tool use."""
        log_event("act.start", {"plan": plan}, agent=self.name, stage=self.stage, version=self.version)
        output = self.client.chat(self.system_prompt, plan)
        log_event("act.complete", {"raw_output": output}, agent=self.name, stage=self.stage, version=self.version)
        return output

    @abstractmethod
    def learn(self, raw_output: str) -> Dict[str, Any]:
        """Validate, repair, and finalize output."""
        start, end = raw_output.find("{"), raw_output.rfind("}")
        if start != -1 and end != -1:
            raw_output = raw_output[start:end + 1]

        try:
            result = json.loads(raw_output)

            if self.schema_file:
                result["_schema_valid"] = self.validator.validate(result, self.schema_file, agent=self.name)(result, self.schema_file, agent=self.name)
            else:
                log_event("learn.warning.no_schema", {"agent": self.name}, agent=self.name, stage=self.stage, version=self.version)

            if result.get("_schema_valid"):
                log_event("learn.success", {"keys": list(result.keys())}, agent=self.name, stage=self.stage, version=self.version)
            else:
                log_event("learn.partial", {"reason": "schema failed"}, agent=self.name, stage=self.stage, version=self.version)

            return result

        except json.JSONDecodeError:
            error = {"error": "Invalid JSON", "raw_output": raw_output}
            log_event("learn.failure", error, agent=self.name, stage=self.stage, version=self.version)
            return error
        except Exception as e:
            error = {"error": str(e), "raw_output": raw_output}
            log_event("learn.exception", error, agent=self.name, stage=self.stage, version=self.version)
            return error

    # ---------- PRAL orchestration ----------
    def run(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Unified entry point running the full PRAL loop."""
        perception = self.perceive(user_input, context)
        plan = self.reason(perception)
        raw_output = self.act(plan)
        return self.learn(raw_output)


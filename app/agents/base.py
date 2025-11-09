# app/agents/base.py
import os, json, time
from typing import Any, Dict, Optional
from app.utils.file_loader import FileLoader
from app.utils.llm_config import ProviderFactory
from app.utils.logger import log
from app.utils.validation import ValidationService

from abc import ABC, abstractmethod

class BaseAgent(ABC):
    """
     Abstract base class for all SageCompass agents.
     Provides:
           - PRAL cycle stubs
           - Default system prompt loading
           - Validation and event logging
    """

    stage: str = "global"
    name: Optional[str] = None
    version: Optional[str] = None


    def __init__(self, agent_name: str):
        self.name = agent_name

        # --- Load config ---
        try:
            self.config = FileLoader.load_agent_config(agent_name)
        except FileNotFoundError as e:
            log("agent.config.missing", {"agent": agent_name, "error": str(e)})
            raise RuntimeError(f"Missing configuration for agent '{agent_name}'") from e

        # --- Version (YAML overrides class default) ---
        if "version" in self.config:
            self.version = self.config["version"]

        # --- Load prompt ---
        try:
            self.prompt = FileLoader.load_prompt(agent_name)
        except FileNotFoundError as e:
            log("agent.prompt.missing", {"agent": agent_name, "error": str(e)})
            raise RuntimeError(f"Missing prompt for agent '{agent_name}'") from e

        # --- Load schema ---
        try:
            self.schema = FileLoader.load_schema(agent_name)
        except FileNotFoundError as e:
            log("agent.schema.missing", {"agent": agent_name, "error": str(e)})
            raise RuntimeError(f"Missing schema for agent '{agent_name}'") from e

        # --- Initialize provider (LLM) ---
        self.llm, self.llm_params = ProviderFactory.for_agent(agent_name)

        # --- Utilities ---
        self.validator = ValidationService()

        # --- Load system prompt (critical) ---
        try:
            system_prompt = FileLoader.load_prompt("system")
            if not system_prompt:
                raise ValueError("system.prompt is empty")
        except Exception as e:
            log("prompt.system.error", {"agent": agent_name, "error": str(e)})
            raise RuntimeError("Critical: system.prompt missing or unreadable") from e

        # --- Compose combined system prompt ---
        self.system_prompt = f"{system_prompt}\n\n{self.prompt}"

    # ---------- PRAL stubs ----------

    @abstractmethod
    def perceive(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Collects user input and context into a structured perception."""
        perception = {
            "input": user_input,
            "context": context or {},
            "timestamp": time.time(),
        }
        log("agent.perceive", perception, agent=self.name, stage=self.stage, version=self.version)
        return perception

    @abstractmethod
    def reason(self, perception: Dict[str, Any]) -> str:
        """Plan reasoning or prepare LLM message."""
        plan = f"Input:\n{perception['input']}\n\nReturn JSON per schema."
        log("agent.reason", {"plan": plan}, agent=self.name, stage=self.stage, version=self.version)
        return plan

    @abstractmethod
    def act(self, plan: str) -> str:
        """Execute the reasoning step using the LLM provider."""
        log("agent.act.start", {"plan_preview": plan[:120]}, agent=self.name, stage=self.stage, version=self.version)
        try:
            output = self.llm.invoke(plan)
            log("agent.act.complete", {"output_preview": str(output)[:200]}, agent=self.name, stage=self.stage, version=self.version)
            return output
        except Exception as e:
            log("agent.act.error", {"error": str(e)}, agent=self.name, stage=self.stage, version=self.version)
            raise

    @abstractmethod
    def learn(self, raw_output: str) -> Dict[str, Any]:
        """Validate, repair, and finalize output."""
        start, end = raw_output.find("{"), raw_output.rfind("}")
        candidate = raw_output[start:end + 1] if start != -1 and end != -1 else raw_output

        try:
            result = json.loads(candidate)
        except json.JSONDecodeError:
            error = {"error": "Invalid JSON", "raw_output": raw_output}
            log("agent.learn.decode_error", error, agent=self.name, stage=self.stage, version=self.version)
            return error

        try:
            valid = self.validator.validate(result, self.schema, agent=self.name)
            result["_schema_valid"] = valid
            level = "success" if valid else "schema_failed"
            log(f"agent.learn.{level}", {"keys": list(result.keys())}, agent=self.name, stage=self.stage, version=self.version)
            return result
        except Exception as e:
            error = {"error": str(e), "raw_output": raw_output}
            log("agent.learn.exception", error, agent=self.name, stage=self.stage, version=self.version)
            return error

    # ---------- PRAL orchestration ----------
    def run(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Unified entry point running the full PRAL loop."""
        perception = self.perceive(user_input, context)
        plan = self.reason(perception)
        raw_output = self.act(plan)
        return self.learn(raw_output)

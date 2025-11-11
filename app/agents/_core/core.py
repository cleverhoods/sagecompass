# Agent abstract.
import json, time
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from langchain_core.prompts import ChatPromptTemplate  # missing import
from app.utils.agent_loader import AgentLoader
from app.utils.provider_config import ProviderFactory
from app.utils.logger import log
from app.utils.validation import ValidationService

class CoreAgent(ABC):
    """
     Abstract base class for all SageCompass agents.
     Provides PRAL cycle stubs:
       - Perceive - context gathering (collect user input + environment)
       - Reason - prompt loading and reasoning plan creation
       - Act - LLM execution / task fulfillment
       - Learn - output validation and schema alignment
    """

    name: Optional[str] = None
    version: Optional[str] = None

    def __init__(self, agent_name: str):
        agent_data = AgentLoader.load_agent(agent_name)
        if not agent_data:
            raise RuntimeError(f"Failed to load agent: {agent_name}")

        self.name = agent_data["name"]
        self.config = agent_data["config"]
        self.schema = agent_data["schema"]
        self.prompt = agent_data["agent_system_prompt"]
        self.system_prompt = agent_data["core_system_prompt"]

        # --- Utilities ---
        self.validator = ValidationService()

        # --- Initialize provider (LLM) ---
        self.llm, self.llm_params = ProviderFactory.for_agent(self.name)


    # --- Lifecycle dispatcher (dynamic hooks) ---
    def _run_stage(self, stage: str, func, *args, **kwargs):
        """Executes one PRAL stage with before/after hooks."""
        before = getattr(self, f"_before_{stage}", None)
        after = getattr(self, f"_after_{stage}", None)

        if callable(before):
            before(*args, **kwargs)

        result = func(*args, **kwargs)

        if callable(after):
            after(result)

        return result

    # --- Defaults used by PRAL stubs ---
    @abstractmethod
    def _implement_perceive(self, user_input, context=None) -> Dict[str, Any]:
        pass

    @abstractmethod
    def _implement_reason(self, perception: Dict[str, Any]) -> str:
        pass

    @abstractmethod
    def _implement_act(self, plan: str) -> str:
        pass

    @abstractmethod
    def _implement_learn(self, raw_output: str) -> Dict[str, Any]:
        pass

    # --- PRAL (enforced), each routed via _run_stage ---
    def perceive(self, user_input, context=None):
        return self._run_stage("perceive", self._implement_perceive, user_input, context)

    def reason(self, perception):
        return self._run_stage("reason", self._implement_reason, perception)

    def act(self, plan):
        return self._run_stage("act", self._implement_act, plan)

    def learn(self, raw_output):
        return self._run_stage("learn", self._implement_learn, raw_output)

    # --- Orchestration ---
    def run(self, user_input, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        p = self.perceive(user_input, context)
        r = self.reason(p)
        a = self.act(r)
        return self.learn(a)

    def build_prompt(self, user_input: str, last_ai_output: str = ""):
        """Always prepends the global system prompt before the agent prompt."""
        return ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("system", self.prompt),
            ("human", user_input),
            ("ai", last_ai_output or "")
        ])

    # --- Helpers ---
    def _normalize_output(self, raw_output: str) -> Dict[str, Any]:
        if not raw_output:
            return {"error": "empty_output"}
        s, e = raw_output.find("{"), raw_output.rfind("}")
        snippet = raw_output[s:e+1] if s != -1 and e != -1 else raw_output
        try:
            return json.loads(snippet)
        except Exception:
            return {"error": "invalid_json", "raw_output": raw_output}

    def _validate(self, result, schema):
        """Run ValidationService on the result dict using the agent's schema."""
        valid = False
        try:
            valid = self.validator.validate(result, schema, agent=self.name)
            log("validation.success", {"agent": self.name})
        except Exception as e:
            log("validation.error", {"agent": self.name, "error": str(e)}, level="error")
            result["_validation_error"] = str(e)
        result["_schema_valid"] = bool(valid)
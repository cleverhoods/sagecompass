from app.agents._core.core import CoreAgent
from app.utils.logger import log
import time


class ProblemFramingAgent(CoreAgent):
    """Transforms vague user queries into structured, actionable problem statements."""

    def _implement_perceive(self, user_input: str, context=None):
        """Collect user input and enrich perception if needed."""
        perception = {
            "input": user_input,
            "context": context or {},
            "timestamp": time.time(),
            "agent": self.name,
        }
        log("agent.perceive", {"agent": self.name, "input_preview": user_input[:100]})
        return perception

    def _implement_reason(self, perception):
        """Build the reasoning plan (prompt + variables) for LLM execution."""
        user_input = perception.get("input", "")
        prompt = self.build_prompt(user_input)
        plan = {"prompt": prompt, "vars": {"user_input": user_input}}
        log("agent.reason.plan", {"agent": self.name, "has_prompt": bool(prompt)})
        return plan

    def _implement_act(self, plan):
        """Execute the reasoning plan via the LLM provider."""
        chain = plan["prompt"] | self.llm
        raw_output = chain.invoke(plan["vars"])
        log("agent.act", {"agent": self.name})
        return raw_output

    def _implement_learn(self, raw_output):
        """Normalize, validate against this agent's schema, set status."""
        # LangChain may return an AIMessage; extract text safely.
        text = raw_output.content if hasattr(raw_output, "content") else str(raw_output)
        result = self._normalize_output(text)
        try:
            self._validate(result, self.schema)
        except Exception as e:
            result["_schema_valid"] = False
            result["_validation_error"] = str(e)
        result["status"] = "ok" if result.get("_schema_valid") else "invalid_output"
        return result

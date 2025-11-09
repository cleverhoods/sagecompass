# app/agents/problem_framing.py
from app.agents.base import BaseAgent
from app.utils.logger import log


class ProblemFramingAgent(BaseAgent):
    """Agent responsible for reframing user questions into solvable problem statements."""

    stage = "1"

    def __init__(self):
        super().__init__("problem_framing")

    # ---------- PRAL methods ----------

    def perceive(self, user_input: str, context=None):
        """Collect and structure the input + context."""
        perception = super().perceive(user_input, context)
        # you can enrich perception here later if needed
        return perception

    def reason(self, perception):
        """Define reasoning plan — what the LLM should do."""
        plan = (
            f"Reframe the following question into a clear, actionable problem statement.\n\n"
            f"User input:\n{perception['input']}\n\n"
            f"Return JSON matching the schema."
        )
        log("agent.reason.plan", {"agent": self.name, "plan": plan[:200]})
        return plan

    def act(self, plan):
        """Execute reasoning via provider LLM."""
        log("agent.act.start", {"agent": self.name})
        output = self.llm.invoke(plan)
        log("agent.act.complete", {"agent": self.name, "output_preview": str(output)[:200]})
        return output

    def learn(self, raw_output):
        """Validate and finalize the result."""
        return super().learn(raw_output)

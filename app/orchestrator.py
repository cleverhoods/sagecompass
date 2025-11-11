from app.agents.problem_framing.agent import ProblemFramingAgent
from app.utils.logger import log
from app.utils.validation import ValidationService

class SageCompass:
    """Sequential multi-agent orchestrator (Phase 4)."""

    def __init__(self, pipeline=None):
        self.pipeline = pipeline or ["problem_framing"]   # extend later
        self.state = {"context": {}, "trace": []}
        self.validator = ValidationService()
        self.agents = self._load_agents(self.pipeline)

    def _load_agents(self, names):
        """Instantiate each agent in the pipeline."""
        mapping = {
            "problem_framing": ProblemFramingAgent,
            # "cost_model": CostModelAgent,
            # "data_readiness": DataReadinessAgent,
        }
        return [mapping[n](n) for n in names if n in mapping]

    def ask(self, question: str, context=None):
        """Run the full PRAL pipeline sequentially."""
        input_data = question
        self.state["context"] = context or {}

        for agent in self.agents:
            log("orchestrator.stage.start", {"agent": agent.name})
            result = agent.run(input_data, self.state)

            # store
            self.state[agent.name] = result
            self.state["trace"].append({"agent": agent.name, "result": result})

            # validate schema
            try:
                valid = self.validator.validate(result, agent.schema, agent=agent.name)
                if not valid:
                    raise ValueError(f"{agent.name} produced invalid output")
            except Exception as e:
                log("orchestrator.validation.error",
                    {"agent": agent.name, "error": str(e)}, level="error")
                break

            # prepare input for next agent
            input_data = result

        log("orchestrator.pipeline.complete", {"agents": self.pipeline})
        return self.state

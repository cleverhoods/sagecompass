# app/agents/problem_framing.py
from app.agents.base import BaseAgent

class ProblemFramingAgent(BaseAgent):
    stage = "1"
    name = "problem_framing"

    def __init__(self):
        super().__init__(
            prompt_file="problem_framing",
            schema_file="problem_framing.json"
        )

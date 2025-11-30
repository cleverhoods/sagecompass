from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Generic, TypeVar, Type, Any, Dict, List

import json
from pydantic import BaseModel
from langchain_core.messages import SystemMessage, HumanMessage

from app.utils.provider_config import ProviderFactory
from app.utils.logger import log


T = TypeVar("T", bound=BaseModel)

# global_system.prompt is next to this file: app/agents/global_system.prompt
GLOBAL_PROMPT_PATH = Path(__file__).resolve().parent / "global_system.prompt"


@dataclass
class LLMAgent(Generic[T]):
    """
    Thin wrapper around an LLM for a specific agent.

    - Loads provider via ProviderFactory.for_agent(self.name)
    - Loads:
      - global_system.prompt (shared for all agents)
      - agent-specific system.prompt from self.prompt_path
    - Uses OpenAI structured output via llm.with_structured_output(self.output_model)
    - Accepts a structured payload dict and turns it into messages:
      [global system, agent system, human(JSON payload)]
    """

    name: str
    output_model: Type[T]
    prompt_path: Path

    llm: Any = field(init=False)
    llm_params: dict[str, Any] = field(init=False, default_factory=dict)

    global_system_prompt: str = field(init=False)
    agent_system_prompt: str = field(init=False)

    def __post_init__(self) -> None:
        # Each agent gets its own configured LLM instance.
        instance, params = ProviderFactory.for_agent(self.name)
        self.llm = instance
        self.llm_params = params

        self.global_system_prompt = self._load_global_system_prompt()
        self.agent_system_prompt = self._load_agent_system_prompt()

    # --- Prompt loading -------------------------------------------------------

    @staticmethod
    def _load_global_system_prompt() -> str:
        try:
            with open(GLOBAL_PROMPT_PATH, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            log(
                "agent.global_prompt.missing",
                {"path": str(GLOBAL_PROMPT_PATH)},
            )
            raise

    def _load_agent_system_prompt(self) -> str:
        """
        Load the system.prompt template for this agent.
        """
        try:
            with open(self.prompt_path, "r", encoding="utf-8") as f:
                template_text = f.read()
            return template_text
        except FileNotFoundError:
            log(
                "agent.prompt.missing",
                {"agent": self.name, "path": str(self.prompt_path)},
            )
            raise

    # --- Message construction --------------------------------------------------

    def build_messages(self, payload: Dict[str, Any]) -> List[SystemMessage | HumanMessage]:
        """
        Construct the message list for this agent:

        1) Global system instructions (shared across all agents)
        2) Agent-specific system instructions (with {format_instructions} placeholder)
        3) Human message containing the JSON payload derived from PipelineState
        """
        # For now we leave {format_instructions} in the agent prompt but pass an
        # empty string, because structured_output already injects the schema.
        agent_system_text = self.agent_system_prompt.format(format_instructions="")

        # Optional debug
        log(
            "agent.build_messages",
            {
                "agent": self.name,
                "payload_keys": list(payload.keys()),
            },
        )

        return [
            SystemMessage(content=self.global_system_prompt),
            SystemMessage(content=agent_system_text),
            HumanMessage(content=json.dumps(payload, ensure_ascii=False)),
        ]

    # --- Main execution -------------------------------------------------------

    def run_with_payload(self, payload: Dict[str, Any]) -> T:
        """
        Execute the agent with a structured payload dict.

        Typical payload structure (decided by each agent), e.g.:
        {
            "original_input": "...",
            "problem_frame": {...},
            "retrieved_context": "..."
        }
        """
        messages = self.build_messages(payload)

        # Structured output directly to the Pydantic model (no manual parser).
        structured_llm = self.llm.with_structured_output(self.output_model)

        try:
            result: T = structured_llm.invoke(messages)
            return result
        except Exception as e:
            # Centralized error logging for any agent.
            log(
                "agent.invoke.error",
                {
                    "agent": self.name,
                    "error": str(e),
                },
            )
            raise

    def run(self, human_instructions: str) -> T:
        """
        Backwards-compatible wrapper.

        Treats the given string as a single 'instructions' field in the payload.
        New agents should prefer run_with_payload(payload).
        """
        payload = {"instructions": human_instructions}
        return self.run_with_payload(payload)

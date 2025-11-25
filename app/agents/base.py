from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Generic, TypeVar, Type, Any

from pydantic import BaseModel
from langchain_core.prompts import ChatPromptTemplate

from app.utils.provider_config import ProviderFactory
from app.utils.file_loader import FileLoader
from app.utils.logger import log


T = TypeVar("T", bound=BaseModel)


@dataclass
class LLMAgent(Generic[T]):
    """
    Thin wrapper around an LLM + prompt template for a specific agent.

    - Loads provider via ProviderFactory.for_agent(self.name)
    - Loads system.prompt from self.prompt_path
    - Uses OpenAI structured output via llm.with_structured_output(self.output_model)
    """

    name: str
    output_model: Type[T]
    prompt_path: Path

    llm: Any = field(init=False)
    llm_params: dict[str, Any] = field(init=False, default_factory=dict)

    def __post_init__(self) -> None:
        # Each agent gets its own configured LLM instance.
        instance, params = ProviderFactory.for_agent(self.name)
        self.llm = instance
        self.llm_params = params

    # --- Helpers ---------------------------------------------------------

    def load_prompt_template(self) -> str:
        """
        Load the system.prompt template for this agent.
        Falls back to FileLoader if you later want an indirection layer.
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
            # Hard fail – you really want these files present.
            raise

    # --- Main execution --------------------------------------------------

    def run(self, human_instructions: str) -> T:
        """
        Execute the agent with a natural-language 'human_instructions' block.

        Uses:
        - ChatPromptTemplate.from_template(system.prompt)
        - llm.with_structured_output(self.output_model)

        'format_instructions' is passed as an empty string because the schema
        is already injected via the structured-output tool. The placeholder
        can stay in the prompt for readability.
        """
        template_text = self.load_prompt_template()

        # Optional debug: inspect how the schema + prompt look for this agent.
        log(
            "run",
            {
                "agent": self.name,
                "template_text": template_text,
                # You can comment this out later if it’s too noisy
                # "human_preview": human_instructions[:800],
            },
        )

        # Structured output directly to the Pydantic model (no manual parser).
        structured_llm = self.llm.with_structured_output(self.output_model)
        prompt = ChatPromptTemplate.from_template(template_text)
        chain = prompt | structured_llm

        try:
            result: T = chain.invoke(
                {
                    # We keep the variable so `{format_instructions}` doesn't break,
                    # but the tools-based schema is what really matters.
                    "format_instructions": "",
                    "human_instructions": human_instructions,
                }
            )
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

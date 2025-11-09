# app/orchestrator.py
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableSequence
from app.utils.file_loader import FileLoader
from app.utils.provider_config import ProviderFactory


class SageCompass:
    """
    Main orchestration layer.
    Loads agent config, initializes LLM, and runs the reasoning chain.
    """

    def __init__(self, agent_name: str = "problem_framing"):
        # --- Load agent configuration ---
        self.agent_name = agent_name
        self.agent_config = FileLoader.load_agent_config(agent_name) or {}

        # --- Load agent-specific and system prompts ---
        self.prompt_text = FileLoader.load_prompt(agent_name)
        self.system_prompt = FileLoader.load_prompt("system") or \
                             "You are SageCompass, an ML strategy advisor."

        # --- Initialize LLM instance ---
        self.llm, self.llm_params = ProviderFactory.for_agent(agent_name)

        # --- Initialize chain ---
        self.chain = self._init_chain()

    # ---------------- Internal methods ---------------- #

    def _init_chain(self):
        """Builds the LLM reasoning chain."""
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("human", self.prompt_text or "{question}")
        ])
        return RunnableSequence(prompt | self.llm)

    # ---------------- Public interface ---------------- #

    def ask(self, question: str) -> str:
        """Entry point for UI."""
        result = self.chain.invoke({"question": question})
        return result.content if hasattr(result, "content") else str(result)

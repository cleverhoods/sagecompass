# `agents/` — Domain Reasoning Units

Agents are **stateless, recreatable** reasoning components. They own:
- domain reasoning logic
- prompt files (`prompts/system.prompt`, optional few-shots)
- **Pydantic OutputSchema** (structured outputs)

## Canonical rules
- See `../RULES.md` (repo-level) for MUST/SHOULD rules.
- This README exists to map the folder to the LangChain/LangGraph mental model + key docs.

## What goes here
- `agent.py`: `build_agent()` factory (DI-friendly; no import-time side effects)
- `schema.py`: OutputSchema (Pydantic) used downstream by nodes
- `prompts/`: file-based prompts; no hardcoded prompt strings in Python

## Key docs
- LangChain Structured Output (Pydantic/JSON/dataclasses): https://docs.langchain.com/oss/python/langchain/structured-output
- LangChain Tools (tool calling concepts): https://docs.langchain.com/oss/python/langchain/tools
- LangChain Middleware (guardrails/policy hooks): https://docs.langchain.com/oss/python/langchain/middleware/custom
- LangChain Testing (trajectory evals + patterns): https://docs.langchain.com/oss/python/langchain/test

# `tools/` — Capabilities (Typed + Policy-Enforced)

Tools are callable capabilities exposed to agents or used by nodes.
Policy must be enforced **in code** (middleware / wrappers), not prompts.

## Canonical rules
- See `../RULES.md` for tool policy enforcement and DI rules.

## Key docs
- LangChain Tools (concepts + patterns): https://docs.langchain.com/oss/python/langchain/tools
- LangChain Middleware (`wrap_tool_call` for enforcement/retries): https://docs.langchain.com/oss/python/langchain/middleware/custom

# Middlewares

This folder contains langchain middleware implementations.

## Contracts

- Middleware must follow LangChain v1 hook/decorator patterns (e.g., `@after_agent`, `@wrap_model_call`, `@wrap_tool_call`, `@dynamic_prompt`).
- Middleware may:
  - validate/normalize agent outputs,
  - shape errors,
  - enforce execution policies,
  - attach metadata to the agent runtime result.
- Middleware must not be the only location where routing decisions exist. Nodes must persist routing signals into `SageState`.

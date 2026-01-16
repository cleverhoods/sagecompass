# `nodes/` — Orchestration Units

Nodes are orchestration units that:
- call DI-injected agents/models/tools
- validate structured outputs (OutputSchema)
- update owned state keys
- decide routing (conditional edges or Command)

## Canonical rules
- Use `../.shared/components.yml` → `component_types.nodes.contracts` for DI, purity, bounded loops, and logging requirements.

## Key docs
- LangGraph Graph API (routing patterns, Command): https://docs.langchain.com/oss/python/langgraph/use-graph-api

# `graphs/` — Graph Composition (Main Graph + Subgraphs)

Graphs are **composition-only**: they wire nodes and control flow. No business logic.

## Canonical rules
- Use `../.shared/components.yml` → `component_types.graphs.contracts` for routing, bounded loops, persistence, and testing expectations.

## What goes here
- `graph.py`: main SageCompass graph
- `subgraphs/phases/<phase>/`: phase subgraphs (each with a contract + subgraph builder)
- `subgraphs/<name>/`: non-phase subgraphs (e.g., ambiguity_preflight)
- `write_graph.py`: vector-store writer graph (if applicable)

## Key docs
- LangGraph Graph API (state, branches/loops, Command, Send): https://docs.langchain.com/oss/python/langgraph/use-graph-api
- LangGraph Persistence (checkpointers, threads, interrupts): https://docs.langchain.com/oss/python/langgraph/persistence
- LangGraph Store reference (namespaces, get/put/search): https://reference.langchain.com/python/langgraph/store/
- LangGraph Testing (partial execution, InMemorySaver): https://docs.langchain.com/oss/python/langgraph/test

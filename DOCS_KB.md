# SageCompass Knowledge Base

A single place to find framework docs, contract locations, and canonical references for architecture reviews. Update link versions when dependencies change (see `langgraph/backend/pyproject.toml`).

## Framework documentation (current ranges)
- LangGraph (>=1.0.3,<2.0.0): https://langgraph.dev/ and https://python.langchain.com/docs/langgraph
- LangChain Core/Agents (>=1.0.4,<2.0.0): https://python.langchain.com/docs and https://docs.langchain.com/
- LangSmith: https://docs.smith.langchain.com/
- Pydantic (>=2.12.4,<3.0.0): https://docs.pydantic.dev/
- dotenv: https://saurabh-kumar.com/python-dotenv/

## Project contract map
- Global scope: `AGENTS.md` (repo root) → monorepo shape + changelog policy.
- LangGraph workspace: `langgraph/AGENTS.md`.
- Backend runtime contracts: `langgraph/backend/AGENTS.md`.
- App-layer contracts and indices: `langgraph/backend/app/AGENTS.md` and `langgraph/backend/app/README.md`.
- Folder contracts: `langgraph/backend/app/{agents,nodes,graphs,tools,middlewares,utils}/README.md`.
- State contract: `langgraph/backend/app/state.py`.
- Entrypoint/DI examples: `langgraph/backend/app/main.py`, `langgraph/backend/app/graphs/graph.py`, `langgraph/backend/app/runtime.py`.
- Baseline agent example: `langgraph/backend/app/agents/problem_framing/*`.

## How to refresh this page
1) Check dependency ranges in `langgraph/backend/pyproject.toml`.
2) Update framework links if a major version bump occurs.
3) Add any new contract locations (new AGENTS/README/state files) to the map.
4) Keep external links pointing to primary docs (and mirror-friendly alternates if needed).

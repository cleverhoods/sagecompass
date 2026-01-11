# LangGraph backend

## Architectural reasoning

This section captures the "why" behind recurring patterns in the backend so we can answer
questions consistently and avoid repeating tribal knowledge during reviews.

### Type-only imports with `TYPE_CHECKING`
Node modules rely on `from __future__ import annotations` plus `TYPE_CHECKING` guards so
we can keep rich type signatures without introducing runtime import coupling. This keeps
node factories lightweight at import time and reduces the risk of circular imports while
still letting type checkers resolve the full types.

### Dependency injection (DI-first)
Node factories accept injected runnables or tools so orchestration can be tested and
composed without importing or constructing concrete dependencies at import time. This
supports fast unit tests, controlled integration tests, and clearer boundaries between
orchestration and implementation.

### Intentional exception: LangChain `@tool` usage
The tools layer currently uses LangChain's `@tool` decorator for clarity and ecosystem
alignment, even though it constructs tool instances at import time. This is a known
exception to the DI-first, no import-time construction preference and is tracked for
future refinement.

### Contract-driven platform rules
The platform contracts in `app/platform/contract/` make behavioral guarantees executable
and testable (state ownership, tool allowlists, prompt requirements, etc.). This keeps
high-level architectural intent enforced in code and avoids drift between docs and
runtime behavior. Detailed metadata for each contract is now captured in `.shared/contracts.yml`
so tooling and documentation can refer to a single source of truth.

- **`app/platform/contract/agents.py`**
  - **Benefit**: Validates that every agent exposes a Pydantic `OutputSchema` whose fields stay typed and avoid raw `dict`/`Any`, so downstream nodes can trust the structured response.
  - **Consumers**: Agents
- **`app/platform/contract/tools.py`**
  - **Benefit**: Builds and validates the tool allowlist (including the structured output tool) so agents and middleware only call approved tool names.
  - **Consumers**: Agents via middleware, Middlewares
- **`app/platform/contract/guardrails.py`**
  - **Benefit**: Drives guardrail enforcement through the shared policy entrypoint so middleware and gating nodes reject the same unsafe or out-of-scope inputs.
  - **Consumers**: Middlewares and gating nodes
- **`app/platform/contract/prompts.py`**
  - **Benefit**: Checks that prompts declare the placeholders they need and honor the required suffix ordering, keeping dynamic prompt rendering deterministic.
  - **Consumers**: Agents (via dynamic prompt middleware)
- **`app/platform/contract/state.py`**
  - **Benefit**: Limits SageState updates to known top-level keys and owner groups, preventing nodes from mutating unauthorized data structures.
  - **Consumers**: Nodes, Supervisors, Middleware that updates state
- **`app/platform/contract/structured_output.py`**
  - **Benefit**: Ensures nodes extract `structured_response` and validate it against the agent’s schema before writing phase state, which surfaces failures explicitly.
  - **Consumers**: Nodes wired to agents
- **`app/platform/runtime/evidence.py`**
  - **Benefit**: Requires nodes to hydrate evidence via `collect_phase_evidence`, respect the `missing_store` flag, and build deterministic metadata before updating phase state.
  - **Consumers**: Nodes that need context evidence
- **`app/platform/observability/logger.py`**
  - **Benefit**: Tracks that every component uses `get_logger`/`configure_logging` so logs stay in the structured pipeline instead of ad‑hoc stdlib messages.
  - **Consumers**: Agents, nodes, middlewares, tools
- **`app/platform/contract/phases.py`**
  - **Benefit**: Validates that each `PhaseContract` key matches its `name` and declares a BaseModel `output_schema`, keeping phase wiring sane.
  - **Consumers**: Graphs/phase registry
- **`app/platform/contract/namespaces.py`**
  - **Benefit**: Provides typed namespace parts so store-related tools build consistent, tenant-aware namespaces every time.
  - **Consumers**: Tools that read/write the LangGraph Store

### Opinionated component boundaries
The repo splits agents, nodes, graphs, schemas, tools, and platform code so each layer
has a narrow responsibility. This makes it easier to reason about changes, apply targeted
contracts, and keep orchestration-only modules free of business logic.

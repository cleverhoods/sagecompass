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

### Contract-driven platform rules
The platform contracts in `app/platform/contract/` make behavioral guarantees executable
and testable (state ownership, tool allowlists, prompt requirements, etc.). This keeps
high-level architectural intent enforced in code and avoids drift between docs and
runtime behavior.

### Opinionated component boundaries
The repo splits agents, nodes, graphs, schemas, tools, and platform code so each layer
has a narrow responsibility. This makes it easier to reason about changes, apply targeted
contracts, and keep orchestration-only modules free of business logic.

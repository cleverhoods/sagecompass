# SageCompass Engineering Rules (Canonical)

> Scope: `langgraph/backend/**`.

RULES.md is a policy index of enforceable invariants. Canonical contracts live in code and tests.

## Policy Index (MUST / MUST NOT)

### Global invariants
- MUST prefer explicit state + explicit routing.
- MUST keep graphs inspectable (topology explains behavior).
- MUST be DI-first; MUST NOT construct models/agents/tools/stores/checkpointers/graphs at import time.
- MUST avoid re-exporting anything that constructs agents/models/tools at import time.
- MUST bound loops via state limits and/or recursion limits.
- MUST redact secrets/PII in logs and persistence.

### Documentation + version alignment
- MUST treat `uv.lock` as the source of truth for installed versions.
- MUST use APIs that exist in pinned versions.
- MUST link official docs for non-trivial framework guidance.
- MUST NOT add new dependencies without explicit proposal + `uv.lock` updates.

### State + contracts
- MUST use `SageState` from `app/state/state.py`.
- MUST keep `GatingContext` for guardrail metadata only; ambiguity lives in `app/state/ambiguity.py`.
- MUST define routing keys as typed model fields; MUST NOT access state via dict fallbacks.
- MUST keep docstrings on `BaseModel` classes and node/graph factory functions.
- MUST validate state updates with `validate_state_update` (`app/platform/contract/state.py`).
- MUST validate artifact payloads with `ArtifactEnvelope` (`app/platform/contract/artifacts.py`).
- MUST build namespaces with `NamespaceParts`/`build_namespace` (`app/platform/contract/namespaces.py`).

### Prompts
- MUST validate prompt placeholders/suffix order with `PromptContract` helpers (`app/platform/contract/prompts.py`).
- MUST keep prompt files under agent folders (`system.prompt` required).
- MUST NOT inject retrieved context into prompts.

### Graphs + phases
- MUST keep graph modules composition-only (`app/graphs/README.md`).
- MUST route explicitly with `Command(goto=...)` when updating + routing.
- MUST have a single routing owner per phase (supervisor).
- MUST build phases from `PhaseContract` (`app/graphs/subgraphs/phases/contract.py`).
- MUST validate phase registries with `validate_phase_registry` (`app/platform/contract/phases.py`).
- MUST NOT use `Send` except for explicit map/reduce patterns.

### Nodes
- MUST implement nodes as `make_node_*` factories.
- MUST keep nodes orchestration-only (no domain reasoning).
- MUST log entry, routing decisions, errors, and output summaries (no raw sensitive data).
- MUST validate structured outputs with `validate_structured_response` (`app/platform/contract/structured_output.py`).
- MUST keep node control flow shallow (no nested if/else beyond one level).
- MUST use guard clauses with early returns for invalid inputs.
- MUST isolate complex branching into pure helper functions with unit tests.

### Agents
- MUST be stateless and created via `build_agent()`.
- MUST return structured outputs via Pydantic OutputSchema validated before state writes.
- MUST keep OutputSchema fields explicit (avoid raw `dict`/`Any`).
- MUST validate agent schemas with `validate_agent_schema` (`app/platform/contract/agents.py`).

### Tools
- MUST be typed, stateless, and DI-injected.
- MUST enforce tool allowlists/restrictions in code (middleware/tool wrappers).
- MUST build allowlists with `build_allowlist_contract` (`app/platform/contract/tools.py`).

### Guardrails
- MUST centralize guardrail logic in `app/platform/policy/*`.
- MUST call the same guardrail policies from the gate node and middleware.
- MUST use `evaluate_guardrails_contract` (`app/platform/contract/guardrails.py`).

### Storage + memory
- MUST use LangGraph Store for long-term memory and decision artifacts.
- MUST persist artifacts as immutable events plus a mutable `latest` pointer.

### Platform folder governance
- MUST satisfy platform domain governance enforced by `tests/unit/platform/test_platform_contracts.py`.

### Tooling + quality gates
- MUST keep tool configuration in `pyproject.toml`.
- MUST run `uv run poe lint`, `uv run poe type`, `uv run pytest` before proposing changes.
- MUST register pytest markers under `[tool.pytest.ini_options]` (strict markers).
- MUST test against real pinned frameworks; MUST NOT shadow framework packages via `sys.path` stubs.
- MUST maintain at least one bounded real-provider integration test (see `tests/README.md`).

### Change policy
- MUST update PhaseContract conventions, persistence docs, and integration coverage when adding new phases or artifact types.
- MUST update `uv.lock` when changing dependencies.

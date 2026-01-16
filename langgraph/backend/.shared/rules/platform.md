# Platform contracts and governance (MUST / MUST NOT)

Source: `app/RULES.md` → “Documentation + version alignment”, “State + contracts”, “Platform folder governance”, “Change policy”.

## MUST
- Treat `uv.lock` as the source of truth for installed versions; use APIs that exist in pinned versions.
- Link official docs for non-trivial framework guidance.
- Use `app/platform/core/contract/README.md` as the knowledge base for every audit/review; audits must cite the Docs map when validating LangChain/LangGraph/LangSmith alignment.
- Update the Docs map when adding/changing contracts so its links remain authoritative.
- Validate state updates with `validate_state_update` (`app/platform/core/contract/state.py`).
- Validate artifact payloads with `ArtifactEnvelope` (`app/platform/core/contract/artifacts.py`).
- Build namespaces with `NamespaceParts`/`build_namespace` (`app/platform/core/contract/namespaces.py`).
- Validate phase registries with `validate_phase_registry` (`app/platform/core/contract/registry.py`).
- Validate agent schemas with `validate_agent_schema` (`app/platform/adapters/agents.py`).
- Use `evaluate_guardrails_contract` (`app/platform/adapters/guardrails.py`).
- Satisfy platform domain governance enforced by `tests/unit/platform/test_platform_contracts.py`.
- When adding new phases or artifact types, update PhaseContract conventions, persistence docs, and integration coverage.
- Treat `app/platform/core/contract/**` as the canonical enforcement targets for backend invariants.
- Keep platform logic aligned with the platform contract tests (`tests/unit/platform/test_platform_contracts.py`).
- Keep configuration and path conventions centralized under `app/platform/config/**`.
- Keep policy logic pure and deterministic under `app/platform/core/policy/**`.
- Keep runtime helpers under `app/platform/runtime/**` and use them for evidence hydration.

## Hexagonal Architecture (Core Purity)

### MUST
- Keep `app/platform/core/` pure: NO imports from app orchestration (`app.state`, `app.graphs`, `app.nodes`, `app.agents`, `app.tools`) or wiring (`app.platform.adapters`, `app.platform.config`, `app.platform.observability`, `app.platform.runtime`, `app.platform.utils`).
- Put runtime wrappers and coordination logic in `app/platform/adapters/`, NOT in `app/platform/core/`.
- Use adapter functions for all boundary translation between core DTOs and application State models.
- Import logging, tools, and agent utilities through adapters (`app.platform.adapters.logging`, `app.platform.adapters.tools`, `app.platform.adapters.agents`).
- Validate architecture compliance with `tests/architecture/test_core_purity.py` and `tests/architecture/test_adapter_boundary.py`.
- Keep core DTOs pure: only plain dicts, primitives, and framework-agnostic types (LangChain base types allowed, but not state-specific models).
- Make core policy functions return DTOs, not State models.

### MUST NOT
- Import from `app/platform/adapters/` within `app/platform/core/`.
- Add state coordination, logging, or config loading to `core/contract/` or `core/policy/`.
- Import `SageState`, `PhaseEntry`, `GatingContext`, or other state models into core DTOs.
- Put wrapper functions that call wiring modules (observability, runtime, config) in core/contract/.

### Architecture Layers
- **Core** (`platform/core/`): Pure types, validators, policy logic (extractable, testable without framework)
- **Adapters** (`platform/adapters/`): Boundary translation (DTOs ↔ State) + runtime wrappers
- **Runtime** (`platform/runtime/`, `platform/config/`, `platform/observability/`): Wiring and infrastructure
- **Application** (`app/nodes/`, `app/graphs/`, `app/agents/`): LangGraph orchestration

Only adapters may import from both core and application layers.

## MUST NOT
- Add new dependencies without explicit proposal + `uv.lock` updates.
- Change dependencies without updating `uv.lock`.

# LangGraph Python Principles

> Comprehensive architectural principles for the SageCompass LangGraph component,
> categorized by implementation grade.

---

## Grade Definitions

| Grade | Description | When to Apply |
|-------|-------------|---------------|
| **Standard** | Foundational principles every developer must follow | All code changes |
| **Advanced** | Patterns for complex scenarios and extensibility | Feature development, refactoring |
| **Production** | Requirements for production-ready, maintainable code | Pre-release, code review |
| **Enterprise** | Governance, compliance, scale, and auditability | Critical systems, regulated environments |

---

## Standard Grade

Foundational principles that apply to all code in the langgraph component.

### DI-First + Import Purity

**Source:** `langgraph/CLAUDE.md`, `.shared/rules/di-import-purity.md`

- Be DI-first
- Never construct models/agents/tools/stores/checkpointers/graphs at import time
- Never re-export anything that constructs agents/models/tools at import time
- **Exception:** `app/tools/` uses LangChain's `@tool` decorator (import-time construction)

**Rationale:** Keeps graphs inspectable; topology must explain behavior.

### Node Orchestration Only

**Source:** `.shared/rules/nodes.md`, `app/README.md`

- Keep nodes orchestration-only (no domain reasoning in nodes)
- Nodes invoke DI-injected agents/models/tools
- Nodes validate structured outputs
- Nodes update owned state keys
- Nodes decide routing (conditional edges or `Command`)
- Isolate complex branching into pure helper functions with unit tests
- Prefer small, pure functions for branching/decision logic
- Keep control flow shallow (no nested if/else beyond one level)
- Use guard clauses with early returns for invalid inputs or no-op paths

**Forbidden:** Put domain reasoning into node modules.

### Graph Composition Only

**Source:** `.shared/rules/graphs.md`, `app/graphs/README.md`

- Keep graph modules composition-only (no business logic)
- Graphs exist purely for wiring and routing control
- Route explicitly with `Command(goto=...)`
- Build phases from `PhaseContract`
- Validate phase registries with `validate_phase_registry`

**Structure:**
- Main graph: `graphs/graph.py`
- Phase subgraphs: `graphs/subgraphs/phases/<phase>/`
- Each phase must have a `contract.py` describing the PhaseContract

### Agent Statelessness & Structured Output

**Source:** `.shared/rules/agents.md`, `app/agents/README.md`

- Be stateless and created via `build_agent()`
- Return structured outputs via Pydantic OutputSchema validated before state writes
- Keep OutputSchema fields explicit (avoid raw `dict`/`Any`)
- Validate agent schemas with `validate_agent_schema`
- Prompts are file-based (`prompts/system.prompt`, optional few-shots)

**Forbidden:** Store hidden mutable state on agent instances.

### Schema Design Rules

**Source:** `.shared/rules/schemas.md`, `app/schemas/CLAUDE.md`

- Keep schemas as shared semantic data definitions, not bound to a single node or agent
- Define schemas with typed Pydantic `BaseModel`s and clear docstrings
- Keep schema fields explicit (avoid raw `dict`/`Any`) when they surface as structured outputs

**Forbidden:**
- Embed orchestration logic or IO in schemas
- Construct models/agents/tools/stores/checkpointers at import time

### Tool Design & Determinism

**Source:** `.shared/rules/tools.md`, `app/tools/CLAUDE.md`

- Be typed, stateless, and DI-injected
- Enforce tool allowlists/restrictions in code (middleware/tool wrappers)
- Build allowlists with `build_allowlist_contract` when tools are bound or injected
- Make tool calling deterministic; middleware/nodes must inject tool outputs explicitly
- Agents may be constructed with empty tool sets; attach tools dynamically to avoid prompt bloat

**Forbidden:** Rely on model-initiated tool calls for core logic.

### Prompt Asset Organization

**Source:** `.shared/rules/prompts.md`, `app/agents/README.md`

- Validate prompt placeholders/suffix order with `PromptContract` helpers
- Keep prompt files under agent folders (`system.prompt` required)
- `global_system.prompt` may live under `app/agents/` as a shared prompt asset
- Prompts are file-based; no hardcoded prompt strings in Python

**Forbidden:** Inject retrieved context into prompts.

### State Contracts & Ownership

**Source:** `.shared/rules/state-contracts.md`, `app/state/CLAUDE.md`

- Use `SageState` from `app/state/state.py`
- Keep `GatingContext` for guardrail metadata only
- Define routing keys as typed model fields
- Keep docstrings on `BaseModel` classes and node/graph factory functions
- Validate state updates with `validate_state_update`
- Routing-relevant keys must have a single owner/writer
- State models must be paired with explicit routing decisions

**Forbidden:** Access state via dict fallbacks for routing keys.

### Explicit Routing & State Management

**Source:** `.shared/rules/graphs.md`, `.shared/rules/di-import-purity.md`

- Route explicitly with `Command(goto=...)` when updating + routing
- Prefer explicit state models paired with explicit routing decisions
- Have a single routing owner per phase (supervisor)
- MUST NOT use `Send` except for explicit map/reduce patterns

### Bounded Loops & Limits

**Source:** `.shared/rules/di-import-purity.md`

- Bound loops via state limits and/or recursion limits
- Must enforce in graphs and nodes to prevent infinite execution

---

## Advanced Grade

Patterns for complex scenarios, extensibility, and sophisticated architecture.

### Hexagonal Architecture (Ports & Adapters)

**Source:** `app/platform/README.md`, `app/platform/core/README.md`

Separate **pure core logic** from **framework-specific orchestration** using three layers:

| Layer | Purpose | Location |
|-------|---------|----------|
| **Core** | Pure, extractable business logic, contracts, policies, DTOs | `platform/core/` |
| **Adapter** | Boundary translation (DTO ↔ State conversions) | `platform/adapters/` |
| **Application** | LangGraph nodes, graphs, agents (orchestration) | `app/nodes/`, `app/graphs/`, `app/agents/` |

**Why:** Framework independence, testability, extractability, clear boundaries.

**Enforcement:** `tests/architecture/test_core_purity.py`, `tests/architecture/test_adapter_boundary.py`

### Dependency Inversion Principle

**Source:** `app/platform/README.md`, `app/platform/core/README.md`

- Core defines contracts; application implements them. Never reverse.
- Core exports DTOs and contracts
- Adapters translate between DTOs ↔ State models
- Runtime layer uses adapters to call core

**Forbidden:** Core importing from runtime/adapters (breaks dependency inversion).

### Core Purity (NO Wiring Dependencies)

**Source:** `.shared/rules/platform.md`, `app/platform/core/README.md`

Keep `app/platform/core/` pure with **NO imports from:**
- App orchestration (`app.state`, `app.graphs`, `app.nodes`, `app.agents`, `app.tools`)
- Wiring (`app.platform.adapters`, `app.platform.config`, `app.platform.observability`, `app.platform.runtime`, `app.platform.utils`)

**Architecture Layers:**
- **Core** (`platform/core/`): Pure types, validators, policy logic
- **Adapters** (`platform/adapters/`): Boundary translation + runtime wrappers
- **Runtime** (`platform/runtime/`, `platform/config/`, `platform/observability/`): Wiring and infrastructure
- **Application** (`app/nodes/`, `app/graphs/`, `app/agents/`): LangGraph orchestration

**Key Rule:** Only adapters may import from both core and application layers.

**Forbidden:**
- Import from `app/platform/adapters/` within `app/platform/core/`
- Add state coordination, logging, or config loading to `core/contract/` or `core/policy/`
- Import `SageState`, `PhaseEntry`, `GatingContext` into core DTOs

### Adapter Boundary Translation

**Source:** `.shared/rules/platform.md`, `app/platform/adapters/README.md`

- Use adapter functions for all boundary translation between core DTOs and application State models
- Import logging, tools, and agent utilities through adapters
- Adapters are simple, stateless translation functions (NOT classes)
- Bidirectional conversion between DTOs and state models

**Pattern:** `DTO → Adapter → State Model` (or reverse)

### Evidence Hydration Pattern

**Source:** `.shared/rules/guardrails-and-memory.md`, `app/platform/README.md`

- Centralize evidence hydration in `app/platform/runtime` helpers
- Nodes must NOT read from the Store directly (bypass runtime helpers)
- Collect evidence through adapters (`app/platform/adapters/evidence.collect_phase_evidence`)
- Use adapter functions to translate between evidence DTOs and state models

**Structure:** `Core DTO → Runtime Hydration → Adapter Translation → State Models`

### Type Safety Patterns

**Source:** `.shared/rules/quality-gates.md`, `langgraph/CLAUDE.md`

| Pattern | Use Instead Of | Why |
|---------|----------------|-----|
| `TypeVar` | `assert isinstance` | Returns specific types from generic validators |
| `TypeGuard` | `assert isinstance` | Survives Python `-O` optimization, reusable |
| `Mapping[str, object]` | `Any` | For heterogeneous dicts, prefer `object` |

**Framework Usage (ABSOLUTELY NO WORKAROUNDS):**
- We USE frameworks, we do NOT work around them
- When encountering type errors, read framework's type stubs
- Match code to framework's expected types exactly

**Forbidden Type Workarounds:**
- `cast()` to bypass type checking
- `# type: ignore` without justification
- `Any` types when proper types exist
- Wrapper functions that don't match protocols
- `assert isinstance()` for type narrowing

**Only acceptable type ignores:** Documented framework bugs (include version + issue link).

### Artifact & Namespace Contracts

**Source:** `.shared/rules/state-contracts.md`, `.shared/rules/platform.md`

- Validate artifact payloads with `ArtifactEnvelope`
- Build namespaces with `NamespaceParts`/`build_namespace`
- Persist artifacts as immutable events plus a mutable `latest` pointer
- ArtifactEnvelope contains: namespace, key, payload, provenance

### Long-Term Memory & Storage

**Source:** `.shared/rules/guardrails-and-memory.md`

- Use LangGraph Store for long-term memory and decision artifacts
- Persist artifacts as immutable events plus a mutable `latest` pointer
- When adding new phases or artifact types, update PhaseContract conventions, persistence docs, and integration coverage

---

## Production Grade

Requirements for production-ready, maintainable, and testable code.

### Test Structure & Organization

**Source:** `.shared/rules/testing-structure.md`, `tests/CLAUDE.md`

**Structure:** `tests/[test_type]/[category]/[mirrored_structure]`

| Test Type | Purpose |
|-----------|---------|
| `unit/` | Fast, isolated tests |
| `integration/` | Cross-component tests |
| `e2e/` | Full pipeline tests |

**Categories:**
- `architecture/` - Structural validation
- `platform/` - Hexagonal layer
- `orchestration/` - LangGraph components

**Rules:**
- Mirror `app/` directory structure within each category exactly
- Place architecture tests in `tests/unit/architecture/`

**Forbidden:**
- Mix test types in same directory
- Place tests outside the mirrored structure
- Skip the category level in test paths

### Test Naming Conventions

**Source:** `.shared/rules/testing-naming.md`

- Name test files: `test_<module_name>.py`
- Name test functions: `test_<function>_<scenario>_<expected>`
- Use pytest markers: `@pytest.mark.unit`, `@pytest.mark.integration`, `@pytest.mark.architecture`

**Examples:**
- `test_evidence_to_items_converts_dicts_to_models()`
- `test_validate_agent_schema_raises_when_invalid()`

**Forbidden:** Vague names like `test_it_works` or `test_function`.

### Test Priorities & Coverage

**Source:** `.shared/rules/testing-priorities.md`

**MUST Test (High Priority):**
1. Contract Validators (`platform/core/contract/`)
2. Policy Logic (`platform/core/policy/`)
3. Adapter Translations (`platform/adapters/`)
4. Runtime Helpers (`platform/runtime/`)
5. Architecture Rules (`tests/unit/architecture/`)

**SHOULD Test (Medium Priority):**
6. Node Factories (`nodes/`)
7. Agent Builders (`agents/`)
8. Schemas (`schemas/`)

**MAY Test (Lower Priority):**
9. Graph Composition (`graphs/`)
10. Utilities (`utils/`)

**Coverage Targets:**
| Component | Target |
|-----------|--------|
| Architecture tests | 100% |
| Contract/Policy | >90% |
| Adapters/Runtime | >80% |
| Nodes/Agents | >60% |
| Overall | >75% |

**Forbidden:**
- Framework internals (LangGraph, LangChain)
- Simple getters/setters with no logic
- Pass-through delegation functions

### Test Quality & AAA Pattern

**Source:** `.shared/rules/testing-quality.md`

- Keep unit tests < 1ms, integration < 100ms
- Make tests isolated (no external dependencies for unit tests)
- Make tests deterministic (same input → same output)
- Use Arrange-Act-Assert pattern
- Keep tests focused (one concept per test)
- Make tests independent (no inter-test dependencies)

```python
def test_phase_result_to_entry_converts_dto_to_state():
    # Arrange
    result = PhaseResult(phase_name="test", data={"key": "value"}, status="complete")
    # Act
    entry = phase_result_to_entry(result)
    # Assert
    assert isinstance(entry, PhaseEntry)
    assert entry.status == "complete"
```

**Forbidden:**
- Slow unit tests (> 1ms)
- Test inter-dependencies
- Real external services in unit tests
- Multiple concepts in one test

### Test Fixtures

**Source:** `.shared/rules/testing-fixtures.md`

- Define fixtures in `conftest.py` (pytest auto-discovers them)
- Place fixtures at **lowest directory level** where all consumers exist
- Use factory fixtures for complex objects (return builder function)
- Override fixtures by redefining in nested `conftest.py`

**Placement Hierarchy:**
1. 1 test file → Inline in that file
2. 1 directory → `conftest.py` in that dir
3. 1 category → `conftest.py` at category level
4. Global (rare) → `tests/conftest.py`

**Factory Pattern:**
```python
@pytest.fixture
def make_phase_entry():
    def _make(status="complete", data=None):
        return PhaseEntry(status=status, data=data or {})
    return _make
```

**Key Principle:** Pytest searches upward only for fixtures—never down or sideways.

**Forbidden:**
- Import fixtures from other test files (only conftest.py)
- Put all fixtures in root `tests/conftest.py`
- Create fixture chains across different conftest.py files
- Use `autouse=True` except for truly global setup

### Quality Gates & Tooling

**Source:** `.shared/rules/quality-gates.md`, `langgraph/CLAUDE.md`

**Commands to run before proposing changes:**

| Task | Command |
|------|---------|
| Lint | `uv run poe lint` |
| Type check | `uv run poe type` or `poe type_stats` |
| Tests | `uv run pytest` |
| Unit tests | `uv run poe test_unit` |
| Integration tests | `uv run poe test_integration` |
| Architecture tests | `uv run poe test_architecture` |
| Format | `uv run poe format` |
| Fast QA | `uv run poe qa_fast` |
| Full QA | `uv run poe qa` |

**Rules:**
- Keep tool configuration in `pyproject.toml`
- Register pytest markers under `[tool.pytest.ini_options]` (strict markers)
- Test against real pinned frameworks (from `uv.lock`)
- Maintain at least one bounded real-provider integration test
- **NEVER run raw commands** - ALWAYS use poe tasks defined in `pyproject.toml`

### QA Lanes

**Source:** `langgraph/CLAUDE.md`

| Lane | When | Command |
|------|------|---------|
| `qa_fast` | After ANY code change | `uv run poe qa_fast` |
| `qa` | When touching high-risk areas | `uv run poe qa` |

**High-Risk Areas (require full QA):**
- `app/platform/core/contract/`
- `app/platform/core/policy/`
- `app/platform/core/dto/`
- `app/platform/config/`
- `app/state/`
- `app/graphs/`
- `app/platform/adapters/`

### Structured Logging

**Source:** `.shared/rules/nodes.md`, `.shared/rules/middlewares.md`

- Log entry, routing decisions, errors, and output summaries (no raw sensitive data)
- Use logging through adapters (`app/platform/adapters/logging.get_logger`)
- Use guardrail evaluation through adapters
- Redact secrets/PII in logs and persistence
- Use structured logging with context

### Dependency Management

**Source:** `langgraph/CLAUDE.md`, `.shared/rules/platform.md`

- Treat `uv.lock` as the source of truth for installed versions
- Never read uv.lock directly (10k+ lines)
- Check specific package version: `uv pip show <package-name>`
- Check if package exists: `grep <package> pyproject.toml`

**When adding dependencies:**
1. Propose explicitly before adding
2. Run `uv add <package>` to update lockfile
3. Document migration impact in `../UNRELEASED.md`

**Forbidden:**
- Add new dependencies without explicit proposal + `uv.lock` updates
- Change dependencies without updating `uv.lock`

---

## Enterprise Grade

Governance, compliance, auditability, and cross-cutting requirements for critical systems.

### Centralized Guardrail Logic

**Source:** `.shared/rules/guardrails-and-memory.md`, `.shared/rules/middlewares.md`, `app/platform/README.md`

- Centralize guardrail logic in `app/platform/core/policy/*`
- Call the same guardrail policies from the gate node AND middleware
- Use `evaluate_guardrails_contract`
- Middleware is the policy boundary (admissibility, redaction/normalization, tool-call validation/allowlists, output shaping)
- Enforce tool allowlists/restrictions in code via middleware/tool wrappers
- Build allowlists with `build_allowlist_contract`
- Validate allowlist contains schema with `validate_allowlist_contains_schema`

**Forbidden:** Implement domain reasoning inside middleware.

### Redaction & Data Security

**Source:** `.shared/rules/di-import-purity.md`, `.shared/rules/guardrails-and-memory.md`, `.shared/rules/middlewares.md`

- Redact secrets/PII in logs and persistence (applies globally)
- All logging must exclude sensitive data
- Middleware handles redaction/normalization at policy boundary

### Platform Contract Enforcement

**Source:** `.shared/rules/platform.md`

- Treat `app/platform/core/contract/**` as the canonical enforcement targets for backend invariants
- Keep platform logic aligned with platform contract tests (`tests/unit/platform/test_platform_contracts.py`)
- Satisfy platform domain governance enforced by `tests/unit/platform/test_platform_contracts.py`
- Use `app/platform/core/contract/README.md` as the knowledge base for every audit/review

### Structured Output Validation

**Source:** `.shared/rules/nodes.md`, `.shared/rules/quality-gates.md`

- Validate structured outputs with `validate_structured_response`
- This function is generic (TypeVar) and returns the specific schema type—no assert needed
- Agents return structured outputs via Pydantic OutputSchema
- Outputs validated before state writes
- Keep OutputSchema fields explicit (avoid raw `dict`/`Any`)

### Platform Configuration & Path Management

**Source:** `.shared/rules/platform.md`

- Keep configuration and path conventions centralized under `app/platform/config/**`
- Keep policy logic pure and deterministic under `app/platform/core/policy/**`
- Keep runtime helpers under `app/platform/runtime/**` and use them for evidence hydration

### Operating Loop

**Source:** `langgraph/CLAUDE.md`

1. **Plan**: Confirm relevant component via maps and document minimal changes
2. **Implement**: Make smallest correct change, keeping DI/import purity in mind
3. **Fast QA loop**: `uv run poe qa_fast`
4. **Full QA loop (conditional)**: Run `uv run poe qa` when touching high-risk areas
5. **Done gate**: Update `../UNRELEASED.md`, verify map references, double-check instruction surface

### Session Start Ritual

**Source:** `langgraph/CLAUDE.md`, `.shared/efficient-commands.md`

1. Read `.shared/sys.yml` (comprehensive path index)
2. Based on task, read relevant map:
   - Platform work: `.shared/maps/platform.yml`
   - Component locations: `.shared/maps/components.yml`
   - Contract enforcement: `.shared/maps/contracts.yml`
3. Only use grep/find when maps don't cover target

### Documentation Principles

**Source:** `../CLAUDE.md`, `.shared/rules/platform.md`

- Maintain version alignment with locked dependencies
- Cite official docs (links) when describing framework behavior
- Propose new dependencies explicitly before adding
- No meta-commentary in token-sensitive files (CLAUDE.md, UNRELEASED.md, .shared/)
- State facts, commands, and rules only

### CHANGELOG & UNRELEASED.md Policy

**Source:** `../CLAUDE.md`

All changes MUST be documented using **UNRELEASED.md workflow**.

**Format:** Keep a Changelog style

**Entry rules:**
- One change = one bullet with component prefix: `[langgraph]`, `[gradio-ui]`, `[drupal]`, `[docs]`
- Use imperative phrasing
- Include references when applicable: `(PR #123)` / `(issue #456)`

**Workflow:**
- Development → Update `UNRELEASED.md`
- Release → Merge into `CHANGELOG.md`, clear UNRELEASED

### Cross-Cutting Non-Negotiables

**Source:** `langgraph/CLAUDE.md`

All code must satisfy:
- DI-first + no import-time construction
- Platform governance, version alignment, and contract enforcement
- Graph composition and routing expectations
- Tooling, lint/type/test requirements before submitting changes

---

## Quick Reference by Area

### When Working On...

| Area | Required Grades | Key Principles |
|------|-----------------|----------------|
| **New node** | Standard, Production | Node orchestration only, DI-first, test structure |
| **New agent** | Standard, Production | Stateless, structured output, prompt files |
| **Platform core** | Standard, Advanced, Enterprise | Core purity, hexagonal architecture, contract enforcement |
| **Platform adapter** | Standard, Advanced | Boundary translation, adapter pattern |
| **State changes** | Standard, Enterprise | State contracts, single owner, full QA |
| **Graph changes** | Standard, Enterprise | Composition only, explicit routing, full QA |
| **New tool** | Standard | DI-injected, typed, deterministic |
| **Guardrails/Policy** | Standard, Enterprise | Centralized logic, redaction, middleware boundary |
| **Tests** | Production | Structure, naming, AAA pattern, coverage targets |
| **Any code change** | Production | qa_fast, quality gates |

---

## Directory Structure Reference

```
langgraph/
├── app/
│   ├── state/          # Canonical state definitions
│   ├── graphs/         # Graph composition only
│   ├── nodes/          # Orchestration factories
│   ├── agents/         # Domain reasoning units
│   ├── tools/          # Typed, DI-injected capabilities
│   ├── middlewares/    # Policy boundary
│   ├── schemas/        # Shared semantic data definitions
│   └── platform/
│       ├── core/
│       │   ├── contract/   # Pure type definitions, validators
│       │   ├── dto/        # Pure data transfer objects
│       │   └── policy/     # Pure decision logic
│       ├── adapters/       # Boundary translation
│       ├── runtime/        # Evidence hydration, state helpers
│       ├── config/         # Environment, paths
│       ├── observability/  # Logging, debugging
│       └── utils/          # Cross-cutting utilities
├── tests/
│   ├── unit/
│   │   ├── architecture/   # Structural validation
│   │   ├── platform/       # Hexagonal layer tests
│   │   └── orchestration/  # LangGraph component tests
│   ├── integration/
│   └── e2e/
└── .shared/
    ├── sys.yml             # Comprehensive path index
    ├── rules/              # Principle definitions
    └── maps/               # Component/contract maps
```

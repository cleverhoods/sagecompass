# LangGraph (Python) Architecture Principles

> Comprehensive architectural principles for the SageCompass LangGraph component,
> categorized by implementation grade.
>
> **Version:** 1.0 | **LangGraph:** >=1.0.3 | **Updated:** 2026-01

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

### 1. DI-First + Import Purity

**Source:** [`langgraph/CLAUDE.md`](../langgraph/CLAUDE.md), [`.shared/rules/di-import-purity.md`](../langgraph/.shared/rules/di-import-purity.md)

**Learn more:** [Dependency Injection (Wikipedia)](https://en.wikipedia.org/wiki/Dependency_injection)

- Be DI-first
- Never construct models/agents/tools/stores/checkpointers/graphs at import time
- Never re-export anything that constructs agents/models/tools at import time
- **Exception:** `app/tools/` uses LangChain's `@tool` decorator (import-time construction)

**Rationale:** Keeps graphs inspectable; topology must explain behavior.

### 2. Node Factory Pattern

**Source:** [`.shared/rules/nodes.md`](../langgraph/.shared/rules/nodes.md)

**Learn more:** [Factory Pattern (Wikipedia)](https://en.wikipedia.org/wiki/Factory_method_pattern)

- Implement nodes as `make_node_*` factories
- Factory functions return node callables configured with DI-injected dependencies
- Keep factory signatures explicit about required dependencies

**Pattern:**
```python
def make_node_example(agent: Agent, store: BaseStore) -> Callable:
    def node(state: SageState) -> Command:
        # orchestration logic
        return Command(goto="next")
    return node
```

**Rationale:** Factories enable dependency injection, making nodes testable without framework mocking.

**Forbidden:** Define nodes as module-level functions that directly instantiate dependencies.

### 3. Node Orchestration Only

**Source:** [`.shared/rules/nodes.md`](../langgraph/.shared/rules/nodes.md), [`app/README.md`](../langgraph/app/README.md)

- Keep nodes orchestration-only (no domain reasoning in nodes)
- Nodes invoke DI-injected agents/models/tools
- Nodes validate structured outputs
- Nodes update owned state keys
- Nodes decide routing (conditional edges or `Command`)

**Forbidden:** Put domain reasoning into node modules.

### 4. Pure Decision Functions

**Source:** [`.shared/rules/nodes.md`](../langgraph/.shared/rules/nodes.md)

**Learn more:** [Pure Functions (Wikipedia)](https://en.wikipedia.org/wiki/Pure_function)

- Isolate complex branching into pure helper functions with unit tests
- Prefer small, pure functions for branching/decision logic
- Keep control flow shallow (no nested if/else beyond one level)
- Use guard clauses with early returns for invalid inputs or no-op paths
- Keep decision functions separate from I/O

**Rationale:** Pure functions are easier to test, reason about, and reuse.

### 5. Graph Composition Only

**Source:** [`.shared/rules/graphs.md`](../langgraph/.shared/rules/graphs.md), [`app/graphs/README.md`](../langgraph/app/graphs/README.md)

- Keep graph modules composition-only (no business logic)
- Graphs exist purely for wiring and routing control
- Route explicitly with `Command(goto=...)`
- Build phases from `PhaseContract`
- Validate phase registries with `validate_phase_registry`

**Structure:**
- Main graph: `graphs/graph.py`
- Phase subgraphs: `graphs/subgraphs/phases/<phase>/`
- Each phase must have a `contract.py` describing the PhaseContract

**Rationale:** Graphs should be declarative topology; business logic belongs in nodes/agents.

**Forbidden:** Embed conditionals, transformations, or domain logic in graph modules.

### 6. Agent Statelessness & Structured Output

**Source:** [`.shared/rules/agents.md`](../langgraph/.shared/rules/agents.md), [`app/agents/README.md`](../langgraph/app/agents/README.md)

**Learn more:** [Pydantic (official docs)](https://docs.pydantic.dev/) · [LangGraph structured output](https://langchain-ai.github.io/langgraph/concepts/agentic_concepts/#structured-output)

- Be stateless and created via `build_agent()`
- Return structured outputs via Pydantic OutputSchema validated before state writes
- Keep OutputSchema fields explicit (avoid raw `dict`/`Any`)
- Validate agent schemas with `validate_agent_schema`
- Prompts are file-based (`prompts/system.prompt`, optional few-shots)

**Forbidden:** Store hidden mutable state on agent instances.

### 7. Schema Design Rules

**Source:** [`.shared/rules/schemas.md`](../langgraph/.shared/rules/schemas.md), [`app/schemas/CLAUDE.md`](../langgraph/app/schemas/CLAUDE.md)

- Keep schemas as shared semantic data definitions, not bound to a single node or agent
- Define schemas with typed Pydantic `BaseModel`s and clear docstrings
- Keep schema fields explicit (avoid raw `dict`/`Any`) when they surface as structured outputs

**Forbidden:**
- Embed orchestration logic or IO in schemas
- Construct models/agents/tools/stores/checkpointers at import time

### 8. Tool Design & Determinism

**Source:** [`.shared/rules/tools.md`](../langgraph/.shared/rules/tools.md), [`app/tools/CLAUDE.md`](../langgraph/app/tools/CLAUDE.md)

- Be typed, stateless, and DI-injected
- Enforce tool allowlists/restrictions in code (middleware/tool wrappers)
- Build allowlists with `build_allowlist_contract` when tools are bound or injected
- Make tool calling deterministic; middleware/nodes must inject tool outputs explicitly
- Agents may be constructed with empty tool sets; attach tools dynamically to avoid prompt bloat

**Forbidden:** Rely on model-initiated tool calls for core logic.

### 9. Prompt Asset Organization

**Source:** [`.shared/rules/prompts.md`](../langgraph/.shared/rules/prompts.md), [`app/agents/README.md`](../langgraph/app/agents/README.md)

- Validate prompt placeholders/suffix order with `PromptContract` helpers
- Keep prompt files under agent folders (`system.prompt` required)
- `global_system.prompt` may live under `app/agents/` as a shared prompt asset
- Prompts are file-based; no hardcoded prompt strings in Python
- Context flows through evidence hydration pattern (see #19), not direct prompt injection

**Forbidden:** Hardcode retrieved context into prompt template files. Use runtime evidence hydration instead.

**Rationale:** Separates static prompt assets from dynamic context, enabling prompt versioning and testability.

### 10. State Contracts & Ownership

**Source:** [`.shared/rules/state-contracts.md`](../langgraph/.shared/rules/state-contracts.md), [`app/state/CLAUDE.md`](../langgraph/app/state/CLAUDE.md)

- Use `SageState` from `app/state/state.py`
- Keep `GatingContext` for guardrail metadata only
- Define routing keys as typed model fields
- Keep docstrings on `BaseModel` classes and node/graph factory functions
- Validate state updates with `validate_state_update`
- Routing-relevant keys must have a single owner/writer
- State models must be paired with explicit routing decisions

**Forbidden:** Access state via dict fallbacks for routing keys.

### 11. Explicit Routing & State Management

**Source:** [`.shared/rules/graphs.md`](../langgraph/.shared/rules/graphs.md), [`.shared/rules/di-import-purity.md`](../langgraph/.shared/rules/di-import-purity.md)

**Learn more:** [LangGraph Command](https://langchain-ai.github.io/langgraph/concepts/low_level/#command)

- Route explicitly with `Command(goto=...)` when updating + routing
- Prefer explicit state models paired with explicit routing decisions
- Have a single routing owner per phase (supervisor)
- MUST NOT use `Send` except for explicit map/reduce patterns

**Rationale:** Explicit routing makes graph behavior predictable and debuggable; implicit routing hides control flow.

### 12. Bounded Loops & Limits

**Source:** [`.shared/rules/di-import-purity.md`](../langgraph/.shared/rules/di-import-purity.md)

- Bound loops via state limits and/or recursion limits
- Must enforce in graphs and nodes to prevent infinite execution

**Rationale:** Unbounded loops can exhaust resources and block pipelines; explicit limits ensure predictable termination.

### 13. Observable Side Effects

**Source:** [`.shared/rules/nodes.md`](../langgraph/.shared/rules/nodes.md)

- Avoid hidden state; pass dependencies explicitly (DI-first)
- Make side effects observable/injectable so unit tests can assert behavior
- Separate I/O operations from decision logic
- Use dependency injection to provide testable implementations

**Rationale:** Observable side effects enable unit testing without mocking entire frameworks.

---

## Advanced Grade

Patterns for complex scenarios, extensibility, and sophisticated architecture.

### 14. Hexagonal Architecture (Ports & Adapters)

**Source:** [`app/platform/README.md`](../langgraph/app/platform/README.md), [`app/platform/core/README.md`](../langgraph/app/platform/core/README.md)

**Learn more:** [Hexagonal Architecture (Wikipedia)](https://en.wikipedia.org/wiki/Hexagonal_architecture_(software)) · [Alistair Cockburn's original article](https://alistair.cockburn.us/hexagonal-architecture/)

Separate **pure core logic** from **framework-specific orchestration** using three layers:

| Layer | Purpose | Location |
|-------|---------|----------|
| **Core** | Pure, extractable business logic, contracts, policies, DTOs | `platform/core/` |
| **Adapter** | Boundary translation (DTO ↔ State conversions) | `platform/adapters/` |
| **Application** | LangGraph nodes, graphs, agents (orchestration) | `app/nodes/`, `app/graphs/`, `app/agents/` |

**Why:** Framework independence, testability, extractability, clear boundaries.

**Enforcement:** [`tests/unit/architecture/test_core_purity.py`](../langgraph/tests/unit/architecture/test_core_purity.py), [`tests/unit/architecture/test_adapter_boundary.py`](../langgraph/tests/unit/architecture/test_adapter_boundary.py)

### 15. Dependency Inversion Principle

**Source:** [`app/platform/README.md`](../langgraph/app/platform/README.md), [`app/platform/core/README.md`](../langgraph/app/platform/core/README.md)

**Learn more:** [SOLID Principles (Wikipedia)](https://en.wikipedia.org/wiki/SOLID) · [Dependency Inversion Principle](https://en.wikipedia.org/wiki/Dependency_inversion_principle)

- Core defines contracts; application implements them. Never reverse.
- Core exports DTOs and contracts
- Adapters translate between DTOs ↔ State models
- Runtime layer uses adapters to call core

**Forbidden:** Core importing from runtime/adapters (breaks dependency inversion).

### 16. Core Purity (NO Wiring Dependencies)

**Source:** [`.shared/rules/platform.md`](../langgraph/.shared/rules/platform.md), [`app/platform/core/README.md`](../langgraph/app/platform/core/README.md)

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

### 17. Cross-Layer Import Rules

**Source:** [`.shared/rules/platform.md`](../langgraph/.shared/rules/platform.md)

- Only adapters may import from both core and application layers
- Core MUST NOT import from adapters, runtime, config, or application
- Application layers import through adapters, never directly from core internals
- Runtime/config/observability are infrastructure layers, not business logic

**Import Direction:** `Application → Adapters → Core` (never reverse)

### 18. Adapter Boundary Translation

**Source:** [`.shared/rules/platform.md`](../langgraph/.shared/rules/platform.md), [`app/platform/adapters/README.md`](../langgraph/app/platform/adapters/README.md)

- Use adapter functions for all boundary translation between core DTOs and application State models
- Import logging, tools, and agent utilities through adapters
- Adapters are simple, stateless translation functions (NOT classes)
- Bidirectional conversion between DTOs and state models

**Pattern:** `DTO → Adapter → State Model` (or reverse)

### 19. Evidence Hydration Pattern

**Source:** [`.shared/rules/guardrails-and-memory.md`](../langgraph/.shared/rules/guardrails-and-memory.md), [`app/platform/README.md`](../langgraph/app/platform/README.md)

- Centralize evidence hydration in `app/platform/runtime` helpers
- Nodes must NOT read from the Store directly (bypass runtime helpers)
- Collect evidence through adapters (`app/platform/adapters/evidence.collect_phase_evidence`)
- Use adapter functions to translate between evidence DTOs and state models

**Structure:** `Core DTO → Runtime Hydration → Adapter Translation → State Models`

### 20. Framework Protocol Compliance

**Source:** [`langgraph/CLAUDE.md`](../langgraph/CLAUDE.md)

**Learn more:** [Python Protocols (PEP 544)](https://peps.python.org/pep-0544/)

**CRITICAL PRINCIPLE:** We USE frameworks, we do NOT work around them.

**When encountering type errors:**
1. Read the framework's type stubs (`.venv/lib/python3.12/site-packages/{framework}/**/*.py`)
2. Understand the framework's Protocol/TypeAlias definitions
3. Match your code to the framework's expected types exactly
4. If framework types seem wrong, verify installed version matches docs before assuming bug

**Example - LangGraph nodes:**
- ❌ WRONG: Wrap with `_as_runtime_node()` + `# type: ignore[call-overload]`
- ✅ RIGHT: Read `langgraph/graph/_node.py`, see `_NodeWithRuntime` protocol, match signature exactly

### 21. Type Safety Patterns

**Source:** [`.shared/rules/quality-gates.md`](../langgraph/.shared/rules/quality-gates.md), [`langgraph/CLAUDE.md`](../langgraph/CLAUDE.md)

**Learn more:** [TypeVar (Python docs)](https://docs.python.org/3/library/typing.html#typing.TypeVar) · [TypeGuard (Python docs)](https://docs.python.org/3/library/typing.html#typing.TypeGuard) · [PEP 647 – User-Defined Type Guards](https://peps.python.org/pep-0647/)

| Pattern | Use Instead Of | Why |
|---------|----------------|-----|
| `TypeVar` | `assert isinstance` | Returns specific types from generic validators |
| `TypeGuard` | `assert isinstance` | Survives Python `-O` optimization, reusable |
| `Mapping[str, object]` | `Any` | For heterogeneous dicts, prefer `object` |

**Forbidden Type Workarounds:**
- `cast()` to bypass type checking
- `# type: ignore` without justification
- `Any` types when proper types exist
- Wrapper functions that don't match protocols
- `assert isinstance()` for type narrowing

**Only acceptable type ignores:** Documented framework bugs (include version + issue link).

### 22. Artifact & Namespace Contracts

**Source:** [`.shared/rules/state-contracts.md`](../langgraph/.shared/rules/state-contracts.md), [`.shared/rules/platform.md`](../langgraph/.shared/rules/platform.md)

**Learn more:** [Event Sourcing Pattern](https://martinfowler.com/eaaDev/EventSourcing.html)

- Validate artifact payloads with `ArtifactEnvelope`
- Build namespaces with `NamespaceParts`/`build_namespace`
- Persist artifacts as immutable events plus a mutable `latest` pointer
- ArtifactEnvelope contains: namespace, key, payload, provenance

### 23. Long-Term Memory & Storage

**Source:** [`.shared/rules/guardrails-and-memory.md`](../langgraph/.shared/rules/guardrails-and-memory.md)

**Learn more:** [LangGraph Memory Concepts](https://langchain-ai.github.io/langgraph/concepts/memory/) · [LangGraph Store](https://langchain-ai.github.io/langgraph/concepts/persistence/#memory-store)

- Use LangGraph Store for long-term memory and decision artifacts
- Persist artifacts as immutable events plus a mutable `latest` pointer
- When adding new phases or artifact types, update PhaseContract conventions, persistence docs, and integration coverage

---

## Production Grade

Requirements for production-ready, maintainable, and testable code.

### 24. Test Structure & Organization

**Source:** [`.shared/rules/testing-structure.md`](../langgraph/.shared/rules/testing-structure.md), [`tests/CLAUDE.md`](../langgraph/tests/CLAUDE.md)

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

### 25. Test Naming Conventions

**Source:** [`.shared/rules/testing-naming.md`](../langgraph/.shared/rules/testing-naming.md)

- Name test files: `test_<module_name>.py`
- Name test functions: `test_<function>_<scenario>_<expected>`
- Use pytest markers: `@pytest.mark.unit`, `@pytest.mark.integration`, `@pytest.mark.architecture`

**Examples:**
- `test_evidence_to_items_converts_dicts_to_models()`
- `test_validate_agent_schema_raises_when_invalid()`

**Forbidden:** Vague names like `test_it_works` or `test_function`.

### 26. Test Priorities & Coverage

**Source:** [`.shared/rules/testing-priorities.md`](../langgraph/.shared/rules/testing-priorities.md)

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

### 27. Test Quality & AAA Pattern

**Source:** [`.shared/rules/testing-quality.md`](../langgraph/.shared/rules/testing-quality.md)

**Learn more:** [Arrange-Act-Assert Pattern](https://wiki.c2.com/?ArrangeActAssert)

- Keep unit tests fast (target < 50ms each), integration < 500ms
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
- Slow unit tests (> 100ms suggests I/O or external calls)
- Test inter-dependencies
- Real external services in unit tests
- Multiple concepts in one test

### 28. Test Fixtures

**Source:** [`.shared/rules/testing-fixtures.md`](../langgraph/.shared/rules/testing-fixtures.md)

**Learn more:** [pytest fixtures (official docs)](https://docs.pytest.org/en/stable/explanation/fixtures.html)

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

### 29. Quality Gates & Tooling

**Source:** [`.shared/rules/quality-gates.md`](../langgraph/.shared/rules/quality-gates.md), [`langgraph/CLAUDE.md`](../langgraph/CLAUDE.md)

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

### 30. QA Lanes

**Source:** [`langgraph/CLAUDE.md`](../langgraph/CLAUDE.md)

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

### 31. Code Style Automation

**Source:** [`langgraph/CLAUDE.md`](../langgraph/CLAUDE.md)

**Learn more:** [Ruff (official docs)](https://docs.astral.sh/ruff/)

**Do not manually check or mention style** - automated tools enforce this:
- Format code: `uv run poe format` (Ruff)
- Check types: `uv run poe type_stats` (mypy)
- Check lint: `uv run poe lint` (Ruff)

Always run `uv run poe format` before commits. Never discuss style in code reviews - linters handle it.

**Forbidden:** Manual style checking or style discussions in reviews.

### 32. Poe Tasks Only

**Source:** [`langgraph/CLAUDE.md`](../langgraph/CLAUDE.md)

**Learn more:** [poethepoet (official docs)](https://poethepoet.natn.io/)

**NEVER run raw commands** - ALWAYS use the poe tasks defined in `pyproject.toml`:

| Task | Command |
|------|---------|
| Type checking | `uv run poe type_stats` |
| Scoped type check | `uv run poe type_stats_scoped {path}` |
| Unit tests | `uv run poe test_unit` |
| Integration tests | `uv run poe test_integration` |
| Architecture tests | `uv run poe test_architecture` |
| Linting | `uv run poe lint` |
| Formatting | `uv run poe format` |

**Why:** Poe tasks have correct flags, paths, and configuration. Raw commands bypass project standards.

### 33. Architecture Compliance Testing

**Source:** [`.shared/rules/platform.md`](../langgraph/.shared/rules/platform.md), [`tests/unit/architecture/`](../langgraph/tests/unit/architecture/)

- Validate architecture compliance with dedicated tests
- [`test_core_purity.py`](../langgraph/tests/unit/architecture/test_core_purity.py) - Ensures core has no forbidden imports
- [`test_adapter_boundary.py`](../langgraph/tests/unit/architecture/test_adapter_boundary.py) - Validates adapter translation patterns
- Run with: `uv run poe test_architecture`

**Coverage Target:** 100% of architectural rules must have corresponding tests.

### 34. Middleware Testability

**Source:** [`.shared/rules/middlewares.md`](../langgraph/.shared/rules/middlewares.md)

- Keep middleware testable with pure decision helpers and minimal wiring
- Extract policy decisions into pure functions that can be unit tested
- Middleware integration tests should verify wiring, not business logic
- Use dependency injection to make middleware components swappable

**Rationale:** Middleware sits at critical boundaries; testability ensures reliability.

### 35. Structured Logging

**Source:** [`.shared/rules/nodes.md`](../langgraph/.shared/rules/nodes.md), [`.shared/rules/middlewares.md`](../langgraph/.shared/rules/middlewares.md)

**Learn more:** [Structured Logging (structlog)](https://www.structlog.org/en/stable/why.html)

- Log entry, routing decisions, errors, and output summaries (no raw sensitive data)
- Use logging through adapters (`app/platform/adapters/logging.get_logger`)
- Use guardrail evaluation through adapters
- Redact secrets/PII in logs and persistence
- Use structured logging with context

### 36. Dependency Management

**Source:** [`langgraph/CLAUDE.md`](../langgraph/CLAUDE.md), [`.shared/rules/platform.md`](../langgraph/.shared/rules/platform.md)

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

### 37. Token Efficiency

**Source:** [`langgraph/CLAUDE.md`](../langgraph/CLAUDE.md), [`.shared/efficient-commands.md`](../langgraph/.shared/efficient-commands.md)

**CRITICAL:** These token efficiency rules apply everywhere under `langgraph/**`.

**Purpose-based reading strategies:**
- **EDIT goal:** Read full file without limits
- **UNDERSTAND goal:** Read first 30-50 lines (imports, class definitions)
- **FIND goal:** Grep first, then read specific section
- **VERIFY goal:** Use Grep with `files_with_matches` only

**File size guidelines:**
- < 5KB: Safe to read entirely
- 5-50KB: Use offset/limit
- 50-500KB: Use head/tail only
- \> 500KB: DO NOT READ (use grep/awk)

**Forbidden:** Reading lock files (uv.lock), cache directories, or files without limits.

### 38. Centralized Guardrail Logic

**Source:** [`.shared/rules/guardrails-and-memory.md`](../langgraph/.shared/rules/guardrails-and-memory.md), [`.shared/rules/middlewares.md`](../langgraph/.shared/rules/middlewares.md), [`app/platform/README.md`](../langgraph/app/platform/README.md)

- Centralize guardrail logic in `app/platform/core/policy/*`
- Call the same guardrail policies from the gate node AND middleware
- Use `evaluate_guardrails_contract`
- Middleware is the policy boundary (admissibility, redaction/normalization, tool-call validation/allowlists, output shaping)
- Enforce tool allowlists/restrictions in code via middleware/tool wrappers
- Build allowlists with `build_allowlist_contract`
- Validate allowlist contains schema with `validate_allowlist_contains_schema`

**Forbidden:** Implement domain reasoning inside middleware.

### 39. Redaction & Data Security

**Source:** [`.shared/rules/di-import-purity.md`](../langgraph/.shared/rules/di-import-purity.md), [`.shared/rules/guardrails-and-memory.md`](../langgraph/.shared/rules/guardrails-and-memory.md), [`.shared/rules/middlewares.md`](../langgraph/.shared/rules/middlewares.md)

**Learn more:** [OWASP Logging Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html)

- Redact secrets/PII in logs and persistence (applies globally)
- All logging must exclude sensitive data
- Middleware handles redaction/normalization at policy boundary

### 40. Platform Contract Enforcement

**Source:** [`.shared/rules/platform.md`](../langgraph/.shared/rules/platform.md)

- Treat `app/platform/core/contract/**` as the canonical enforcement targets for backend invariants
- Keep platform logic aligned with platform contract tests (`tests/unit/platform/test_platform_contracts.py`)
- Satisfy platform domain governance enforced by `tests/unit/platform/test_platform_contracts.py`
- Use `app/platform/core/contract/README.md` as the knowledge base for every audit/review

### 41. Structured Output Validation

**Source:** [`.shared/rules/nodes.md`](../langgraph/.shared/rules/nodes.md), [`.shared/rules/quality-gates.md`](../langgraph/.shared/rules/quality-gates.md)

- Validate structured outputs with `validate_structured_response`
- This function is generic (TypeVar) and returns the specific schema type—no assert needed
- Agents return structured outputs via Pydantic OutputSchema
- Outputs validated before state writes
- Keep OutputSchema fields explicit (avoid raw `dict`/`Any`)

### 42. Platform Configuration & Path Management

**Source:** [`.shared/rules/platform.md`](../langgraph/.shared/rules/platform.md)

- Keep configuration and path conventions centralized under `app/platform/config/**`
- Keep policy logic pure and deterministic under `app/platform/core/policy/**`
- Keep runtime helpers under `app/platform/runtime/**` and use them for evidence hydration

### 43. Operating Loop

**Source:** [`langgraph/CLAUDE.md`](../langgraph/CLAUDE.md)

1. **Plan**: Confirm relevant component via maps and document minimal changes
2. **Implement**: Make smallest correct change, keeping DI/import purity in mind
3. **Fast QA loop**: `uv run poe qa_fast`
4. **Full QA loop (conditional)**: Run `uv run poe qa` when touching high-risk areas
5. **Done gate**: Update `../UNRELEASED.md`, verify map references, double-check instruction surface

### 44. Session Start Ritual

**Source:** [`langgraph/CLAUDE.md`](../langgraph/CLAUDE.md), [`.shared/efficient-commands.md`](../langgraph/.shared/efficient-commands.md)

1. Read `.shared/sys.yml` (comprehensive path index)
2. Based on task, read relevant map:
   - Platform work: `.shared/maps/platform.yml`
   - Component locations: `.shared/maps/components.yml`
   - Contract enforcement: `.shared/maps/contracts.yml`
3. Only use grep/find when maps don't cover target

### 45. Documentation Principles

**Source:** [`../CLAUDE.md`](../CLAUDE.md), [`.shared/rules/platform.md`](../langgraph/.shared/rules/platform.md)

- Maintain version alignment with locked dependencies
- Cite official docs (links) when describing framework behavior
- Propose new dependencies explicitly before adding
- No meta-commentary in token-sensitive files (CLAUDE.md, UNRELEASED.md, .shared/)
- State facts, commands, and rules only

### 46. CHANGELOG & UNRELEASED.md Policy

**Source:** [`../CLAUDE.md`](../CLAUDE.md)

**Learn more:** [Keep a Changelog](https://keepachangelog.com/)

All changes MUST be documented using **UNRELEASED.md workflow**.

**Format:** Keep a Changelog style

**Entry rules:**
- One change = one bullet with component prefix: `[langgraph]`, `[gradio-ui]`, `[drupal]`, `[docs]`
- Use imperative phrasing
- Include references when applicable: `(PR #123)` / `(issue #456)`

**Workflow:**
- Development → Update `UNRELEASED.md`
- Release → Merge into `CHANGELOG.md`, clear UNRELEASED

### Cross-Cutting Non-Negotiables (Summary)

**Source:** [`langgraph/CLAUDE.md`](../langgraph/CLAUDE.md)

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

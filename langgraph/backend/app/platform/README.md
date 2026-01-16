# `platform` - Platform Layer

## Overview

The platform layer provides the **foundational infrastructure** for the SageCompass backend. It implements a **hexagonal architecture** that separates pure business logic from framework-specific orchestration, ensuring the codebase remains maintainable, testable, and framework-independent.

## Why This Layer Exists

Without proper architectural boundaries, application code becomes tightly coupled to LangGraph:

```python
# WITHOUT PLATFORM LAYER - Everything mixed together
def problem_framing_node(state: SageState) -> Command:
    # Guardrail logic mixed with state management
    if "unsafe" in state.messages[-1].content:
        state.gating.guardrail = GuardrailResult(is_safe=False, ...)

    # Evidence hydration mixed with node orchestration
    phase_entry = state.phases.get("problem_framing") or PhaseEntry()
    store = get_store()
    for item in phase_entry.evidence:
        doc = store.get(item.namespace, item.key)
        # ... inline hydration logic

    # Validation mixed with execution
    if "problem_framing" not in state.phases:
        raise ValueError("Invalid state update!")

    # All concerns tangled together!
```

**With the platform layer**, concerns are cleanly separated:

```python
# WITH PLATFORM LAYER - Clean separation
def problem_framing_node(state: SageState) -> Command:
    # Use platform contracts for validation
    validate_state_update(update, owner="problem_framing")

    # Use platform runtime helpers for evidence
    bundle = collect_phase_evidence(state, phase="problem_framing")

    # Use platform policies for decisions
    guardrail = evaluate_guardrails(user_input)

    # Use adapters for state translation
    context = guardrail_to_gating(guardrail, user_input)

    # Node only orchestrates - all logic in platform!
```

## Hexagonal Architecture

The platform implements hexagonal architecture (ports and adapters) with three layers:

```
┌─────────────────────────────────────────────────────────┐
│                   APPLICATION LAYER                      │
│  (app/nodes, app/graphs, app/agents, app/middlewares)  │
│  - LangGraph orchestration                              │
│  - State management (SageState, PhaseEntry, etc.)       │
│  - Calls platform services via contracts                │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                   PLATFORM LAYER                        │  ← YOU ARE HERE
│  ┌────────────────────────────────────────────────────┐ │
│  │  Adapters (platform/adapters)                      │ │
│  │  - Translate between DTOs ↔ State models           │ │
│  │  - Boundary translation, no business logic         │ │
│  └────────────┬───────────────────────────────────────┘ │
│               │                                         │
│  ┌────────────▼───────────────────────────────────────┐ │
│  │  Core (platform/core)                              │ │
│  │  - Pure DTOs (no framework dependencies)           │ │
│  │  - Contracts and validators                        │ │
│  │  - Policy evaluation (pure functions)              │ │
│  └────────────────────────────────────────────────────┘ │
│                                                         │
│  ┌────────────────────────────────────────────────────┐ │
│  │  Runtime Helpers (platform/runtime)                │ │
│  │  - Evidence hydration, state helpers               │ │
│  │  - Uses core DTOs internally                       │ │
│  └────────────────────────────────────────────────────┘ │
│                                                         │
│  ┌────────────────────────────────────────────────────┐ │
│  │  Infrastructure (platform/config, observability)   │ │
│  │  - Configuration loading, logging                  │ │
│  │  - Cross-cutting concerns                          │ │
│  └────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

## Directory Structure

### `adapters/` - Boundary Translation
**Purpose:** Translate between pure core DTOs and framework-specific state models.

**Contains:**
- `evidence.py` - Evidence ↔ State translation
- `guardrails.py` - Guardrails ↔ GatingContext translation
- `phases.py` - PhaseResult ↔ PhaseEntry translation

**Why it exists:** Keeps core DTOs pure (no state dependencies) while enabling LangGraph integration.

**Learn more:** [adapters/README.md](./adapters/README.md)

---

### `core/` - Pure Business Logic
**Purpose:** Framework-independent contracts, DTOs, and policies.

**Contains:**
- `core/contract/` - Type validators and enforcement (validate_state_update, etc.)
- `core/dto/` - Pure data transfer objects (EvidenceBundle, GuardrailResult, etc.)
- `core/policy/` - Pure decision logic (evaluate_guardrails, etc.)

**Why it exists:** Enables core logic to be extracted, tested without framework setup, and reused across projects.

**Dependency rule:** Core has NO imports from `app/state/`, `app/nodes/`, or LangGraph-specific types.

**Learn more:** [core/README.md](./core/README.md)

---

### `config/` - Configuration Management
**Purpose:** Environment loading, file access, and path conventions.

**Contains:**
- `env.py` - Environment variable loading
- `paths.py` - Centralized path resolution
- `loaders.py` - File loading utilities

**When to use:** Loading prompts, schemas, configuration files, or accessing environment variables.

---

### `observability/` - Logging and Debugging
**Purpose:** Structured logging and debugging hooks.

**Contains:**
- `logger.py` - Structured logging with context
- Debug hooks for development

**When to use:** Logging events, errors, or debug information with structured context.

---

### `runtime/` - Runtime Helpers
**Purpose:** State introspection, evidence hydration, and phase routing.

**Contains:**
- `evidence.py` - Evidence hydration from LangGraph Store
- `state_helpers.py` - State inspection and manipulation helpers

**When to use:** Hydrating evidence, extracting user messages, phase routing logic.

**Note:** Runtime helpers use core DTOs internally to maintain clean boundaries.

---

### `utils/` - Shared Utilities
**Purpose:** Cross-cutting utilities (prompts, models, providers).

**Contains:**
- `namespace_utils.py` - Namespace construction helpers
- Prompt composition utilities
- Model factory functions

**When to use:** Building prompts, creating models, constructing namespaces.

---

## How the Layers Work Together

### Example: Guardrail Evaluation

**1. Core Policy (Pure Logic):**
```python
# app/platform/core/policy/guardrails.py
def evaluate_guardrails(input_text: str) -> GuardrailResult:
    """Pure function - no framework dependencies."""
    return GuardrailResult(
        is_safe=not _contains_unsafe_patterns(input_text),
        is_in_scope=_is_domain_relevant(input_text),
        reasons=[...],
    )
```

**2. Adapter (Translation):**
```python
# app/platform/adapters/guardrails.py
def guardrail_to_gating(
    guardrail: GuardrailResult,
    original_input: str,
) -> GatingContext:
    """Translate DTO to state model."""
    decision = "no-go" if not guardrail.is_safe else "go"
    return GatingContext(
        original_input=original_input,
        guardrail=guardrail,
        decision=decision,
    )
```

**3. Node (Orchestration):**
```python
# app/nodes/gating.py
def gating_node(state: SageState) -> Command:
    """Orchestrate using platform services."""
    # 1. Use core policy
    result = evaluate_guardrails(state.gating.original_input)

    # 2. Use adapter
    context = guardrail_to_gating(result, state.gating.original_input)

    # 3. Use contract
    update = {"gating": context}
    validate_state_update(update, owner="gating")

    # 4. Return state update
    return Command(update=update, goto=next_node)
```

### Example: Evidence Hydration

**1. Core DTO (Pure Data):**
```python
# app/platform/core/dto/evidence.py
@dataclass(frozen=True)
class EvidenceBundle:
    """Pure DTO - no state dependencies."""
    evidence: Sequence[dict]
    context_docs: list[Document]
    missing_store: bool = False
```

**2. Runtime Helper (Orchestration):**
```python
# app/platform/runtime/evidence.py
def collect_phase_evidence(state: SageState, phase: str) -> EvidenceBundle:
    """Collect and hydrate evidence, returning pure DTO."""
    phase_entry = state.phases.get(phase) or PhaseEntry()
    evidence = list(phase_entry.evidence or [])
    context_docs = hydrate_evidence_docs(evidence, phase=phase)
    evidence_dicts = [
        {"namespace": item.namespace, "key": item.key, "score": item.score}
        for item in evidence
    ]
    return EvidenceBundle(
        evidence=evidence_dicts,
        context_docs=context_docs,
        missing_store=False,
    )
```

**3. Adapter (Translation):**
```python
# app/platform/adapters/evidence.py
def evidence_to_items(bundle: EvidenceBundle) -> list[EvidenceItem]:
    """Convert DTO dicts to state models."""
    return [
        EvidenceItem.model_validate(item)
        for item in bundle.evidence
    ]
```

**4. Node (Usage):**
```python
# app/nodes/problem_framing.py
def problem_framing_node(state: SageState) -> Command:
    # Get pure DTO from runtime
    bundle = collect_phase_evidence(state, phase="problem_framing")

    # Use adapter for state models
    evidence_items = evidence_to_items(bundle)

    # Update state
    state.phases["problem_framing"] = PhaseEntry(
        evidence=evidence_items,
        ...
    )
```

## Design Principles

### 1. Dependency Inversion
**Core defines contracts, application implements them.**

```python
# GOOD - Core defines interface, runtime implements
# Core: app/platform/core/dto/evidence.py
@dataclass(frozen=True)
class EvidenceBundle: ...

# Runtime: app/platform/runtime/evidence.py (depends on core)
def collect_phase_evidence(...) -> EvidenceBundle: ...

# BAD - Core depends on runtime
# Core importing from runtime breaks dependency inversion
```

### 2. Pure Core Layer
**No framework dependencies in core.**

```python
# GOOD - Pure function in core/policy
def evaluate_guardrails(input_text: str) -> GuardrailResult:
    return GuardrailResult(...)

# BAD - Framework dependency in core
def evaluate_guardrails(state: SageState) -> None:  # SageState is framework-specific!
    state.gating.guardrail = ...
```

### 3. Explicit Boundaries
**Adapters make translation explicit.**

```python
# GOOD - Explicit adapter
bundle = collect_phase_evidence(state, phase)  # Returns DTO
items = evidence_to_items(bundle)  # Adapter translates

# BAD - Implicit/hidden translation
bundle = collect_phase_evidence(state, phase)
items = bundle.evidence  # Assumes evidence is already EvidenceItems
```

### 4. Separation of Concerns
**Each layer has a single responsibility.**

- **Core** - Business logic and contracts
- **Adapters** - Data translation (no logic)
- **Runtime** - Orchestration helpers
- **Config** - Configuration loading
- **Observability** - Logging and debugging

## Testing

Platform components are tested in `tests/unit/platform/`:

```
tests/unit/platform/
├── adapters/       # Adapter translation tests
├── config/         # Configuration tests
├── contract/       # Contract validation tests
├── observability/  # Logging tests
├── policy/         # Policy evaluation tests
├── runtime/        # Runtime helper tests
└── utils/          # Utility tests
```

**Key testing benefit:** Core layer tests require NO LangGraph setup since core has no framework dependencies.

## Benefits

1. **Framework Independence** - Can upgrade/replace LangGraph without touching core logic
2. **Testability** - Test core policies without mocking LangGraph state
3. **Extractability** - Core can be extracted into a shared library
4. **Clear Boundaries** - Enforced by import structure and adapters
5. **Maintainability** - Each layer has single responsibility
6. **Type Safety** - DTOs and adapters enforce correct data flow

## When to Use Platform vs. Application

**Use platform layer for:**
- Contracts and validation logic (state, agents, prompts, etc.)
- Pure business rules and policies (guardrails, access control)
- Reusable utilities (namespace construction, evidence hydration)
- Configuration and logging infrastructure

**Use application layer for:**
- LangGraph node implementations
- Graph composition and routing
- Agent builders
- Middleware wiring
- State management

## Migration Guide

If you're adding new functionality:

1. **Start with core** - Define DTOs in `core/dto/`, policies in `core/policy/`
2. **Add adapters** - Create translation functions in `adapters/`
3. **Use in runtime** - Reference DTOs in `runtime/` helpers
4. **Orchestrate** - Use platform services in nodes/graphs

## Related Documentation

- Core layer architecture: [core/README.md](./core/README.md)
- Adapter layer: [adapters/README.md](./adapters/README.md)
- Platform configuration: `.shared/platform.yml`

## References

- Hexagonal Architecture: https://alistair.cockburn.us/hexagonal-architecture/
- Clean Architecture: https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html
- Dependency Inversion Principle: https://en.wikipedia.org/wiki/Dependency_inversion_principle
- Ports and Adapters: https://jmgarridopaz.github.io/content/hexagonalarchitecture.html

# `platform/core` - Platform Core Abstraction

## Why This Exists

This directory implements **hexagonal architecture** (also called "ports and adapters" or "clean architecture") for the SageCompass backend platform layer.

### The Problem

Without proper layering, application code becomes tightly coupled to framework-specific types and state management:

```python
# TIGHT COUPLING - Hard to test, hard to extract, hard to change frameworks
def evaluate_guardrails(state: SageState) -> None:
    """Directly depends on LangGraph's SageState."""
    if not state.gating.guardrail:
        state.gating.guardrail = GuardrailResult(...)  # Mixed with state management
```

This creates several issues:
1. **Framework lock-in** - Core logic can't be extracted or reused outside LangGraph
2. **Testing complexity** - Tests require full LangGraph state setup
3. **Dependency confusion** - Business logic mixed with framework orchestration
4. **Migration risk** - Upgrading or replacing LangGraph requires touching core logic

### The Solution

Separate **pure core logic** from **framework-specific orchestration** using a 3-layer architecture:

```
┌─────────────────────────────────────────┐
│  Runtime Layer (app/nodes, app/graphs)  │  ← LangGraph orchestration
│  - Owns SageState, LangGraph runtime    │
│  - Calls core contracts via adapters    │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│  Adapter Layer (app/platform/adapters)  │  ← Boundary translation
│  - Translates between DTOs ↔ State      │
│  - No business logic                    │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│  Core Layer (app/platform/core)         │  ← Pure, extractable
│  - No LangGraph dependencies            │
│  - Pure functions, DTOs, contracts      │
│  - Testable without framework setup     │
└─────────────────────────────────────────┘
```

With this structure:

```python
# CLEAN SEPARATION - Pure, testable, extractable

# Core layer (pure)
def evaluate_guardrails(input_text: str) -> GuardrailResult:
    """Pure function - no framework dependencies."""
    return GuardrailResult(
        is_safe=not contains_unsafe_content(input_text),
        is_in_scope=is_domain_relevant(input_text),
        reasons=[...],
    )

# Adapter layer (translation)
def guardrail_to_gating(guardrail: GuardrailResult, original_input: str) -> GatingContext:
    """Translate DTO to state model."""
    return GatingContext(original_input=original_input, guardrail=guardrail, ...)

# Runtime layer (orchestration)
def gating_node(state: SageState) -> Command:
    """LangGraph node - orchestrates using core + adapters."""
    result = evaluate_guardrails(state.gating.original_input)  # Pure core
    context = guardrail_to_gating(result, state.gating.original_input)  # Adapter
    return Command(update={"gating": context})  # State update
```

## Directory Structure

### `core/contract/`
**Purpose:** Type definitions and validators that enforce backend invariants.

**What goes here:**
- Contract models (PhaseContract, PromptContract, etc.)
- Validation functions (validate_state_update, validate_agent_schema, etc.)
- Helper functions that enforce rules (build_namespace, etc.)

**Dependencies:** Can import from `core/dto/` and standard library only.

**Example:**
```python
# app/platform/core/contract/state.py
def validate_state_update(update: dict, owner: str) -> None:
    """Validate that state updates follow ownership rules."""
    # Pure validation - no LangGraph state dependencies
```

### `core/dto/`
**Purpose:** Pure data transfer objects for boundary translation.

**What goes here:**
- Immutable dataclasses/frozen models
- No business logic, only data structure
- No framework dependencies (no SageState, PhaseEntry, etc.)

**Dependencies:** Standard library + Pydantic/LangChain types only. Never imports from `app/state/`.

**Example:**
```python
# app/platform/core/dto/guardrails.py
@dataclass(frozen=True)
class GuardrailResult:
    """Pure DTO - no state management concerns."""
    is_safe: bool
    is_in_scope: bool
    reasons: list[str]
```

### `core/policy/`
**Purpose:** Pure, deterministic policy evaluation functions.

**What goes here:**
- Decision logic (guardrails, access control, validation)
- Pure functions: same input → same output
- No side effects, no state mutations

**Dependencies:** Can import from `core/dto/` and standard library only.

**Example:**
```python
# app/platform/core/policy/guardrails.py
def evaluate_guardrails(input_text: str) -> GuardrailResult:
    """Pure policy evaluation - deterministic and testable."""
    return GuardrailResult(
        is_safe=not _contains_unsafe_patterns(input_text),
        is_in_scope=_is_domain_relevant(input_text),
        reasons=[...],
    )
```

## Dependency Rules

**MUST follow these rules:**

1. **Core has NO framework dependencies**
   - Never import `SageState`, `PhaseEntry`, `GatingContext`, `AmbiguityContext`
   - Never import from `app/state/`, `app/nodes/`, `app/graphs/`
   - Only import from `core/dto/`, standard library, Pydantic, base LangChain types

2. **Core exports DTOs and contracts**
   - DTOs are the "currency" of the boundary
   - Adapters translate between DTOs ↔ State models
   - Runtime layer uses adapters to call core

3. **Keep logic pure**
   - Functions in `core/policy/` should be deterministic
   - No global state, no side effects
   - Easy to test without mocking

## Benefits

1. **Extractability** - Core logic can be extracted into a library and reused
2. **Testability** - Test core logic without LangGraph setup
3. **Framework independence** - Can upgrade/replace LangGraph without touching core
4. **Clear boundaries** - Separation of concerns enforced by imports
5. **Migration safety** - Core logic survives framework changes

## Testing

Tests for core layer live in `tests/unit/platform/contract/`, `tests/unit/platform/policy/`.

Since core has no framework dependencies, tests are simple:

```python
def test_evaluate_guardrails_blocks_unsafe():
    result = evaluate_guardrails("unsafe content here")
    assert result.is_safe is False
    # No LangGraph setup required!
```

## When to Use Core vs. Runtime

**Use core layer when:**
- Implementing business rules or policies
- Defining contracts or validation logic
- Creating data structures for boundary translation
- Writing deterministic, testable logic

**Use runtime layer when:**
- Orchestrating LangGraph nodes and graphs
- Managing SageState updates
- Handling LangGraph-specific concerns (interrupts, commands, etc.)
- Wiring together core logic with state management

## References

- Hexagonal Architecture: https://alistair.cockburn.us/hexagonal-architecture/
- Clean Architecture: https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html
- Dependency Inversion Principle: https://en.wikipedia.org/wiki/Dependency_inversion_principle

# `platform/adapters` - Platform Adapter Layer

## Why This Exists

The adapter layer provides **boundary translation** between pure core DTOs and framework-specific state models. This is a critical component of hexagonal architecture that keeps the core layer pure while enabling integration with LangGraph.

### The Problem

We want our core logic to be pure and framework-independent:

```python
# Core layer returns pure DTO
def collect_phase_evidence(state: SageState, phase: str) -> EvidenceBundle:
    """Should return pure DTO, but what about PhaseEntry?"""
    # PROBLEM: EvidenceBundle needs both DTOs AND state-specific data
    return EvidenceBundle(
        phase_entry=state.phases[phase],  # State model (framework-specific)
        evidence=[...],  # Pure data
        context_docs=[...],  # Pure data
    )
```

This violates our clean architecture because:
1. **DTO pollution** - Pure DTOs contain framework-specific types (PhaseEntry)
2. **Circular dependency** - Core DTO imports from app/state/
3. **Testing complexity** - Can't test DTOs without state models
4. **Extractability broken** - Can't extract core without bringing LangGraph state

### The Solution

Keep DTOs pure and use **adapters** to translate at the boundary:

```python
# CLEAN SEPARATION with adapters

# Core DTO (pure - no state dependencies)
@dataclass(frozen=True)
class EvidenceBundle:
    """Pure DTO with only data, no state models."""
    evidence: Sequence[dict]  # Plain dicts
    context_docs: list[Document]  # LangChain base type
    missing_store: bool = False

# Adapter function (translation layer)
def evidence_to_items(bundle: EvidenceBundle) -> list[EvidenceItem]:
    """Translate DTO dicts to state models."""
    return [
        EvidenceItem.model_validate(item)
        for item in bundle.evidence
    ]

# Runtime usage (orchestration)
def problem_framing_node(state: SageState) -> Command:
    # Get pure DTO from core
    bundle = collect_phase_evidence(state, phase="problem_framing")

    # Use adapter to get state models
    evidence_items = evidence_to_items(bundle)

    # Update state with framework-specific models
    state.phases["problem_framing"] = PhaseEntry(
        evidence=evidence_items,
        ...
    )
```

## Architecture Layers

```
┌───────────────────────────────────────────────┐
│  Runtime Layer (nodes/graphs)                 │
│  - Owns SageState, PhaseEntry, GatingContext  │
│  - Calls adapters for translation             │
└────────────────┬──────────────────────────────┘
                 │
┌────────────────▼──────────────────────────────┐
│  Adapter Layer (platform/adapters)            │  ← YOU ARE HERE
│  - Translates DTOs ↔ State Models             │
│  - Pure functions, no business logic          │
│  - Bidirectional conversion                   │
└────────────────┬──────────────────────────────┘
                 │
┌────────────────▼──────────────────────────────┐
│  Core Layer (platform/core)                   │
│  - Pure DTOs (EvidenceBundle, GuardrailResult)│
│  - No state dependencies                      │
└───────────────────────────────────────────────┘
```

## What Goes in Adapters

### Adapter Functions (NOT Classes)

Adapters are simple, stateless translation functions:

**From DTO to State:**
```python
def evidence_to_items(bundle: EvidenceBundle) -> list[EvidenceItem]:
    """Convert DTO evidence dicts to state EvidenceItem models."""
    return [EvidenceItem.model_validate(item) for item in bundle.evidence]

def phase_result_to_entry(result: PhaseResult) -> PhaseEntry:
    """Convert PhaseResult DTO to PhaseEntry state model."""
    return PhaseEntry(
        data=result.data,
        status=result.status,
        evidence=[EvidenceItem.model_validate(e) for e in result.evidence or []],
    )
```

**From State to DTO:**
```python
def items_to_evidence_dicts(items: list[EvidenceItem]) -> list[dict]:
    """Convert state EvidenceItems to plain dicts for DTO."""
    return [
        {"namespace": item.namespace, "key": item.key, "score": item.score}
        for item in items
    ]

def phase_entry_to_result(entry: PhaseEntry, phase_name: str) -> PhaseResult:
    """Convert PhaseEntry state model to PhaseResult DTO."""
    return PhaseResult(
        phase_name=phase_name,
        data=entry.data,
        status=entry.status,
        evidence=items_to_evidence_dicts(entry.evidence),
    )
```

### Helper Functions

Adapters can include convenience helpers for common patterns:

```python
def update_phase_evidence(
    phase_entry: PhaseEntry,
    evidence_bundle: EvidenceBundle,
) -> PhaseEntry:
    """Update phase entry with new evidence from bundle."""
    return PhaseEntry(
        data=phase_entry.data,
        error=phase_entry.error,
        status=phase_entry.status,
        evidence=evidence_to_items(evidence_bundle),
    )
```

## Current Adapters

### `evidence.py`
**Purpose:** Translate between evidence DTOs and state models. Provides runtime wrapper for evidence collection.

**Translation Functions:**
- `evidence_to_items()` - DTO dicts → EvidenceItem models
- `items_to_evidence_dicts()` - EvidenceItem models → DTO dicts
- `update_phase_evidence()` - Merge evidence bundle into phase entry

**Runtime Wrappers:**
- `collect_phase_evidence()` - Wrapper that coordinates core evidence collection with logging

**When to use:** When working with evidence data from core layer in nodes.

### `guardrails.py`
**Purpose:** Translate between guardrail DTOs and gating context. Provides canonical guardrail evaluation entrypoint.

**Translation Functions:**
- `guardrail_to_gating()` - Create GatingContext from GuardrailResult
- `update_gating_guardrail()` - Update existing GatingContext with new guardrail
- `extract_guardrail_summary()` - Extract logging/display summary

**Runtime Wrappers:**
- `evaluate_guardrails_contract()` - Canonical entrypoint that coordinates policy evaluation with config building

**When to use:** When integrating guardrail policy evaluation with state.

### `phases.py`
**Purpose:** Translate between phase DTOs and state models.

**Functions:**
- `phase_result_to_entry()` - PhaseResult DTO → PhaseEntry
- `phase_entry_to_result()` - PhaseEntry → PhaseResult DTO
- `merge_phase_results()` - Merge new results into existing entry
- `extract_phase_summary()` - Extract logging/display summary

**When to use:** When handling phase execution results in nodes.

### `logging.py`
**Purpose:** Provide structured logging wrappers that coordinate with observability layer.

**Functions:**
- `configure_logging()` - Initialize structured logging
- `get_logger()` - Get logger for named component
- `log()` - Emit structured log event

**When to use:** When you need logging in agents, nodes, middlewares, or tools.

### `tools.py`
**Purpose:** Provide tool allowlist building wrapper.

**Functions:**
- `build_allowlist_contract()` - Build canonical tool allowlist including structured output tool

**When to use:** In agent builders when configuring tool allowlists.

### `agents.py`
**Purpose:** Provide agent schema loading and validation wrapper.

**Functions:**
- `validate_agent_schema()` - Load and validate agent OutputSchema with contract enforcement

**When to use:** In agent builders to validate schema before agent construction.

## Adapter Principles

### 1. No Business Logic
Adapters only translate data structure, they don't make decisions:

```python
# GOOD - Simple translation
def guardrail_to_gating(guardrail: GuardrailResult, input: str) -> GatingContext:
    decision = "no-go" if not guardrail.is_safe or not guardrail.is_in_scope else "go"
    return GatingContext(original_input=input, guardrail=guardrail, decision=decision)

# BAD - Business logic in adapter
def guardrail_to_gating(guardrail: GuardrailResult, input: str) -> GatingContext:
    # Re-evaluating guardrails is business logic, not translation
    if "unsafe_keyword" in input:
        guardrail = GuardrailResult(is_safe=False, ...)
    return GatingContext(...)
```

### 2. Bidirectional When Possible
Provide both directions of translation:

```python
# Forward: DTO → State
def phase_result_to_entry(result: PhaseResult) -> PhaseEntry: ...

# Reverse: State → DTO
def phase_entry_to_result(entry: PhaseEntry, name: str) -> PhaseResult: ...
```

### 3. Pure Functions
Adapters should be stateless and deterministic:

```python
# GOOD - Pure function
def evidence_to_items(bundle: EvidenceBundle) -> list[EvidenceItem]:
    return [EvidenceItem.model_validate(item) for item in bundle.evidence]

# BAD - Side effects
_cache = {}
def evidence_to_items(bundle: EvidenceBundle) -> list[EvidenceItem]:
    if bundle not in _cache:  # Stateful caching
        _cache[bundle] = [...]
    return _cache[bundle]
```

### 4. Type Safety
Use type hints to ensure correct translation:

```python
def guardrail_to_gating(
    guardrail: GuardrailResult,  # Core DTO
    original_input: str,
) -> GatingContext:  # State model
    """Type hints enforce the translation boundary."""
    ...
```

## When to Create New Adapters

Create a new adapter file when you:

1. **Add a new DTO** in `core/dto/` that needs state integration
2. **Need bidirectional translation** between DTO and state model
3. **Have repetitive conversion logic** in multiple nodes

**Don't create adapters for:**
- Simple value mapping (use inline code)
- One-time conversions (use inline code)
- Business logic (belongs in core/policy/ or nodes)

## Testing

Adapter tests live in `tests/unit/platform/adapters/`.

Tests verify correct bidirectional translation:

```python
def test_evidence_to_items_converts_dicts_to_models():
    bundle = EvidenceBundle(evidence=[{"namespace": [...], "key": "test", "score": 0.9}])
    items = evidence_to_items(bundle)
    assert len(items) == 1
    assert isinstance(items[0], EvidenceItem)
    assert items[0].key == "test"

def test_round_trip_preserves_data():
    # State → DTO → State should preserve data
    original = PhaseEntry(data={"key": "value"}, status="complete", ...)
    dto = phase_entry_to_result(original, "test")
    restored = phase_result_to_entry(dto)
    assert restored.data == original.data
    assert restored.status == original.status
```

## Benefits

1. **Pure core layer** - DTOs have no state dependencies
2. **Testable boundaries** - Test translation in isolation
3. **Clear contracts** - Explicit conversion points
4. **Type safety** - Compiler catches DTO/State mismatches
5. **Migration path** - Can change state models without touching core

## Related Documentation

- Core layer architecture: `app/platform/core/README.md`
- State models: `app/state/`
- DTOs: `app/platform/core/dto/`

## References

- Hexagonal Architecture: https://alistair.cockburn.us/hexagonal-architecture/
- Data Transfer Objects: https://martinfowler.com/eaaCatalog/dataTransferObject.html
- Adapter Pattern: https://refactoring.guru/design-patterns/adapter

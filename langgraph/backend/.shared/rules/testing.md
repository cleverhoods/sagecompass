# Test Organization Rules

> Extracted from `tests/CLAUDE.md`. Defines test structure, naming, priorities, and quality guidelines.

## Test Organization Principles

### 1. Two-Dimensional Structure

**Rule:** `tests/[test_type]/[category]/[mirrored_structure]`

**Test Types** (execution characteristics):
- `unit/` - Fast, isolated, no external dependencies
- `integration/` - Cross-component, may use test fixtures
- `e2e/` - End-to-end workflows, may use real services

**Test Categories** (what domain/layer):
- `architecture/` - Cross-cutting structural validation (import rules, boundaries)
- `platform/` - Platform layer (hexagonal architecture components)
- `orchestration/` - LangGraph orchestration (agents, nodes, graphs, middlewares, tools, schemas, state)

**Mirrored Structure:**
Within each category, mirror the `app/` directory structure exactly.

### 2. Category Mapping

**architecture** → No app/ equivalent (validates relationships)
- Tests import rules, layer boundaries, folder structure
- Examples: core purity, adapter boundaries, structural integrity

**platform** → `app/platform/`
- Tests hexagonal architecture layer
- Mirrors: core/, adapters/, runtime/, config/, observability/, utils/

**orchestration** → `app/agents/`, `app/nodes/`, `app/graphs/`, `app/middlewares/`, `app/tools/`, `app/schemas/`, `app/state/`
- Tests LangGraph framework components and domain models
- Mirrors all LangGraph orchestration modules and domain definitions

### 3. Mirroring Examples

**Platform category examples:**
```
app/platform/core/contract/phases.py
→ tests/unit/platform/core/contract/test_phases.py

app/platform/adapters/evidence.py
→ tests/unit/platform/adapters/test_evidence.py

app/platform/runtime/state_helpers.py
→ tests/unit/platform/runtime/test_state_helpers.py
```

**Orchestration category examples:**
```
app/nodes/problem_framing.py
→ tests/unit/orchestration/nodes/test_problem_framing.py

app/agents/ambiguity_scan/agent.py
→ tests/unit/orchestration/agents/ambiguity_scan/test_agent.py

app/graphs/graph.py
→ tests/unit/orchestration/graphs/test_graph.py

app/middlewares/dynamic_prompt.py
→ tests/unit/orchestration/middlewares/test_dynamic_prompt.py

app/schemas/ambiguities.py
→ tests/unit/orchestration/schemas/test_ambiguities.py

app/state/__init__.py
→ tests/unit/orchestration/state/test_state.py
```

**Architecture category examples:**
```
Core purity validation
→ tests/unit/architecture/test_core_purity.py

Adapter boundary validation
→ tests/unit/architecture/test_adapter_boundary.py

Platform structure validation
→ tests/unit/architecture/test_platform_structure.py
```

### 4. Separate Tests by Scope

**Unit Tests** (`tests/unit/`)
- Fast (<1ms per test)
- Isolated (no external dependencies)
- Test single functions/classes
- Use mocks/fixtures for dependencies

**Integration Tests** (`tests/integration/`)
- Cross-component workflows
- May use test fixtures (in-memory stores)
- Test component interactions
- Still offline (no live services)

**E2E Tests** (`tests/e2e/`)
- Full pipeline validation
- May require credentials/config
- Test complete workflows
- Use realistic data

**Architecture Tests** (`tests/unit/architecture/`)
- Validate hexagonal architecture rules
- AST-based import checking
- Enforce layer boundaries
- Fast, deterministic

### 5. Test Markers

Use pytest markers to categorize tests:

```python
import pytest

@pytest.mark.unit
def test_pure_function():
    """Unit: Fast, isolated test."""
    pass

@pytest.mark.integration
def test_cross_component_flow():
    """Integration: Tests component interaction."""
    pass

@pytest.mark.architecture
def test_core_purity():
    """Architecture: Validates import rules."""
    pass

@pytest.mark.external_connection
def test_api_call():
    """External: Requires live service."""
    pass
```

## Test Naming Conventions

### File Naming

**Pattern:** `test_<module_name>.py`

**Examples:**
```
app/platform/adapters/evidence.py → test_evidence.py
app/nodes/problem_framing.py → test_problem_framing.py
```

### Function Naming

**Pattern:** `test_<function>_<scenario>_<expected>`

**Examples:**
```python
def test_evidence_to_items_converts_dicts_to_models():
    """Test what + scenario + expected outcome."""
    pass

def test_build_allowlist_includes_schema_name():
    """Clear, descriptive name."""
    pass

def test_validate_agent_schema_raises_when_invalid():
    """Explicit about error cases."""
    pass
```

## What to Test (Priority Order)

### High Priority (Must Test)

1. **Contract Validators** (`platform/core/contract/`)
   - Architectural contracts enforcement
   - Type validation
   - State update validation

2. **Policy Logic** (`platform/core/policy/`)
   - Business rules
   - Guardrail decisions
   - Pure logic functions

3. **Adapter Translations** (`platform/adapters/`)
   - DTO ↔ State conversions
   - Boundary translation correctness
   - Data integrity

4. **Runtime Helpers** (`platform/runtime/`)
   - Evidence hydration
   - Phase state management
   - Critical helper functions

5. **Architecture Rules** (`tests/unit/architecture/`)
   - Import purity
   - Layer boundaries
   - Structural integrity

### Medium Priority (Should Test)

6. **Node Factories** (`nodes/`)
   - State update logic
   - Routing decisions
   - Error handling

7. **Agent Builders** (`agents/`)
   - Schema validation
   - Middleware configuration
   - Tool binding

8. **Schemas** (`schemas/`)
   - Field validation
   - Type constraints
   - Serialization

### Lower Priority (Nice to Have)

9. **Graph Composition** (`graphs/`)
   - Node connections
   - Routing rules
   - Often tested via integration tests

10. **Utilities** (`utils/`)
    - If complex logic exists
    - Otherwise covered by usage tests

## What NOT to Test

**Don't test:**
- Framework code (LangGraph, LangChain internals)
- Simple getters/setters with no logic
- Pass-through functions that just delegate
- Auto-generated code
- Configuration loading (unless validation logic)

## Test Quality Guidelines

### Good Test Characteristics

**Fast** - Unit tests < 1ms, integration < 100ms
**Isolated** - No external dependencies
**Deterministic** - Same input → same output
**Readable** - Clear intent and expectations
**Focused** - One concept per test
**Independent** - Tests don't depend on each other

### Test Structure

Use **Arrange-Act-Assert** pattern:

```python
def test_phase_result_to_entry_converts_dto_to_state():
    # Arrange: Set up test data
    result = PhaseResult(
        phase_name="test_phase",
        data={"key": "value"},
        status="complete",
    )

    # Act: Execute the function
    entry = phase_result_to_entry(result)

    # Assert: Verify expectations
    assert isinstance(entry, PhaseEntry)
    assert entry.data == {"key": "value"}
    assert entry.status == "complete"
```

## Fixtures and Conftest

### Shared Fixtures

Place shared fixtures in `conftest.py` at appropriate levels:

```
tests/conftest.py              # Global fixtures
tests/unit/conftest.py         # All unit test fixtures
tests/unit/platform/conftest.py # Platform-specific fixtures
```

### Fixture Naming

```python
# conftest.py
@pytest.fixture
def sample_evidence_bundle():
    """Provide a standard EvidenceBundle for tests."""
    return EvidenceBundle(
        evidence=[{"namespace": ["test"], "key": "1", "score": 0.9}],
        context_docs=[],
        missing_store=False,
    )
```

## Running Tests

```bash
# Fast unit tests (default)
uv run poe test_unit

# Integration tests
uv run poe test_integration

# Architecture tests only
uv run poe test_architecture

# All tests
uv run poe test_all

# Specific marker
pytest -m architecture

# Specific file
pytest tests/unit/platform/adapters/test_evidence.py

# Specific test
pytest tests/unit/platform/adapters/test_evidence.py::test_evidence_to_items_converts_dicts_to_models
```

## Coverage Expectations

### Minimum Coverage by Layer

- **Architecture tests:** 100% of enforcement rules
- **Contract layer:** >90% (critical validators)
- **Policy layer:** >90% (business logic)
- **Adapter layer:** >80% (boundary translation)
- **Runtime helpers:** >80% (widely used utilities)
- **Nodes/Agents:** >60% (often tested via integration)
- **Overall:** >75%

*Note: Focus on meaningful coverage, not just line coverage.*

## Adding New Tests

When adding tests for a new module:

1. **Create test file** in mirrored location
   ```bash
   # For app/platform/adapters/new_module.py
   touch tests/unit/platform/adapters/test_new_module.py
   ```

2. **Add marker** if needed
   ```python
   import pytest

   pytestmark = pytest.mark.unit  # Mark entire module
   ```

3. **Import module under test**
   ```python
   from app.platform.adapters.new_module import function_to_test
   ```

4. **Write tests** following naming conventions
   ```python
   def test_function_to_test_does_what_when_scenario():
       pass
   ```

5. **Run tests** to verify
   ```bash
   pytest tests/unit/platform/adapters/test_new_module.py -v
   ```

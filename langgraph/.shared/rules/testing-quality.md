# Test Quality (MUST / MUST NOT)

Source: Test quality guidelines for langgraph component.

## MUST

- Keep unit tests < 1ms, integration < 100ms
- Make tests isolated (no external dependencies for unit tests)
- Make tests deterministic (same input → same output)
- Use Arrange-Act-Assert pattern
- Keep tests focused (one concept per test)
- Make tests independent (no inter-test dependencies)

## MUST NOT

- Create slow unit tests (> 1ms)
- Let tests depend on each other's execution order
- Use real external services in unit tests
- Test multiple concepts in one test function

## Arrange-Act-Assert Pattern

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

## Fixtures

- Place shared fixtures in `conftest.py` at appropriate level
- Use descriptive fixture names: `sample_evidence_bundle`, not `fixture1`
- Keep fixtures minimal and focused

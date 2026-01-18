# Test Naming (MUST / MUST NOT)

Source: Test naming conventions for langgraph component.

## MUST

- Name test files as `test_<module_name>.py`
- Name test functions as `test_<function>_<scenario>_<expected>`
- Use pytest markers: `@pytest.mark.unit`, `@pytest.mark.integration`, `@pytest.mark.architecture`
- Make test names describe what + scenario + expected outcome

## MUST NOT

- Use vague names like `test_it_works` or `test_function`
- Skip the `test_` prefix on test functions
- Mix markers inappropriately (e.g., `@pytest.mark.unit` on integration tests)

## File Naming Examples

```
app/platform/adapters/evidence.py → test_evidence.py
app/nodes/problem_framing.py → test_problem_framing.py
```

## Function Naming Examples

```python
def test_evidence_to_items_converts_dicts_to_models():
    """Clear: what + scenario + expected."""

def test_validate_agent_schema_raises_when_invalid():
    """Explicit about error cases."""
```

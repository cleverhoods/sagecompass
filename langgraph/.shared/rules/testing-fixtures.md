# Test Fixtures (MUST / MUST NOT)

## MUST

- Define fixtures in `conftest.py` (pytest auto-discovers them)
- Place fixtures at **lowest directory level** where all consumers exist
- Use factory fixtures for complex objects (return builder function)
- Override fixtures by redefining in nested `conftest.py`

## MUST NOT

- Import fixtures from other test files (only conftest.py)
- Put all fixtures in root `tests/conftest.py` (causes hidden dependencies)
- Create fixture chains across different conftest.py files
- Use `autouse=True` except for truly global setup

## Placement Hierarchy

| Consumers | Location |
|-----------|----------|
| 1 test file | Inline in that file |
| 1 directory | `conftest.py` in that dir |
| 1 category | `conftest.py` at category level |
| Global (rare) | `tests/conftest.py` |

## Factory Pattern

```python
@pytest.fixture
def make_phase_entry():
    def _make(status="complete", data=None):
        return PhaseEntry(status=status, data=data or {})
    return _make
```

## Key Principle

Pytest searches **upward only** for fixtures—never down or sideways. This prevents coupling between unrelated test modules.

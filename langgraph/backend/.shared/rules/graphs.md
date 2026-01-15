# Graphs + phases (MUST / MUST NOT)

Source: `app/RULES.md` → “Graphs + phases”.

## MUST
- Keep graph modules composition-only (`app/graphs/README.md`).
- Route explicitly with `Command(goto=...)` when updating + routing.
- Have a single routing owner per phase (supervisor).
- Build phases from `PhaseContract` (`app/graphs/subgraphs/phases/contract.py`).
- Validate phase registries with `validate_phase_registry` (`app/platform/core/contract/registry.py`).

## MUST NOT
- Use `Send` except for explicit map/reduce patterns.

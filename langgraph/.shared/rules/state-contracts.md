# State + contracts (MUST / MUST NOT)

Source: `app/RULES.md` → “State + contracts”.

## MUST
- Use `SageState` from `app/state/state.py`.
- Keep `GatingContext` for guardrail metadata only; ambiguity lives in `app/state/ambiguity.py`.
- Define routing keys as typed model fields.
- Keep docstrings on `BaseModel` classes and node/graph factory functions.
- Validate state updates with `validate_state_update` (`app/platform/core/contract/state.py`).
- Validate artifact payloads with `ArtifactEnvelope` (`app/platform/core/contract/artifacts.py`).
- Build namespaces with `NamespaceParts`/`build_namespace` (`app/platform/core/contract/namespaces.py`).

## MUST NOT
- Access state via dict fallbacks for routing keys.

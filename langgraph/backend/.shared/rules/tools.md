# Tools (MUST / MUST NOT)

Source: `app/RULES.md` → “Tools”.

## MUST
- Be typed, stateless, and DI-injected.
- Enforce tool allowlists/restrictions in code (middleware/tool wrappers).
- Build allowlists with `build_allowlist_contract` (`app/platform/contract/tools.py`) when tools are bound or injected.
- Make tool calling deterministic; middleware/nodes must inject tool outputs explicitly rather than relying on model-initiated calls.
- Agents may be constructed with empty tool sets; attach tools dynamically to avoid prompt bloat.

## MUST NOT
- Rely on model-initiated tool calls for core logic.

s> Scope: Applies to all files under `langgraph/` unless overridden by a deeper CLAUDE.md.

# LangGraph Contributions (Codex)

For any changes under `langgraph/`, follow the architectural contracts documented in the nearest component guidance and contract sources. Keep contributions aligned with the LangGraph-oriented layout described there and avoid introducing patterns that conflict with the stated state/graph/agent/tool separation.

Key expectations:
- Follow the nearest component guidance and contracts within the specific subsystem you are changing.
- Favor Pythonic readability; avoid import-time side effects and keep module boundaries consistent with the documented folder structure.

Changes outside `langgraph/` are out of scope for this file.
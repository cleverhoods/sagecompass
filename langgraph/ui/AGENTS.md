> Scope: Applies to all files under `langgraph/backend/app/ui/`.

# Gradio UI Contracts (Python)

This UI layer is Gradio-only. Keep it testable, dependency-injected, and free of import-time side effects.

## Runtime + DI
- Do **not** launch Gradio at import time. Expose builder/launcher functions that are invoked explicitly by callers.

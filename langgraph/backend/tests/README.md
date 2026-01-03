# Backend tests

This suite defaults to an **offline lane**:
- it runs against the **real pinned frameworks** (LangChain/LangGraph/Pydantic as installed via `uv.lock`)
- it performs **no network calls**
- it uses deterministic fakes (e.g., `GenericFakeChatModel`, `FakeEmbeddings`) and in-memory persistence (e.g., `InMemorySaver`) where appropriate

We do **not** shadow framework packages via `sys.path` stubs.

## Lanes

- **Offline lane (default):** `UV_NO_SYNC=1 uv run pytest`
- **Real-deps lane:** `uv run pytest -m real_deps`
- **Integration lane (opt-in):** `uv run pytest -m integration` (requires any needed API keys)

## OpenAI integration requirements

OpenAI-backed integration tests require:
- `OPENAI_API_KEY`
- Optional: `OPENAI_MODEL` (defaults to `gpt-4.1-mini` in tests)

They use LangChain's OpenAI integration (`langchain_openai.ChatOpenAI`).
Docs: https://python.langchain.com/docs/integrations/chat/openai/

Testing approach follows `../RULES.md` §12 (LangChain “Test”):
- deterministic unit tests by default
- bounded, opt-in integration tests
- record/replay (VCR) where needed to stabilize external calls

## Layout

Recommended:
- `tests/unit/**` — deterministic, offline tests
- `tests/integration/**` — bounded tests that may hit real services (often paired with VCR cassettes)

Within each, you may mirror the `app/` component layout (agents/nodes/graphs/tools/middlewares) for clarity.

## Running

```bash
# Offline lane (default)
UV_NO_SYNC=1 uv run pytest

# Real-deps lane
uv run pytest -m real_deps

# Integration lane (opt-in)
uv run pytest -m integration
```

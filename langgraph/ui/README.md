# SageCompass UI
Gradio-based UI that drives a LangGraph graph over HTTP.

## Running the demo

1. Start the LangGraph API server so it can expose the `agent` graph:
    
    ```bash
    # Run this from the langgraph/backend folder.
    uv run langgraph dev
    ```

2. Launch the Gradio frontend:

    ```bash
    # Run this from the langgraph/ui folder.
    uv run python -m main
    ```

The UI posts serialized `SageState` payloads to `http://127.0.0.1:2024/runs` by default, so keep the API server running while the chat is open. Use the **Send** button or press Enter to submit new prompts and the **Reset conversation** button to clear the chat history/state.

### Streaming updates

After creating a stateless run the UI subscribes to `/runs/{run_id}/stream`, decodes each SSE payload, and updates the chat history as soon as the backend emits it. The interface now looks like a running assistant instead of showing every status message in a single block.

## Programmatic entry point

Call `ui.main.build_sagecompass_ui()` (or instantiate `ui.main.SageCompassUI`) if you need to embed the UI in a script, point it at a different LangGraph endpoint, or change the host/port before launching.

# langgraph/backend/app/ui/ui.py
from __future__ import annotations

from typing import Any

import gradio as gr

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage

EXAMPLE_MESSAGES = [
    "At Auping can we use support logs, product reviews, and return reasons to identify early signals of quality degradation in certain mattress models before defect rates rise?",
    "Am I cool?",
    "Could we build a single, agency-wide model in our digital marketing - web development agency that forecasts required developer capacity per client per sprint based on project history, tech stack, and ticket complexity, to optimize planning?"
]


class SageCompassUI:
    """
    Minimal Gradio UI for SageCompass that treats SageState as canonical.

    - internal state stores langchain messages
    - handler appends HumanMessage and calls self.app.invoke(payload)
    - Gradio renders chat history; UI tracks langchain messages separately
    """

    def __init__(self, app: Any, host: str = "0.0.0.0", port: int = 1111, inbrowser: bool = True):
        self.app = app
        self.host = host
        self.port = port
        self.inbrowser = inbrowser

    # ---------- Core handler ----------
    def _handle_user_message(self, message: str, _history: list[dict[str, str]], messages: list[BaseMessage]):
        """
        Minimal, direct handler.

        - Expects messages to be a list of langchain messages
        - Returns: (assistant_reply, updated_messages)
        """
        user_message = (message or "").strip()
        if not user_message:
            # nothing to send; render current messages
            return "", messages

        if messages is None:
            messages = []
        messages = list(messages)
        messages.append(HumanMessage(content=user_message))

        # Call graph / app synchronously
        try:
            if hasattr(self.app, "invoke"):
                result = self.app.invoke({"messages": messages, "user_query": user_message}, config={})
            else:
                result = self.app({"messages": messages, "user_query": user_message})
        except Exception:
            import traceback
            print(traceback.format_exc())
            # Make the error visible in UI
            messages = messages + [AIMessage(content="Internal error while running agent. See server logs.")]
            return "", messages

        if isinstance(result, dict):
            messages = [msg for msg in result.get("messages", []) if isinstance(msg, BaseMessage)]

        # Return assistant reply and updated messages
        assistant_reply = ""
        if messages:
            last = messages[-1]
            if isinstance(last, AIMessage):
                assistant_reply = last.content if isinstance(last.content, str) else str(last.content)
        return assistant_reply, messages

    # ---------- UI / Launch ----------
    def launch(self):
        """Build and launch a minimal Gradio Blocks UI."""
        messages = gr.State([])
        demo = gr.ChatInterface(
            fn=self._handle_user_message,
            title="SageCompass",
            examples=[[example, []] for example in EXAMPLE_MESSAGES],
            additional_inputs=[messages],
            additional_outputs=[messages],
        )

        demo.launch(
            server_name=self.host,
            server_port=self.port,
            share=False,
            inbrowser=self.inbrowser,
        )

if __name__ == "__main__":
    main()

from __future__ import annotations

from typing import Any, Dict, List

import gradio as gr

from app.state import SageState
from app.ui.state import init_state, summarize_problem_frame
from app.ui.i18n import TranslationService


class SageCompassUI:
    """
    Gradio UI wrapper for the SageCompass LangGraph app.

    Responsibilities:
    - Render a minimal chat UI.
    - Invoke the graph with the latest user query.
    - Surface the updated problem frame to the user.
    """

    def __init__(self, app):
        self.app = app
        self.i18n = TranslationService()

    def _run_graph(self, state: SageState) -> SageState:
        result = self.app.invoke(state)
        return result  # type: ignore[return-value]

    def handle_user_question(
        self,
        user_message: str,
        history: List[Dict[str, Any]] | None,
        state: SageState | None,
    ):
        history = history or []
        state = state or init_state()

        user_message = (user_message or "").strip()
        if not user_message:
            return history, state, gr.update(value="")

        inferred_lang = self.i18n.infer_user_lang(user_message)

        state = init_state()
        state["user_query"] = user_message
        state["user_lang"] = inferred_lang  # fallback; graph may overwrite

        history.append({"role": "user", "content": user_message})

        state = self._run_graph(state)

        if not (state.get("user_lang") or "").strip():
            state["user_lang"] = inferred_lang

        assistant_text = self.i18n.translate_text(state, summarize_problem_frame(state))
        history.append({"role": "assistant", "content": assistant_text})

        return history, state, gr.update(value="")

    def launch(self):
        with gr.Blocks(title="SageCompass") as demo:
            gr.Markdown("# SageCompass")

            chatbot = gr.Chatbot(label="Conversation", height=400)
            state = gr.State(init_state())

            gr.Markdown("---")

            with gr.Row():
                msg = gr.Textbox(
                    label="Your question",
                    placeholder="Ask SageCompass…",
                    scale=4,
                )
                submit_btn = gr.Button("Submit", variant="primary")

            submit_btn.click(
                fn=self.handle_user_question,
                inputs=[msg, chatbot, state],
                outputs=[chatbot, state, msg],
            )

        demo.launch(
            server_name="0.0.0.0",
            server_port=1111,
            share=False,
            inbrowser=True,
        )

from __future__ import annotations

from typing import Any

import gradio as gr

from streamer import (
    DEFAULT_ASSISTANT,
    DEFAULT_API_URL,
    DEFAULT_HOST,
    DEFAULT_INBROWSER,
    DEFAULT_PORT,
    SageCompassStreamer,
)

EXAMPLE_MESSAGES = [
    "At Auping can we use support logs, product reviews, and return reasons to identify early signals of quality degradation in certain mattress models before defect rates rise?",
    "Am I cool?",
    "Could we build a single, agency-wide model in our digital marketing - web development agency that forecasts required developer capacity per client per sprint based on project history, tech stack, and ticket complexity, to optimize planning?",
]

CSS = """
#progress_md {
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 12px;
  padding: 12px 14px;
  font-size: 0.95rem;
  line-height: 1.35rem;
}
#progress_md ul { margin: 6px 0 0 18px; }
#progress_md strong { display: inline-block; margin-bottom: 4px; }
"""


class SageCompassUI:
    """Gradio chat surface that drives a LangGraph API backend."""

    def __init__(
        self,
        api_url: str = DEFAULT_API_URL,
        assistant_id: str = DEFAULT_ASSISTANT,
        host: str = DEFAULT_HOST,
        port: int = DEFAULT_PORT,
        inbrowser: bool = DEFAULT_INBROWSER,
    ):
        self.streamer = SageCompassStreamer(api_url=api_url, assistant_id=assistant_id)
        self.host = host
        self.port = port
        self.inbrowser = inbrowser

    def _submit(
        self,
        user_message: str,
        history: list[dict[str, str]] | None,
        state: dict[str, Any] | None,
    ):
        # streamer.stream(...) must yield 5 outputs:
        # (chatbot_value, history_holder, state_holder, message_box_value, progress_md)
        yield from self.streamer.stream(user_message, state)

    def _stream_response(
        self,
        user_message: str,
        history: list[dict[str, str]] | None,
        state: dict[str, Any] | None,
    ):
        yield from self._submit(user_message, history, state)

    def launch(self) -> None:
        """Build and launch the Gradio chat interface."""
        with gr.Blocks(title="SageCompass") as demo:
            gr.Markdown("## SageCompass")

            # ✅ Gradio 6.3.0 Chatbot already expects messages (list of dicts),
            # so DO NOT pass type="messages".
            chatbot = gr.Chatbot(
                render_markdown=True,
                line_breaks=True,
                layout="panel",
                height=420,
            )

            message_box = gr.Textbox(
                placeholder="Describe your project or request...",
                label="Send a message",
                lines=1,
                max_lines=4,
            )
            send_button = gr.Button("Send")
            clear_button = gr.Button("Reset conversation")
            history_holder = gr.State([])
            state_holder = gr.State({})

            # ✅ Progress panel: Accordion + Markdown (bold headers + bullets)
            with gr.Accordion("Progress", open=True):
                chain_of_thought_log = gr.Markdown(value="", elem_id="progress_md")

            send_action = self._stream_response

            message_box.submit(
                send_action,
                inputs=[message_box, history_holder, state_holder],
                outputs=[
                    chatbot,
                    history_holder,
                    state_holder,
                    message_box,
                    chain_of_thought_log,
                ],
                queue=True,
            )
            send_button.click(
                send_action,
                inputs=[message_box, history_holder, state_holder],
                outputs=[
                    chatbot,
                    history_holder,
                    state_holder,
                    message_box,
                    chain_of_thought_log,
                ],
                queue=True,
            )
            clear_button.click(
                lambda: ([], [], {}, "", ""),
                inputs=[],
                outputs=[
                    chatbot,
                    history_holder,
                    state_holder,
                    message_box,
                    chain_of_thought_log,
                ],
            )

        # ✅ Gradio 6 moved css= here
        demo.launch(
            server_name=self.host,
            server_port=self.port,
            share=False,
            inbrowser=self.inbrowser,
            css=CSS,
        )


def build_sagecompass_ui(
    *,
    api_url: str | None = None,
    assistant_id: str = DEFAULT_ASSISTANT,
    host: str = DEFAULT_HOST,
    port: int = DEFAULT_PORT,
    inbrowser: bool = DEFAULT_INBROWSER,
) -> SageCompassUI:
    return SageCompassUI(
        api_url=api_url or DEFAULT_API_URL,
        assistant_id=assistant_id,
        host=host,
        port=port,
        inbrowser=inbrowser,
    )


def main() -> None:
    build_sagecompass_ui().launch()


if __name__ == "__main__":
    main()

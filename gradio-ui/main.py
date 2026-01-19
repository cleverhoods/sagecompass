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
    StreamUpdate,
)

EXAMPLE_MESSAGES = [
    {"text": "At our bed manufacturing company can we use support logs, product reviews, and return reasons to identify early signals of quality degradation in certain mattress models before defect rates rise?"},
    {"text": "Fawzy variable"},
    {"text": "Could we build a single, agency-wide model in our digital marketing - web development agency that forecasts required developer capacity per client per sprint based on project history, tech stack, and ticket complexity, to optimize planning?"},
]

CSS = """
#phase_header {
  background: rgba(255,255,255,0.05);
  border-radius: 8px;
  padding: 8px 12px;
  margin-bottom: 12px;
  font-size: 0.9rem;
}
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

    def _stream_response(
        self,
        user_message: str,
        state: dict[str, Any] | None,
    ):
        """Stream responses, yielding Gradio outputs for each update."""
        for update in self.streamer.stream(user_message, state):
            # Unpack StreamUpdate into Gradio outputs:
            # (chatbot, state, textbox, phase)
            yield update.messages, update.state, "", update.phase

    def _on_example_select(self, evt: gr.SelectData):
        v = evt.value
        if isinstance(v, dict):
            return v.get("text", "")
        return str(v)

    def launch(self) -> None:
        """Build and launch the Gradio chat interface."""
        with gr.Blocks(title="SageCompass") as demo:
            gr.Markdown("## SageCompass")

            # Phase indicator header (at top)
            phase_indicator = gr.Markdown(value="**Phase:** \u2014", elem_id="phase_header")

            # Gradio 6.3.0 Chatbot already expects messages (list of dicts),
            # so DO NOT pass type="messages".
            chatbot = gr.Chatbot(
                render_markdown=True,
                line_breaks=True,
                layout="panel",
                height=420,
                examples=EXAMPLE_MESSAGES,
            )

            message_box = gr.Textbox(
                placeholder="Describe your project or request...",
                label="Send a message",
                lines=1,
                max_lines=4,
            )
            send_button = gr.Button("Send")
            clear_button = gr.Button("Reset conversation")
            state_holder = gr.State({})

            inputs = [message_box, state_holder]
            outputs = [chatbot, state_holder, message_box, phase_indicator]

            message_box.submit(
                self._stream_response,
                inputs=inputs,
                outputs=outputs,
                queue=True,
            )
            send_button.click(
                self._stream_response,
                inputs=inputs,
                outputs=outputs,
                queue=True,
            )
            clear_button.click(
                lambda: ([], {}, "", "**Phase:** \u2014"),
                inputs=[],
                outputs=outputs,
            )

            chatbot.example_select(
                self._on_example_select,
                inputs=None,
                outputs=message_box,
            ).then(
                self._stream_response,
                inputs=inputs,
                outputs=outputs,
                queue=True,
            )

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

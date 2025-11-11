import gradio as gr
import json

class SageCompassUI:
    def __init__(self, app):
        self.app = app

    def chat(self, message, _history=None):
        result = self.app.ask(message)
        # Convert dict result to pretty JSON string for Gradio display
        if isinstance(result, dict):
            result = json.dumps(result, indent=2)
        return result

    def launch(self):
        demo = gr.ChatInterface(
            fn=self.chat,
            title="SageCompass",
            theme=gr.themes.Soft(
                primary_hue="blue",
                neutral_hue="gray",
                font=[gr.themes.GoogleFont("Inter"), "sans-serif"]
            ),
            examples=[],
            description="SageCompass reasoning interface",
        )

        demo.launch(server_name="0.0.0.0", server_port=8000, share=False, inbrowser=True)
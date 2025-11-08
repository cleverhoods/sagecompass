import gradio as gr

class SageCompassUI:
    def __init__(self, app):
        self.app = app

    def chat(self, message, _history=None):
        return self.app.ask(message)

    def launch(self):
        demo = gr.ChatInterface(fn=self.chat, title="SageCompass")
        demo.launch(server_name="0.0.0.0", server_port=8000)
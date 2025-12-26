from __future__ import annotations

from dataclasses import dataclass

import gradio as gr


@dataclass
class HilpButtons:
    yes: gr.Button
    no: gr.Button
    unknown: gr.Button
    run: gr.Button


def build_hilp_buttons() -> HilpButtons:
    with gr.Row():
        yes = gr.Button("Yes (Igen)", visible=False)
        no = gr.Button("No (Nem)", visible=False)
        unknown = gr.Button("I’m not sure (Nem tudom)", visible=False)

    run = gr.Button(
        "Run with these clarifications",
        variant="primary",
        visible=False,
    )

    return HilpButtons(
        yes=yes,
        no=no,
        unknown=unknown,
        run=run,
    )

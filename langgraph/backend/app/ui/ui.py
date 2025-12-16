from __future__ import annotations

from typing import Any, Dict, List

import gradio as gr

from app.state import SageState

from app.ui.state import (
    get_hilp_block,
    get_hilp_request,
    init_state,
    is_hilp_active,
    summarize_problem_frame,
)
from app.ui.hilp import (
    build_hilp_markdown,
    pick_next_unanswered_question,
    question_dropdown_choices,
    status_labels_for_lang,
)
from app.ui.i18n import TranslationService


class SageCompassUI:
    """
    Gradio UI wrapper for the SageCompass LangGraph app.

    Responsibilities in this file:
    - Gradio component wiring
    - Graph invocation
    - High-level flow decisions (normal vs HILP)
    """

    def __init__(self, app):
        self.app = app
        self.i18n = TranslationService()

    # ----- LangGraph runner -----

    def _run_graph(self, state: SageState) -> SageState:
        result = self.app.invoke(state)
        return result  # type: ignore[return-value]

    # ----- Gradio callbacks -----

    def handle_user_question(
        self,
        user_message: str,
        history: List[Dict[str, Any]] | None,
        state: SageState | None,
    ):
        history = history or []
        if state is None or not state:
            state = init_state()

        user_message = (user_message or "").strip()
        if not user_message:
            return (
                history,
                state,
                gr.update(visible=False),  # HILP markdown
                gr.update(choices=[], value=None, visible=False),  # dropdown
                gr.update(visible=False),  # Yes
                gr.update(visible=False),  # No
                gr.update(visible=False),  # Unknown
                gr.update(visible=False),  # Run with clarifications
                gr.update(visible=True),   # textbox
                gr.update(visible=True),   # submit
            )

        inferred_lang = self.i18n.infer_user_lang(user_message)

        state = init_state()
        state["user_query"] = user_message
        state["user_lang"] = inferred_lang  # fallback; graph may overwrite

        state = self._run_graph(state)

        if not (state.get("user_lang") or "").strip():
            state["user_lang"] = inferred_lang

        history.append({"role": "user", "content": user_message})

        req = get_hilp_request(state)
        hilp_active = is_hilp_active(state)

        if hilp_active and req:
            req = self.i18n.translate_hilp_request(state, req)

            hilp_block = get_hilp_block(state)
            hilp_answers = dict(hilp_block.get("hilp_answers") or {})

            hilp_md = build_hilp_markdown(req, hilp_answers)
            hilp_md = self.i18n.translate_text(state, hilp_md)

            status_labels = status_labels_for_lang(state.get("user_lang") or "en")
            choices = question_dropdown_choices(req, hilp_answers, status_labels=status_labels)
            selected_qid = pick_next_unanswered_question(req, hilp_answers)

            history.append({"role": "assistant", "content": req.get("prompt", "")})

            return (
                history,
                state,
                gr.update(value=hilp_md, visible=True),
                gr.update(choices=choices, value=selected_qid, visible=True),
                gr.update(visible=True),
                gr.update(visible=True),
                gr.update(visible=True),
                gr.update(visible=True),
                gr.update(visible=False),
                gr.update(visible=False),
            )

        assistant_text = self.i18n.translate_text(state, summarize_problem_frame(state))
        history.append({"role": "assistant", "content": assistant_text})

        return (
            history,
            state,
            gr.update(visible=False),
            gr.update(choices=[], value=None, visible=False),
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=True),
            gr.update(visible=True),
        )

    def handle_hilp_answer(
        self,
        answer_value: str,
        history: List[Dict[str, Any]] | None,
        state: SageState | None,
        selected_qid: str | None,
    ):
        history = history or []
        state = state or init_state()

        hilp_block = get_hilp_block(state)
        req = get_hilp_request(state)
        if not req:
            return (
                history,
                state,
                gr.update(visible=False),
                gr.update(visible=False),
            )

        req = self.i18n.translate_hilp_request(state, req)

        answers: Dict[str, str] = dict(hilp_block.get("hilp_answers") or {})

        if not selected_qid:
            selected_qid = pick_next_unanswered_question(req, answers)

        if selected_qid:
            answers[selected_qid] = answer_value

        hilp_block["hilp_answers"] = answers
        state["hilp"] = hilp_block  # type: ignore[assignment]

        hilp_md = build_hilp_markdown(req, answers)
        hilp_md = self.i18n.translate_text(state, hilp_md)

        status_labels = status_labels_for_lang(state.get("user_lang") or "en")
        choices = question_dropdown_choices(req, answers, status_labels=status_labels)
        next_qid = pick_next_unanswered_question(req, answers)

        return (
            history,
            state,
            gr.update(value=hilp_md, visible=True),
            gr.update(choices=choices, value=next_qid or selected_qid, visible=True),
        )

    def handle_run_with_clarifications(
        self,
        history: List[Dict[str, Any]] | None,
        state: SageState | None,
    ):
        history = history or []
        state = state or init_state()

        state = self._run_graph(state)

        req = get_hilp_request(state)
        hilp_active = is_hilp_active(state)

        if hilp_active and req:
            req = self.i18n.translate_hilp_request(state, req)

            hilp_block = get_hilp_block(state)
            answers: Dict[str, str] = dict(hilp_block.get("hilp_answers") or {})

            hilp_md = build_hilp_markdown(req, answers)
            hilp_md = self.i18n.translate_text(state, hilp_md)

            status_labels = status_labels_for_lang(state.get("user_lang") or "en")
            choices = question_dropdown_choices(req, answers, status_labels=status_labels)
            selected_qid = pick_next_unanswered_question(req, answers)

            msg = "Thanks, I still need a bit more clarification. Please answer the remaining questions."
            history.append({"role": "assistant", "content": self.i18n.translate_text(state, msg)})

            return (
                history,
                state,
                gr.update(value=hilp_md, visible=True),
                gr.update(choices=choices, value=selected_qid, visible=True),
                gr.update(visible=True),
                gr.update(visible=True),
                gr.update(visible=True),
                gr.update(visible=True),
                gr.update(visible=False),
                gr.update(visible=False),
            )

        assistant_text = self.i18n.translate_text(state, summarize_problem_frame(state))
        history.append({"role": "assistant", "content": assistant_text})

        return (
            history,
            state,
            gr.update(visible=False),
            gr.update(choices=[], value=None, visible=False),
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=True),
            gr.update(visible=True),
        )

    # ----- Launch -----

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

            hilp_md = gr.Markdown(visible=False)

            question_dropdown = gr.Dropdown(
                label="Select question to answer",
                choices=[],
                value=None,
                visible=False,
            )

            with gr.Row():
                btn_yes = gr.Button("Yes (Igen)", visible=False)
                btn_no = gr.Button("No (Nem)", visible=False)
                btn_unknown = gr.Button("I’m not sure (Nem tudom)", visible=False)

            run_btn = gr.Button(
                "Run with these clarifications",
                variant="primary",
                visible=False,
            )

            submit_btn.click(
                fn=self.handle_user_question,
                inputs=[msg, chatbot, state],
                outputs=[
                    chatbot,
                    state,
                    hilp_md,
                    question_dropdown,
                    btn_yes,
                    btn_no,
                    btn_unknown,
                    run_btn,
                    msg,
                    submit_btn,
                ],
            )

            btn_yes.click(
                lambda h, s, qid: self.handle_hilp_answer("yes", h, s, qid),
                inputs=[chatbot, state, question_dropdown],
                outputs=[chatbot, state, hilp_md, question_dropdown],
            )

            btn_no.click(
                lambda h, s, qid: self.handle_hilp_answer("no", h, s, qid),
                inputs=[chatbot, state, question_dropdown],
                outputs=[chatbot, state, hilp_md, question_dropdown],
            )

            btn_unknown.click(
                lambda h, s, qid: self.handle_hilp_answer("unknown", h, s, qid),
                inputs=[chatbot, state, question_dropdown],
                outputs=[chatbot, state, hilp_md, question_dropdown],
            )

            run_btn.click(
                fn=self.handle_run_with_clarifications,
                inputs=[chatbot, state],
                outputs=[
                    chatbot,
                    state,
                    hilp_md,
                    question_dropdown,
                    btn_yes,
                    btn_no,
                    btn_unknown,
                    run_btn,
                    msg,
                    submit_btn,
                ],
            )

        demo.launch(
            server_name="0.0.0.0",
            server_port=1111,
            share=False,
            inbrowser=True,
        )

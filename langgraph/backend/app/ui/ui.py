from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import gradio as gr

from app.state import SageState

from app.ui.buttons import HilpButtons, build_hilp_buttons
from app.ui.state import ensure_thread_id, init_state, init_ui_meta, normalize_state, summarize_problem_frame
from app.ui.hilp import (
    build_hilp_markdown,
    pick_next_unanswered_question,
    question_dropdown_choices,
)


@dataclass
class UIControls:
    chatbot: gr.Chatbot
    state: gr.State
    ui_meta: gr.State
    message: gr.Textbox
    submit: gr.Button
    hilp_md: gr.Markdown
    question_dropdown: gr.Dropdown
    hilp_buttons: HilpButtons


def _build_input_row() -> Tuple[gr.Textbox, gr.Button]:
    with gr.Row():
        msg = gr.Textbox(
            label="Your question",
            placeholder="Ask SageCompass…",
            scale=4,
        )
        submit_btn = gr.Button("Submit", variant="primary")
    return msg, submit_btn


def _build_hilp_section() -> Tuple[gr.Markdown, gr.Dropdown, HilpButtons]:
    hilp_md = gr.Markdown(visible=False)

    question_dropdown = gr.Dropdown(
        label="Select question to answer",
        choices=[],
        value=None,
        visible=False,
    )

    hilp_buttons = build_hilp_buttons()
    return hilp_md, question_dropdown, hilp_buttons


def _submit_outputs(ctrls: UIControls) -> List[Any]:
    return [
        ctrls.chatbot,
        ctrls.state,
        ctrls.ui_meta,
        ctrls.hilp_md,
        ctrls.question_dropdown,
        ctrls.hilp_buttons.yes,
        ctrls.hilp_buttons.no,
        ctrls.hilp_buttons.unknown,
        ctrls.hilp_buttons.run,
        ctrls.message,
        ctrls.submit,
    ]


def _hilp_answer_outputs(ctrls: UIControls) -> List[Any]:
    return [
        ctrls.chatbot,
        ctrls.state,
        ctrls.ui_meta,
        ctrls.hilp_md,
        ctrls.question_dropdown,
    ]


class SageCompassUI:
    """
    Gradio UI wrapper for the SageCompass LangGraph app.

    Responsibilities:
    - Render a chat UI that supports HILP interrupts.
    - Invoke the graph, surface interrupt payloads, and resume with user answers.
    """

    def __init__(self, app: Any):
        self.app = app

    # ----- UI helpers -----

    def _hilp_hidden_updates(self) -> Tuple[gr.Update, gr.Update, gr.Update, gr.Update, gr.Update, gr.Update]:
        """Return a consistent set of updates when HILP controls should be hidden."""
        return (
            gr.update(visible=False),  # HILP markdown
            gr.update(choices=[], value=None, visible=False),  # dropdown
            gr.update(visible=False),  # Yes
            gr.update(visible=False),  # No
            gr.update(visible=False),  # Unknown
            gr.update(visible=False),  # Run with clarifications
        )

    def _hilp_visible_updates(
        self,
        *,
        markdown: str,
        choices: List[Tuple[str, str]],
        selected_qid: Optional[str],
    ) -> Tuple[gr.Update, gr.Update, gr.Update, gr.Update, gr.Update, gr.Update]:
        """Return a consistent set of updates when HILP controls should be shown."""
        return (
            gr.update(value=markdown, visible=True),
            gr.update(choices=choices, value=selected_qid, visible=True),
            gr.update(visible=True),
            gr.update(visible=True),
            gr.update(visible=True),
            gr.update(visible=True),
        )

    def _input_updates(self, *, enabled: bool) -> Tuple[gr.Update, gr.Update]:
        """Toggle message textbox and submit button visibility."""
        return (
            gr.update(visible=enabled),
            gr.update(visible=enabled),
        )

    # ----- LangGraph helpers -----

    def _extract_interrupt(self, obj: Any) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Best-effort extraction of interrupt payloads across sync/streaming runs.
        Returns (payload, interrupt_id) when detected, else (None, None).
        """
        if obj is None:
            return None, None

        def _metadata_id(candidate: Any) -> Optional[str]:
            meta = getattr(candidate, "metadata", None)
            if isinstance(meta, dict):
                return meta.get("interrupt_id") or meta.get("checkpoint_id")
            return None

        # Exception-shaped
        for attr in ("interrupt", "interrupts", "value", "data", "payload"):
            if hasattr(obj, attr):
                val = getattr(obj, attr)
                if val:
                    iid = (
                        getattr(obj, "interrupt_id", None)
                        or getattr(obj, "id", None)
                        or _metadata_id(obj)
                    )
                    if isinstance(val, list) and val:
                        return val[0], iid
                    if isinstance(val, dict):
                        return val, iid
        # Dict-shaped events
        if isinstance(obj, dict):
            metadata = obj.get("metadata") or {}
            iid = obj.get("interrupt_id") or obj.get("id") or metadata.get("interrupt_id")
            for key in ("interrupt", "value", "data", "payload"):
                if key in obj and obj[key]:
                    val = obj[key]
                    if isinstance(val, list) and val:
                        return val[0], iid
                    if isinstance(val, dict):
                        return val, iid
            if obj.get("event") == "interrupt":
                data = obj.get("data") or obj.get("value") or obj.get("interrupt")
                if data:
                    if isinstance(data, list) and data:
                        data = data[0]
                    return data, iid

        return None, None

    def _extract_state(self, event: Any, current: Optional[SageState]) -> Optional[SageState]:
        """Extract state payloads from streaming events when available."""
        if isinstance(event, dict):
            if event.get("event") == "values":
                data = event.get("data") or event.get("value")
                if isinstance(data, dict):
                    return data
            for key in ("data", "value", "state"):
                candidate = event.get(key)
                if isinstance(candidate, dict):
                    return candidate

        for attr in ("data", "value", "state"):
            if hasattr(event, attr):
                candidate = getattr(event, attr)
                if isinstance(candidate, dict):
                    return candidate

        return current

    def _run_graph_until_interrupt(
        self,
        state: SageState,
        *,
        ui_meta: Dict[str, Any],
        resume_value: Any | None = None,
    ) -> Tuple[SageState, Optional[Dict[str, Any]], Optional[str]]:
        """
        Run the graph and stop when an interrupt is encountered.
        Returns (state, interrupt_payload, interrupt_id).
        """
        thread_id = ensure_thread_id(ui_meta)
        config: Dict[str, Any] = {"configurable": {"thread_id": thread_id}}
        if ui_meta.get("pending_interrupt_id"):
            config["interrupt_id"] = ui_meta["pending_interrupt_id"]

        runner_input = resume_value if resume_value is not None else state

        try:
            if hasattr(self.app, "stream_events"):
                final_state: Optional[SageState] = None
                for event in self.app.stream_events(runner_input, config=config):
                    payload, iid = self._extract_interrupt(event)
                    if payload is not None:
                        return final_state or state, payload, iid or config.get("interrupt_id")
                    final_state = self._extract_state(event, final_state)
                if final_state is not None:
                    return final_state, None, None

            if hasattr(self.app, "stream"):
                final_state = None
                for event in self.app.stream(runner_input, config=config, stream_mode="values"):
                    payload, iid = self._extract_interrupt(event)
                    if payload is not None:
                        return final_state or state, payload, iid or config.get("interrupt_id")
                    final_state = self._extract_state(event, final_state)
                if final_state is not None:
                    return final_state, None, None

            result = self.app.invoke(runner_input, config=config)
            payload, iid = self._extract_interrupt(result)
            if payload is not None:
                return state, payload, iid or config.get("interrupt_id")
            return result, None, None
        except Exception as exc:  # pragma: no cover - defensive for real runtime
            payload, iid = self._extract_interrupt(exc)
            if payload is not None:
                return state, payload, iid or config.get("interrupt_id")
            raise

    # ----- Gradio callbacks -----

    def handle_user_question(
        self,
        user_message: str,
        history: List[Dict[str, Any]] | None,
        state: SageState | None,
        ui_meta: Dict[str, Any] | None,
    ):
        history = history or []
        state = normalize_state(state)
        ui_meta = ui_meta or init_ui_meta()

        user_message = (user_message or "").strip()
        if not user_message:
            return (
                history,
                state,
                ui_meta,
                *self._hilp_hidden_updates(),
                *self._input_updates(enabled=True),
            )

        ensure_thread_id(ui_meta)

        state["user_query"] = user_message
        state["messages"] = list(state.get("messages") or [])
        state["messages"].append({"role": "user", "content": user_message})
        history.append({"role": "user", "content": user_message})
        state, interrupt_payload, interrupt_id = self._run_graph_until_interrupt(state, ui_meta=ui_meta)
        state = normalize_state(state)
        state["user_query"] = state.get("user_query") or user_message

        if interrupt_payload:
            ui_meta["pending_interrupt"] = interrupt_payload
            ui_meta["pending_interrupt_id"] = interrupt_id
            ui_meta["hilp_answers"] = {}

            hilp_md = build_hilp_markdown(interrupt_payload, {})
            choices = question_dropdown_choices(interrupt_payload, {})
            selected_qid = choices[0][1] if choices else None

            history.append(
                {
                    "role": "assistant",
                    "content": "I need a quick clarification before proceeding.",
                }
            )

            return (
                history,
                state,
                ui_meta,
                *self._hilp_visible_updates(markdown=hilp_md, choices=choices, selected_qid=selected_qid),
                *self._input_updates(enabled=False),
            )

        ui_meta["pending_interrupt"] = None
        ui_meta["pending_interrupt_id"] = None
        ui_meta["hilp_answers"] = {}

        assistant_text = summarize_problem_frame(state)
        history.append({"role": "assistant", "content": assistant_text})
        state["messages"].append({"role": "assistant", "content": assistant_text})

        return (
            history,
            state,
            ui_meta,
            *self._hilp_hidden_updates(),
            *self._input_updates(enabled=True),
        )

    def handle_hilp_answer(
        self,
        answer_value: str,
        history: List[Dict[str, Any]] | None,
        state: SageState | None,
        ui_meta: Dict[str, Any] | None,
        selected_qid: str | None,
    ):
        history = history or []
        state = normalize_state(state)
        ui_meta = ui_meta or init_ui_meta()
        ensure_thread_id(ui_meta)
        req = ui_meta.get("pending_interrupt") or {}

        answers: Dict[str, str] = dict(ui_meta.get("hilp_answers") or {})

        if not selected_qid:
            selected_qid = pick_next_unanswered_question(req, answers)

        if selected_qid:
            answers[selected_qid] = answer_value
        ui_meta["hilp_answers"] = answers

        hilp_md = build_hilp_markdown(req, answers)
        choices = question_dropdown_choices(req, answers)
        next_qid = pick_next_unanswered_question(req, answers)

        return (
            history,
            state,
            ui_meta,
            gr.update(value=hilp_md, visible=bool(hilp_md)),
            gr.update(choices=choices, value=next_qid or selected_qid, visible=bool(choices)),
        )

    def handle_run_with_clarifications(
        self,
        history: List[Dict[str, Any]] | None,
        state: SageState | None,
        ui_meta: Dict[str, Any] | None,
    ):
        history = history or []
        state = normalize_state(state)
        ui_meta = ui_meta or init_ui_meta()
        ensure_thread_id(ui_meta)

        req = ui_meta.get("pending_interrupt") or {}
        answers: Dict[str, str] = dict(ui_meta.get("hilp_answers") or {})
        answers_list = [{"question_id": qid, "answer": ans} for qid, ans in answers.items()]

        user_query = state.get("user_query", "")
        state, interrupt_payload, interrupt_id = self._run_graph_until_interrupt(
            state,
            ui_meta=ui_meta,
            resume_value={"answers": answers_list},
        )
        state = normalize_state(state)
        state["user_query"] = state.get("user_query") or user_query

        if interrupt_payload:
            ui_meta["pending_interrupt"] = interrupt_payload
            ui_meta["pending_interrupt_id"] = interrupt_id
            ui_meta["hilp_answers"] = answers  # keep existing

            hilp_md = build_hilp_markdown(interrupt_payload, answers)
            choices = question_dropdown_choices(interrupt_payload, answers)
            selected_qid = pick_next_unanswered_question(interrupt_payload, answers)

            history.append(
                {
                    "role": "assistant",
                    "content": "Thanks, I still need a bit more clarification. Please answer the remaining questions.",
                }
            )

            return (
                history,
                state,
                ui_meta,
                *self._hilp_visible_updates(
                    markdown=hilp_md,
                    choices=choices,
                    selected_qid=selected_qid,
                ),
                *self._input_updates(enabled=False),
            )

        ui_meta["pending_interrupt"] = None
        ui_meta["pending_interrupt_id"] = None
        ui_meta["hilp_answers"] = {}

        assistant_text = summarize_problem_frame(state)
        history.append({"role": "assistant", "content": assistant_text})
        state["messages"].append({"role": "assistant", "content": assistant_text})

        return (
            history,
            state,
            ui_meta,
            *self._hilp_hidden_updates(),
            *self._input_updates(enabled=True),
        )

    # ----- Launch -----

    def launch(self):
        with gr.Blocks(title="SageCompass") as demo:
            gr.Markdown("# SageCompass")

            chatbot = gr.Chatbot(label="Conversation", height=400)
            state = gr.State(init_state())
            ui_meta = gr.State(init_ui_meta())

            gr.Markdown("---")

            msg, submit_btn = _build_input_row()
            hilp_md, question_dropdown, hilp_buttons = _build_hilp_section()

            ctrls = UIControls(
                chatbot=chatbot,
                state=state,
                ui_meta=ui_meta,
                message=msg,
                submit=submit_btn,
                hilp_md=hilp_md,
                question_dropdown=question_dropdown,
                hilp_buttons=hilp_buttons,
            )

            submit_btn.click(
                fn=self.handle_user_question,
                inputs=[msg, chatbot, state, ui_meta],
                outputs=_submit_outputs(ctrls),
            )

            hilp_buttons.yes.click(
                lambda h, s, meta, qid: self.handle_hilp_answer("yes", h, s, meta, qid),
                inputs=[chatbot, state, ui_meta, question_dropdown],
                outputs=_hilp_answer_outputs(ctrls),
            )

            hilp_buttons.no.click(
                lambda h, s, meta, qid: self.handle_hilp_answer("no", h, s, meta, qid),
                inputs=[chatbot, state, ui_meta, question_dropdown],
                outputs=_hilp_answer_outputs(ctrls),
            )

            hilp_buttons.unknown.click(
                lambda h, s, meta, qid: self.handle_hilp_answer("unknown", h, s, meta, qid),
                inputs=[chatbot, state, ui_meta, question_dropdown],
                outputs=_hilp_answer_outputs(ctrls),
            )

            hilp_buttons.run.click(
                fn=self.handle_run_with_clarifications,
                inputs=[chatbot, state, ui_meta],
                outputs=_submit_outputs(ctrls),
            )

        demo.launch(
            server_name="0.0.0.0",
            server_port=1111,
            share=False,
            inbrowser=True,
        )

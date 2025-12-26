from __future__ import annotations

import gradio as gr

from app.ui.hilp import build_hilp_markdown, pick_next_unanswered_question, question_dropdown_choices
from app.ui.state import init_state, init_ui_meta
from app.ui.ui import SageCompassUI


class _InterruptingApp:
    def __init__(self, payload):
        self.payload = payload

    def stream(self, runner_input, *, config, stream_mode):
        yield {"event": "interrupt", "data": self.payload, "id": "hilp-1"}


class _CompletingApp:
    def stream(self, runner_input, *, config, stream_mode):
        return iter([])

    def invoke(self, runner_input, config=None):
        user_query = ""
        if isinstance(runner_input, dict):
            user_query = runner_input.get("user_query", "")
        return {
            "messages": runner_input.get("messages", []) if isinstance(runner_input, dict) else [],
            "user_query": user_query,
            "phases": {
                "problem_framing": {
                    "status": "complete",
                    "data": {
                        "business_domain": "logistics",
                        "primary_outcome": "fewer delays",
                    },
                }
            },
        }


def test_handle_user_question_surfaces_hilp_interrupt():
    payload = {
        "phase": "problem_framing",
        "reason": "Need quick confirmation",
        "questions": [{"id": "q1", "text": "Is this B2B?"}],
    }
    ui = SageCompassUI(_InterruptingApp(payload))

    (
        history,
        state,
        ui_meta,
        hilp_md,
        question_dropdown,
        btn_yes,
        btn_no,
        btn_unknown,
        run_btn,
        msg_update,
        submit_update,
    ) = ui.handle_user_question("Hello", None, None, None)

    assert ui_meta["pending_interrupt"] == payload
    assert ui_meta["pending_interrupt_id"] == "hilp-1"
    assert history[-1]["role"] == "assistant"
    assert hilp_md.visible is True
    assert question_dropdown.visible is True
    assert btn_yes.visible is True
    assert btn_no.visible is True
    assert btn_unknown.visible is True
    assert run_btn.visible is True
    assert msg_update.visible is False
    assert submit_update.visible is False
    assert state["phases"] == {}
    assert state["user_query"] == "Hello"


def test_handle_hilp_answer_tracks_answers_and_next_question():
    payload = {
        "phase": "problem_framing",
        "questions": [
            {"id": "q1", "text": "Is this regulated?"},
            {"id": "q2", "text": "Is the data sensitive?"},
        ],
    }
    ui_meta = init_ui_meta()
    ui_meta["pending_interrupt"] = payload
    ui = SageCompassUI(_InterruptingApp(payload))

    (
        history,
        state,
        updated_meta,
        hilp_md,
        dropdown_update,
    ) = ui.handle_hilp_answer("yes", [], init_state(), ui_meta, selected_qid="q1")

    assert updated_meta["hilp_answers"]["q1"] == "yes"
    assert "Q1" in hilp_md.value
    assert "Yes" in hilp_md.value
    assert dropdown_update.value == pick_next_unanswered_question(payload, {"q1": "yes"})
    assert history == []
    assert state["phases"] == {}


def test_handle_run_with_clarifications_resumes_and_clears_interrupt():
    payload = {
        "phase": "problem_framing",
        "questions": [{"id": "q1", "text": "Is this regulated?"}],
    }
    ui_meta = init_ui_meta()
    ui_meta["pending_interrupt"] = payload
    ui_meta["pending_interrupt_id"] = "hilp-1"
    ui_meta["hilp_answers"] = {"q1": "yes"}

    ui = SageCompassUI(_CompletingApp())

    (
        history,
        state,
        updated_meta,
        hilp_md,
        question_dropdown,
        btn_yes,
        btn_no,
        btn_unknown,
        run_btn,
        msg_update,
        submit_update,
    ) = ui.handle_run_with_clarifications([], init_state(), ui_meta)

    assert updated_meta["pending_interrupt"] is None
    assert updated_meta["pending_interrupt_id"] is None
    assert updated_meta["hilp_answers"] == {}
    assert "Business domain: logistics" in history[-1]["content"]
    assert hilp_md.visible is False
    assert question_dropdown.visible is False
    assert btn_yes.visible is False
    assert btn_no.visible is False
    assert btn_unknown.visible is False
    assert run_btn.visible is False
    assert msg_update.visible is True
    assert submit_update.visible is True
    assert state["phases"]["problem_framing"]["data"]["business_domain"] == "logistics"
    assert state["phases"]["problem_framing"]["data"]["primary_outcome"] == "fewer delays"


def test_handle_user_question_sets_user_query_and_summarizes():
    ui = SageCompassUI(_CompletingApp())

    (
        history,
        state,
        ui_meta,
        hilp_md,
        question_dropdown,
        btn_yes,
        btn_no,
        btn_unknown,
        run_btn,
        msg_update,
        submit_update,
    ) = ui.handle_user_question("How can I improve logistics?", [], init_state(), init_ui_meta())

    assert state["user_query"] == "How can I improve logistics?"
    assert history[-1]["role"] == "assistant"
    assert "Business domain: logistics" in history[-1]["content"]
    assert hilp_md.visible is False
    assert question_dropdown.visible is False
    assert btn_yes.visible is False
    assert btn_no.visible is False
    assert btn_unknown.visible is False
    assert run_btn.visible is False
    assert msg_update.visible is True
    assert submit_update.visible is True


def test_markdown_and_dropdown_render_answers():
    payload = {
        "phase": "problem_framing",
        "reason": "Need confirmation",
        "confidence": 0.42,
        "questions": [
            {"id": "q1", "text": "Is this B2B?"},
            {"id": "q2", "text": "Is this regulated?"},
        ],
    }
    answers = {"q1": "yes", "q2": "unknown"}

    markdown = build_hilp_markdown(payload, answers)
    choices = question_dropdown_choices(payload, answers)

    assert "Q1 (`q1`)" in markdown
    assert "Yes" in markdown
    assert "I’m not sure" in markdown
    assert "Run with these clarifications" in markdown
    assert choices[0][0].endswith("[answered]")
    assert choices[1][0].endswith("[answered]")

from __future__ import annotations

from app.state import PhaseEntry, SageState


def test_sagestate_declares_core_keys():
    ann = SageState.__annotations__

    assert "messages" in ann
    assert "user_query" in ann
    assert "phases" in ann
    assert "user_lang" in ann
    assert "errors" in ann


def test_phase_entry_accepts_hilp_metadata():
    ann = PhaseEntry.__annotations__

    assert "data" in ann
    assert "status" in ann
    assert "hilp_meta" in ann
    assert "hilp_clarifications" in ann

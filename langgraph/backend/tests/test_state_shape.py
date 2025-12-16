from __future__ import annotations

from app.state import SageState


def test_sagestate_declares_hilp_fields():
    ann = SageState.__annotations__

    assert "messages" in ann
    assert "user_query" in ann
    assert "phases" in ann

    assert "hilp_request" in ann
    assert "hilp_round" in ann
    assert "hilp_answers" in ann
    assert "errors" in ann

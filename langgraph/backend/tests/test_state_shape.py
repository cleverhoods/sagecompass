from __future__ import annotations

from app.state import Hilp, SageState


def test_sagestate_declares_hilp_block():
    ann = SageState.__annotations__

    assert "messages" in ann
    assert "user_query" in ann
    assert "phases" in ann
    assert "hilp" in ann
    assert "errors" in ann


def test_hilp_block_contract_keys():
    hilp_ann = Hilp.__annotations__

    assert "hilp_request" in hilp_ann
    assert "hilp_round" in hilp_ann
    assert "hilp_answers" in hilp_ann
    assert "proceed_anyway" in hilp_ann

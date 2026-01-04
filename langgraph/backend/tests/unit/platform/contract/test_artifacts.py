from __future__ import annotations

from datetime import UTC, datetime

import pytest

from app.platform.contract import ArtifactEnvelope, ArtifactProvenance, EvidencePointer

pytestmark = pytest.mark.compliance


def _provenance() -> ArtifactProvenance:
    return ArtifactProvenance(
        model_id="openai:gpt-4.1-mini",
        prompt_id="prompt-1",
        evidence=[EvidencePointer(namespace=("app", "context"), key="ctx-1")],
    )


def test_artifact_envelope_accepts_utc_timestamp() -> None:
    envelope = ArtifactEnvelope(
        schema_version="1",
        timestamp_utc=datetime.now(UTC),
        provenance=_provenance(),
        payload={"result": "ok"},
    )

    assert envelope.timestamp_utc.tzinfo is not None


def test_artifact_envelope_rejects_naive_timestamp() -> None:
    with pytest.raises(ValueError):
        ArtifactEnvelope(
            schema_version="1",
            timestamp_utc=datetime.now(),
            provenance=_provenance(),
            payload={"result": "ok"},
        )

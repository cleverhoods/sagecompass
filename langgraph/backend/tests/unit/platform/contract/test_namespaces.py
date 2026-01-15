from __future__ import annotations

import pytest

from app.platform.core.contract.namespaces import NamespaceParts, build_namespace

pytestmark = pytest.mark.compliance


def test_build_namespace_omits_empty_tenant() -> None:
    parts = NamespaceParts(
        app="sage",
        tenant=None,
        thread="thread-1",
        phase="problem_framing",
        artifact_type="events",
    )

    assert build_namespace(parts) == (
        "sage",
        "thread-1",
        "problem_framing",
        "events",
    )


def test_build_namespace_includes_tenant() -> None:
    parts = NamespaceParts(
        app="sage",
        tenant="tenant-1",
        thread="thread-1",
        phase="problem_framing",
        artifact_type="events",
    )

    assert build_namespace(parts) == (
        "sage",
        "tenant-1",
        "thread-1",
        "problem_framing",
        "events",
    )

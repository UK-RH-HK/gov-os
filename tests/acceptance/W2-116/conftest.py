"""Fixtures of the W2-116 acceptance tests (README): a case's box, the two stand-in endpoints, the planted project."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_116_support as support  # noqa: E402


@pytest.fixture
def box(tmp_path):
    reason = support.lacking()
    if reason:
        pytest.skip(reason)
    return support.make_box(tmp_path / "box")


@pytest.fixture
def embedder():
    """The build's endpoint (``OLLAMA_HOST``): records every text, can hold its answers."""
    stand_in = support.Embedder()
    yield stand_in
    stand_in.close()


@pytest.fixture
def questions():
    """The questions' endpoint (``GOV_QUERY_OLLAMA_HOST``): never held, so a search is never kept waiting by a build."""
    stand_in = support.Embedder()
    yield stand_in
    stand_in.close()


@pytest.fixture
def env(box, embedder, questions):
    return support.environment(box, embedder.host, questions.host)


@pytest.fixture
def project(box):
    """The project at H1 on ``integrate``, with no store."""
    return support.make_project(box)

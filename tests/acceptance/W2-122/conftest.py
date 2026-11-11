"""Fixtures of the W2-122 acceptance tests (README): a case's box, the stand-in embedder, a base and a tree."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_122_support as support  # noqa: E402


@pytest.fixture
def box(tmp_path):
    reason = support.lacking()
    if reason:
        pytest.skip(reason)
    return support.make_box(tmp_path / "box")


@pytest.fixture
def embedder():
    """The stand-in embedding endpoint, healthy, reporting the pinned revision; closed afterwards."""
    stand_in = support.OllamaStandIn()
    yield stand_in
    stand_in.close()


@pytest.fixture
def env(box, embedder):
    return support.environment(box, embedder.host)


@pytest.fixture
def base(box, env, embedder):
    """A base built cold at commit 1 (its record and stores under its own ``.gov-runtime/``)."""
    project = support.make_base(box)
    support.built(project, env)
    embedder.forget()
    return project


@pytest.fixture
def tree(box, base):
    """The same project at commit 2 (one file changed, one removed, one added), with no store."""
    return support.make_tree(box, base)

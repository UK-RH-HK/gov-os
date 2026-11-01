"""Fixtures of the W2-97 acceptance tests (README): a planted repository, its queue folder and its stubs."""

from __future__ import annotations

import shutil

import pytest

import w2_97_support as S


@pytest.fixture
def q(tmp_path):
    """A planted repository (``main`` and ``w2/integrate`` at H0), its queue, work and stub folders; nothing queued."""
    if shutil.which("git") is None:
        pytest.skip("no git on PATH: no repository can be planted")
    planted = S.Planted(tmp_path)
    yield planted
    shutil.rmtree(planted.work, ignore_errors=True)

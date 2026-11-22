"""Fixtures for the W2-22 acceptance tests (the doctor's Claude Code drift fix, DEC-1227 D6 (a))."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_22_support as support  # noqa: E402


@pytest.fixture(autouse=True)
def codegraph_folders():
    """Once the case is over, the code index's daemon folder of any project it built goes (as W1-27's suite)."""
    since = support.codegraph.mark()
    yield
    support.codegraph.release(since)


@pytest.fixture()
def sandbox(tmp_path):
    """The home, temporary, bin and launcher folders ``gov`` runs with (W1-07)."""
    return support.base.make_sandbox(tmp_path / "sandbox")

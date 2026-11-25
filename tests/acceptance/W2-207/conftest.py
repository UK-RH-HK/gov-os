"""Fixtures for the W2-207 acceptance tests: one planted machine per test, under its tmp_path."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_207_support as support  # noqa: E402


@pytest.fixture
def env(tmp_path):
    e = support.Env(tmp_path / "w2-207")
    e.prices()
    return e

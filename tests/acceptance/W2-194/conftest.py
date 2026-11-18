"""Fixtures for W2-194's acceptance tests (absent reds against the base, a short --base, accepted reds when
scoped). The planted projects are W2-193's (its ``w2_193_support``, shared by name)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "W2-193"))

import w2_193_support as support  # noqa: E402


@pytest.fixture()
def sandbox(tmp_path):
    return support.sandbox_at(tmp_path)

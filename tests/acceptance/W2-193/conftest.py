"""Fixtures for W2-193's acceptance tests (gov close's harness in an adopted repository)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_193_support as support  # noqa: E402


@pytest.fixture()
def sandbox(tmp_path):
    return support.sandbox_at(tmp_path)

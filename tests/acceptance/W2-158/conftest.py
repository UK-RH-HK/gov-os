"""Fixtures for the W2-158 acceptance tests (``gov check --structural``)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_158_support as support  # noqa: E402


def pytest_configure(config):
    config.addinivalue_line("markers", "local_only: measures this machine's real hardware; no W2-158 case is marked so")


@pytest.fixture
def tree(tmp_path):
    """A planted git tree, HOME and records folder; every process a case left is killed at the end."""
    planted = support.Tree(tmp_path)
    try:
        yield planted
    finally:
        planted.cleanup()

"""Fixtures for the W2-157 acceptance tests (the GPU backstop)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_157_support as support  # noqa: E402


def pytest_configure(config):
    config.addinivalue_line("markers", "local_only: measures this machine's real hardware; no W2-157 case is marked so")


@pytest.fixture
def machine(tmp_path):
    """A planted HOME and project, stand-ins and child processes, all stopped and removed at the end of the test."""
    m = support.Machine(tmp_path)
    try:
        yield m
    finally:
        m.cleanup()

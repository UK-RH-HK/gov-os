"""Fixtures for the W2-121b acceptance tests: one planted project per test, in the test's temporary folder.

No model, no network: ``gov dispatch`` runs as a child process on the tree under test; the landing command is a stub
(``w2_121b_support.Landing``). A stub left running is killed (by pid) and every slot lock the test held is released when
the test ends.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_121b_support as support  # noqa: E402


def pytest_configure(config):
    config.addinivalue_line("markers", "local_only: starts a real session or model on this machine; not for CI")


@pytest.fixture
def landing(tmp_path):
    planted = support.Landing(tmp_path)
    try:
        yield planted
    finally:
        planted.cleanup()

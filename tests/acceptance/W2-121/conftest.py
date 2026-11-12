"""Fixtures for the W2-121 acceptance tests: one planted project per test, in the test's temporary folder.

No model, no network, no GPU: ``gov dispatch`` runs as a child process on the tree under test (``PYTHONPATH`` its
``src``), with the stub launch command and notifier of ``w2_121_support``. A session a stub left running is killed
(by pid) when the test ends.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_121_support as support  # noqa: E402


def pytest_configure(config):
    config.addinivalue_line("markers", "local_only: starts a real session or model on this machine; not for CI")


@pytest.fixture
def project(tmp_path):
    planted = support.Project(tmp_path)
    try:
        yield planted
    finally:
        planted.cleanup()

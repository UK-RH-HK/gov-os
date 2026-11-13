"""Fixtures for the W2-159 acceptance tests: one planted project per test, in the test's temporary folder.

No model, no network, no live session: ``gov session-watch stop-check`` runs as a child process on the tree under test
(``PYTHONPATH`` its ``src``) against files planted in ``tmp_path``, with the process list, the clock and the ``gov``
program replaced by the test overrides of the ticket's Interface.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_159_support as support  # noqa: E402


def pytest_configure(config):
    config.addinivalue_line("markers", "local_only: starts a real session or model on this machine; not for CI")


@pytest.fixture
def w(tmp_path):
    return support.Watch(tmp_path)

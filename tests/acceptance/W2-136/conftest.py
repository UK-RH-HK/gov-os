"""Fixtures for the W2-136 acceptance tests: a planted ticket store per test, in the test's temporary folder.

No model, no network, no GPU: ``gov plan`` runs as a child process on the tree under test (``PYTHONPATH`` its
``src``), with no ``GOV_*`` or ``GIT_*`` variable of the session running the tests.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_136_support as support  # noqa: E402


@pytest.fixture
def planted(tmp_path):
    """``planted(tickets, files=(), name="repo", order=None)``: a new store under the test's folder."""
    def make(tickets, files=(), name="repo", order=None, **kw):
        return support.build(tmp_path / name, tickets, files, order, **kw)
    return make

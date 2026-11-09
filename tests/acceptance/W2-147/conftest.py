"""Fixtures for W2-147's acceptance tests: in process, no model, no network, no GPU; planted stores in the test's
temporary folder only. ``GOV_*`` and ``GIT_*`` variables of the session running the tests are cleared."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
if not os.environ.get("PYTHONPATH"):  # without one, the worktree's own src
    sys.path.insert(0, str(HERE.parents[2] / "src"))


@pytest.fixture(autouse=True)
def _clean_env(monkeypatch):
    for key in [k for k in os.environ if k.startswith(("GOV_", "GIT_"))]:
        monkeypatch.delenv(key)

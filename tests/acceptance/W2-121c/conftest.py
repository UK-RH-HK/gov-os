"""Fixtures for the W2-121c acceptance tests: one fixture machine per test, under its ``tmp_path``.

No model, no network, never the real ``~/.gov-os``: every ``gov`` child runs with a ``HOME`` in the test's folder.
Processes the test started are killed, and a lock it holds is released, when the test ends.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_121c_support as support  # noqa: E402


@pytest.fixture
def box(tmp_path):
    machine = support.Box(tmp_path / "w2-121c")
    try:
        yield machine
    finally:
        machine.cleanup()

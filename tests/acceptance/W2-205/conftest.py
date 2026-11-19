"""Fixtures for the W2-205 acceptance tests: one fixture machine per test, under its ``tmp_path``.

No model, no network, never the real ``~/.gov-os`` and never the machine's real load: every ``gov`` child and every
hook runs with a ``HOME`` in the test's folder. Processes the test started are killed when the test ends.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_205_support as support  # noqa: E402


@pytest.fixture
def box(tmp_path):
    machine = support.Home(tmp_path / "w2-205")
    try:
        yield machine
    finally:
        machine.cleanup()


@pytest.fixture
def make_rig(tmp_path):
    """The relaunch fixture (a launch sandbox and a fixture machine on one HOME), for a lead's address."""
    made = []

    def make(lead):
        rig = support.Rig(tmp_path, lead)
        made.append(rig)
        return rig

    try:
        yield make
    finally:
        for rig in made:
            rig.cleanup()

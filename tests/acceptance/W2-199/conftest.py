"""Fixtures for the W2-199 acceptance tests: one fixture machine per test, under its ``tmp_path``.

No model, no network, never the real ``~/.gov-os`` and never the machine's real load: every ``gov`` child runs with a
``HOME`` in the test's folder and a planted loadavg file. Processes the test started are released and killed when the
test ends.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_199_support as support  # noqa: E402


@pytest.fixture
def box(tmp_path):
    """The 20-CPU machine (the owner's), configuration file with ``heavy_slots: 2``, load 3.0."""
    machine = support.Machine(tmp_path / "w2-199")
    try:
        yield machine
    finally:
        machine.cleanup()


@pytest.fixture
def make_box(tmp_path):
    """A factory for machines of other profiles; each is cleaned up."""
    made = []

    def make(profile=support.PROFILE_20, heavy_slots=2):
        machine = support.Machine(tmp_path / f"w2-199-{len(made)}", profile=profile, heavy_slots=heavy_slots)
        made.append(machine)
        return machine

    try:
        yield make
    finally:
        for machine in made:
            machine.cleanup()

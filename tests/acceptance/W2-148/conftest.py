"""Fixtures for the W2-148 acceptance tests (the operator agent; DEC-1104 (2), OPERATOR-AGENT-1).

``world`` is a fresh planted world per test (w2_148_support.World): an operator root with the install copied from this
tree's ``governance/project/operator/`` and its APPROVED, a live planted repository with a bare remote, a live planted
HOME, the CTO's scratch, a transcripts folder, a clock file, stub channels and stubs for claude, crontab and sudo on
PATH. Nothing outside the temporary folder is touched. The case marked ``live`` (none in the default run) would start
a real claude session.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_148_support as support  # noqa: E402


def pytest_configure(config):
    config.addinivalue_line("markers", "live: needs a real claude session; never in the default run")


@pytest.fixture()
def world(tmp_path):
    return support.World(tmp_path / "w").build()

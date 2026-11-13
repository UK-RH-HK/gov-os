"""W2-23 fixtures: every case plants its own repository, HOME and temporary folder under pytest's ``tmp_path``."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

HERE = str(Path(__file__).resolve().parent)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import w2_23_support as support  # noqa: E402


def pytest_configure(config):
    config.addinivalue_line("markers", "local_only: a case that cannot run in CI (README, 'Cases out of CI')")


@pytest.fixture
def box(tmp_path):
    return support.make_box(tmp_path / "box")


@pytest.fixture
def project(tmp_path):
    """The programme's repository, committed, with ignored untracked files of the owner's (no code graph)."""
    return support.plant_project(tmp_path / "harbour")

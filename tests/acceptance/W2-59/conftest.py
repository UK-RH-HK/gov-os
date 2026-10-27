"""W2-59 acceptance fixtures: one stand-in pin per session, built from this worktree (README)."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_59_support as support  # noqa: E402


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "local_only: needs the gitleaks binary of this machine (the retrieval-regression check indexes a "
                   "temporary dev tier); not for CI")


@pytest.fixture(scope="session")
def stand_in():
    """The stand-in pin: this worktree's wheel, installed non-editable in its own environment, instrumented."""
    base = support.short_temporary_folder("w259-pin-")
    try:
        yield support.make_stand_in(base)
    finally:
        shutil.rmtree(base, ignore_errors=True)


@pytest.fixture
def pin_markers(stand_in):
    """The stand-in's marker folder, emptied before the case."""
    stand_in.clear_markers()
    return stand_in


@pytest.fixture(scope="session")
def gitleaks():
    """The gitleaks binary of this machine, found on the test runner's own ``PATH``; the case is skipped without it."""
    found = shutil.which("gitleaks")
    if found is None:
        pytest.skip("gitleaks is not installed: the retrieval-regression check cannot index a dev tier")
    return Path(found).resolve()

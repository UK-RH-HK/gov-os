"""Fixtures of the W2-126 acceptance tests (README): the code under test, a stand-in embedder, a box of folders."""

from __future__ import annotations

import os
import subprocess
import sys

import pytest

import w2_126_support as S


def pytest_configure(config):
    config.addinivalue_line("markers", "local_only: needs this machine's dev tiers (GOV_DEV_TIERS); never in CI")


@pytest.fixture(scope="session", autouse=True)
def code_under_test():
    """Every child process imports ``gov`` from this repository's own ``src/`` (DEC-732)."""
    done = subprocess.run([sys.executable, "-c", "import gov; print(gov.__file__)"], capture_output=True, text=True,
                          env={"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "PYTHONPATH": str(S.SRC)})
    origin = done.stdout.strip()
    assert origin.startswith(str(S.SRC) + os.sep), f"gov is imported from {origin!r}, not from {S.SRC}"
    return origin


@pytest.fixture
def stand_in():
    server = S.StandIn()
    yield server
    server.close()


@pytest.fixture
def box(tmp_path, stand_in):
    reason = S.lacking()
    if reason:
        pytest.skip(reason)
    return S.Box(tmp_path / "box", stand_in)

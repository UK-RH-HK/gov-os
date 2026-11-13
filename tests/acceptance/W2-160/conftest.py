"""Fixtures for the W2-160 acceptance tests: stand-in jobs, a folder of job files, a planted project root.

No model, no network, no live session: ``gov wait`` and ``gov session-watch helper-watch`` run as child processes on the tree
under test (``PYTHONPATH`` its ``src``) against files planted in ``tmp_path``; every stand-in process is killed and reaped by
its pid in the ``procs`` fixture's teardown.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_160_support as support  # noqa: E402


def pytest_configure(config):
    config.addinivalue_line("markers", "local_only: starts a real session or model on this machine; not for CI")


@pytest.fixture
def procs():
    stand_ins = support.Procs()
    yield stand_ins
    stand_ins.close()


@pytest.fixture
def wait(tmp_path):
    return support.Wait(tmp_path)


@pytest.fixture
def w(tmp_path):
    return support.Watch(tmp_path)

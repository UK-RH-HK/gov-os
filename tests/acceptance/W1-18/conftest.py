"""Fixtures for the W1-18 acceptance tests."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w1_18_support as support  # noqa: E402


def pytest_configure(config):
    config.addinivalue_line("markers", "local_only: needs the real Ollama daemon on this machine; not for CI")


@pytest.fixture(scope="session")
def module():
    """The files of the Ollama lifecycle module, once the ticket has written them."""
    reason = None
    try:
        return support.module_paths()
    except support.ModuleMissing as exc:
        reason = str(exc)
    pytest.fail(reason, pytrace=False)


@pytest.fixture()
def stage(module, tmp_path):
    """This test's stand-ins and child environment. Every stand-in process is ended afterwards."""
    stage = support.Stage(tmp_path / "stage")
    try:
        yield stage
    finally:
        stage.close()

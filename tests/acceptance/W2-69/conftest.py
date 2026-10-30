"""Fixtures for the W2-69 acceptance tests."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_69_support as support  # noqa: E402


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "local_only: runs the gitleaks or codebase-memory binary of this machine; not for CI")


@pytest.fixture()
def sandbox(tmp_path):
    """HOME, TMPDIR and the test's own folder, in this test's temporary folder; removed after the test."""
    made = support.make_sandbox(tmp_path / "w2-69")
    yield made
    shutil.rmtree(made.base, ignore_errors=True)


@pytest.fixture()
def project(sandbox):
    """A project with the kernel's ``.gitleaks.toml`` and an empty runtime folder."""
    return support.make_check_project(sandbox)


@pytest.fixture()
def stand_in(sandbox):
    """The stand-in gitleaks, first on PATH when a case asks for it."""
    return support.install_stand_in(sandbox)


@pytest.fixture(scope="session")
def slots(tmp_path_factory, request):
    """The folder of the lock files that bound this suite's heavy check runs across xdist workers: the folder all
    workers' temporary folders share (pytest keeps and removes it as it keeps its own)."""
    base = tmp_path_factory.getbasetemp()
    under_xdist = hasattr(request.config, "workerinput")
    return (base.parent if under_xdist else base) / "w2-69-slots"

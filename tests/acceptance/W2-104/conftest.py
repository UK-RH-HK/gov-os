"""Fixtures for the W2-104 acceptance tests: a temporary project, a sandbox and the stub model."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_104_support as support  # noqa: E402


@pytest.fixture()
def project(tmp_path):
    """A small committed project built from scratch; skills are planted in it by each case."""
    return support.make_project(tmp_path / "project")


@pytest.fixture()
def sandbox(tmp_path):
    """HOME, TMPDIR, the bytecode cache and an unrelated folder, outside the project."""
    return support.make_sandbox(tmp_path / "sandbox")


@pytest.fixture()
def stub(tmp_path):
    """The stub ``claude``, in a folder of its own that the cases put first on PATH."""
    return support.install_stub(tmp_path / "stub")

"""Fixtures for the W2-100 acceptance tests: a temporary project and the stub model (both in pytest's tmp_path)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_100_support as support  # noqa: E402


@pytest.fixture()
def project(tmp_path):
    """A small committed project built from scratch; skills are planted in it by each case."""
    return support.make_project(tmp_path / "project")


@pytest.fixture()
def base(tmp_path):
    """The folder holding HOME, TMPDIR and the bytecode cache of a gov run, outside the project."""
    return tmp_path / "sandbox"


@pytest.fixture()
def stub(tmp_path):
    """The stub ``claude``, alone in a folder of its own that the cases put first on PATH."""
    return support.install_stub(tmp_path / "stub")

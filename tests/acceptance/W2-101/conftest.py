"""Fixtures for the W2-101 acceptance tests: a temporary project and the stub model, both under ``tmp_path``."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_101_support as support  # noqa: E402


@pytest.fixture()
def project(tmp_path):
    """A small committed project built from scratch; parts are planted in it by each case."""
    return support.make_project(tmp_path / "project")


@pytest.fixture()
def stub(tmp_path):
    """The stub ``claude``, in a folder of its own that the cases put first on PATH."""
    return support.install_stub(tmp_path / "stub")

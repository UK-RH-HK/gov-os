"""Fixtures for the W1-50 acceptance tests."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w1_50_support as support  # noqa: E402

check_support = support.check_support


@pytest.fixture()
def sandbox(tmp_path):
    """``HOME``, the system temporary directory and an unrelated directory, all outside the project."""
    return check_support.make_sandbox(tmp_path / "sandbox")


@pytest.fixture()
def project(tmp_path):
    """A committed project on ``main`` with a clean working tree and the fixture tickets, all in progress."""
    return check_support.make_project(tmp_path / "project")

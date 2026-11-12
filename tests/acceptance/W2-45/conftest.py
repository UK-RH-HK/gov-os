"""Fixtures for the W2-45 acceptance tests (``gov check`` runner semantics and scale)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_45_support as support  # noqa: E402


@pytest.fixture(scope="session")
def code_under_test():
    """The ``gov`` the cases start is this repository's ``src/``, found from this folder's location (DEC-732)."""
    assert (support.SRC / "gov" / "__init__.py").is_file(), f"no gov package under {support.SRC}"
    return support.SRC


@pytest.fixture()
def project(tmp_path, code_under_test):
    """A temporary git repository built from scratch, with one commit and no declared check."""
    built = support.Project(tmp_path / "project")
    built.commit_all("initial project")
    return built

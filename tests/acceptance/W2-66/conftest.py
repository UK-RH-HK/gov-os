"""Fixtures for W2-66's acceptance tests (path-scoped regression at close)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_66_support as support  # noqa: E402


@pytest.fixture()
def sandbox(tmp_path):
    return support.cli_support.make_sandbox(tmp_path / "sandbox")


@pytest.fixture()
def fixture(tmp_path):
    """The fixture project with the default test map and a green base."""
    return support.Fixture(tmp_path / "project", tmp_path / "told")


@pytest.fixture()
def make_fixture(tmp_path):
    """Builds the fixture project with other arguments: ``make_fixture(test_map=..., green=...)``."""
    def make(**keys):
        return support.Fixture(tmp_path / "project", tmp_path / "told", **keys)
    return make


@pytest.fixture(scope="module")
def module_dir(tmp_path_factory, request):
    """A folder for a module's shared close (one close, several cases that read it)."""
    return tmp_path_factory.mktemp(request.module.__name__.rsplit(".", 1)[-1])

"""Fixtures for the W1-34 acceptance tests."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w1_34_support as support  # noqa: E402


@pytest.fixture(scope="session")
def form():
    """The decision-package template: the one file a package is written from."""
    return support.form()


@pytest.fixture(scope="session")
def package_text():
    """The text of every decision-package template file, the form and anything published beside it."""
    return support.joined(support.package_files())


@pytest.fixture(scope="session")
def record_text():
    """The text of every decision-record template file."""
    return support.joined(support.record_files())

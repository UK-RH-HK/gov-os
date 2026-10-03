"""Fixtures for the W1-48 acceptance tests."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w1_48_support as support  # noqa: E402


def pytest_configure(config):
    config.addinivalue_line("markers", "local_only: needs a tool installed on this machine; not for CI")


def _load(loader):
    try:
        return loader()
    except support.Missing as exc:
        reason = str(exc)
    pytest.fail(reason, pytrace=False)


@pytest.fixture(scope="session")
def registry():
    """The project's tool registry (W1-06), parsed from the working tree."""
    return _load(support.load_registry)


@pytest.fixture(scope="session")
def schema():
    """The tool-registry schema of the kernel template (W1-04), parsed."""
    return _load(support.load_schema)


@pytest.fixture(scope="session")
def decisions():
    """The entries of ``docs/DECISION_REGISTER.md``, by id."""
    return _load(support.load_decisions)

"""Fixtures for the W1-12 acceptance tests."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w1_12_support as support  # noqa: E402


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "local_only: runs the openspec binary under Node v22.23.3 (DEC-202); not for CI")


def built(make):
    """What ``make`` returns, or a plain failure with its reason when the ticket has not built it yet."""
    reason = None
    try:
        return make()
    except support.Missing as exc:
        reason = str(exc)
    pytest.fail(reason, pytrace=False)


@pytest.fixture()
def get():
    """Calls a support function; a missing deliverable is a plain failure with its reason."""
    return built


@pytest.fixture()
def schema(get):
    """``schema.yaml`` of the forked schema, once the ticket has written it."""
    return get(support.schema_doc)


@pytest.fixture()
def project(get, tmp_path):
    """A product project in a temporary directory, holding the template's ``openspec/`` folder.

    Nothing is installed by a test: without the openspec binary the test is skipped.
    """
    if support.openspec_bin() is None:
        pytest.skip("openspec is not installed under Node v22.23.3 on this machine")
    return get(lambda: support.Project(tmp_path))

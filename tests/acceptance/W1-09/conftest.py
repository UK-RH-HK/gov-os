"""Fixtures for the W1-09 acceptance tests."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w1_09_support as support  # noqa: E402


@pytest.fixture(scope="session")
def api(tmp_path_factory):
    """The public interface of ``gov.tasks``; every test that uses it fails here until it exists."""
    interface = support.Api(tmp_path_factory.mktemp("w1-09-api"))
    reason = None
    try:
        interface.exists()
    except support.TasksMissing as exc:
        reason = str(exc)
    if reason:
        pytest.fail(reason, pytrace=False)
    return interface


@pytest.fixture()
def project(api, tmp_path):
    """This test's own temporary project: a git repository with no ticket yet."""
    return support.Project(tmp_path / "project", api)


@pytest.fixture(scope="session")
def vendored():
    """The vendored ticket script; every test that uses it fails here until it exists."""
    if not support.VENDORED.is_file():
        pytest.fail(f"the vendored ticket script does not exist: {support.VENDORED_REL}", pytrace=False)
    return support.VENDORED

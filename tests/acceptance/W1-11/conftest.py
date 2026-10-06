"""Fixtures for the W1-11 acceptance tests."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w1_11_support as support  # noqa: E402


def pytest_configure(config):
    config.addinivalue_line("markers", "local_only: needs the dev tiers on this machine (GOV_DEV_TIERS); not for CI")


@pytest.fixture(scope="session")
def api(tmp_path_factory):
    """The public interface of ``gov.decisions``. A call fails with ``CheckerMissing`` until the package exists."""
    return support.Api(tmp_path_factory.mktemp("w1-11-api"))


@pytest.fixture()
def project(tmp_path):
    """This test's own empty git repository."""
    return support.Project(tmp_path / "repo")


@pytest.fixture()
def b_dev(tmp_path):
    """This test's own clone of the b-dev tier; the tier itself is never checked or written."""
    source = support.DEV_TIERS / support.B_DEV
    if not (source / ".git").exists():
        pytest.skip(f"no dev tier at {source} (GOV_DEV_TIERS)")
    return support.clone(source, tmp_path / "tier")

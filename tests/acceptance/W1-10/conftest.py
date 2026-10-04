"""Fixtures for the W1-10 acceptance tests."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w1_10_support as support  # noqa: E402


def pytest_configure(config):
    config.addinivalue_line("markers", "local_only: needs the dev tiers on this machine (GOV_DEV_TIERS); not for CI")


@pytest.fixture(scope="session")
def api(tmp_path_factory):
    """The public interface of ``gov.store`` and ``gov.records``; every test fails here until both exist."""
    interface = support.Api(tmp_path_factory.mktemp("w1-10-api"))
    reason = None
    try:
        interface.exists()
    except support.StoreMissing as exc:
        reason = str(exc)
    if reason:
        pytest.fail(reason, pytrace=False)
    return interface


@dataclass(frozen=True)
class Fixture:
    root: Path
    commits: dict   # commit name -> commit id
    summary: dict | None = None   # what ``load`` returned, when the fixture loads


@pytest.fixture(scope="session")
def base(tmp_path_factory):
    """The fixture repository. Never loaded: it is the source of every test's own clone."""
    root = tmp_path_factory.mktemp("w1-10-base") / "repo"
    return Fixture(root, support.build_fixture(root))


@pytest.fixture(scope="session")
def graph(api, base, tmp_path_factory):
    """A clone of the fixture repository, loaded once. Tests only query it."""
    root = support.clone(base.root, tmp_path_factory.mktemp("w1-10-graph") / "repo")
    return Fixture(root, base.commits, api.load(root))


@pytest.fixture()
def repo(api, base, tmp_path):
    """This test's own clone of the fixture repository, not loaded yet."""
    return Fixture(support.clone(base.root, tmp_path / "repo"), base.commits)

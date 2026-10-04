"""Fixtures for the W1-17 acceptance tests."""

from __future__ import annotations

import shutil
import sys
from dataclasses import dataclass
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w1_17_support as support  # noqa: E402


def pytest_configure(config):
    config.addinivalue_line("markers", "local_only: clones a dev tier (GOV_DEV_TIERS) and indexes it; not for CI")


def _built(make):
    """What ``make`` returns, or a plain failure with its reason when the ticket has not built it yet."""
    reason = None
    try:
        return make()
    except support.Missing as exc:
        reason = str(exc)
    pytest.fail(reason, pytrace=False)


@pytest.fixture(scope="session")
def caller(tmp_path_factory):
    """Calls into this worktree's ``src/`` in a child process; no check that the ticket's interface exists."""
    return support.Api(tmp_path_factory.mktemp("w1-17-api"))


@pytest.fixture(scope="session")
def api(caller):
    """The public interface of ``gov.retrieval.lexical``; every test fails here until it exists.

    Every index build calls the secret filter, which runs the gitleaks binary (DEC-287). Nothing is installed by
    a test: once the interface exists, a machine without the binary skips.
    """
    interface = caller
    _built(interface.exists)
    if shutil.which("gitleaks") is None:
        pytest.skip("gitleaks is not on PATH on this machine; the secret filter cannot run (DEC-287)")
    return interface


@dataclass(frozen=True)
class Fixture:
    root: Path
    report: dict | None = None   # what ``refresh`` returned, when the fixture is indexed


@pytest.fixture(scope="session")
def base(tmp_path_factory):
    """The fixture repository. Never indexed: it is the source of every test's own clone."""
    return _built(lambda: support.build_fixture(tmp_path_factory.mktemp("w1-17-base") / "repo"))


@pytest.fixture(scope="session")
def indexed(api, base, tmp_path_factory):
    """A clone of the fixture repository, indexed once. Tests only read it (``search(..., refresh=False)``)."""
    root = support.clone(base, tmp_path_factory.mktemp("w1-17-indexed") / "repo")
    return Fixture(root, api.refresh(root))


@pytest.fixture()
def repo(api, base, tmp_path):
    """This test's own clone of the fixture repository, not indexed yet."""
    return support.clone(base, tmp_path / "repo")


@pytest.fixture()
def family_check(api):
    """The index-freshness check, as ``gov check --list --json`` lists it."""
    return _built(lambda: support.family_check(api))

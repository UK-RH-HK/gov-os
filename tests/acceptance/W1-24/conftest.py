"""Fixtures for the W1-24 acceptance tests."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w1_24_support as support  # noqa: E402


def _built(make):
    """What ``make`` returns, or a plain failure with its reason when the ticket has not built it yet."""
    reason = None
    try:
        return make()
    except support.Missing as exc:
        reason = str(exc)
    pytest.fail(reason, pytrace=False)


@pytest.fixture(scope="session")
def box(tmp_path_factory):
    """The places and environments of the calls. It needs nothing of the ticket."""
    return support.Api(tmp_path_factory.mktemp("w1-24-api"))


@pytest.fixture(scope="session")
def api(box):
    """The Python interface; every test that uses it fails here until ``gov.context.context`` exists."""
    _built(box.exists)
    return box


@pytest.fixture(scope="session")
def cli(box):
    """The command; every test that uses it fails here until ``src/gov/context/command.py`` exists."""
    _built(box.command_exists)
    return box


@pytest.fixture(scope="session")
def base(tmp_path_factory):
    """The fixture repository. Never indexed: it is the source of every clone."""
    return support.build_fixture(tmp_path_factory.mktemp("w1-24-base") / "repo")


@pytest.fixture(scope="session")
def project(box, base, tmp_path_factory):
    """A clone of the fixture with its record graph loaded. A context only reads, so every test shares it;
    a test that changes a project takes ``repo``."""
    root = support.clone(base, tmp_path_factory.mktemp("w1-24-project") / "repo")
    box.build_store(root)
    return root


@pytest.fixture()
def repo(base, tmp_path):
    """This test's own clone of the fixture repository, not indexed."""
    return support.clone(base, tmp_path / "repo")


@pytest.fixture(scope="session")
def indexed_project(box, base, tmp_path_factory):
    """A clone of the fixture with store and lexical index. Supplementary context tests use it.
    Skips when gitleaks is not available."""
    if not box.has_gitleaks():
        pytest.skip("gitleaks is not on PATH")
    root = support.clone(base, tmp_path_factory.mktemp("w1-24-indexed") / "repo")
    _built(lambda: box.build_all(root))
    return root


@pytest.fixture(scope="session")
def family_check(box):
    """The context-reproducibility check, as ``gov check --list --json`` lists it."""
    return _built(lambda: support.family_check(box))

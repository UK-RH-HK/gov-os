"""Fixtures for the W1-21 acceptance tests."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w1_21_support as support  # noqa: E402


def pytest_configure(config):
    config.addinivalue_line("markers", "local_only: clones a dev tier (GOV_DEV_TIERS) and indexes it; not for CI")
    config.addinivalue_line(
        "markers", "needs(*names): what the case needs installed on this machine (gitleaks, sqlite_vec, ollama, "
                   "reranker); it skips, with the reason, when one is absent. Nothing is installed by a test.")


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_setup(item):
    """A case that needs what this machine lacks skips, whatever the state of the ticket."""
    names = [name for marker in item.iter_markers("needs") for name in marker.args]
    reasons = support.lacking(*names)
    if reasons:
        pytest.skip("; ".join(reasons))


def pytest_terminal_summary(terminalreporter):
    if support.MEASURED:
        terminalreporter.write_sep("=", "W1-21 measured on the dev tiers")
        for line in support.MEASURED:
            terminalreporter.write_line(line)


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
    return support.Api(tmp_path_factory.mktemp("w1-21-api"))


@pytest.fixture(scope="session")
def api(box):
    """The Python interface; every test that uses it fails here until ``gov.retrieval.retrieve`` exists."""
    _built(box.exists)
    return box


@pytest.fixture(scope="session")
def cli(box):
    """The command; every test that uses it fails here until ``src/gov/retrieve/command.py`` exists."""
    _built(box.command_exists)
    return box


@pytest.fixture(scope="session")
def ollama():
    """The stand-in Ollama endpoint, healthy for the whole session, on its own loopback port."""
    stand_in = support.OllamaStandIn()
    try:
        yield stand_in
    finally:
        stand_in.close()


@pytest.fixture(scope="session")
def base(tmp_path_factory):
    """The fixture repository. Never indexed: it is the source of every clone."""
    return support.build_fixture(tmp_path_factory.mktemp("w1-21-base") / "repo")


@pytest.fixture(scope="session")
def project(box, base, ollama, tmp_path_factory):
    """A clone of the fixture with its lexical index, its vectors (through the stand-in endpoint) and its record
    graph. A retrieval only reads, so every test shares it; a test that changes a project takes ``repo``."""
    root = support.clone(base, tmp_path_factory.mktemp("w1-21-project") / "repo")
    lexical, semantic, _ = box.build(root, ollama.host)
    assert semantic["available"], f"the fixture's vectors were not built: {semantic!r}"
    return root


@pytest.fixture()
def repo(base, tmp_path):
    """This test's own clone of the fixture repository, not indexed."""
    return support.clone(base, tmp_path / "repo")


@pytest.fixture(scope="session")
def family_check(box):
    """The retrieval-regression check, as ``gov check --list --json`` lists it."""
    return _built(lambda: support.family_check(box))

"""Fixtures for the W1-19 acceptance tests."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w1_19_support as support  # noqa: E402


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


def _built(make):
    """What ``make`` returns, or a plain failure with its reason when the ticket has not built it yet."""
    reason = None
    try:
        return make()
    except support.Missing as exc:
        reason = str(exc)
    pytest.fail(reason, pytrace=False)


@pytest.fixture(scope="session")
def api(tmp_path_factory):
    """The public interface of the three modules; every test that is not skipped fails here until it exists."""
    interface = support.Api(tmp_path_factory.mktemp("w1-19-api"))
    _built(interface.exists)
    return interface


@pytest.fixture(scope="session")
def base(tmp_path_factory):
    """The fixture repository. Never indexed: it is the source of every test's own clone."""
    return support.build_fixture(tmp_path_factory.mktemp("w1-19-base") / "repo")


@pytest.fixture()
def repo(base, tmp_path):
    """This test's own clone of the fixture repository, not indexed yet."""
    return support.clone(base, tmp_path / "repo")


@pytest.fixture(scope="session")
def policy_base(tmp_path_factory):
    """The policy fixture (DEC-381): four namespaces that differ only in ``embedding_policy``. Never indexed."""
    return support.build_policy_fixture(tmp_path_factory.mktemp("w1-19-policy") / "repo")


@pytest.fixture()
def policy_repo(policy_base, tmp_path):
    """This test's own clone of the policy fixture, not indexed yet."""
    return support.clone(policy_base, tmp_path / "policy")


@pytest.fixture()
def ollama():
    """The stand-in Ollama endpoint, healthy, on its own loopback port; ended afterwards."""
    stand_in = support.OllamaStandIn()
    try:
        yield stand_in
    finally:
        stand_in.close()


@pytest.fixture(scope="module")
def indexed(api, base, tmp_path_factory):
    """``(root, endpoint, report)``: a clone of the fixture, embedded once through the stand-in endpoint.
    Tests only read it."""
    stand_in = support.OllamaStandIn()
    try:
        root = support.clone(base, tmp_path_factory.mktemp("w1-19-indexed") / "repo")
        report = api.call(support.SEMANTIC, "refresh", support.path_arg(root),
                          env=api.scratch_env(ollama_host=stand_in.host))
        yield root, stand_in, report
    finally:
        stand_in.close()

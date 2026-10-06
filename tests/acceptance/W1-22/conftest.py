"""Fixtures for the W1-22 acceptance tests."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w1_22_support as support  # noqa: E402


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "needs(*names): what the case needs installed on this machine (gitleaks, sqlite_vec); "
                   "it skips, with the reason, when one is absent. Nothing is installed by a test.")


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_setup(item):
    names = [name for marker in item.iter_markers("needs") for name in marker.args]
    reasons = support.lacking(*names)
    if reasons:
        pytest.skip("; ".join(reasons))


def _built(make):
    reason = None
    try:
        return make()
    except support.Missing as exc:
        reason = str(exc)
    pytest.fail(reason, pytrace=False)


@pytest.fixture(scope="session")
def box(tmp_path_factory):
    return support.Api(tmp_path_factory.mktemp("w1-22-api"))


@pytest.fixture(scope="session")
def validator_api(box):
    """Every test that uses this fixture fails here until ``gov.retrieval.validate.validate`` exists."""
    _built(lambda: box.exists(support.VALIDATE_MODULE, support.VALIDATE_FUNCTION))
    return box


@pytest.fixture(scope="session")
def canary_api(box):
    """Every test that uses this fixture fails here until ``gov.retrieval.canary.run_canaries`` exists."""
    _built(lambda: box.exists(support.CANARY_MODULE, support.CANARY_FUNCTION))
    return box


@pytest.fixture(scope="session")
def ollama():
    stand_in = support.OllamaStandIn()
    try:
        yield stand_in
    finally:
        stand_in.close()


@pytest.fixture(scope="session")
def base(tmp_path_factory):
    """The fixture repository. Never indexed: it is the source of every per-test project."""
    return support.build_fixture(tmp_path_factory.mktemp("w1-22-base") / "repo")

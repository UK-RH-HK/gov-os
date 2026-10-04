"""Fixtures for the W1-15 acceptance tests."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w1_15_support as support  # noqa: E402


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "local_only: runs the gitleaks binary or clones a dev tier (GOV_DEV_TIERS); not for CI")


def _built(make):
    """What ``make`` returns, or a plain failure with its reason when the ticket has not built it yet."""
    reason = None
    try:
        return make()
    except support.Missing as exc:
        reason = str(exc)
    pytest.fail(reason, pytrace=False)


@pytest.fixture()
def sandbox(tmp_path):
    """HOME, TMPDIR, an unrelated working directory and an empty PATH directory, outside any project."""
    return support.make_sandbox(tmp_path / "sandbox")


@pytest.fixture(scope="session")
def module():
    """``src/gov/secrets/``, once the ticket has written it."""
    return _built(support.package_dir)


@pytest.fixture()
def project(module, tmp_path):
    """A project in a temporary directory: the test path map, and the kernel's gitleaks configuration at its root."""
    return _built(lambda: support.Project(tmp_path / "project"))


@pytest.fixture()
def gitleaks():
    """The gitleaks binary. Nothing is installed by a test: without the binary the test is skipped."""
    found = support.scanner()
    if found is None:
        pytest.skip("gitleaks is not on PATH on this machine")
    return found


@pytest.fixture()
def config(request):
    """The gitleaks configuration file named by the test's parameter: ``repository`` or ``template``."""
    return _built(lambda: support.config_path(request.param))


@pytest.fixture()
def family_check(sandbox):
    """The secrets-indexing check, as ``gov check --list --json`` lists it."""
    return _built(lambda: support.family_check(sandbox))


@pytest.fixture()
def store_project(family_check, tmp_path):
    """A project for the family check: the kernel's gitleaks configuration at its root, and no derived store yet."""
    return _built(lambda: support.Project(tmp_path / "project"))

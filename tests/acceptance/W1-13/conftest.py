"""Fixtures for the W1-13 acceptance tests."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w1_13_support as support  # noqa: E402

cli_support = support.cli_support


@pytest.fixture(scope="session")
def interface():
    """The envelope fields and exit codes of ``docs/interfaces/API-0002.yaml``."""
    return cli_support.load_interface(support.REPO_ROOT)


@pytest.fixture(scope="session")
def driver(tmp_path_factory):
    return support.Driver(tmp_path_factory.mktemp("w1-13-driver"))


@pytest.fixture(scope="session")
def built(tmp_path_factory, driver):
    """``gov readiness`` is built. Until then every test of its behaviour fails here."""
    base = tmp_path_factory.mktemp("w1-13-built")
    probe = support.Project(base / "project", driver)
    run = probe.gov(cli_support.make_sandbox(base / "sandbox"), support.COMMAND, "--json")
    if support.NOT_IMPLEMENTED in run.stdout:
        pytest.fail("gov readiness is not built yet: it returns NOT_IMPLEMENTED", pytrace=False)
    return True


@pytest.fixture()
def sandbox(tmp_path):
    return cli_support.make_sandbox(tmp_path / "sandbox")


@pytest.fixture()
def raw_project(driver, tmp_path):
    """This test's own temporary project, whether or not ``gov readiness`` is built."""
    return support.Project(tmp_path / "project", driver)


@pytest.fixture()
def project(built, raw_project):
    """This test's own temporary project, with ``gov readiness`` built."""
    return raw_project


@pytest.fixture()
def raw_gov(raw_project, sandbox):
    def _gov(*args):
        return raw_project.gov(sandbox, *args)

    return _gov


@pytest.fixture()
def gov(project, sandbox):
    """``gov(*args)`` runs the command line in this test's project, committed and loaded first."""

    def _gov(*args):
        return project.gov(sandbox, *args)

    return _gov

"""Fixtures for the W1-27 acceptance tests."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "W1-07"))

import w1_27_support as support  # noqa: E402


def pytest_configure(config):
    config.addinivalue_line("markers", "local_only: needs the dev tiers on this machine (GOV_DEV_TIERS); not for CI")


@pytest.fixture(scope="session")
def live(tmp_path_factory):
    """A committed copy of the working tree. Never run a command in it: it is the source of every test's own copy."""
    return support.copy_working_tree(tmp_path_factory.mktemp("w1-27-live") / "repo")


@pytest.fixture(scope="session")
def cli(live):
    """The copy, once it declares the ``gov`` command."""
    reason = None
    try:
        support.entry_point(live)
    except support.base.CliMissing as exc:
        reason = str(exc)
    if reason:
        pytest.fail(reason, pytrace=False)
    return live


@pytest.fixture(scope="session")
def interface(live):
    """The envelope fields and exit codes of ``docs/interfaces/API-0002.yaml``."""
    return support.base.load_interface(live)


@pytest.fixture()
def sandbox(tmp_path):
    """HOME, TMPDIR, the launcher's directory, the bytecode cache and an unrelated directory, outside the project."""
    return support.make_sandbox(tmp_path / "sandbox")


@pytest.fixture()
def project(cli, tmp_path):
    """This test's own committed copy of the working tree; it is both the project and the code under test."""
    target = tmp_path / "repo"
    shutil.copytree(cli, target, symlinks=True)
    return target


@pytest.fixture()
def gov(project, sandbox):
    """``gov(*args, cwd=None)`` runs the command line in this test's project."""

    def _gov(*args, cwd=None):
        return support.run_gov(project, sandbox, *args, cwd=cwd)

    return _gov


@pytest.fixture()
def rebuild_project(cli, tmp_path):
    """A tiny project for rebuild tests (~3 tracked files, ~2–3 s per rebuild).

    Revised after implementation: rebuild goes through the lexical index's
    owner and its secrets filter (DEC-440); the full fixture's ~955 tracked
    files made it time out at 30 s.  The ``gov`` code comes from the
    session-scope ``cli`` fixture via ``run_gov_with_code``.
    """
    return support.make_rebuild_project(cli, tmp_path / "repo")


@pytest.fixture()
def rebuild_gov(cli, rebuild_project, sandbox):
    """``rebuild_gov(*args)`` runs gov with code from ``cli`` and project from ``rebuild_project``."""

    def _gov(*args, cwd=None):
        return support.run_gov_with_code(cli, rebuild_project, sandbox, *args, cwd=cwd)

    return _gov

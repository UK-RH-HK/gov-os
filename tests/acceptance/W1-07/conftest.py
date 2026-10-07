"""Fixtures for the W1-07 acceptance tests."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w1_07_support as support  # noqa: E402


def pytest_configure(config):
    config.addinivalue_line("markers", "local_only: needs the dev tiers on this machine (GOV_DEV_TIERS); not for CI")


@pytest.fixture(scope="session")
def live(tmp_path_factory):
    """A committed copy of the working tree. Never run a command in it: it is the source of every test's own copy."""
    return support.copy_working_tree(tmp_path_factory.mktemp("w1-07-live") / "repo")


@pytest.fixture(scope="session")
def cli(live):
    """The copy, once it declares the ``gov`` command."""
    reason = None
    try:
        support.entry_point(live)
    except support.CliMissing as exc:
        reason = str(exc)
    if reason:
        pytest.fail(reason, pytrace=False)
    return live


@pytest.fixture(scope="session")
def interface(live):
    """The envelope fields and exit codes of ``docs/interfaces/API-0002.yaml``."""
    return support.load_interface(live)


@pytest.fixture(scope="session")
def small_live(tmp_path_factory):
    """A committed project with only a few tracked files. For commands whose work grows with tree size (DEC-440)."""
    return support.copy_minimal_project(tmp_path_factory.mktemp("w1-07-small") / "repo")


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
def small_project(small_live, tmp_path):
    """This test's own copy of the small project (DEC-440)."""
    target = tmp_path / "small-repo"
    shutil.copytree(small_live, target, symlinks=True)
    return target


@pytest.fixture()
def small_gov(small_project, cli, sandbox):
    """``gov(*args)`` on a project with only a few tracked files, using the full copy's code (DEC-440)."""

    def _gov(*args, cwd=None):
        return support.run_gov_with_code(cli, small_project, sandbox, *args, cwd=cwd)

    return _gov

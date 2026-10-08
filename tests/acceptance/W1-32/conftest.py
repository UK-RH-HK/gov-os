"""Fixtures for the W1-32 acceptance tests."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w1_32_support as support  # noqa: E402

cli_support = support.cli_support


def pytest_configure(config):
    config.addinivalue_line("markers", "local_only: needs the dev tiers on this machine (GOV_DEV_TIERS); not for CI")


@pytest.fixture(autouse=True)
def this_repository_is_never_paused():
    """The freeze flag of this worktree is the owner's: no case sets it, clears it or reads a pause state from it.

    Inside a launched worker session the flag's path shows as a placeholder
    device whether or not a flag exists (W1-28's conftest, DEC-402).
    """
    real = support.REPO_ROOT / support.FREEZE_FLAG_REL
    before = support.flag_state(real)
    yield
    assert support.flag_state(real) == before, f"{real} changed during the test: a case wrote outside its project"


@pytest.fixture(scope="session")
def interface():
    """The envelope fields and exit codes of ``docs/interfaces/API-0002.yaml``."""
    return cli_support.load_interface(support.REPO_ROOT)


@pytest.fixture(scope="session")
def driver(tmp_path_factory):
    """Calls a public function of this worktree's ``src/`` in a new process (W1-13's driver)."""
    return support.spec_support.Driver(tmp_path_factory.mktemp("w1-32-driver"))


@pytest.fixture()
def sandbox(tmp_path):
    """HOME, TMPDIR, the launcher's directory, the bytecode cache and an unrelated directory, outside the project."""
    return cli_support.make_sandbox(tmp_path / "sandbox")


@pytest.fixture()
def empty_project(driver, tmp_path):
    """This test's own temporary project with no ticket, no change and no record; its store is loaded."""
    project = support.make_project(tmp_path / "empty-project", driver)
    support.settle(project)
    return project


@pytest.fixture()
def project(driver, tmp_path):
    """This test's own temporary project with tickets in every queue, decision packages and two specifications."""
    return support.populate(support.make_project(tmp_path / "project", driver))


@pytest.fixture()
def status(project, sandbox):
    """``status(*args)`` runs ``gov status --json`` in this test's project."""

    def _status(*args):
        return support.status(project, sandbox, *args)

    return _status


# --------------------------------------------------------------------------
# The launcher (as W1-28's conftest builds it)
# --------------------------------------------------------------------------

@pytest.fixture(scope="session")
def launch_base(tmp_path_factory):
    """The launcher's temporary project (W1-46's, with DEC-386's roster entry), built once."""
    import w1_32_launch_support as launch_support

    return launch_support.w28.make_project(tmp_path_factory.mktemp("w1-32-launch-base") / "repo")


@pytest.fixture()
def launch_project(launch_base, tmp_path, sandbox):
    """This test's own copy of the launcher's project, with a held-out stand-in made up here."""
    import w1_32_launch_support as launch_support

    target = tmp_path / "launch-repo"
    shutil.copytree(launch_base, target, symlinks=True)
    stand_in = launch_support.w28.w47.make_stand_in(sandbox.elsewhere / "held-out-stand-in")
    launch_support.w28.w47.configure_stand_in(target, stand_in)
    return target


@pytest.fixture()
def cli(sandbox):
    """This suite's stand-in for the CLI at ``<HOME>/.local/bin/claude``: it starts nothing and never a model."""
    import w1_32_launch_support as launch_support

    return launch_support.install_stand_in_cli(sandbox)

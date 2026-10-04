"""Fixtures for the W1-46 acceptance tests."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w1_46_support as support  # noqa: E402


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "local_only: starts a real worker session on this machine (CLI, bwrap, socat); not for CI")


@pytest.fixture(scope="session")
def base(tmp_path_factory):
    """The temporary project, built once. Never run a command in it: every test works on its own copy."""
    return support.make_project(tmp_path_factory.mktemp("w1-46-base") / "repo")


@pytest.fixture(scope="session")
def launcher(base, tmp_path_factory):
    """``gov launch`` is a command of the project's ``gov``. Until it is, every test that launches fails here."""
    sandbox = support.cli_support.make_sandbox(tmp_path_factory.mktemp("w1-46-help"))
    run = support.run_gov(base, sandbox, "launch", "--help")
    if run.returncode != 0:
        pytest.fail(f"gov launch is not a command yet (gov launch --help ends with exit code {run.returncode}): "
                    f"{run.stderr.strip()[-300:]}", pytrace=False)
    return base


@pytest.fixture()
def sandbox(tmp_path):
    """HOME, TMPDIR, the console script's directory, the bytecode cache and an unrelated directory."""
    return support.cli_support.make_sandbox(tmp_path / "sandbox")


@pytest.fixture()
def project(base, tmp_path):
    """This test's own copy of the project, with a ``held-out.yaml`` that names a stand-in directory."""
    target = tmp_path / "repo"
    shutil.copytree(base, target, symlinks=True)
    return target


@pytest.fixture()
def stand_in(project, sandbox):
    """A stand-in for the held-out directory, outside the project, configured in the project (DEC-218)."""
    directory = support.w47.make_stand_in(sandbox.elsewhere / "held-out-stand-in")
    support.w47.configure_stand_in(project, directory)
    return directory


@pytest.fixture()
def cli(sandbox):
    """The stand-in CLI at ``<HOME>/.local/bin/claude`` and the bare-name decoy on PATH."""
    return support.install_stand_in_cli(sandbox)


@pytest.fixture()
def launch(launcher, project, stand_in, sandbox, cli):
    """``launch(role, ticket=None, *cli_args)`` runs ``gov launch <role> <ticket> [-- cli_args]`` in the project."""

    def _launch(role, ticket=None, *cli_args):
        return support.launch(project, sandbox, cli, role, ticket or support.TICKET_OF.get(role, "DAEO-zz90"),
                              *cli_args)

    return _launch


@pytest.fixture()
def guard(project, sandbox):
    """``guard(tool_name, tool_input, role, ticket=None, cwd=None)``: the committed settings' decision on one call."""

    def _guard(tool_name, tool_input, role, ticket=None, cwd=None, mode="default"):
        return support.ask_guard(project, sandbox, tool_name, tool_input, role,
                                 ticket or support.TICKET_OF.get(role), cwd=cwd, mode=mode)

    return _guard

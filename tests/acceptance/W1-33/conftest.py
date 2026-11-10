"""Fixtures for the W1-33 acceptance tests.

The temporary project, the guard and ``gov launch`` are W1-46's: the same
fixtures as ``tests/acceptance/W1-46/conftest.py``, built on its support code.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w1_33_support as support  # noqa: E402

launch_support = support.launch_support


@pytest.fixture(scope="session")
def base(tmp_path_factory):
    """The temporary project, built once. Never run a command in it: every test works on its own copy."""
    return launch_support.make_project(tmp_path_factory.mktemp("w1-33-base") / "repo")


@pytest.fixture()
def sandbox(tmp_path):
    return launch_support.cli_support.make_sandbox(tmp_path / "sandbox")


@pytest.fixture()
def project(base, tmp_path):
    target = tmp_path / "repo"
    shutil.copytree(base, target, symlinks=True)
    return target


@pytest.fixture()
def guard(project, sandbox):
    """``guard(tool_name, tool_input, role, ticket)``: the committed settings' decision on one call. No call is made."""

    def _guard(tool_name, tool_input, role, ticket=None, cwd=None):
        return launch_support.ask_guard(project, sandbox, tool_name, tool_input, role,
                                        ticket or support.w47.TICKET_OF[role], cwd=cwd)

    return _guard


@pytest.fixture()
def launch(project, sandbox):
    """``launch(role)`` runs ``gov launch <role> <ticket>`` with a stand-in CLI that starts no session.

    The resource gate is planted open in the sandbox's HOME, its readings passed to the process (W2-20 S19 runs the
    gate on every launch; DEC-1088 (5)(b)). The gate is W2-20's, not under test here.
    """
    directory = support.w47.make_stand_in(sandbox.elsewhere / "held-out-stand-in")
    support.w47.configure_stand_in(project, directory)
    cli = launch_support.install_stand_in_cli(sandbox)
    gate = support.plant_open_gate(sandbox.home, sandbox.elsewhere / "gate-readings")

    def _launch(role, ticket=None):
        ticket = ticket or launch_support.TICKET_OF.get(role) or support.w47.TICKET_OF[role]
        before = len(launch_support.calls(cli))
        env = {**launch_support.gov_environment(project, sandbox, cli), **gate}
        run = launch_support.run_gov(project, sandbox, "launch", role, ticket, cli=cli, env=env)
        return launch_support.Launch(run, tuple(launch_support.calls(cli)[before:]))

    return _launch

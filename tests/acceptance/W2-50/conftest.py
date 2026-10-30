"""Fixtures for the W2-50 acceptance tests."""

from __future__ import annotations

import os
import pwd
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_50_support as support  # noqa: E402


def _real_runs_root():
    """The real ``~/gov-os-runs``, from the password database: immune to ``HOME``. Only its existence is read."""
    return os.path.join(pwd.getpwuid(os.getuid()).pw_dir, support.RUNS)


@pytest.fixture(scope="session", autouse=True)
def the_real_runs_root_is_never_made():
    """No case may create the real ``~/gov-os-runs``: every process under test has a temporary HOME."""
    before = os.path.lexists(_real_runs_root())
    yield
    assert os.path.lexists(_real_runs_root()) == before, (
        "the real ~/gov-os-runs appeared or vanished during the W2-50 tests: a case wrote outside its sandbox")


@pytest.fixture()
def sandbox(tmp_path):
    """HOME, TMPDIR and an unrelated folder, disjoint siblings in this test's own folder."""
    return support.make_sandbox(tmp_path / "w2-50")


@pytest.fixture()
def project(sandbox):
    """This test's fixture project, a ticket worktree at ``~/gov-os-worktrees/W2-90`` of the temporary HOME."""
    return support.make_project(sandbox)


@pytest.fixture()
def guard(sandbox, project):
    """``guard(tool, target_or_command, role=engineer, ticket=MAIN's tk id)``: the guard's decision on one call."""

    def _guard(tool_name, target, role=support.ENGINEER, ticket=support.MAIN.tk):
        return support.ask_guard(sandbox, tool_name, support.tool_input(tool_name, target), role, ticket, project)

    return _guard


@pytest.fixture()
def cli(sandbox):
    """The stand-in CLI at ``<HOME>/.local/bin/claude``: it starts no session and never a model."""
    return support.install_stand_in_cli(sandbox)

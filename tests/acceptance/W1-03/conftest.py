"""Fixtures for the W1-03 acceptance tests."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w1_03_support as support  # noqa: E402


@pytest.fixture(scope="session")
def hook():
    """The containment check's PostToolUse hook script in the kernel template."""
    try:
        return support.hook_entry()
    except support.HookMissing as exc:
        reason = str(exc)
    pytest.fail(reason, pytrace=False)


@pytest.fixture()
def sandbox(tmp_path):
    """``HOME``, the system temporary directory and an unrelated directory, all outside the project."""
    return support.make_sandbox(tmp_path / "sandbox")


@pytest.fixture()
def project(hook, tmp_path):
    """A committed project with a clean working tree and the fixture tickets, all in progress."""
    return support.make_project(tmp_path / "project")


@pytest.fixture()
def check(sandbox):
    """``check(project, command, role, ticket, subagent=None, bash=None, failed=False)`` runs the hook once."""

    def _check(project, command, role=None, ticket=None, subagent=None, bash=None, failed=False):
        return support.run_hook(project, command, sandbox, role=role, ticket=ticket, subagent=subagent,
                                bash=bash, failed=failed)

    return _check


@pytest.fixture()
def after_bash(sandbox, check):
    """``after_bash(project, command, role, ticket, changed=(), subagent=None, failed=False)``.

    Runs ``command`` for real in the project, checks that it changed the paths in
    ``changed``, then runs the containment hook as the harness does after the
    call. Returns the hook's result.
    """

    def _after_bash(project, command, role=None, ticket=None, changed=(), subagent=None, failed=False):
        command = command.format(root=project, elsewhere=sandbox.elsewhere, tmpdir=sandbox.tmpdir)
        bash = support.run_bash(project, command, sandbox)
        support.assert_changed(project, *changed, command=command)
        return check(project, command, role, ticket, subagent=subagent, bash=bash, failed=failed)

    return _after_bash

"""Fixtures for the W1-03 acceptance tests."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w1_03_support as support  # noqa: E402


def _entry(find):
    try:
        return find()
    except support.HookMissing as exc:
        reason = str(exc)
    pytest.fail(reason, pytrace=False)


@pytest.fixture(scope="session")
def hook():
    """The containment check's PostToolUse hook script in the kernel template."""
    return _entry(support.hook_entry)


@pytest.fixture(scope="session")
def guard_hook(hook):
    """The kernel's PreToolUse hook script, where the check takes its before-snapshot (DEC-126)."""
    return _entry(support.guard_entry)


@pytest.fixture()
def sandbox(tmp_path):
    """``HOME``, the system temporary directory and an unrelated directory, all outside the project."""
    return support.make_sandbox(tmp_path / "sandbox")


@pytest.fixture()
def project(hook, guard_hook, tmp_path):
    """A committed project with a clean working tree and the fixture tickets, all in progress."""
    return support.make_project(tmp_path / "project")


@pytest.fixture()
def earlier_work(sandbox):
    """``earlier_work(project, command)`` leaves uncommitted work in the tree, as an earlier call did.

    No hook runs: the work is in the tree before the call under test begins.
    """

    def _earlier_work(project, command, changed=()):
        command = command.format(root=project, elsewhere=sandbox.elsewhere, tmpdir=sandbox.tmpdir)
        support.run_bash(project, command, sandbox)
        support.assert_changed(project, *changed, command=command)

    return _earlier_work


@pytest.fixture()
def before_bash(sandbox):
    """``before_bash(project, command, role, ticket, subagent=None, literal=False)`` -> (call, guard result).

    Runs the PreToolUse hook as the harness does before a Bash call. The command
    is saved as a script and the call is ``bash <script>``; with ``literal`` the
    command itself is the call.
    """

    def _before_bash(project, command, role=None, ticket=None, subagent=None, literal=False):
        command = command.format(root=project, elsewhere=sandbox.elsewhere, tmpdir=sandbox.tmpdir)
        call = support.literal_call(command) if literal else support.script_call(sandbox, command)
        return call, support.run_guard(project, call, sandbox, role=role, ticket=ticket, subagent=subagent)

    return _before_bash


@pytest.fixture()
def check(sandbox):
    """``check(project, call, role, ticket, subagent=None, bash=None, failed=False, seen=None)``.

    Runs the PostToolUse hook once for ``call``.
    """

    def _check(project, call, role=None, ticket=None, subagent=None, bash=None, failed=False, seen=None):
        return support.run_check(project, call, sandbox, role=role, ticket=ticket, subagent=subagent,
                                 bash=bash, failed=failed, seen=seen)

    return _check


@pytest.fixture()
def after_bash(sandbox, before_bash, check):
    """``after_bash(project, command, role, ticket, changed=(), subagent=None, failed=False, snapshot=True)``.

    One whole Bash call: the PreToolUse hook, then ``command`` for real in the
    project, then the PostToolUse hook. Checks that the command changed the paths
    in ``changed``. Returns the PostToolUse result, with the findings added since
    the call began.

    ``snapshot=False`` leaves the PreToolUse hook out, as when it never ran or
    timed out: the check then has no before-snapshot for the call.
    """

    def _after_bash(project, command, role=None, ticket=None, changed=(), subagent=None, failed=False,
                    snapshot=True):
        seen = len(support.finding_lines(project))
        if snapshot:
            call, guard = before_bash(project, command, role, ticket, subagent=subagent)
            support.assert_let_through(guard, call)
        else:
            command = command.format(root=project, elsewhere=sandbox.elsewhere, tmpdir=sandbox.tmpdir)
            call = support.script_call(sandbox, command)
        bash = support.run_bash(project, call.command, sandbox)
        support.assert_changed(project, *changed, command=command)
        return check(project, call, role, ticket, subagent=subagent, bash=bash, failed=failed, seen=seen)

    return _after_bash

"""Fixtures for the W1-50 acceptance tests."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w1_50_support as support  # noqa: E402

check_support = support.check_support


def _entry(find):
    try:
        return find()
    except check_support.HookMissing as exc:
        reason = str(exc)
    pytest.fail(reason, pytrace=False)


@pytest.fixture(scope="session")
def hook():
    """The containment check's PostToolUse hook script in the kernel template."""
    return _entry(check_support.hook_entry)


@pytest.fixture(scope="session")
def guard_hook(hook):
    """The kernel's PreToolUse hook script, where the check takes its before-snapshot (DEC-126)."""
    return _entry(check_support.guard_entry)


@pytest.fixture()
def sandbox(tmp_path):
    """``HOME``, the system temporary directory and an unrelated directory, all outside the project."""
    return check_support.make_sandbox(tmp_path / "sandbox")


@pytest.fixture()
def project(hook, guard_hook, tmp_path):
    """A committed project on ``main`` with a clean working tree and the fixture tickets, all in progress."""
    return check_support.make_project(tmp_path / "project")


@pytest.fixture()
def call(sandbox):
    """``call(project, command, role, ticket, subagent=None, session_id=None)`` -> (result, state after).

    One whole Bash call that moves ``HEAD`` and leaves a clean tree: the
    PreToolUse hook, the command for real, the PostToolUse hook. ``state
    after`` is taken between the command and the PostToolUse hook.
    """

    def _call(project, command, role=None, ticket=None, subagent=None, session_id=None):
        seen = len(check_support.finding_lines(project))
        before = check_support.head(project)
        the_call = check_support.script_call(sandbox, command)
        guard = check_support.run_guard(project, the_call, sandbox, role=role, ticket=ticket, subagent=subagent,
                                        session_id=session_id)
        check_support.assert_let_through(guard, the_call)
        bash = check_support.run_bash(project, the_call.command, sandbox)
        assert bash.returncode == 0, (
            f"the fixture command `{command}` failed: {bash.stdout.strip()!r} {bash.stderr.strip()!r}"
        )
        left = check_support.state(project, support.WATCHED)
        assert left[0][0] != before[0], f"the fixture command `{command}` did not move HEAD"
        assert left[0][1] == before[1], f"the fixture command `{command}` left the branch {before[1]!r}"
        assert left[1] == "", f"the fixture command `{command}` left uncommitted changes:\n{left[1]}"
        result = check_support.run_check(project, the_call, sandbox, role=role, ticket=ticket, subagent=subagent,
                                         bash=bash, seen=seen, session_id=session_id)
        return result, left

    return _call


@pytest.fixture()
def during_a_call(sandbox):
    """``during_a_call(project, role, ticket, work)`` -> (result, state after).

    A Bash call of one actor that changes nothing itself (``true``), as a
    ticket lead's call that waits for its worker. ``work()`` runs between the
    call's PreToolUse hook and its end: it is what another actor does in the
    same working tree meanwhile. The result is the PostToolUse check of the
    waiting call, with the findings that check alone added.
    """

    def _during(project, role, ticket, work):
        waiting = check_support.script_call(sandbox, "true")
        guard = check_support.run_guard(project, waiting, sandbox, role=role, ticket=ticket)
        check_support.assert_let_through(guard, waiting)
        before = check_support.head(project)
        work()
        bash = check_support.run_bash(project, waiting.command, sandbox)
        left = check_support.state(project, support.WATCHED)
        assert left[0][0] != before[0], "the other actor's work did not move HEAD during the call"
        assert left[1] == "", f"the other actor's work left uncommitted changes:\n{left[1]}"
        seen = len(check_support.finding_lines(project))
        result = check_support.run_check(project, waiting, sandbox, role=role, ticket=ticket, bash=bash, seen=seen)
        return result, left

    return _during

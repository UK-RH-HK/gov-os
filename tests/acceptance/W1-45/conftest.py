"""Fixtures for the W1-45 acceptance tests.

W1-45 tests the orchestrator's write scope (DEC-156, DEC-171) on both the guard
(PreToolUse hook) and the containment check (PostToolUse hook).  The fixtures
reuse the W1-02 and W1-03 support modules: W1-02 for the guard's ``run_hook``
and assertions, W1-03 for the containment check's ``run_check``, ``make_project``
and assertions.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Add the test directories of W1-02 and W1-03 to the module search path so
# their support modules can be imported by name.
_tests = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_tests / "W1-02"))
sys.path.insert(0, str(_tests / "W1-03"))

import w1_02_support as guard_support   # noqa: E402
import w1_03_support as check_support   # noqa: E402


# -- Session-scoped hooks (existence check) ------------------------------------

@pytest.fixture(scope="session")
def hook():
    """The kernel's PreToolUse hook script in the template directory."""
    try:
        return guard_support.hook_entry()
    except guard_support.HookMissing as exc:
        pytest.fail(str(exc), pytrace=False)


@pytest.fixture(scope="session")
def containment_hook(hook):
    """The kernel's PostToolUse hook script in the template directory."""
    try:
        return check_support.hook_entry()
    except check_support.HookMissing as exc:
        pytest.fail(str(exc), pytrace=False)


# -- Per-test project and sandbox ----------------------------------------------

@pytest.fixture()
def sandbox(tmp_path):
    """HOME, system temp and an unrelated directory, all outside the project."""
    return check_support.make_sandbox(tmp_path / "sandbox")


@pytest.fixture()
def project(hook, containment_hook, tmp_path):
    """A committed project with both hooks installed and the fixture tickets in progress."""
    return check_support.make_project(tmp_path / "project")


# -- Guard (PreToolUse) fixtures -----------------------------------------------

@pytest.fixture()
def call(sandbox):
    """Run the PreToolUse hook once for a tool call and return the guard's decision."""

    def _call(project, tool_name, tool_input, role=None, ticket=None, subagent=None, env=None):
        return guard_support.run_hook(project, tool_name, tool_input, sandbox, role=role, ticket=ticket,
                                      subagent=subagent, extra_env=env)

    return _call


@pytest.fixture()
def write(call):
    """``write(project, relpath, role, ticket, tool_name="Write")`` -- one file write through the guard."""

    def _write(project, target, role=None, ticket=None, tool_name="Write", subagent=None):
        path = Path(target)
        if not path.is_absolute():
            path = Path(project) / target
        return call(project, tool_name, guard_support.edit_tool_input(tool_name, path),
                    role=role, ticket=ticket, subagent=subagent)

    return _write


@pytest.fixture()
def bash_guard(call):
    """``bash_guard(project, command, role, ticket)`` -- one Bash call through the guard only (no containment)."""

    def _bash(project, command, role=None, ticket=None, subagent=None, env=None):
        command = command.format(root=project)
        return call(project, "Bash", guard_support.bash_tool_input(command), role=role, ticket=ticket,
                    subagent=subagent, env=env)

    return _bash


# -- Containment (PostToolUse) fixtures ----------------------------------------

@pytest.fixture()
def before_bash(sandbox):
    """Run the PreToolUse hook as the harness does before a Bash call; returns ``(call, guard_result)``."""

    def _before_bash(project, command, role=None, ticket=None, subagent=None):
        command = command.format(root=project, elsewhere=sandbox.elsewhere, tmpdir=sandbox.tmpdir)
        the_call = check_support.script_call(sandbox, command)
        return the_call, check_support.run_guard(project, the_call, sandbox, role=role, ticket=ticket,
                                                  subagent=subagent)

    return _before_bash


@pytest.fixture()
def check(sandbox):
    """Run the PostToolUse hook once for a call."""

    def _check(project, call, role=None, ticket=None, subagent=None, bash=None, failed=False, seen=None):
        return check_support.run_check(project, call, sandbox, role=role, ticket=ticket, subagent=subagent,
                                       bash=bash, failed=failed, seen=seen)

    return _check


@pytest.fixture()
def after_bash(sandbox, before_bash, check):
    """One whole Bash call: PreToolUse hook, the real command, PostToolUse hook.

    The command is saved as a script outside the project (the guard cannot tell
    what it does, so the call is let through and the before-snapshot exists).
    ``changed`` names the paths ``git status`` must show after the command; an
    empty tuple (the default) skips the check.
    """

    def _after_bash(project, command, role=None, ticket=None, changed=(), subagent=None, failed=False,
                    snapshot=True):
        seen = len(check_support.finding_lines(project))
        if snapshot:
            the_call, guard = before_bash(project, command, role, ticket, subagent=subagent)
            check_support.assert_let_through(guard, the_call)
        else:
            command = command.format(root=project, elsewhere=sandbox.elsewhere, tmpdir=sandbox.tmpdir)
            the_call = check_support.script_call(sandbox, command)
        bash = check_support.run_bash(project, the_call.command, sandbox)
        check_support.assert_changed(project, *changed, command=command)
        return check(project, the_call, role, ticket, subagent=subagent, bash=bash, failed=failed, seen=seen)

    return _after_bash

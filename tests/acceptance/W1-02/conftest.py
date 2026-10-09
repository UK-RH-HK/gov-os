"""Fixtures for the W1-02 acceptance tests."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w1_02_support as support  # noqa: E402


@pytest.fixture(scope="session")
def hook():
    """The guard's PreToolUse hook script in the kernel template."""
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
    """A committed project with the standard tickets, all in progress."""
    return support.make_project(tmp_path / "project")


@pytest.fixture()
def call(sandbox):
    """``call(project, tool_name, tool_input, role=None, ticket=None, subagent=None, env=None)`` runs the hook once.

    ``role`` and ``ticket`` become ``GOV_ROLE`` and ``GOV_TICKET``; left out, the
    session declares nothing. ``env`` adds variables to the hook's environment.
    """

    def _call(project, tool_name, tool_input, role=None, ticket=None, subagent=None, env=None):
        return support.run_hook(project, tool_name, tool_input, sandbox, role=role, ticket=ticket,
                                subagent=subagent, extra_env=env)

    return _call


@pytest.fixture()
def write(call):
    """``write(project, relpath_or_path, role, ticket, tool_name="Write")`` attempts one file write."""

    def _write(project, target, role=None, ticket=None, tool_name="Write", subagent=None):
        path = Path(target)
        if not path.is_absolute():
            path = Path(project) / target
        return call(project, tool_name, support.edit_tool_input(tool_name, path),
                    role=role, ticket=ticket, subagent=subagent)

    return _write


@pytest.fixture()
def bash(call):
    """``bash(project, command, role, ticket)`` attempts one Bash call; ``{root}`` is the project path.

    The command is a ``str.format`` template, so a literal brace is doubled:
    ``${{HOME}}`` reaches the guard as ``${HOME}``.
    """

    def _bash(project, command, role=None, ticket=None, subagent=None, env=None, **paths):
        command = command.format(root=project, **paths)
        return call(project, "Bash", support.bash_tool_input(command), role=role, ticket=ticket,
                    subagent=subagent, env=env)

    return _bash


@pytest.fixture(scope="module")
def guarded(hook, tmp_path_factory):
    """A committed project with a stand-in settings file and a stand-in held-out file (DEC-508, DEC-525).

    One project for a module: the cases only ask the guard for decisions.
    """
    import w1_02_protected_support as protected

    return protected.make_guarded(tmp_path_factory.mktemp("guarded"))

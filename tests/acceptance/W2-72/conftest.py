"""Fixtures for the W2-72 acceptance tests."""

from __future__ import annotations

import importlib
import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_72_support as support  # noqa: E402

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
    """``call(project, command, role, ticket, check_environment=None)`` -> (result, state after).

    One whole Bash call that moves ``HEAD`` on the same branch and leaves a clean tree: the PreToolUse hook,
    the command for real, the PostToolUse hook (the containment check). ``state after`` is taken between the
    command and the check. ``check_environment`` replaces variables of the check's environment only.
    """

    def _call(project, command, role, ticket, check_environment=None):
        seen = len(check_support.finding_lines(project))
        before = check_support.head(project)
        the_call = check_support.script_call(sandbox, command)
        guard = check_support.run_guard(project, the_call, sandbox, role=role, ticket=ticket)
        check_support.assert_let_through(guard, the_call)
        bash = check_support.run_bash(project, the_call.command, sandbox)
        assert bash.returncode == 0, (
            f"the fixture command `{command}` failed: {bash.stdout.strip()!r} {bash.stderr.strip()!r}"
        )
        left = check_support.state(project, support.WATCHED)
        assert left[0][0] != before[0], f"the fixture command `{command}` did not move HEAD"
        assert left[0][1] == before[1], f"the fixture command `{command}` left the branch {before[1]!r}"
        assert left[1] == "", f"the fixture command `{command}` left uncommitted changes:\n{left[1]}"
        result = check_support.run_check(project, the_call, sandbox, role=role, ticket=ticket, bash=bash, seen=seen,
                                         environment=check_environment)
        return result, left

    return _call


def _caller_free(monkeypatch):
    for name in (check_support.ROLE_ENV, check_support.TICKET_ENV, "CLAUDE_PROJECT_DIR"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", os.devnull)
    monkeypatch.setenv("GIT_CONFIG_SYSTEM", os.devnull)
    monkeypatch.syspath_prepend(str(support.SOURCES))


def _imported(name, function):
    try:
        module = importlib.import_module(name)
    except ImportError as exc:
        pytest.fail(f"`import {name}` fails: {exc}", pytrace=False)
    assert str(module.__file__).startswith(str(support.SOURCES)), (
        f"`{name}` was imported from {module.__file__}, not from this worktree's {support.SOURCES}"
    )
    found = getattr(module, function, None)
    if not callable(found):
        pytest.fail(f"{name} has no function `{function}`", pytrace=False)
    return found


@pytest.fixture()
def judge(monkeypatch):
    """``judge(root, commit_ids)`` -> the findings of ``gov.guard.containment.judge_commits`` (DEC-453),
    imported from this worktree's ``src`` in a process that says nothing of a caller."""
    _caller_free(monkeypatch)

    def _judge(root, commit_ids):
        return _imported("gov.guard.containment", "judge_commits")(str(root), list(commit_ids))

    return _judge


@pytest.fixture()
def read_merge(monkeypatch):
    """``read_merge(root, commit_id)`` -> ``gov.guard.containment_merge.read_merge`` (DEC-398), the reader the
    approval check reads merges through, imported from this worktree's ``src``."""
    _caller_free(monkeypatch)

    def _read(root, commit_id):
        return _imported("gov.guard.containment_merge", "read_merge")(str(root), commit_id)

    return _read

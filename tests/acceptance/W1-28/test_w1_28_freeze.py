"""KPI success 1 [CAP-05.a] and both failure lines.

"gov pause sets the freeze flag and the next write by any role is denied; gov
pause --off clears it." Failure: "A write succeeds while paused", "The flag
lives outside the repository runtime directory".

The flag is the file ``.gov-runtime/freeze`` of the project (DEC-109), which
the guard reads (``FREEZE_FLAG`` in ``src/gov/guard/decide.py``): the guard is
asked, as W1-02's suite asks it, before the pause, while paused and after
``--off``. CAP-05's acceptance line adds that ``git status --porcelain`` is
unchanged by the denied writes.

Every pause here is the owner's (``w1_28_support.pause``, DP-3).
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

import w1_28_support as support

cli_support = support.cli_support


def test_pause_sets_the_flag_in_the_runtime_directory(project, pause, interface):
    assert not support.is_paused(project), "the fixture project starts frozen"
    support.succeeded(pause(), interface)
    flag = support.flag(project)
    assert flag.is_file() and not flag.is_symlink(), f"gov pause did not create the file {support.FREEZE_FLAG_REL}"


@pytest.mark.parametrize("role", support.GUARD_ROLES)
def test_the_next_write_by_each_role_is_denied_until_pause_is_lifted(project, sandbox, pause, interface, role):
    _, rel = support.NORMAL_WRITE[role]
    support.assert_allowed(support.guard_write(project, sandbox, role), f"before the pause, Write on {rel} by {role}")

    support.succeeded(pause(), interface)
    for tool_name in ("Edit", "Write"):
        support.assert_denied(support.guard_write(project, sandbox, role, tool_name),
                              f"while paused, {tool_name} on {rel} by {role}")

    support.succeeded(pause("--off"), interface)
    assert not support.is_paused(project), f"gov pause --off left {support.FREEZE_FLAG_REL}"
    support.assert_allowed(support.guard_write(project, sandbox, role), f"after --off, Write on {rel} by {role}")


@pytest.mark.parametrize("role", [support.ENGINEER, support.ORCHESTRATOR])
def test_a_bash_write_is_denied_while_paused(paused, sandbox, role):
    _, rel = support.NORMAL_WRITE[role]
    command = f"echo changed > {rel}"
    support.assert_denied(support.guard_bash(paused, sandbox, role, command),
                          f"while paused, Bash `{command}` by {role}")


def test_reads_stay_open_while_paused(paused, sandbox):
    result = support.guard_bash(paused, sandbox, support.ENGINEER, "git status --porcelain")
    support.assert_allowed(result, "while paused, Bash `git status --porcelain`")


def test_git_status_is_unchanged_by_the_denied_writes(paused, sandbox):
    before = support.porcelain(paused)
    for role in support.GUARD_ROLES:
        _, rel = support.NORMAL_WRITE[role]
        support.guard_write(paused, sandbox, role)
        support.guard_bash(paused, sandbox, role, f"echo changed > {rel}")
    assert support.porcelain(paused) == before, \
        f"git status --porcelain changed while paused:\n{support.porcelain(paused)}"


def test_the_flag_lives_in_the_runtime_directory_of_the_project_and_nowhere_else(project, sandbox, pause,
                                                                                 interface):
    """Failure 2. The command runs from another directory: the flag follows ``--root``, not the caller."""
    skip = (".git", support.RUNTIME_REL, support.TICKETS_REL)  # a record may be written in a ticket (DP-6)
    before = {"project": cli_support.snapshot(project, skip=skip),
              "home": cli_support.snapshot(sandbox.home, skip=()),
              "elsewhere": cli_support.snapshot(sandbox.elsewhere, skip=())}
    run = pause(cwd=sandbox.elsewhere)
    support.succeeded(run, interface)

    flag = support.flag(project)
    assert flag.is_file(), f"the flag is not {support.FREEZE_FLAG_REL} of the project\n{run.describe()}"
    runtime = os.path.realpath(Path(project) / support.RUNTIME_REL)
    assert os.path.realpath(flag) == os.path.join(runtime, "freeze"), \
        f"the flag resolves outside the project's runtime directory: {os.path.realpath(flag)}"
    after = {"project": cli_support.snapshot(project, skip=skip),
             "home": cli_support.snapshot(sandbox.home, skip=()),
             "elsewhere": cli_support.snapshot(sandbox.elsewhere, skip=())}
    for place in before:
        changed = cli_support.snapshot_difference(before[place], after[place])
        assert not changed, f"gov pause wrote outside {support.RUNTIME_REL}/ ({place}): {changed}\n{run.describe()}"


def test_the_flag_is_not_seen_by_git(paused):
    """The runtime directory is derived state, ignored by git: a pause adds no flag to ``git status``."""
    assert support.FREEZE_FLAG_REL not in support.porcelain(paused), support.porcelain(paused)
    assert support.RUNTIME_REL + "/" not in support.porcelain(paused), support.porcelain(paused)

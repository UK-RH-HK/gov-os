"""W1-50, KPI line 1 (DEC-402), review findings on the record of an unmarked presence (DEC-136).

"...the guard treats an empty file, or one without the marker, at the flag's
path as no freeze and records its presence."

The record is one line the hook appends to ``.gov-runtime/records.jsonl`` for a
call it lets through. The hook runs outside the sandbox, so what it writes is
held by nothing but itself. Three behaviours, each with something unmarked
(the sandbox's placeholder) at the flag's path:

- **the records file is a symbolic link**: nothing is written through it. The
  link's target is unchanged (or not created), and the call is decided as it
  is without the link;
- **the records file is a named pipe**: the hook answers at once, with the
  decision it gives without the pipe. A hook that hangs is a call the harness
  lets through when its time limit ends, so a hang fails open (DEC-179);
- **a call that a later rule denies is not recorded**: a record describes a
  call that was let through (DEC-171, DEC-177).

The readings and their sources are in ``w1_50_freeze_README.md``.
"""

from __future__ import annotations

import os
import stat

import pytest

import w1_50_freeze_support as support
from w1_50_freeze_support import freeze_project, freeze_sandbox  # noqa: F401  fixtures

guard_support = support.guard_support
RECORDS = support.RECORDS_REL
PROJECT_TEST_REL = f"tests/acceptance/{guard_support.TICKET_WBS_ID}/test_fixture.py"  # a file of the fixture project
OUTSIDE_PATHS_REL = "README.md"   # outside the engineer ticket's allowed_paths
HARMLESS = "ls"
SUDO = "sudo ls"
INSTALL = "pip install requests"
# "At once": far above what one hook run takes on a loaded machine, far below the harness's own time limit.
ANSWER_WITHIN_S = 10.0


@pytest.fixture()
def project(freeze_project):  # noqa: F811
    support.put_placeholder(freeze_project)
    return freeze_project


@pytest.fixture()
def sandbox(freeze_sandbox):  # noqa: F811
    return freeze_sandbox


def _allowed_calls(project, sandbox):
    """One allowed call of each tool that is recorded: ``(what, result)``."""
    yield "Write", support.guard_write(project, sandbox, "Write")
    yield "Edit", support.guard_write(project, sandbox, "Edit")
    yield f"Bash `{HARMLESS}`", support.guard_bash(project, sandbox, HARMLESS)


# --------------------------------------------------------------------------
# 1. The records file is a symbolic link
# --------------------------------------------------------------------------

def _target_in_the_project(project, sandbox):
    return project / PROJECT_TEST_REL


def _target_outside_the_project(project, sandbox):
    path = sandbox.elsewhere / "a-file-outside-the-project.txt"
    path.write_text("not the project's\n", encoding="utf-8")
    return path


def _target_that_does_not_exist(project, sandbox):
    return sandbox.elsewhere / "no-such-file.jsonl"


LINK_TARGETS = {
    "an-acceptance-test-of-the-project": _target_in_the_project,
    "a-file-outside-the-project": _target_outside_the_project,
    "a-missing-file-outside-the-project": _target_that_does_not_exist,
}


@pytest.mark.parametrize("target_kind", sorted(LINK_TARGETS))
def test_nothing_is_written_through_a_records_file_that_is_a_link(project, sandbox, target_kind):
    target = LINK_TARGETS[target_kind](project, sandbox)
    before = target.read_bytes() if target.exists() else None
    (project / RECORDS).symlink_to(target)

    for what, result in _allowed_calls(project, sandbox):
        support.assert_not_frozen(result, f"with {RECORDS} a link to {target_kind}, {what}")
        after = target.read_bytes() if os.path.lexists(target) else None
        if before is None:
            assert after is None, (
                f"with {RECORDS} a link to {target_kind}, {what} made the guard create the link's target, outside "
                f"the project: {target} now holds {after[:200]!r}"
            )
        else:
            assert after == before, (
                f"with {RECORDS} a link to {target_kind}, {what} made the guard write through the link: {target} "
                f"grew from {len(before)} to {len(after or b'')} bytes; its end is now {(after or b'')[-200:]!r}"
            )


# --------------------------------------------------------------------------
# 2. The records file is a named pipe
# --------------------------------------------------------------------------

def _write(project, sandbox):
    return support.guard_write(project, sandbox, "Write")


# call: (how it is made, the decision the hook gives without the pipe)
PIPE_CALLS = {
    "a-sudo-command": (lambda project, sandbox: support.guard_bash(project, sandbox, SUDO), "deny"),
    "an-install-by-a-worker": (lambda project, sandbox: support.guard_bash(project, sandbox, INSTALL), "deny"),
    "a-harmless-command": (lambda project, sandbox: support.guard_bash(project, sandbox, HARMLESS), "allow"),
    "a-write-inside-the-ticket-s-paths": (_write, "allow"),
}


@pytest.mark.parametrize("call", sorted(PIPE_CALLS))
def test_a_named_pipe_as_records_file_does_not_hold_the_hook(project, sandbox, call, monkeypatch):
    """Nobody reads the pipe, so opening it for writing never returns. The hook must not open it."""
    make, expected = PIPE_CALLS[call]
    without = make(project, sandbox)
    assert without.decision == expected and without.returncode == 0, \
        f"without the pipe, {call} is not answered {expected!r}: {without.describe()}"
    records = project / RECORDS
    if os.path.lexists(records):
        records.unlink()
    os.mkfifo(records)
    # This test's own time limit: the hook's process is killed when it ends, so the run cannot hang.
    monkeypatch.setattr(guard_support, "HOOK_TIMEOUT_S", ANSWER_WITHIN_S)

    result = make(project, sandbox)

    assert result.decision != "timeout", (
        f"with a named pipe at {RECORDS}, the hook gave no answer to {call} within {ANSWER_WITHIN_S:.0f} s: the "
        f"harness lets a call through when its hook times out"
    )
    assert result.decision == expected and result.returncode == 0, (
        f"with a named pipe at {RECORDS}, {call} is not answered {expected!r}, as it is without the pipe: "
        f"{result.describe()}"
    )
    assert stat.S_ISFIFO(os.lstat(records).st_mode), f"the hook replaced the named pipe at {RECORDS}"


# --------------------------------------------------------------------------
# 3. A call that is denied is not recorded
# --------------------------------------------------------------------------

# call: how it is made. Each is denied by a rule that has nothing to do with the flag.
DENIED_CALLS = {
    "a-sudo-command": lambda project, sandbox: support.guard_bash(project, sandbox, SUDO),
    "an-install-by-a-worker": lambda project, sandbox: support.guard_bash(project, sandbox, INSTALL),
    "a-write-outside-the-ticket-s-paths":
        lambda project, sandbox: support.guard_write(project, sandbox, "Write", rel=OUTSIDE_PATHS_REL),
}


@pytest.mark.parametrize("call", sorted(DENIED_CALLS))
def test_a_denied_call_is_not_recorded(project, sandbox, call):
    """``records.jsonl`` holds what was let through (DEC-171, DEC-177): a denied call is not in it as "recorded"."""
    result = DENIED_CALLS[call](project, sandbox)
    assert result.decision == "deny" and result.returncode == 0, \
        f"with a placeholder at {support.FLAG_REL}, {call} was not denied: {result.describe()}"
    assert "frozen" not in result.stdout.lower(), f"{call} was denied as frozen: {result.describe()}"
    lines = support.json_lines(project, RECORDS)
    assert lines == [], f"{call} was denied and {RECORDS} holds a line for it: {lines}"

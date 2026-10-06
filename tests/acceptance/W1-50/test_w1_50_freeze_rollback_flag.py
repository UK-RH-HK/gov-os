"""W1-50, KPI line 1 (DEC-402), a review finding on ``gov pause --rollback`` (DEC-136).

"A freeze flag set by gov pause carries a marker line."

**Red by design until ``gov pause --rollback`` is changed.** The command sets
the flag and reads it back once, before its reverts. The project ignores
``.gov-runtime/``, so git treats the flag as a file it may overwrite or remove:
a revert of a ticket commit that touched the flag's path does so, and the
command still answers ``paused: true``.

- **The ticket added the flag to git and later removed it.** Two commits with
  its ``Task:`` trailer: one force-added ``.gov-runtime/freeze``, a later one
  removed it. The reverts, newest first, put the committed content over the
  real flag and then delete it.
- **The ticket removed a flag that was tracked before it.** One commit of the
  ticket removed it. Its revert puts the old content, here empty, over the
  real flag: a file stays at the path, unmarked, which the guard reads as no
  freeze (DEC-402).

What is pinned holds whichever way the command is repaired (the flag set again
after the last step, or a commit that touches the flag not reverted): **when
``--rollback`` has ended, with success or with an error, the flag at the path
is a marked regular file and the guard denies the next write** (DEC-378: the
rollback freezes first and the flag stays whatever its result; DEC-402 and
DEC-404: a pause that reports "paused" is a freeze the guard reads). Whether
the command succeeds, which commits it reverts and what it records are not
asked here.

``gov pause`` is run as W1-28's suite runs it, on a temporary project only.
The readings and their sources are in ``w1_50_freeze_README.md``.
"""

from __future__ import annotations

import os

import w1_50_freeze_support as support
from w1_50_freeze_support import (  # noqa: F401  fixtures
    freeze_interface, freeze_pause, freeze_project, freeze_sandbox)

pause_support = support.pause_support
COMMITTED_TEXT = ""   # what was committed at the flag's path: the sandbox's placeholder, empty (DEC-402)


def _commit(project, subject, ticket=None):
    """Commit what is staged; with ``ticket``, its ``Task:`` trailer in the final block (DEC-182)."""
    trailers = ("--trailer", f"Task: {ticket}", "--trailer", f"Role: {support.ENGINEER}") if ticket else ()
    pause_support.git(project, "commit", "-q", "-m", subject, *trailers)
    return pause_support.head(project)


def _add_the_flag_to_git(project, subject, ticket=None):
    """One commit that force-adds a file at the flag's path: the project ignores ``.gov-runtime/``."""
    support.put_text(project, COMMITTED_TEXT)
    pause_support.git(project, "add", "--force", "--", support.FLAG_REL)
    return _commit(project, subject, ticket)


def _remove_the_flag_from_git(project, subject, ticket):
    """One commit that removes the flag's path from git and from the working tree."""
    pause_support.git(project, "rm", "-q", "--", support.FLAG_REL)
    return _commit(project, subject, ticket)


def _assert_the_history_is_ready(project, sandbox):
    """Nothing at the flag's path, nothing uncommitted, the runtime folder ignored, and no freeze."""
    assert not os.path.lexists(support.flag(project)), "the history leaves something at the flag's path"
    assert pause_support.porcelain(project) == "", f"the history leaves changes:\n{pause_support.porcelain(project)}"
    pause_support.git(project, "check-ignore", "-q", "--", support.FLAG_REL)  # fails when the path is not ignored
    support.assert_not_frozen(support.guard_write(project, sandbox), "before the rollback")


def _assert_frozen_after_the_rollback(project, sandbox, run, interface, what):
    """However ``--rollback`` ended: an answer in the envelope, a marked regular file at the path, a write denied."""
    envelope = pause_support.cli_support.assert_envelope(run, interface, command="pause")
    said = "paused: true" if envelope["ok"] else f"the error {envelope['error']['code']}"
    what = f"{what}, gov pause --rollback ended with {said}"
    flag = support.flag(project)
    assert os.path.lexists(flag), \
        f"{what} and nothing is at {support.FLAG_REL}: its reverts took the flag away (DEC-378)\n{run.describe()}"
    support.assert_marker(flag, support.OWNER_NAME, what)
    support.assert_frozen(support.guard_write(project, sandbox), f"{what}; the next write")
    if envelope["ok"]:
        assert envelope["result"].get("paused") is True, f"{what}: the result does not say paused\n{run.describe()}"


def test_rollback_of_a_ticket_that_added_and_removed_the_flag_ends_frozen(freeze_project, freeze_sandbox,
                                                                          freeze_pause, freeze_interface):
    """The reverts put the committed file over the flag and then delete it: the flag must be there at the end."""
    _add_the_flag_to_git(freeze_project, "the flag's path, added by mistake", support.TICKET)
    _remove_the_flag_from_git(freeze_project, "the flag's path, removed again", support.TICKET)
    _assert_the_history_is_ready(freeze_project, freeze_sandbox)

    run = freeze_pause("--rollback", support.TICKET)

    _assert_frozen_after_the_rollback(freeze_project, freeze_sandbox, run, freeze_interface,
                                      "with a ticket that added the flag's path to git and removed it")


def test_rollback_of_a_ticket_that_removed_a_tracked_flag_ends_frozen(freeze_project, freeze_sandbox, freeze_pause,
                                                                      freeze_interface):
    """The revert puts the old content, empty, over the flag: a file is there, and it must be the marked one."""
    _add_the_flag_to_git(freeze_project, "the flag's path, tracked before the ticket")
    _remove_the_flag_from_git(freeze_project, "the flag's path, removed from git", support.TICKET)
    _assert_the_history_is_ready(freeze_project, freeze_sandbox)

    run = freeze_pause("--rollback", support.TICKET)

    _assert_frozen_after_the_rollback(freeze_project, freeze_sandbox, run, freeze_interface,
                                      "with a ticket that removed a tracked file at the flag's path")

"""W1-50 — an uncommitted edit of a ticket's file does not reopen a closed ticket for the check.

Added after implementation, from the review after the suite went green
(DEC-136, DEC-137).

DEC-318 (owner): "A commit whose trailers name a closed ticket is judged by
that ticket's role and `allowed_paths` only if it is an ancestor of the
ticket's close commit; otherwise it is a finding."

DEC-358 (owner): "A ticket's close commit is the latest commit in HEAD's
history in which the ticket's status becomes `closed`."

Both speak of what the history holds. The fixture ``support.closed_ticket``
closes ``DAEO-zz97``: the committed ticket file at ``HEAD`` holds
``status: closed`` and its close commit is in ``HEAD``'s history. Here the
ticket's file is then changed to ``status: in_progress`` in the working tree
only, and a commit with a worker's trailers that names the ticket is made
after the close commit. No commit reopens the ticket, so the commit names a
closed ticket and is no ancestor of its close commit: a finding.

The edit of the ticket's file is the orchestrator's own uncommitted change of
a path outside ``tests/acceptance/**``. It is no finding (DEC-156) and the
check leaves it in the working tree.

The last two tests hold the neighbour the decisions settle: a reopening that
is committed. The ticket is in progress at ``HEAD`` and in the working tree,
and a commit that names it is judged as any commit of a ticket in progress.

Not tested, because no decision settles them (package DP-14 in the README): a
ticket in progress at ``HEAD`` whose file holds ``status: closed`` only in the
working tree, a ticket ``open`` at ``HEAD`` and ``in_progress`` only in the
working tree, and ``allowed_paths`` that differ between the two.

Every call is an orchestrator session's own call (DEC-319).
"""

from __future__ import annotations

import pytest

import w1_50_support as support

check_support = support.check_support

ORCHESTRATOR = support.ORCHESTRATOR
ENGINEER = support.ENGINEER
DESIGNER = support.DESIGNER
TICKET = support.TICKET
CLOSED = support.CLOSED_TICKET
TICKET_FILE = f".tickets/{CLOSED}.md"

CLOSED_WORK = ((support.CLOSED_TEST, (DESIGNER, CLOSED)), (support.CLOSED_SOURCE, (ENGINEER, CLOSED)))
REOPEN_IN_THE_TREE = support.set_status_in_the_working_tree(CLOSED, "in_progress")


def _status_lines(text):
    return [line for line in text.splitlines() if line.startswith("status:")]


def _assert_closed_at_head_and_in_progress_in_the_tree(project, close_commit, path):
    """Guard against an empty test: the two states disagree, and the judged commit comes after the close commit."""
    at_head = _status_lines(check_support.git(project, "show", f"HEAD:{TICKET_FILE}"))
    in_tree = _status_lines(check_support.read(project, TICKET_FILE))
    assert at_head == ["status: closed"], f"the fixture is wrong: at HEAD the ticket's file holds {at_head}"
    assert in_tree == ["status: in_progress"], f"the fixture is wrong: the working tree holds {in_tree}"
    assert support.status_changes(project)[0] == close_commit, (
        "the fixture is wrong: a commit after the close commit changes the ticket's file"
    )
    assert support.is_ancestor(project, close_commit, "HEAD"), (
        "the fixture is wrong: the close commit is not in HEAD's history"
    )
    assert not support.is_ancestor(project, support.commit_of(project, path), close_commit), (
        "the fixture is wrong: the commit is an ancestor of the close commit"
    )


# name: (the commit's trailers, the path). Each path is inside what the role had on the ticket while it ran.
AFTER_THE_CLOSE = {
    "engineer-commit-inside-the-ticket-s-paths": ((ENGINEER, CLOSED), support.CLOSED_LATE_SOURCE),
    "test-designer-commit-of-an-acceptance-test": ((DESIGNER, CLOSED), support.CLOSED_LATE_TEST),
}


@pytest.mark.parametrize("case", sorted(AFTER_THE_CLOSE), ids=sorted(AFTER_THE_CLOSE))
def test_a_ticket_reopened_only_in_the_working_tree_stays_closed_for_a_commit_of_the_same_call(
        project, sandbox, call_leaving_changes, case):
    """One call of the orchestrator edits the ticket's file to ``status: in_progress``, does not commit it, and
    makes the commit that names the ticket."""
    trailers, path = AFTER_THE_CLOSE[case]
    close_commit = support.closed_ticket(project, sandbox, *CLOSED_WORK)
    command = REOPEN_IN_THE_TREE + " && " + support.commit(path, trailers)
    result, left = call_leaving_changes(project, command, ORCHESTRATOR, TICKET, uncommitted=[TICKET_FILE])
    _assert_closed_at_head_and_in_progress_in_the_tree(project, close_commit, path)
    what = (f"`{command}` by the orchestrator on {TICKET}: {CLOSED} is closed at HEAD and in progress only in the "
            f"working tree")
    check_support.assert_caught(result, path, what=what, action=check_support.FLAGGED)
    check_support.assert_left_as_the_call_left_it(project, left, what)


def test_a_ticket_reopened_only_in_the_working_tree_before_the_call_stays_closed(project, sandbox,
                                                                                 call_leaving_changes):
    """The ticket's file was already edited, and not committed, when the call began. The call only commits."""
    trailers, path = (ENGINEER, CLOSED), support.CLOSED_LATE_SOURCE
    close_commit = support.closed_ticket(project, sandbox, *CLOSED_WORK)
    support.run(project, sandbox, REOPEN_IN_THE_TREE)
    command = support.commit(path, trailers)
    result, left = call_leaving_changes(project, command, ORCHESTRATOR, TICKET, uncommitted=[TICKET_FILE],
                                        dirty_before=True)
    _assert_closed_at_head_and_in_progress_in_the_tree(project, close_commit, path)
    what = (f"`{command}` by the orchestrator on {TICKET}: {CLOSED} is closed at HEAD and was set in progress in "
            f"the working tree before the call")
    check_support.assert_caught(result, path, what=what, action=check_support.FLAGGED)
    check_support.assert_left_as_the_call_left_it(project, left, what)


# --------------------------------------------------------------------------
# A reopening that is committed: the ticket is in progress
# --------------------------------------------------------------------------

def _closed_and_reopened_by_a_commit(project, sandbox):
    """The fixture's closed ticket, then a commit that sets ``status: in_progress``. Returns the close commit."""
    close_commit = support.closed_ticket(project, sandbox, *CLOSED_WORK)
    support.set_status(project, sandbox, "in_progress", f"{support.CLOSED_WBS} reopened")
    at_head = _status_lines(check_support.git(project, "show", f"HEAD:{TICKET_FILE}"))
    in_tree = _status_lines(check_support.read(project, TICKET_FILE))
    assert at_head == in_tree == ["status: in_progress"], (
        f"the fixture is wrong: the ticket's file holds {at_head} at HEAD and {in_tree} in the working tree"
    )
    return close_commit


def test_commits_made_after_a_committed_reopening_pass_inside_the_ticket_s_paths(project, sandbox, call):
    """A test designer's and an engineer's commit, neither an ancestor of the earlier close commit."""
    close_commit = _closed_and_reopened_by_a_commit(project, sandbox)
    command = support.commits((support.CLOSED_LATE_TEST, (DESIGNER, CLOSED)),
                              (support.CLOSED_LATE_SOURCE, (ENGINEER, CLOSED)))
    result, left = call(project, command, ORCHESTRATOR, TICKET)
    for path in (support.CLOSED_LATE_TEST, support.CLOSED_LATE_SOURCE):
        assert not support.is_ancestor(project, support.commit_of(project, path), close_commit), (
            f"the fixture is wrong: the commit of {path} is an ancestor of the earlier close commit"
        )
    what = f"`{command}` by the orchestrator on {TICKET}, after a commit reopened {CLOSED}"
    check_support.assert_silent(result, what)
    check_support.assert_left_as_the_call_left_it(project, left, what)


def test_a_commit_made_after_a_committed_reopening_is_flagged_outside_the_ticket_s_paths(project, sandbox, call):
    """The orchestrator may write README.md itself; the reopened ticket's ``allowed_paths`` do not hold it."""
    _closed_and_reopened_by_a_commit(project, sandbox)
    command = support.commits((support.CLOSED_LATE_SOURCE, (ENGINEER, CLOSED)), (support.README, (ENGINEER, CLOSED)))
    result, left = call(project, command, ORCHESTRATOR, TICKET)
    what = f"`{command}` by the orchestrator on {TICKET}, after a commit reopened {CLOSED}"
    check_support.assert_caught(result, support.README, what=what, action=check_support.FLAGGED)
    check_support.assert_not_recorded(result, support.CLOSED_LATE_SOURCE, what=what)
    check_support.assert_left_as_the_call_left_it(project, left, what)

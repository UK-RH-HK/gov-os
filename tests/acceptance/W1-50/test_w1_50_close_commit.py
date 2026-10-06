"""W1-50 — which commit is a ticket's close commit.

DEC-358 (owner): "A ticket's close commit is the latest commit in HEAD's
history in which the ticket's status becomes `closed`. When no such commit is
found for a ticket whose status is `closed`, that is a finding."

DEC-318 (owner): "A commit whose trailers name a closed ticket is judged by
that ticket's role and `allowed_paths` only if it is an ancestor of the
ticket's close commit; otherwise it is a finding."

The closed ticket is ``DAEO-zz97`` (engineer, ``lib/closed/**``). Every status
change is a commit with ``Role: orchestrator`` that names the ticket, which is
allowed outside ``tests/acceptance/**`` whatever the ticket's state (DEC-359).
Every call is an orchestrator session's own call (DEC-319). The plain case,
one close commit that changes only the ticket's file, is in
``test_w1_50_ticket_state.py``.
"""

from __future__ import annotations

import w1_50_support as support

check_support = support.check_support

ORCHESTRATOR = support.ORCHESTRATOR
ENGINEER = support.ENGINEER
DESIGNER = support.DESIGNER
TICKET = support.TICKET
CLOSED = support.CLOSED_TICKET

FIRST_WORK = ((support.CLOSED_TEST, (DESIGNER, CLOSED)), (support.CLOSED_SOURCE, (ENGINEER, CLOSED)))
SECOND_WORK = ((support.CLOSED_LATE_TEST, (DESIGNER, CLOSED)), (support.CLOSED_LATE_SOURCE, (ENGINEER, CLOSED)))
TAKE_MAIN = "git merge -q --ff-only main"


def _status(project, ticket):
    text = check_support.read(project, f".tickets/{ticket}.md")
    return [line for line in text.splitlines() if line.startswith("status:")]


def _closed_reopened_and_closed_again(project, sandbox):
    """Work, a close, a reopening, more work, a second close. Returns the ids of the two close commits."""
    support.two_more_tickets(project, sandbox)
    support.run(project, sandbox, support.commits(*FIRST_WORK))
    first = support.set_status(project, sandbox, "closed", f"{support.CLOSED_WBS} closed: first close")
    support.set_status(project, sandbox, "in_progress", f"{support.CLOSED_WBS} reopened")
    support.run(project, sandbox, support.commits(*SECOND_WORK))
    second = support.set_status(project, sandbox, "closed", f"{support.CLOSED_WBS} closed: second close")
    return first, second


# --------------------------------------------------------------------------
# A ticket closed, reopened and closed again: the latest close commit counts
# --------------------------------------------------------------------------

def test_work_between_two_closes_is_judged_by_the_ticket_because_the_latest_close_commit_counts(project, sandbox,
                                                                                               call):
    """A branch that is behind takes in the whole history. The work done after the reopening is no ancestor of
    the first close commit and is an ancestor of the second; it stays inside the ticket's paths."""
    first, second = _closed_reopened_and_closed_again(project, sandbox)
    check_support.git(project, "checkout", "-q", support.LEAD_BRANCH)
    result, left = call(project, TAKE_MAIN, ORCHESTRATOR, TICKET)
    assert _status(project, CLOSED) == ["status: closed"], "the fixture is wrong: the ticket is not closed"
    for path, _ in SECOND_WORK:
        work = support.commit_of(project, path)
        assert not support.is_ancestor(project, work, first), (
            f"the fixture is wrong: the commit of {path} is an ancestor of the first close commit"
        )
        assert support.is_ancestor(project, work, second), (
            f"the fixture is wrong: the commit of {path} is not an ancestor of the second close commit"
        )
    what = (f"`{TAKE_MAIN}` by the orchestrator on {TICKET}, bringing {CLOSED}'s work, its close, its reopening, "
            f"more work and its second close")
    check_support.assert_silent(result, what)
    check_support.assert_left_as_the_call_left_it(project, left, what)


def test_a_commit_made_after_the_second_close_that_names_the_ticket_is_flagged(project, sandbox, call):
    """The ticket was in progress twice; what counts is that the commit is no ancestor of the latest close."""
    path = "lib/closed/later.py"
    _, second = _closed_reopened_and_closed_again(project, sandbox)
    command = support.commit(path, (ENGINEER, CLOSED))
    result, left = call(project, command, ORCHESTRATOR, TICKET)
    assert not support.is_ancestor(project, support.commit_of(project, path), second), (
        "the fixture is wrong: the commit is an ancestor of the second close commit"
    )
    what = f"a commit of {path} with trailers {(ENGINEER, CLOSED)}, made after {CLOSED} was closed a second time"
    check_support.assert_caught(result, path, what=what, action=check_support.FLAGGED)
    check_support.assert_left_as_the_call_left_it(project, left, what)


# --------------------------------------------------------------------------
# A close inside a larger commit
# --------------------------------------------------------------------------

def _closed_inside_a_larger_commit(project, sandbox):
    """The commit that sets ``status: closed`` also changes ``governance/project/bootstrap.md``. Returns its id."""
    support.two_more_tickets(project, sandbox)
    support.run(project, sandbox, support.commits(*FIRST_WORK))
    close_commit = support.set_status(project, sandbox, "closed", f"{support.CLOSED_WBS} closed, with its close row",
                                      also=support.BOOTSTRAP)
    changed = check_support.git(project, "show", "--name-only", "--format=", close_commit).split()
    assert sorted(changed) == sorted([f".tickets/{CLOSED}.md", support.BOOTSTRAP]), (
        f"the fixture is wrong: the close commit changes {changed}"
    )
    return close_commit


def test_a_close_inside_a_larger_commit_is_the_close_commit(project, sandbox, call):
    """The ticket's work before that commit passes inside the ticket's paths, as with a close commit of its own."""
    close_commit = _closed_inside_a_larger_commit(project, sandbox)
    check_support.git(project, "checkout", "-q", support.LEAD_BRANCH)
    result, left = call(project, TAKE_MAIN, ORCHESTRATOR, TICKET)
    for path, _ in FIRST_WORK:
        assert support.is_ancestor(project, support.commit_of(project, path), close_commit), (
            f"the fixture is wrong: the commit of {path} is not an ancestor of the close commit"
        )
    what = f"`{TAKE_MAIN}` by the orchestrator on {TICKET}, bringing {CLOSED}'s work and a larger commit that closes it"
    check_support.assert_silent(result, what)
    check_support.assert_left_as_the_call_left_it(project, left, what)


def test_a_commit_made_after_a_close_inside_a_larger_commit_is_flagged(project, sandbox, call):
    path = support.CLOSED_LATE_SOURCE
    close_commit = _closed_inside_a_larger_commit(project, sandbox)
    command = support.commit(path, (ENGINEER, CLOSED))
    result, left = call(project, command, ORCHESTRATOR, TICKET)
    assert not support.is_ancestor(project, support.commit_of(project, path), close_commit), (
        "the fixture is wrong: the commit is an ancestor of the close commit"
    )
    what = f"a commit of {path} with trailers {(ENGINEER, CLOSED)}, made after a larger commit closed {CLOSED}"
    check_support.assert_caught(result, path, what=what, action=check_support.FLAGGED)
    check_support.assert_left_as_the_call_left_it(project, left, what)


# --------------------------------------------------------------------------
# A ticket whose status is closed, with no close commit in HEAD's history
# --------------------------------------------------------------------------

def test_a_commit_that_names_a_closed_ticket_with_no_close_commit_is_flagged(project, sandbox, call):
    """The ticket's file came into the history already holding ``status: closed`` and was never changed.

    No commit moves the status from another value to ``closed``. The commit
    that names the ticket stays inside the ticket's paths, which the
    orchestrator may write itself. See the README, "The ticket's close commit",
    for why this form is the one tested.
    """
    path = support.CLOSED_SOURCE
    support.two_more_tickets(project, sandbox, closed_status="closed")
    assert _status(project, CLOSED) == ["status: closed"], "the fixture is wrong: the ticket is not closed"
    assert len(support.status_changes(project)) == 1, (
        "the fixture is wrong: more than one commit changes the ticket's file"
    )
    command = support.commit(path, (ENGINEER, CLOSED))
    result, left = call(project, command, ORCHESTRATOR, TICKET)
    what = (f"a commit of {path} with trailers {(ENGINEER, CLOSED)}; {CLOSED} has status closed and no commit "
            f"in which its status becomes closed")
    check_support.assert_caught(result, path, what=what, action=check_support.FLAGGED)
    check_support.assert_left_as_the_call_left_it(project, left, what)

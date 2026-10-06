"""W1-50 — a commit that names a closed ticket, or one that was never started.

DEC-318 (owner): "A commit whose trailers name a closed ticket is judged by
that ticket's role and `allowed_paths` only if it is an ancestor of the
ticket's close commit; otherwise it is a finding. A commit that names a ticket
that was never started is a finding."

The fixture ``support.closed_ticket`` closes ``DAEO-zz97`` with a close commit
in the form the repository's closes have (README, "The ticket's close
commit"), and adds ``DAEO-zz98`` with ``status: open``. Every call is an
orchestrator session's own call (DEC-319).

The commits judged here carry a worker's ``Role`` trailer. A commit with
``Role: orchestrator`` that names a closed or an open ticket (the close commit
itself is one) is allowed outside ``tests/acceptance/**`` (DEC-359):
``test_w1_50_orchestrator_task_names.py``. How the check finds the close
commit when a ticket's history holds none or several is DEC-358:
``test_w1_50_close_commit.py``.
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
OPEN = support.OPEN_TICKET

CLOSED_WORK = ((support.CLOSED_TEST, (DESIGNER, CLOSED)), (support.CLOSED_SOURCE, (ENGINEER, CLOSED)))


def _status(project, ticket):
    text = check_support.read(project, f".tickets/{ticket}.md")
    return [line for line in text.splitlines() if line.startswith("status:")]


# --------------------------------------------------------------------------
# A closed ticket's commit that is an ancestor of the close commit
# --------------------------------------------------------------------------

def test_a_closed_ticket_s_commits_before_its_close_commit_pass_inside_that_ticket_s_paths(project, sandbox, call):
    """A branch that is behind takes in ``main``: the closed ticket's work and, after it, the close commit.

    The call is silent. The two work commits are ancestors of the close commit
    (DEC-318). The close commit itself carries ``Role: orchestrator`` and names
    the ticket it closes; it changes only the ticket's file, outside
    ``tests/acceptance/**``, and is allowed (DEC-359).
    """
    close_commit = support.closed_ticket(project, sandbox, *CLOSED_WORK)
    check_support.git(project, "checkout", "-q", support.LEAD_BRANCH)
    command = "git merge -q --ff-only main"
    result, left = call(project, command, ORCHESTRATOR, TICKET)
    assert _status(project, CLOSED) == ["status: closed"], "the fixture is wrong: the ticket is not closed"
    for path in (support.CLOSED_TEST, support.CLOSED_SOURCE):
        assert support.is_ancestor(project, support.commit_of(project, path), close_commit), (
            f"the fixture is wrong: the commit of {path} is not an ancestor of the close commit"
        )
    what = f"`{command}` by the orchestrator on {TICKET}, bringing {CLOSED}'s work and its close commit"
    check_support.assert_silent(result, what)
    check_support.assert_left_as_the_call_left_it(project, left, what)


def test_a_closed_ticket_s_commit_before_its_close_commit_is_flagged_outside_that_ticket_s_paths(project, sandbox,
                                                                                               call):
    """The orchestrator may write README.md itself; the closed ticket's ``allowed_paths`` do not hold it."""
    close_commit = support.closed_ticket(project, sandbox, *CLOSED_WORK, (support.README, (ENGINEER, CLOSED)))
    check_support.git(project, "checkout", "-q", support.LEAD_BRANCH)
    command = "git merge -q --ff-only main"
    result, left = call(project, command, ORCHESTRATOR, TICKET)
    assert support.is_ancestor(project, support.commit_of(project, support.README), close_commit), (
        "the fixture is wrong: the commit of README.md is not an ancestor of the close commit"
    )
    what = f"`{command}` by the orchestrator on {TICKET}, bringing a commit of README.md that names {CLOSED}"
    check_support.assert_caught(result, support.README, what=what, action=check_support.FLAGGED)
    check_support.assert_not_recorded(result, support.CLOSED_TEST, support.CLOSED_SOURCE, what=what)
    check_support.assert_left_as_the_call_left_it(project, left, what)


# --------------------------------------------------------------------------
# A closed ticket's commit that is not an ancestor of the close commit
# --------------------------------------------------------------------------

# name: (the commit's trailers, the path). Each path is inside what the role had on the ticket while it ran.
AFTER_THE_CLOSE = {
    "engineer-commit-inside-the-ticket-s-paths": ((ENGINEER, CLOSED), support.CLOSED_LATE_SOURCE),
    # Flagged before W1-50 too: the orchestrator may not write an acceptance test itself.
    "test-designer-commit-of-an-acceptance-test": ((DESIGNER, CLOSED), support.CLOSED_LATE_TEST),
}


@pytest.mark.parametrize("case", sorted(AFTER_THE_CLOSE), ids=sorted(AFTER_THE_CLOSE))
def test_a_commit_made_after_the_close_commit_that_names_the_closed_ticket_is_flagged(project, sandbox, call, case):
    trailers, path = AFTER_THE_CLOSE[case]
    close_commit = support.closed_ticket(project, sandbox, *CLOSED_WORK)
    command = support.commit(path, trailers)
    result, left = call(project, command, ORCHESTRATOR, TICKET)
    assert not support.is_ancestor(project, support.commit_of(project, path), close_commit), (
        "the fixture is wrong: the commit is an ancestor of the close commit"
    )
    what = f"a commit of {path} with trailers {trailers}, made after {CLOSED} was closed"
    check_support.assert_caught(result, path, what=what, action=check_support.FLAGGED)
    check_support.assert_left_as_the_call_left_it(project, left, what)


def test_a_merged_commit_that_is_not_in_the_close_commit_s_history_is_flagged(project, sandbox, call):
    """A branch cut before the close and never merged before it: its commit is older than the close commit
    and still no ancestor of it. The orchestrator merges the branch after the close."""
    path = support.CLOSED_LATE_SOURCE
    close_commit = support.closed_ticket(project, sandbox, *CLOSED_WORK, late_steps=((path, (ENGINEER, CLOSED)),))
    command = support.merge(branch=support.LATE_BRANCH, trailers=(ORCHESTRATOR, support.ORCHESTRATOR_TICKET))
    result, left = call(project, command, ORCHESTRATOR, TICKET)
    assert support.is_merge(project), f"the fixture command `{command}` made no merge commit"
    assert not support.is_ancestor(project, support.commit_of(project, path), close_commit), (
        "the fixture is wrong: the merged commit is an ancestor of the close commit"
    )
    what = f"`{command}` by the orchestrator on {TICKET}, bringing a commit of {path} that names {CLOSED}"
    check_support.assert_caught(result, path, what=what, action=check_support.FLAGGED)
    check_support.assert_left_as_the_call_left_it(project, left, what)


# --------------------------------------------------------------------------
# A ticket that was never started
# --------------------------------------------------------------------------

# name: (the commit's trailers, the path)
NEVER_STARTED = {
    "engineer-commit-inside-the-ticket-s-paths": ((ENGINEER, OPEN), support.OPEN_SOURCE),
    # Flagged before W1-50 too: the orchestrator may not write an acceptance test itself.
    "test-designer-commit-of-an-acceptance-test": ((DESIGNER, OPEN), support.OPEN_TEST),
}


@pytest.mark.parametrize("case", sorted(NEVER_STARTED), ids=sorted(NEVER_STARTED))
def test_a_commit_that_names_a_ticket_that_was_never_started_is_flagged(project, sandbox, call, case):
    trailers, path = NEVER_STARTED[case]
    support.closed_ticket(project, sandbox)
    assert _status(project, OPEN) == ["status: open"], "the fixture is wrong: the ticket is not open"
    command = support.commit(path, trailers)
    result, left = call(project, command, ORCHESTRATOR, TICKET)
    what = f"a commit of {path} with trailers {trailers}; {OPEN} has status open and no history but its creation"
    check_support.assert_caught(result, path, what=what, action=check_support.FLAGGED)
    check_support.assert_left_as_the_call_left_it(project, left, what)

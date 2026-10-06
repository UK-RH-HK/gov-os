"""W1-50 — an orchestrator commit whose ``Task`` names a closed ticket, one never started, or no ticket.

DEC-359 (owner, amends DEC-318): "A commit with `Role: orchestrator` whose
`Task:` trailer names a closed ticket, a ticket never started, or a name that
is no ticket (such as `Task: decision-record`) is allowed for every path
outside `tests/acceptance/**`. Inside `tests/acceptance/**` it stays a finding
(MR-3)."

Without DEC-359 the same commits would be findings: DEC-318 for a closed
ticket's commit that is no ancestor of the close commit and for a ticket never
started, DEC-268 for a ``Task`` that names no ticket. Both still hold for a
commit with a worker's ``Role`` trailer (``test_w1_50_ticket_state.py``,
``test_w1_50_trailer_forms.py``).

The fixture ``support.closed_ticket`` closes ``DAEO-zz97`` and adds
``DAEO-zz98`` with ``status: open``. Every commit judged here is made after
that close. Every call is an orchestrator session's own call (DEC-319).
"""

from __future__ import annotations

import pytest

import w1_50_support as support

check_support = support.check_support

ORCHESTRATOR = support.ORCHESTRATOR
TICKET = support.TICKET
CLOSED = support.CLOSED_TICKET
OPEN = support.OPEN_TICKET
NO_TICKET = support.NO_TICKET

# name: (the Task trailer's value, a path under tests/acceptance/)
TASK_NAMES = {
    "a-closed-ticket": (CLOSED, support.CLOSED_LATE_TEST),
    "a-ticket-never-started": (OPEN, support.OPEN_TEST),
    "no-ticket": (NO_TICKET, support.NEW_TEST),
}


def _fixture(project, sandbox):
    close_commit = support.closed_ticket(project, sandbox, (support.CLOSED_SOURCE, (support.ENGINEER, CLOSED)))
    assert not (project / ".tickets" / f"{NO_TICKET}.md").exists(), "the fixture is wrong: the name is a ticket"
    return close_commit


@pytest.mark.parametrize("case", sorted(TASK_NAMES), ids=sorted(TASK_NAMES))
def test_an_orchestrator_commit_with_such_a_task_is_silent_outside_the_acceptance_tests(project, sandbox, call,
                                                                                       case):
    """Green before W1-50 and after it: today the caller decides, and the orchestrator may write README.md."""
    task, _ = TASK_NAMES[case]
    close_commit = _fixture(project, sandbox)
    command = support.commit(support.README, (ORCHESTRATOR, task))
    result, left = call(project, command, ORCHESTRATOR, TICKET)
    assert not support.is_ancestor(project, support.commit_of(project, support.README), close_commit), (
        "the fixture is wrong: the commit is an ancestor of the close commit"
    )
    what = f"a commit of README.md with trailers {(ORCHESTRATOR, task)}, in the orchestrator's own call on {TICKET}"
    check_support.assert_silent(result, what)
    check_support.assert_left_as_the_call_left_it(project, left, what)


@pytest.mark.parametrize("case", sorted(TASK_NAMES), ids=sorted(TASK_NAMES))
def test_an_orchestrator_commit_with_such_a_task_is_flagged_inside_the_acceptance_tests(project, sandbox, call,
                                                                                       case):
    """MR-3. Green before W1-50 and after it: the orchestrator may not write an acceptance test."""
    task, path = TASK_NAMES[case]
    _fixture(project, sandbox)
    command = support.commit(path, (ORCHESTRATOR, task))
    result, left = call(project, command, ORCHESTRATOR, TICKET)
    what = f"a commit of {path} with trailers {(ORCHESTRATOR, task)}, in the orchestrator's own call on {TICKET}"
    check_support.assert_caught(result, path, what=what, action=check_support.FLAGGED)
    check_support.assert_left_as_the_call_left_it(project, left, what)


def test_a_merge_that_brings_such_orchestrator_commits_is_silent(project, sandbox, call):
    """Three orchestrator commits on a branch cut after the close, one per kind of ``Task``, each outside
    ``tests/acceptance/**``. The orchestrator merges the branch; the merge commit names a ticket in progress."""
    close_commit = _fixture(project, sandbox)
    steps = ((support.README, (ORCHESTRATOR, CLOSED)), (support.NOTES, (ORCHESTRATOR, OPEN)),
             (support.SECOND_SOURCE, (ORCHESTRATOR, NO_TICKET)))
    support.ticket_branch(project, sandbox, *steps)
    command = support.merge()
    result, left = call(project, command, ORCHESTRATOR, TICKET)
    assert support.is_merge(project), f"the fixture command `{command}` made no merge commit"
    assert not support.is_ancestor(project, support.commit_of(project, support.README), close_commit), (
        "the fixture is wrong: the commit that names the closed ticket is an ancestor of the close commit"
    )
    what = f"`{command}` by the orchestrator on {TICKET}, bringing orchestrator commits that name {CLOSED}, " \
           f"{OPEN} and {NO_TICKET!r}"
    check_support.assert_silent(result, what)
    check_support.assert_left_as_the_call_left_it(project, left, what)


def test_a_merge_that_brings_such_an_orchestrator_commit_of_an_acceptance_test_is_flagged(project, sandbox, call):
    """The finding names the acceptance test, and not the path of the orchestrator commit next to it."""
    _fixture(project, sandbox)
    steps = ((support.README, (ORCHESTRATOR, NO_TICKET)), (support.NEW_TEST, (ORCHESTRATOR, NO_TICKET)))
    support.ticket_branch(project, sandbox, *steps)
    command = support.merge()
    result, left = call(project, command, ORCHESTRATOR, TICKET)
    assert support.is_merge(project), f"the fixture command `{command}` made no merge commit"
    what = f"`{command}` by the orchestrator on {TICKET}, bringing an orchestrator commit of {support.NEW_TEST}"
    check_support.assert_caught(result, support.NEW_TEST, what=what, action=check_support.FLAGGED)
    check_support.assert_not_recorded(result, support.README, what=what)
    check_support.assert_left_as_the_call_left_it(project, left, what)

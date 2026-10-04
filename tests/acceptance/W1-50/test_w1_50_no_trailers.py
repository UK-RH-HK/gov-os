"""W1-50 — a commit with no ``Role`` or ``Task`` trailer is judged against the caller, as today.

KPI success 4 [CAP-58.h]: "A commit with no Role or Task trailer is judged
against the caller, as today".

KPI failure 3: "A commit with no Role or Task trailer is judged by anything
other than the caller".

Every commit here that is "without trailers" carries neither trailer. A commit
that carries only one of the two is an open question (README, package DP-2).

The first two tests hold before W1-50 and after it: they are green in the red
run and guard against a regression.
"""

from __future__ import annotations

import pytest

import w1_50_support as support

check_support = support.check_support

ORCHESTRATOR = support.ORCHESTRATOR
ENGINEER = support.ENGINEER
DESIGNER = support.DESIGNER
TICKET = support.TICKET
AS_DESIGNER = support.AS_DESIGNER
NO_TRAILERS = support.NO_TRAILERS

# name: (GOV_ROLE, GOV_TICKET, the path the commit changes, the caller may write that path)
AGAINST_THE_CALLER = {
    "engineer-inside-its-ticket-paths": (ENGINEER, TICKET, support.SOURCE, True),
    "engineer-outside-its-ticket-paths": (ENGINEER, TICKET, support.README, False),
    "engineer-acceptance-test": (ENGINEER, TICKET, support.ACCEPTANCE_FILE, False),
    "test-designer-acceptance-test": (DESIGNER, TICKET, support.NEW_TEST, True),
    "test-designer-source-file": (DESIGNER, TICKET, support.SOURCE, False),
    "orchestrator-outside-the-ticket-paths": (ORCHESTRATOR, TICKET, support.README, True),
    "orchestrator-acceptance-test": (ORCHESTRATOR, TICKET, support.NEW_TEST, False),
    "no-role-at-all": (None, None, support.SOURCE, False),
}


@pytest.mark.parametrize("case", sorted(AGAINST_THE_CALLER), ids=sorted(AGAINST_THE_CALLER))
def test_a_commit_without_trailers_is_judged_against_the_caller(project, call, case):
    """Green before W1-50 and after it."""
    role, ticket, path, allowed = AGAINST_THE_CALLER[case]
    command = support.commit(path, NO_TRAILERS)
    result, left = call(project, command, role, ticket)
    what = f"a commit of {path} without trailers, in a call with GOV_ROLE={role!r} on {ticket}"
    if allowed:
        check_support.assert_silent(result, what)
    else:
        check_support.assert_caught(result, path, what=what, action=check_support.FLAGGED)
    check_support.assert_left_as_the_call_left_it(project, left, what)


def test_a_commit_without_trailers_made_during_another_actor_s_call_is_judged_against_that_caller(
        project, sandbox, during_a_call):
    """Green before W1-50 and after it: nothing names the worker, so the waiting orchestrator is the measure."""
    command = support.commit(support.NEW_TEST, NO_TRAILERS)
    result, left = during_a_call(project, ORCHESTRATOR, TICKET, lambda: support.run(project, sandbox, command))
    what = f"the orchestrator's call, during which someone committed {support.NEW_TEST} without trailers"
    check_support.assert_caught(result, support.NEW_TEST, what=what, action=check_support.FLAGGED)
    check_support.assert_left_as_the_call_left_it(project, left, what)


def test_in_one_move_only_the_commit_without_trailers_is_judged_against_the_caller(project, call):
    """Two commits of acceptance tests in a call of the orchestrator; one carries the test designer's trailers."""
    command = support.commits((support.ACCEPTANCE_FILE, NO_TRAILERS), (support.NEW_TEST, AS_DESIGNER))
    result, left = call(project, command, ORCHESTRATOR, TICKET)
    what = f"`{command}` in a call of the orchestrator on {TICKET}"
    check_support.assert_caught(result, support.ACCEPTANCE_FILE, what=what, action=check_support.FLAGGED)
    check_support.assert_not_recorded(result, support.NEW_TEST, what=what)
    assert support.NEW_TEST not in result.report, (
        f"{what}: the report names {support.NEW_TEST}, the test designer's commit: {result.report!r}"
    )
    check_support.assert_left_as_the_call_left_it(project, left, what)


def test_a_merged_commit_without_trailers_inside_the_caller_s_paths_is_silent(project, sandbox, call):
    """The orchestrator may write README.md itself (DEC-156), so the commit it merges passes."""
    support.ticket_branch(project, sandbox, (support.NEW_TEST, AS_DESIGNER), (support.README, NO_TRAILERS))
    command = support.merge()
    result, left = call(project, command, ORCHESTRATOR, TICKET)
    assert support.is_merge(project), f"the fixture command `{command}` made no merge commit"
    what = f"`{command}` by the orchestrator on {TICKET}, bringing a commit of README.md without trailers"
    check_support.assert_silent(result, what)
    check_support.assert_left_as_the_call_left_it(project, left, what)

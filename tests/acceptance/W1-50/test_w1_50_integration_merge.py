"""W1-50 — an integration merge by the orchestrator is judged by the commits it brings.

KPI success 1 [CAP-58.h]: "A forward HEAD move, including an integration merge
by the orchestrator, is judged commit by commit ...".

KPI success 2 [CAP-58.h]: "A merge commit itself is not a finding when every
commit it brings passes that check".

KPI failure 1: "An integration merge whose commits each stay inside the allowed
paths of their own Role and Task trailers raises a finding".

KPI failure 2: "A commit that changes a path outside the allowed paths of its
own Role and Task trailers raises no finding, whoever the caller is".

The case of 2026-10-04 (DEC-254): the main orchestrator merges a ticket branch
that holds a test designer's commit under ``tests/acceptance/`` and an
engineer's commit. Each test makes that merge in one Bash call of the
orchestrator: ``git merge --no-ff --no-commit`` and ``git commit``.
"""

from __future__ import annotations

import pytest

import w1_50_support as support

check_support = support.check_support

ORCHESTRATOR = support.ORCHESTRATOR
TICKET = support.TICKET
AS_DESIGNER = support.AS_DESIGNER
AS_ENGINEER = support.AS_ENGINEER
NO_TRAILERS = support.NO_TRAILERS

GOOD_COMMITS = ((support.NEW_TEST, AS_DESIGNER), (support.SOURCE, AS_ENGINEER))


# name: (main gets a commit of its own, the merge commit's trailers, GOV_TICKET of the orchestrator)
PASSING_MERGES = {
    "diverged-branches": (True, support.AS_ORCHESTRATOR, TICKET),
    "no-ff-merge-of-a-branch-that-is-ahead": (False, support.AS_ORCHESTRATOR, TICKET),
    "merge-commit-without-trailers": (True, NO_TRAILERS, TICKET),
    "orchestrator-on-another-ticket": (True, support.AS_ORCHESTRATOR, support.ORCHESTRATOR_TICKET),
}


@pytest.mark.parametrize("case", sorted(PASSING_MERGES), ids=sorted(PASSING_MERGES))
def test_an_integration_merge_of_commits_inside_their_own_paths_is_silent(project, sandbox, call, case):
    """No finding for the commits, and none for the merge commit itself."""
    main_moves_on, merge_trailers, ticket = PASSING_MERGES[case]
    support.ticket_branch(project, sandbox, *GOOD_COMMITS, main_moves_on=main_moves_on)
    command = support.merge(trailers=merge_trailers)
    result, left = call(project, command, ORCHESTRATOR, ticket)
    assert support.is_merge(project), f"the fixture command `{command}` made no merge commit"
    assert check_support.read(project, support.NEW_TEST), f"the merge did not bring in {support.NEW_TEST}"
    what = f"`{command}` by the orchestrator on {ticket}"
    check_support.assert_silent(result, what)
    check_support.assert_left_as_the_call_left_it(project, left, what)


# name: (the trailers of the third commit on the ticket branch, the path it changes)
FAILING_MERGES = {
    "engineer-commit-outside-its-ticket-paths": (AS_ENGINEER, support.README),
    "engineer-commit-of-an-acceptance-test": (AS_ENGINEER, support.ACCEPTANCE_FILE),
    "test-designer-commit-of-a-source-file": (AS_DESIGNER, support.SECOND_SOURCE),
    # KPI success 4: no trailers, so the caller decides, and the orchestrator may not write an acceptance test.
    "commit-without-trailers-of-an-acceptance-test": (NO_TRAILERS, support.ACCEPTANCE_FILE),
}


@pytest.mark.parametrize("case", sorted(FAILING_MERGES), ids=sorted(FAILING_MERGES))
def test_a_merge_that_brings_a_commit_outside_its_own_paths_is_flagged(project, sandbox, call, case):
    """The finding names the path of that commit. It is flagged and never reverted (DEC-129)."""
    trailers, path = FAILING_MERGES[case]
    support.ticket_branch(project, sandbox, *GOOD_COMMITS, (path, trailers))
    command = support.merge()
    result, left = call(project, command, ORCHESTRATOR, TICKET)
    assert support.is_merge(project), f"the fixture command `{command}` made no merge commit"
    what = f"`{command}` by the orchestrator on {TICKET}, bringing a commit of {path} with trailers {trailers}"
    check_support.assert_caught(result, path, what=what, action=check_support.FLAGGED)
    check_support.assert_not_recorded(result, support.NEW_TEST, support.SOURCE, what=what)
    for inside in (support.NEW_TEST, support.SOURCE):
        assert inside not in result.report, f"{what}: the report names {inside}, a commit inside its own paths"
    check_support.assert_left_as_the_call_left_it(project, left, what)

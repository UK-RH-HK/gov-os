"""W1-50 — who the caller is decides whether a commit is judged by its own trailers.

DEC-319 (owner): "In a worker's call, a commit whose `Role` trailer differs
from the caller's role is a finding. Own-trailer judging applies only in an
orchestrator session's own call."

DEC-266: "A non-fast-forward merge is judged commit by commit only when it is
made in an orchestrator session's own call (the main orchestrator's integration
merge, or a lead taking `w1/integrate` into its ticket branch). A merge in any
other caller's call stays flagged, as W1-03 tests it."

DEC-327: "In a worker's call, a forward HEAD move is judged commit by commit
against the caller, not by its two ends. A worker's commit outside its paths
is a finding even when a later commit of the same call undoes it."

An orchestrator session's own call has ``GOV_ROLE=orchestrator`` and no
subagent. A worker's call is a session of another role, or a subagent of
another role inside an orchestrator session (DEC-117).
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
AS_ENGINEER = support.AS_ENGINEER
AS_ORCHESTRATOR = support.AS_ORCHESTRATOR

# name: (the commit's trailers, the path it changes). Each path is inside the paths of the commit's own trailers.
OTHER_ROLE_COMMITS = {
    "test-designer-commit-of-an-acceptance-test": (AS_DESIGNER, support.NEW_TEST),
    "engineer-commit-of-a-source-file": (AS_ENGINEER, support.SOURCE),
    "orchestrator-commit-of-a-source-file": (AS_ORCHESTRATOR, support.SOURCE),
}

# name: (GOV_ROLE, subagent type, the commit of OTHER_ROLE_COMMITS made in that call)
WORKER_CALLS = {
    # Flagged before W1-50 too: the engineer may not write an acceptance test itself.
    "engineer-session-test-designer-commit": (ENGINEER, None, "test-designer-commit-of-an-acceptance-test"),
    # Flagged before W1-50 too: the test designer may not write a source file itself.
    "test-designer-session-engineer-commit": (DESIGNER, None, "engineer-commit-of-a-source-file"),
    # The engineer may write the source file itself: only the Role trailer makes this a finding.
    "engineer-session-orchestrator-commit": (ENGINEER, None, "orchestrator-commit-of-a-source-file"),
    "engineer-subagent-of-an-orchestrator-session-orchestrator-commit": (
        ORCHESTRATOR, ENGINEER, "orchestrator-commit-of-a-source-file"),
}


@pytest.mark.parametrize("case", sorted(WORKER_CALLS), ids=sorted(WORKER_CALLS))
def test_in_a_worker_s_call_a_commit_with_another_role_s_trailer_is_a_finding(project, call, case):
    """DEC-319: the commit stays inside the paths of its own trailers and is a finding all the same."""
    role, subagent, commit = WORKER_CALLS[case]
    trailers, path = OTHER_ROLE_COMMITS[commit]
    command = support.commit(path, trailers)
    result, left = call(project, command, role, TICKET, subagent=subagent)
    what = (f"a commit of {path} with trailers {trailers}, in a call with GOV_ROLE={role!r} "
            f"and subagent {subagent!r} on {TICKET}")
    check_support.assert_caught(result, path, what=what, action=check_support.FLAGGED)
    check_support.assert_left_as_the_call_left_it(project, left, what)


@pytest.mark.parametrize("commit", sorted(OTHER_ROLE_COMMITS), ids=sorted(OTHER_ROLE_COMMITS))
def test_the_same_commit_in_an_orchestrator_session_s_own_call_is_judged_by_its_trailers(project, call, commit):
    """DEC-319, second sentence: the three commits of the test above, each inside its own trailers' paths."""
    trailers, path = OTHER_ROLE_COMMITS[commit]
    command = support.commit(path, trailers)
    result, left = call(project, command, ORCHESTRATOR, TICKET)
    what = f"a commit of {path} with trailers {trailers}, in the orchestrator's own call on {TICKET}"
    check_support.assert_silent(result, what)
    check_support.assert_left_as_the_call_left_it(project, left, what)


def test_a_worker_s_commit_with_its_own_role_s_trailer_is_judged_against_the_caller(project, call):
    """DEC-319 names only a Role trailer that differs: the engineer's own commits are judged as the engineer's."""
    command = support.commits((support.SOURCE, AS_ENGINEER), (support.README, AS_ENGINEER))
    result, left = call(project, command, ENGINEER, TICKET)
    what = f"`{command}` in a call of the engineer on {TICKET}"
    check_support.assert_caught(result, support.README, what=what, action=check_support.FLAGGED)
    check_support.assert_not_recorded(result, support.SOURCE, what=what)
    check_support.assert_left_as_the_call_left_it(project, left, what)


# --------------------------------------------------------------------------
# DEC-327: a worker's call is judged commit by commit against the caller
# --------------------------------------------------------------------------

# name: the trailers of both commits. The engineer on DAEO-zz90 may not write README.md.
UNDONE_BY_THE_WORKER = {
    "commits-with-the-worker-s-own-trailers": AS_ENGINEER,
    "commits-without-trailers": support.NO_TRAILERS,
}


@pytest.mark.parametrize("case", sorted(UNDONE_BY_THE_WORKER), ids=sorted(UNDONE_BY_THE_WORKER))
def test_a_worker_s_commit_outside_its_paths_is_flagged_although_a_later_commit_undoes_it(project, call, case):
    """DEC-327: "A worker's commit outside its paths is a finding even when a later commit of the same call
    undoes it." The two ends of the move hold the same files."""
    command = support.undone(support.README, UNDONE_BY_THE_WORKER[case])
    result, left = call(project, command, ENGINEER, TICKET)
    assert check_support.git(project, "diff", "--name-only", "HEAD~2", "HEAD") == "", (
        "the fixture is wrong: the two commits together change a file"
    )
    what = f"`{command}` in a call of the engineer on {TICKET}"
    check_support.assert_caught(result, support.README, what=what, action=check_support.FLAGGED)
    check_support.assert_left_as_the_call_left_it(project, left, what)


# --------------------------------------------------------------------------
# DEC-266: a merge is judged commit by commit only in an orchestrator session's own call
# --------------------------------------------------------------------------

# name: (GOV_ROLE, subagent type)
OTHER_MERGERS = {
    "engineer-session": (ENGINEER, None),
    "test-designer-session": (DESIGNER, None),
    "engineer-subagent-of-an-orchestrator-session": (ORCHESTRATOR, ENGINEER),
}


@pytest.mark.parametrize("case", sorted(OTHER_MERGERS), ids=sorted(OTHER_MERGERS))
def test_a_merge_in_any_other_caller_s_call_stays_flagged(project, sandbox, call, case):
    """Every merged commit carries both trailers and stays inside their paths; the merge is flagged all the same.

    The W1-03 suite holds the same rule for commits without trailers
    (``test_a_merge_that_is_not_a_fast_forward_is_flagged``).
    """
    role, subagent = OTHER_MERGERS[case]
    support.ticket_branch(project, sandbox, (support.SOURCE, AS_ENGINEER), (support.SECOND_SOURCE, AS_ENGINEER))
    command = support.merge(trailers=(ENGINEER, TICKET))
    result, left = call(project, command, role, TICKET, subagent=subagent)
    assert support.is_merge(project), f"the fixture command `{command}` made no merge commit"
    what = f"`{command}` in a call with GOV_ROLE={role!r} and subagent {subagent!r} on {TICKET}"
    check_support.assert_flagged_and_nothing_reverted(project, result, left, what)


def test_a_lead_s_merge_of_the_integration_branch_into_its_ticket_branch_is_silent(project, sandbox, call):
    """DEC-266 names it: "a lead taking `w1/integrate` into its ticket branch". ``main`` stands for that branch.

    The merge brings one commit from ``main``, with the orchestrator's
    trailers and a path the orchestrator may write.
    """
    support.ticket_branch(project, sandbox, (support.NEW_TEST, AS_DESIGNER), (support.SOURCE, AS_ENGINEER))
    check_support.git(project, "checkout", "-q", support.TICKET_BRANCH)
    command = support.merge(branch="main")
    result, left = call(project, command, ORCHESTRATOR, TICKET)
    assert support.is_merge(project), f"the fixture command `{command}` made no merge commit"
    assert left[0][1] == support.TICKET_BRANCH, f"the merge was not made on {support.TICKET_BRANCH}"
    what = f"`{command}` by the lead on {support.TICKET_BRANCH}"
    check_support.assert_silent(result, what)
    check_support.assert_left_as_the_call_left_it(project, left, what)

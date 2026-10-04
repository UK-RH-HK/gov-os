"""W1-50 — what the finding record holds for a commit judged by its trailers.

DEC-270: "In a finding for a commit judged by its trailers, `role` and `ticket`
hold the caller's values, as today; the commit id and its trailers are named in
`reason`."

DEC-122 defines the record. The caller here is the orchestrator on its own
ticket ``DAEO-zz91``; the commits name the engineer ticket ``DAEO-zz90``, so
the caller's ticket and the commit's ticket can be told apart.

"Named in `reason`" is read as: `reason` holds the commit's id, in full or
abbreviated to at least seven characters, and the values of the commit's
``Role`` and ``Task`` trailers.
"""

from __future__ import annotations

import w1_50_support as support

check_support = support.check_support

ORCHESTRATOR = support.ORCHESTRATOR
ENGINEER = support.ENGINEER
DESIGNER = support.DESIGNER
TICKET = support.TICKET
CALLER_TICKET = support.ORCHESTRATOR_TICKET
AS_DESIGNER = support.AS_DESIGNER
AS_ENGINEER = support.AS_ENGINEER


def _assert_names(project, result, path, trailers, what):
    """Every finding for ``path`` holds the caller's role and ticket, and names the commit and its trailers."""
    commit_id = support.commit_of(project, path)
    role, task = trailers
    for finding in support.findings_naming(result, path, what):
        assert finding["role"] == ORCHESTRATOR, (
            f"{what}: `role` of the finding is {finding['role']!r}, not the caller's {ORCHESTRATOR!r}"
        )
        assert finding["ticket"] == CALLER_TICKET, (
            f"{what}: `ticket` of the finding is {finding['ticket']!r}, not the caller's {CALLER_TICKET!r}"
        )
        reason = finding["reason"]
        assert support.names_commit(reason, commit_id), (
            f"{what}: `reason` does not name the commit {commit_id[:12]}: {reason!r}"
        )
        assert role in reason and task in reason, (
            f"{what}: `reason` does not name the commit's trailers Role: {role} and Task: {task}: {reason!r}"
        )


def test_the_finding_holds_the_caller_s_role_and_ticket_and_names_the_commit_and_its_trailers(project, call):
    command = support.commit(support.README, AS_ENGINEER)
    result, left = call(project, command, ORCHESTRATOR, CALLER_TICKET)
    what = f"`{command}` in a call of the orchestrator on {CALLER_TICKET}"
    check_support.assert_caught(result, support.README, what=what, action=check_support.FLAGGED)
    _assert_names(project, result, support.README, AS_ENGINEER, what)


def test_each_of_two_commits_outside_their_paths_is_named_with_its_own_id_and_trailers(project, call):
    """An engineer's commit and a test designer's, with a commit inside its paths between them."""
    command = support.commits(
        (support.README, AS_ENGINEER), (support.NEW_TEST, AS_DESIGNER), (support.SOURCE, AS_DESIGNER))
    result, left = call(project, command, ORCHESTRATOR, CALLER_TICKET)
    what = f"`{command}` in a call of the orchestrator on {CALLER_TICKET}"
    check_support.assert_caught(result, support.README, support.SOURCE, what=what, action=check_support.FLAGGED)
    _assert_names(project, result, support.README, AS_ENGINEER, what)
    _assert_names(project, result, support.SOURCE, AS_DESIGNER, what)


def test_the_finding_for_a_merged_commit_names_that_commit_not_the_merge_commit(project, sandbox, call):
    support.ticket_branch(project, sandbox, (support.NEW_TEST, AS_DESIGNER), (support.README, AS_ENGINEER))
    command = support.merge(trailers=(ORCHESTRATOR, CALLER_TICKET))
    result, left = call(project, command, ORCHESTRATOR, CALLER_TICKET)
    assert support.is_merge(project), f"the fixture command `{command}` made no merge commit"
    what = f"`{command}` by the orchestrator on {CALLER_TICKET}"
    check_support.assert_caught(result, support.README, what=what, action=check_support.FLAGGED)
    _assert_names(project, result, support.README, AS_ENGINEER, what)
    merge_commit = check_support.git(project, "rev-parse", "HEAD").strip()
    assert support.commit_of(project, support.README) != merge_commit, "the fixture is wrong: the merge changed README"


def test_the_finding_in_a_waiting_lead_s_call_holds_the_lead_s_role_and_ticket(project, sandbox, during_a_call):
    """The worker's commit is found by the lead's call (DEC-254): the record is the lead's, the reason names the
    worker's commit."""
    command = support.commit(support.README, AS_ENGINEER)
    result, left = during_a_call(project, ORCHESTRATOR, CALLER_TICKET,
                                 lambda: support.run(project, sandbox, command))
    what = f"the lead's call on {CALLER_TICKET}, during which a worker ran `{command}`"
    check_support.assert_caught(result, support.README, what=what, action=check_support.FLAGGED)
    _assert_names(project, result, support.README, AS_ENGINEER, what)

"""W1-50 — a worker's commit made during another actor's call is judged by its own trailers.

KPI success 3 [CAP-58.h]: "A worker's commit made during another actor's call
is judged by its own trailers".

KPI failure 2: "A commit that changes a path outside the allowed paths of its
own Role and Task trailers raises no finding, whoever the caller is".

The case of the parallel run (DEC-254): in a ticket's worktree the lead
(``GOV_ROLE=orchestrator``) waits for its worker with its own Bash calls. The
worker commits during such a call, and the check of the lead's call sees
``HEAD`` moved. Each test runs the lead's call around the worker's commit and
reads what the check of the lead's call reports and records.
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
WORKER_SESSION = check_support.OTHER_SESSION_ID


def test_a_test_designer_s_commit_during_the_lead_s_call_is_silent(project, call, during_a_call):
    """The worker is a session of its own: its call has both hooks, and its own check is silent as well."""
    command = support.commits((support.NEW_TEST, AS_DESIGNER), (support.ACCEPTANCE_FILE, AS_DESIGNER))
    own = {}

    def worker():
        own["result"], _ = call(project, command, DESIGNER, TICKET, session_id=WORKER_SESSION)

    result, left = during_a_call(project, ORCHESTRATOR, TICKET, worker)
    check_support.assert_silent(own["result"], f"the test designer's own call `{command}`")
    what = f"the lead's call, during which the test designer ran `{command}`"
    check_support.assert_silent(result, what)
    check_support.assert_left_as_the_call_left_it(project, left, what)


# name: (the worker's commits)
INSIDE = {
    "test-designer-commit": ((support.NEW_TEST, AS_DESIGNER),),
    "test-designer-commit-then-engineer-commit": ((support.NEW_TEST, AS_DESIGNER), (support.SOURCE, AS_ENGINEER)),
    # Green before W1-50 too: the orchestrator may write the source file itself.
    "engineer-commit": ((support.SOURCE, AS_ENGINEER),),
}


@pytest.mark.parametrize("case", sorted(INSIDE), ids=sorted(INSIDE))
def test_a_worker_s_commit_inside_its_own_paths_is_silent_in_the_waiting_call(project, sandbox, during_a_call,
                                                                              case):
    """Only the lead's call sees the commit here: no hook runs around the worker's command."""
    command = support.commits(*INSIDE[case])
    result, left = during_a_call(project, ORCHESTRATOR, TICKET, lambda: support.run(project, sandbox, command))
    what = f"the lead's call, during which a worker ran `{command}`"
    check_support.assert_silent(result, what)
    check_support.assert_left_as_the_call_left_it(project, left, what)


# name: (the worker's trailers, the path its commit changes)
OUTSIDE = {
    "test-designer-commit-of-a-source-file": (AS_DESIGNER, support.SOURCE),
    "engineer-commit-outside-its-ticket-paths": (AS_ENGINEER, support.README),
    # Green before W1-50 too: the orchestrator may not write an acceptance test either.
    "engineer-commit-of-an-acceptance-test": (AS_ENGINEER, support.ACCEPTANCE_FILE),
}


@pytest.mark.parametrize("case", sorted(OUTSIDE), ids=sorted(OUTSIDE))
def test_a_worker_s_commit_outside_its_own_paths_is_flagged_in_the_waiting_call(project, sandbox, during_a_call,
                                                                                case):
    """The lead may write the source file and README.md itself; the commit is judged by the worker's trailers."""
    trailers, path = OUTSIDE[case]
    command = support.commit(path, trailers)
    result, left = during_a_call(project, ORCHESTRATOR, TICKET, lambda: support.run(project, sandbox, command))
    what = f"the lead's call, during which a worker committed {path} with trailers {trailers}"
    check_support.assert_caught(result, path, what=what, action=check_support.FLAGGED)
    check_support.assert_left_as_the_call_left_it(project, left, what)

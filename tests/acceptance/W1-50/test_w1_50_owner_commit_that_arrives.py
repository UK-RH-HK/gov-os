"""W1-50 — a ``Role: owner`` commit made earlier that becomes new to ``HEAD`` in an agent's call is a finding.

Added after implementation; reason: delegated decision, DEC-390 (package
DP-11). Expected to pass on the implementation as it stands: DEC-390 fixes
the reading the check already has.

DEC-390, DP-11: "as built until the owner says otherwise: a commit carrying
`Role: owner` that becomes new to `HEAD` in an agent session's call is a
finding, also when it was made earlier from the owner's console and arrives by
a merge or a fast-forward. Such a finding is a record of a permitted action
(DEC-254)."

KPI success 5 [CAP-58.h]: "A commit carrying a Role: owner trailer that is made
during any agent session's call is a finding (DEC-360)".

In every test the owner's commit is made before the call, with no hook around
it, on a branch of its own. The call only brings it into the history of
``HEAD``. The path is one the caller may write itself, so only the trailer
makes the commit a finding.

The commit made inside the call is ``test_w1_50_owner_commit.py``; so is the
commit ``HEAD`` was already on when the call began, which is no finding.
"""

from __future__ import annotations

import pytest

import w1_50_support as support

check_support = support.check_support

ORCHESTRATOR = support.ORCHESTRATOR
ENGINEER = support.ENGINEER
TICKET = support.TICKET

ROLE_OWNER = f"Role: {support.OWNER}"
TASK = f"Task: {TICKET}"
FAST_FORWARD = f"git merge -q --ff-only {support.TICKET_BRANCH}"

# name: (GOV_ROLE, a path that caller may write itself, the move is a merge commit)
ARRIVALS = {
    "an-orchestrator-s-no-ff-merge": (ORCHESTRATOR, support.README, True),
    "a-fast-forward-in-an-orchestrator-s-call": (ORCHESTRATOR, support.README, False),
    "a-fast-forward-in-an-engineer-s-call": (ENGINEER, support.SOURCE, False),
}


@pytest.mark.parametrize("case", sorted(ARRIVALS), ids=sorted(ARRIVALS))
def test_a_role_owner_commit_made_before_the_call_that_arrives_in_its_move_is_flagged(project, sandbox, call, case):
    """DEC-390, DP-11. The finding names the owner commit's path."""
    role, path, by_merge = ARRIVALS[case]
    owner_commit = support.commit_with(path, *support.trailer_arguments(TASK, ROLE_OWNER))
    support.ticket_branch_of(project, sandbox, owner_commit, main_moves_on=by_merge)
    commit_id = support.commit_of(project, path, revision=support.TICKET_BRANCH)
    assert support.final_block(project, commit_id) == [TASK.encode(), ROLE_OWNER.encode()], (
        f"the fixture is wrong: the commit's final block is {support.final_block(project, commit_id)}"
    )
    assert not support.is_ancestor(project, commit_id, "HEAD"), (
        "the fixture is wrong: the owner's commit is in HEAD's history before the call"
    )
    command = support.merge() if by_merge else FAST_FORWARD
    result, left = call(project, command, role, TICKET)
    assert support.is_merge(project) == by_merge, f"the fixture command `{command}` made another kind of move"
    assert support.is_ancestor(project, commit_id, "HEAD"), (
        f"the fixture is wrong: `{command}` did not bring the owner's commit into HEAD's history"
    )
    what = (f"`{command}` in a call with GOV_ROLE={role!r} on {TICKET}, bringing commit {commit_id[:12]} of {path} "
            f"with the trailers {(TASK, ROLE_OWNER)}, made before the call")
    check_support.assert_caught(result, path, what=what, action=check_support.FLAGGED)
    check_support.assert_left_as_the_call_left_it(project, left, what)

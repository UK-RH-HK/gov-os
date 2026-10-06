"""W1-50 — a merge commit one of whose parents is an earlier commit of ``HEAD``'s own history.

Added after implementation, from the review after the suite went green
(DEC-136, DEC-137).

DEC-269: "A path a merge commit changes beyond what its parents hold (a
conflict resolution, a hand edit) is judged by the merge commit's own trailers,
or against the caller when it has none. An orchestrator's conflict resolution
under `tests/acceptance/**` is therefore a finding, and elsewhere it is not."

**The move.** Two test designer's commits are in ``HEAD``'s history before the
call: one changes an existing acceptance test, one adds a new one. The
orchestrator's own call then makes a merge commit with ``git commit-tree`` and
moves the branch forward to it:

- first parent: ``HEAD`` as the call found it;
- second parent: the commit before the two test designer's commits. It is in
  ``HEAD``'s history already, so the merge commit brings no commit: the move
  holds one new commit, the merge commit.

**What is tested.** The merge commit's tree is ``HEAD``'s tree with a hand edit
of the existing acceptance test: content of that file that neither parent
holds. That is DEC-269 word for word, whichever commits the parents are, and a
finding for each of the three trailer forms: the orchestrator's and the
engineer's trailers do not allow the path, and without trailers the caller is
the orchestrator.

**What is not tested** (package DP-15 in the README). The case the review
found: the merge commit's tree is the second parent's tree, so the merge commit
undoes the two test designer's commits and holds, for every path, content one
of its parents holds. DEC-269 read by its words finds no change "beyond what
its parents hold" there, and KPI success 2 finds no commit brought that fails.
The reading passed to the test designer (what the merge commit changes against
its first parent is its own change, when a parent is not new in the move) is
the fail-closed one and is not the only one the words allow. No test fixes an
answer.

The other side, an ordinary integration merge whose second parent is new in
the move and brings a test designer's commit, is
``test_an_integration_merge_of_commits_inside_their_own_paths_is_silent``.
"""

from __future__ import annotations

import pytest

import w1_50_support as support

check_support = support.check_support

ORCHESTRATOR = support.ORCHESTRATOR
TICKET = support.TICKET
AS_DESIGNER = support.AS_DESIGNER

EARLIER = "HEAD~2"   # the commit before the two test designer's commits

# name: the merge commit's trailers
MERGE_TRAILERS = {
    "orchestrator-trailers": support.AS_ORCHESTRATOR,
    "engineer-trailers": support.AS_ENGINEER,
    # No trailers: the caller decides, and the orchestrator may not write an acceptance test.
    "no-trailers": support.NO_TRAILERS,
}


@pytest.mark.parametrize("case", sorted(MERGE_TRAILERS), ids=sorted(MERGE_TRAILERS))
def test_a_hand_edit_in_a_merge_commit_whose_second_parent_is_an_earlier_commit_is_flagged(project, sandbox, call,
                                                                                         case):
    """DEC-269: the merge commit holds content of the acceptance test that neither of its parents holds."""
    trailers = MERGE_TRAILERS[case]
    path = support.ACCEPTANCE_FILE
    support.run(project, sandbox, support.commits((path, AS_DESIGNER), (support.NEW_TEST, AS_DESIGNER)))
    before = check_support.git(project, "rev-parse", "HEAD").strip()
    earlier = check_support.git(project, "rev-parse", EARLIER).strip()
    merge_commit = support.commit_tree("$tree", ["HEAD", EARLIER], trailers)
    command = (f"echo by-the-merge >> {path} && git add -- {path} && tree=$(git write-tree) "
               f"&& git update-ref HEAD {merge_commit}")
    result, left = call(project, command, ORCHESTRATOR, TICKET)
    parents = check_support.git(project, "rev-list", "--parents", "-n", "1", "HEAD").split()[1:]
    assert parents == [before, earlier], (
        f"the fixture is wrong: the new commit's parents are {parents}, not {[before, earlier]}"
    )
    assert check_support.git(project, "rev-list", f"{before}..HEAD").split() == [left[0][0]], (
        "the fixture is wrong: the move holds other new commits than the merge commit"
    )
    merged = check_support.git(project, "rev-parse", f"HEAD:{path}")
    for parent in ("HEAD^1", "HEAD^2"):
        assert merged != check_support.git(project, "rev-parse", f"{parent}:{path}"), (
            f"the fixture is wrong: {parent} already holds the merge commit's content of {path}"
        )
    what = (f"a merge commit with trailers {trailers} and the parents HEAD and {EARLIER}, with a hand edit of "
            f"{path}, in the orchestrator's own call on {TICKET}")
    check_support.assert_caught(result, path, what=what, action=check_support.FLAGGED)
    check_support.assert_left_as_the_call_left_it(project, left, what)

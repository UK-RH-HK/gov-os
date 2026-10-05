"""W1-50 — a merge commit that takes each side's change stays silent under the symmetric rule.

Added after implementation; reason: delegated decision, DEC-403 (package DP-20,
option (a)).

DEC-403 reads a merge commit against every parent the way it is read against
the first. The other side of that rule: where the merge commit differs from a
parent because another parent changed the path against the merge base, and the
merge commit holds that parent's content, the path is brought and is no change
of the merge commit's own. An ordinary merge that takes each side's change is
silent in both directions, whichever parent comes first (KPI failure 1).

These cases pass on the implementation as it stands and must keep passing: a
fix that takes every path where the merge commit differs from a parent for the
merge commit's own fails them.

Every call is an orchestrator session's own call (DEC-266, DEC-319). The
histories are built in ``w1_50_symmetric_support.py``; ``assert_taking`` checks
each from git's own answers: the paths where the merge commit differs from a
parent, and that by the words of DEC-403 none of them is its own change.

Shapes other files already hold silent, unchanged (each was worked out again
by the words of DEC-403; none gives another answer):

- an ordinary ``--no-ff`` integration merge:
  ``test_an_integration_merge_of_commits_inside_their_own_paths_is_silent``
  (4 cases) and
  ``test_an_integration_merge_stays_silent_when_main_got_a_test_designer_s_commit_since_the_fork``
  (2 cases);
- a merge-back of a ticket branch that earlier merged the integration branch
  into itself:
  ``test_a_merge_back_of_a_ticket_branch_that_earlier_merged_main_into_itself_is_silent``
  (2 cases);
- a re-merge: ``test_a_second_merge_of_the_same_branch_is_silent``;
- an octopus merge:
  ``test_an_octopus_merge_of_two_branches_with_commits_inside_their_own_paths_is_silent``;
- a merge resolved to the merged side's content:
  ``test_a_merge_that_takes_the_merged_side_s_content_of_paths_both_sides_changed_is_silent``
  and
  ``test_a_conflict_resolved_to_the_merged_side_s_content_is_not_the_merge_commit_s_own_change``.
"""

from __future__ import annotations

import pytest

import w1_50_support as support
import w1_50_symmetric_support as symmetric

check_support = support.check_support

ORCHESTRATOR = support.ORCHESTRATOR
TICKET = support.TICKET


def _assert_silent(project, call, shape):
    result, left = call(project, shape.command, ORCHESTRATOR, TICKET)
    symmetric.assert_taking(project, shape)
    what = f"{shape.what}, in the orchestrator's own call on {TICKET}"
    check_support.assert_silent(result, what)
    check_support.assert_left_as_the_call_left_it(project, left, what)


# name: (which side holds the test designer's commit, the merge commit's first parent is the branch)
EACH_SIDE = {
    f"{sides}-{order}": (sides, turned_round)
    for sides in symmetric.EACH_SIDE_ITS_OWN_PATH
    for order, turned_round in (("an-ordinary-merge", False), ("the-parents-turned-round", True))
}


@pytest.mark.parametrize("case", sorted(EACH_SIDE), ids=sorted(EACH_SIDE))
def test_a_merge_that_takes_each_parent_s_change_of_its_own_path_is_silent(project, sandbox, call, case):
    """The branch changed one path and ``main`` another since the fork; one of the two commits is a test
    designer's, under ``tests/acceptance/**``. The merge commit holds both changes. It differs from each parent
    in the path the other changed, and each was brought. As ``git merge --no-ff`` makes it, and with the same
    tree and the branch for its first parent."""
    sides, turned_round = EACH_SIDE[case]
    shape = symmetric.each_side_changed_its_own_path(project, sandbox, sides, turned_round)
    before = check_support.git(project, "rev-parse", "HEAD").strip()
    branch = check_support.git(project, "rev-parse", support.TICKET_BRANCH).strip()
    _assert_silent(project, call, shape)
    expected = [branch, before] if turned_round else [before, branch]
    assert support.parents_of(project) == expected, (
        f"the fixture is wrong: the merge commit's parents are {support.parents_of(project)}, not {expected}"
    )
    for parent in ("HEAD^1", "HEAD^2"):
        assert len(symmetric.differing(project, "HEAD", parent)) == 1, (
            f"the fixture is wrong: the merge commit differs from {parent} in "
            f"{symmetric.differing(project, 'HEAD', parent)}"
        )


def test_a_merge_of_two_sides_that_made_the_same_change_of_a_test_is_silent(project, sandbox, call):
    """A test designer made the same change of an acceptance test on the branch and on ``main``. The merge
    commit holds that content, which is each parent's: the path differs from no parent, and it is not the
    merge commit's change."""
    shape = symmetric.both_sides_made_the_same_change(project, sandbox)
    _assert_silent(project, call, shape)
    path = support.ACCEPTANCE_FILE
    assert (support.content_at(project, "HEAD", path) == support.content_at(project, "HEAD^1", path)
            == support.content_at(project, "HEAD^2", path)), (
        f"the fixture is wrong: the merge commit does not hold both parents' content of {path}"
    )

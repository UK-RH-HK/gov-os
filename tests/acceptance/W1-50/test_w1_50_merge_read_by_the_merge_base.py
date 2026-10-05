"""W1-50 — a merge commit's own change is read by the merge base (the three-way rule).

Added after implementation; reason: delegated decision, DEC-394 (package
DP-18), as amended by the owner's DEC-398 and accepted by DEC-401. It replaces
the DP-15 rule of DEC-390 ("a merge commit with a parent not new in the move").

**The rule.** A path a merge commit changes against its first parent is
*brought by another parent* only when the merge commit holds that parent's
content of the path and that parent's content of the path differs from the
merge base of the first parent and that parent. Otherwise the change is the
merge commit's *own*, judged by the merge commit's trailers, or against the
caller when it has none (DEC-269). Whether a parent is new in the move no
longer matters.

**Several merge bases, or none: fail closed** (DEC-398). In a criss-cross
history, and in a merge of unrelated histories, nothing counts as brought by
another parent: every path the merge commit changes against its first parent
is its own change, whatever the parents hold.

The third review's two findings against the DP-15 rule:

- **F1.** One extra empty commit evades it: the merge commit's second parent
  is a new empty commit on top of an earlier commit, so no parent is "not new
  in the move", and the merge commit undoes test designer's commits unseen.
- **F2.** It flags an ordinary merge-back of a ticket branch that earlier took
  the integration branch into itself: that earlier merge is a commit of the
  move and has a parent that is not new in it (KPI failure line 1).

Every call here is an orchestrator session's own call (DEC-266, DEC-319), and
every history is a real one built in the throw-away project. The histories are
built in ``w1_50_support.py`` ("Seventh batch"); each builder says what the
merge commit changed itself and what another parent brought, and
``assert_shape`` checks the built history against that, from git's own answers.

Cases other files already hold, unchanged:

- the original DP-15 shape (the second parent is the earlier commit itself):
  ``test_a_merge_commit_that_undoes_test_designer_commits_through_an_earlier_parent_is_flagged``
  (3 cases). The earlier commit is the merge base, so the rule gives the same
  finding;
- an ordinary ``--no-ff`` integration merge bringing a test designer's commit
  under ``tests/acceptance/**`` and an engineer's commit inside its ticket's
  paths: ``test_an_integration_merge_of_commits_inside_their_own_paths_is_silent``
  (4 cases) and
  ``test_an_integration_merge_stays_silent_when_main_got_a_test_designer_s_commit_since_the_fork``
  (2 cases);
- a conflict resolved by hand to the merged side's content, or to content
  neither parent holds: ``test_w1_50_merge_commit_own_changes.py``.
"""

from __future__ import annotations

import pytest

import w1_50_support as support

check_support = support.check_support

ORCHESTRATOR = support.ORCHESTRATOR
TICKET = support.TICKET
AS_DESIGNER = support.AS_DESIGNER
AS_ENGINEER = support.AS_ENGINEER
AS_ORCHESTRATOR = support.AS_ORCHESTRATOR
NO_TRAILERS = support.NO_TRAILERS


def _make(project, call, shape):
    """One call of the orchestrator makes the merge commit of ``shape``. Returns (result, state after, what)."""
    before = check_support.git(project, "rev-parse", "HEAD").strip()
    result, left = call(project, shape.command, ORCHESTRATOR, TICKET)
    support.assert_shape(project, shape, before)
    return result, left, f"{shape.what}, in the orchestrator's own call on {TICKET}"


def _assert_own_changes_flagged(project, shape, made):
    """The merge commit's own changes are named; what another parent brought is not."""
    result, left, what = made
    check_support.assert_caught(result, *shape.own, what=what, action=check_support.FLAGGED)
    if shape.brought:
        check_support.assert_not_recorded(result, *shape.brought, what=what)
    check_support.assert_left_as_the_call_left_it(project, left, what)


def _assert_silent(project, made):
    result, left, what = made
    check_support.assert_silent(result, what)
    check_support.assert_left_as_the_call_left_it(project, left, what)


# --------------------------------------------------------------------------
# F1: the merge commit undoes test designer's commits through a new empty commit
# --------------------------------------------------------------------------

# name: the merge commit's trailers. None of them allows a path under tests/acceptance/**.
NOT_THE_TEST_DESIGNER_S = {
    "orchestrator-trailers": AS_ORCHESTRATOR,
    "engineer-trailers": AS_ENGINEER,
    # No trailers: the caller decides, and the orchestrator may not write an acceptance test.
    "no-trailers": NO_TRAILERS,
}


@pytest.mark.parametrize("case", sorted(NOT_THE_TEST_DESIGNER_S), ids=sorted(NOT_THE_TEST_DESIGNER_S))
def test_a_merge_commit_that_undoes_test_designer_commits_through_a_new_empty_commit_is_flagged(project, sandbox,
                                                                                               call, case):
    """DEC-394, F1. The second parent is new in the move and changes nothing: its content of both acceptance
    tests is the merge base's. The merge commit puts one test back and removes the other; both are its own
    change, and both are named."""
    shape = support.merge_through_a_new_empty_commit(project, sandbox, NOT_THE_TEST_DESIGNER_S[case])
    before = check_support.git(project, "rev-parse", "HEAD").strip()
    earlier = check_support.git(project, "rev-parse", "HEAD~2").strip()
    result, left, what = _make(project, call, shape)
    empty = support.parents_of(project)[1]
    assert not support.is_ancestor(project, empty, before), (
        "the fixture is wrong: the merge commit's second parent was in HEAD's history before the call"
    )
    assert support.parents_of(project, empty) == [earlier] and (
        check_support.git(project, "rev-parse", f"{empty}^{{tree}}")
        == check_support.git(project, "rev-parse", f"{earlier}^{{tree}}")
        == check_support.git(project, "rev-parse", "HEAD^{tree}")), (
        "the fixture is wrong: the second parent is no empty commit on top of the earlier commit, or the merge "
        "commit does not hold the earlier commit's tree"
    )
    assert sorted(check_support.git(project, "rev-list", f"{before}..HEAD").split()) == sorted(
        [left[0][0], empty]), "the fixture is wrong: the move holds other commits than the two new ones"
    assert check_support.read(project, support.NEW_TEST) is None, (
        f"the fixture is wrong: {support.NEW_TEST} is still there after the call"
    )
    check_support.assert_caught(result, support.ACCEPTANCE_FILE, support.NEW_TEST, what=what,
                                action=check_support.FLAGGED)
    check_support.assert_left_as_the_call_left_it(project, left, what)


# --------------------------------------------------------------------------
# Another parent's unchanged content taken over the first parent's later change
# --------------------------------------------------------------------------

# name: the merge commit's trailers
SET_BACK_BY = {
    "orchestrator-trailers": AS_ORCHESTRATOR,
    "no-trailers": NO_TRAILERS,
}


@pytest.mark.parametrize("case", sorted(SET_BACK_BY), ids=sorted(SET_BACK_BY))
def test_a_merge_that_sets_a_test_back_to_the_merged_branch_s_unchanged_content_is_flagged(project, sandbox, call,
                                                                                         case):
    """DEC-394, "consequences accepted". A real merge of a branch that changed a source file only; the merge
    commit holds the branch's content of an acceptance test, which is the merge base's, and so drops the test
    designer's change ``main`` got since the fork. The other parent did not change the path: the change is the
    merge commit's own. The source file the branch did change is brought, and is no finding."""
    shape = support.merge_setting_a_test_back_by_hand(project, sandbox, SET_BACK_BY[case])
    path = support.ACCEPTANCE_FILE
    made = _make(project, call, shape)
    base = support.merge_bases(project, "HEAD^1", "HEAD^2")[0]
    assert (support.content_at(project, "HEAD", path) == support.content_at(project, "HEAD^2", path)
            == support.content_at(project, base, path) != support.content_at(project, "HEAD^1", path)), (
        f"the fixture is wrong: the merge commit does not hold, for {path}, the second parent's content that is "
        f"also the merge base's and not the first parent's"
    )
    _assert_own_changes_flagged(project, shape, made)


def test_a_merge_commit_that_holds_the_merged_branch_s_whole_tree_is_flagged_for_what_it_drops(project, sandbox,
                                                                                               call):
    """DEC-394: "`-s ours` turned round". The merge commit's tree is the merged branch's. It puts back the
    acceptance test a test designer edited on ``main`` and removes the one a test designer added there; the
    branch changed neither. Both are named; the branch's own source file is not."""
    shape = support.merge_holding_the_branch_s_whole_tree(project, sandbox, AS_ORCHESTRATOR)
    made = _make(project, call, shape)
    assert (check_support.git(project, "rev-parse", "HEAD^{tree}")
            == check_support.git(project, "rev-parse", "HEAD^2^{tree}")), (
        "the fixture is wrong: the merge commit does not hold its second parent's tree"
    )
    _assert_own_changes_flagged(project, shape, made)


# --------------------------------------------------------------------------
# Silent: what other parents brought, in the histories the DP-15 rule misread or never met
# --------------------------------------------------------------------------

# name: main gets a commit of its own between the branch's merge of main and the merge-back
MERGE_BACKS = {
    "main-did-not-move-meanwhile": False,
    "main-moved-on-meanwhile": True,
}


@pytest.mark.parametrize("case", sorted(MERGE_BACKS), ids=sorted(MERGE_BACKS))
def test_a_merge_back_of_a_ticket_branch_that_earlier_merged_main_into_itself_is_silent(project, sandbox, call,
                                                                                      case):
    """DEC-394, F2; KPI failure 1. The branch's earlier merge of ``main`` is a commit of the move. What it
    changes against its first parent is another ticket's acceptance test, which its other parent brought by a
    test designer's commit that was on ``main`` before the call. Every commit new in the move stays inside the
    paths of its own trailers: no finding."""
    shape = support.merge_back_after_taking_main(project, sandbox, MERGE_BACKS[case])
    before = check_support.git(project, "rev-parse", "HEAD").strip()
    made = _make(project, call, shape)
    earlier_merges = [commit for commit in check_support.git(project, "rev-list", "--merges",
                                                             f"{before}..HEAD^2").split()]
    assert len(earlier_merges) == 1, (
        f"the fixture is wrong: the merged branch holds the merge commits {earlier_merges} new in the move"
    )
    taken = support.parents_of(project, earlier_merges[0])[1]
    assert support.is_ancestor(project, taken, before), (
        "the fixture is wrong: what the branch's earlier merge took was not in main's history before the call"
    )
    assert support.changes_against_first_parent(project, earlier_merges[0]) == [support.OTHER_TEST], (
        f"the fixture is wrong: the branch's earlier merge changes "
        f"{support.changes_against_first_parent(project, earlier_merges[0])} against its first parent"
    )
    assert support.read_by_the_words(project, earlier_merges[0]) == ([], [support.OTHER_TEST]), (
        "the fixture is wrong: the branch's earlier merge did not take the other ticket's test from its parent"
    )
    _assert_silent(project, made)


def test_a_second_merge_of_the_same_branch_is_silent(project, sandbox, call):
    """The branch was merged before the call; it then got an engineer's commit and a test designer's, and the
    call merges it again. The merge base is the branch's head at the first merge."""
    shape = support.second_merge_of_the_same_branch(project, sandbox)
    before = check_support.git(project, "rev-parse", "HEAD").strip()
    assert support.is_merge(project, before), "the fixture is wrong: the branch was not merged before the call"
    made = _make(project, call, shape)
    assert support.merge_bases(project, "HEAD^1", "HEAD^2") == support.parents_of(project, before)[1:], (
        "the fixture is wrong: the merge base is not the branch's head at the first merge"
    )
    _assert_silent(project, made)


def test_an_octopus_merge_of_two_branches_with_commits_inside_their_own_paths_is_silent(project, sandbox, call):
    """One merge commit with three parents: a test designer's new test from one branch, an engineer's source
    file from the other. Each path is the content of the parent that changed it against its merge base."""
    shape = support.octopus_merge(project, sandbox)
    made = _make(project, call, shape)
    assert check_support.read(project, support.NEW_TEST), f"the merge did not bring in {support.NEW_TEST}"
    _assert_silent(project, made)


def test_a_merge_that_takes_the_merged_side_s_content_of_paths_both_sides_changed_is_silent(project, sandbox, call):
    """``-X theirs`` on an acceptance test (test designer's commits on both sides) and a source file
    (engineer's commits on both sides): the merge commit holds exactly the merged side's content of both, and
    the merged side changed both against the merge base."""
    shape = support.merge_taking_theirs(project, sandbox)
    made = _make(project, call, shape)
    base = support.merge_bases(project, "HEAD^1", "HEAD^2")[0]
    for path in shape.brought:
        held = support.content_at(project, "HEAD", path)
        assert held == support.content_at(project, "HEAD^2", path) and held != support.content_at(
            project, "HEAD^1", path), f"the fixture is wrong: the merge commit does not hold the merged side's {path}"
        assert support.content_at(project, base, path) not in (
            held, support.content_at(project, "HEAD^1", path)), (
            f"the fixture is wrong: not both sides changed {path} against the merge base"
        )
    _assert_silent(project, made)


# --------------------------------------------------------------------------
# Fail closed: several merge bases (a criss-cross history), or none (unrelated histories)
# --------------------------------------------------------------------------

# name: the merge commit's trailers. With none the caller decides, and the caller is the orchestrator.
ORCHESTRATOR_S = {
    "orchestrator-trailers": AS_ORCHESTRATOR,
    "no-trailers": NO_TRAILERS,
}


def _assert_holds_the_other_parent_s_content(project, path):
    held = support.content_at(project, "HEAD", path)
    assert held is not None and held == support.content_at(project, "HEAD^2", path), (
        f"the fixture is wrong: the merge commit does not hold its second parent's content of {path}"
    )


@pytest.mark.parametrize("case", sorted(ORCHESTRATOR_S), ids=sorted(ORCHESTRATOR_S))
def test_a_criss_cross_merge_that_changes_an_acceptance_test_is_flagged(project, sandbox, call, case):
    """DEC-398: with several merge bases nothing counts as brought by another parent. The other parent holds
    the new acceptance test and got it by a test designer's commit, which passes by its own trailers; the merge
    commit's change of the path against its first parent is its own all the same, and the path is named."""
    shape = support.criss_cross_merge(project, sandbox, (support.NEW_TEST, AS_DESIGNER), ORCHESTRATOR_S[case])
    made = _make(project, call, shape)
    _assert_holds_the_other_parent_s_content(project, support.NEW_TEST)
    assert support.trailer_values(project, support.commit_of(project, support.NEW_TEST, "HEAD^2"), "Role") == [
        support.DESIGNER], "the fixture is wrong: the other parent's commit of the test is not a test designer's"
    _assert_own_changes_flagged(project, shape, made)


@pytest.mark.parametrize("case", sorted(ORCHESTRATOR_S), ids=sorted(ORCHESTRATOR_S))
def test_a_criss_cross_merge_that_changes_only_paths_its_trailers_or_the_caller_may_write_is_silent(project,
                                                                                                   sandbox, call,
                                                                                                   case):
    """The same criss-cross merge; the other side's last commit is an engineer's, of a source file inside its
    ticket's paths. The merge commit's own change is that source file, which the orchestrator may write."""
    shape = support.criss_cross_merge(project, sandbox, (support.SOURCE, AS_ENGINEER), ORCHESTRATOR_S[case])
    made = _make(project, call, shape)
    _assert_holds_the_other_parent_s_content(project, support.SOURCE)
    _assert_silent(project, made)


@pytest.mark.parametrize("case", sorted(ORCHESTRATOR_S), ids=sorted(ORCHESTRATOR_S))
def test_a_merge_of_an_unrelated_history_that_adds_an_acceptance_test_is_flagged(project, sandbox, call, case):
    """DEC-398, read for no merge base at all: nothing counts as brought by another parent. The merged history's
    one commit has no parent, carries a test designer's trailers and adds an acceptance test, so it passes by
    its own trailers; the merge commit's change of the path is its own, and the path is named."""
    shape = support.unrelated_merge(project, sandbox, (support.NEW_TEST, AS_DESIGNER), ORCHESTRATOR_S[case])
    made = _make(project, call, shape)
    _assert_holds_the_other_parent_s_content(project, support.NEW_TEST)
    _assert_own_changes_flagged(project, shape, made)


@pytest.mark.parametrize("case", sorted(ORCHESTRATOR_S), ids=sorted(ORCHESTRATOR_S))
def test_a_merge_of_an_unrelated_history_that_adds_a_path_the_orchestrator_may_write_is_silent(project, sandbox,
                                                                                              call, case):
    """The same merge; the merged history's one commit carries the orchestrator's trailers and adds a file
    under ``docs/``. The merge commit's own change is that file, which the orchestrator may write."""
    shape = support.unrelated_merge(project, sandbox, (support.ISLAND_NOTES, AS_ORCHESTRATOR), ORCHESTRATOR_S[case])
    made = _make(project, call, shape)
    _assert_holds_the_other_parent_s_content(project, support.ISLAND_NOTES)
    _assert_silent(project, made)

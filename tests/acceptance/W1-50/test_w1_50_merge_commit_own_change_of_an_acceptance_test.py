"""W1-50 — a merge commit's own change of an acceptance test is a finding whatever its trailers.

Added after implementation; reason: delegated decision, DEC-410 (package DP-27,
option (b)).

DEC-410, DP-27: "the same for `tests/acceptance/**`: a merge commit's own
change there is a finding whatever its trailers, test-designer trailers
included."

Until DEC-410 a merge commit's own change was judged by the merge commit's
trailers (DEC-269). With ``Role: independent-test-designer`` and the ``Task`` of
a ticket in progress, a merge commit that edited an acceptance test by hand,
resolved a conflict in one, or dropped a test designer's change of one was
silent in an orchestrator session's own call. An acceptance test is changed
by a test designer's ordinary commit, which shows the change as its own diff;
never inside a merge commit.

Two callers:

- an **orchestrator session's own call**, the merge commit with a test
  designer's trailers;
- a **test designer session's own call** (``GOV_ROLE=independent-test-designer``),
  the merge commit with a test designer's trailers and with none.

With the orchestrator's trailers, or none, in an orchestrator's own call the
change is a finding since DEC-269; existing cases hold that side of the rule,
unchanged: ``test_a_merge_commit_s_own_change_outside_its_trailers_paths_is_flagged``
(``orchestrator-trailers-acceptance-test``, ``no-trailers-acceptance-test``),
``test_an_orchestrator_s_conflict_resolution_under_acceptance_tests_is_flagged``
and the dropped tests of ``test_w1_50_merge_that_drops_a_parent_s_change.py``.

**The other side.** A test designer's ordinary (non-merge) commit under
``tests/acceptance/**`` stays silent, in its own call
(``test_a_test_designer_s_commit_during_the_lead_s_call_is_silent``), in an
orchestrator's call (``test_commits_inside_the_paths_of_their_own_trailers_are_silent``)
and brought by an orchestrator's ordinary merge
(``test_an_integration_merge_of_commits_inside_their_own_paths_is_silent``);
all unchanged. The last test here adds: an ordinary merge whose merge commit
carries a test designer's trailers and changes nothing itself is silent.

Each test asserts the finding that names the acceptance test. In a test
designer's call it asserts nothing about the other commits of the move: a
merge in a worker's call is judged as DEC-266 and DEC-327 say.
"""

from __future__ import annotations

import pytest

import w1_50_own_change_support as own_change
import w1_50_support as support
import w1_50_symmetric_support as symmetric

check_support = support.check_support

ORCHESTRATOR = support.ORCHESTRATOR
DESIGNER = support.DESIGNER
TICKET = support.TICKET
AS_DESIGNER = support.AS_DESIGNER
NO_TRAILERS = support.NO_TRAILERS

TESTS = symmetric.TESTS
PATH = support.ACCEPTANCE_FILE


# --------------------------------------------------------------------------
# An orchestrator session's own call; the merge commit carries a test designer's trailers
# --------------------------------------------------------------------------

def test_a_hand_edit_of_an_acceptance_test_in_a_merge_commit_with_a_test_designer_s_trailers_is_flagged(
        project, sandbox, call):
    """DEC-410, DP-27. An ordinary integration merge whose merge commit, with a test designer's trailers on a
    ticket in progress, also appends a line to an acceptance test neither side changed. The test is named; the
    paths the branch brought are not."""
    shape = own_change.hand_edit(project, sandbox, PATH, AS_DESIGNER)
    result, left = call(project, shape.command, ORCHESTRATOR, TICKET)
    own_change.assert_content_no_parent_holds(project, PATH)
    what = f"{shape.what}, in the orchestrator's own call on {TICKET}"
    check_support.assert_caught(result, PATH, what=what, action=check_support.FLAGGED)
    check_support.assert_not_recorded(result, *shape.brought, what=what)
    check_support.assert_left_as_the_call_left_it(project, left, what)


def test_a_conflict_resolution_of_an_acceptance_test_in_a_merge_commit_with_a_test_designer_s_trailers_is_flagged(
        project, sandbox, call):
    """DEC-410, DP-27. A test designer's commit on each side appended a line to the same acceptance test; the
    conflict is resolved to content neither parent holds, in a merge commit with a test designer's trailers.
    The test is named."""
    shape = own_change.conflict_resolved_to_new_content(project, sandbox, PATH, AS_DESIGNER, AS_DESIGNER)
    result, left = call(project, shape.command, ORCHESTRATOR, TICKET)
    own_change.assert_content_no_parent_holds(project, PATH)
    what = f"{shape.what}, in the orchestrator's own call on {TICKET}"
    check_support.assert_caught(result, PATH, what=what, action=check_support.FLAGGED)
    check_support.assert_left_as_the_call_left_it(project, left, what)


def _drop(project, call, shape, role):
    before = check_support.git(project, "rev-parse", "HEAD").strip()
    result, left = call(project, shape.command, role, TICKET)
    symmetric.assert_dropping(project, shape, before)
    return result, left, f"{shape.what}, in a call with GOV_ROLE={role!r} on {TICKET}"


def test_a_turned_round_merge_commit_with_a_test_designer_s_trailers_that_drops_tests_is_flagged(project, sandbox,
                                                                                               call):
    """DEC-410, DP-27; shape B of DEC-403. The merge commit's parents are ``HEAD~2`` and ``HEAD`` in that order
    and its tree is ``HEAD~2``'s: it puts back the acceptance test a test designer edited and removes the one a
    test designer added. It carries a test designer's trailers. Both tests are named."""
    shape = symmetric.parents_turned_round(project, sandbox, TESTS, AS_DESIGNER)
    result, left, what = _drop(project, call, shape, ORCHESTRATOR)
    assert check_support.read(project, TESTS.second) is None, (
        f"the fixture is wrong: {TESTS.second} is still there after the call"
    )
    check_support.assert_caught(result, *shape.named, what=what, action=check_support.FLAGGED)
    check_support.assert_left_as_the_call_left_it(project, left, what)


def test_an_ours_merge_with_a_test_designer_s_trailers_that_drops_tests_is_flagged(project, sandbox, call):
    """DEC-410, DP-27; shape D of DEC-403, with porcelain only: ``git checkout -b tmp HEAD~2``, an
    orchestrator's commit of ``README.md``, ``git merge -s ours main`` committed with a test designer's
    trailers, and ``main`` fast-forwarded to the result. Both dropped tests are named; ``README.md`` is not."""
    shape = symmetric.plain_porcelain(project, sandbox, TESTS, AS_DESIGNER)
    result, left, what = _drop(project, call, shape, ORCHESTRATOR)
    check_support.assert_caught(result, *shape.named, what=what, action=check_support.FLAGGED)
    check_support.assert_not_recorded(result, *shape.kept, what=what)
    check_support.assert_left_as_the_call_left_it(project, left, what)


# --------------------------------------------------------------------------
# A test designer session's own call
# --------------------------------------------------------------------------

# name: the merge commit's trailers. With none the caller decides, and the caller is the test designer.
TEST_DESIGNER_S = {
    "test-designer-trailers": AS_DESIGNER,
    "no-trailers": NO_TRAILERS,
}


@pytest.mark.parametrize("case", sorted(TEST_DESIGNER_S), ids=sorted(TEST_DESIGNER_S))
def test_a_hand_edit_of_an_acceptance_test_in_a_merge_commit_made_in_a_test_designer_s_call_is_flagged(
        project, sandbox, call, case):
    """DEC-410, DP-27: "whatever its trailers", and whoever may write the path in an ordinary commit. A test
    designer session's call merges a branch that holds a test designer's new test; the merge commit also
    appends a line to an existing acceptance test neither side changed. That test is named."""
    trailers = TEST_DESIGNER_S[case]
    support.ticket_branch(project, sandbox, (support.NEW_TEST, AS_DESIGNER))
    command = support.merge_with_own_change(PATH, trailers=trailers)
    result, left = call(project, command, DESIGNER, TICKET)
    own_change.assert_content_no_parent_holds(project, PATH)
    what = (f"a --no-ff merge of {support.TICKET_BRANCH} (a test designer's {support.NEW_TEST}) with trailers "
            f"{trailers} whose merge commit itself appends a line to {PATH}, in a test designer session's own "
            f"call on {TICKET}")
    check_support.assert_caught(result, PATH, what=what, action=check_support.FLAGGED)
    check_support.assert_left_as_the_call_left_it(project, left, what)


@pytest.mark.parametrize("case", sorted(TEST_DESIGNER_S), ids=sorted(TEST_DESIGNER_S))
def test_a_turned_round_merge_commit_made_in_a_test_designer_s_call_that_drops_tests_is_flagged(project, sandbox,
                                                                                              call, case):
    """DEC-410, DP-27; shape B of DEC-403, made in a test designer session's own call. The move holds one new
    commit, the merge commit, which undoes a test designer's edit of one acceptance test and removes another.
    Both tests are named."""
    shape = symmetric.parents_turned_round(project, sandbox, TESTS, TEST_DESIGNER_S[case])
    result, left, what = _drop(project, call, shape, DESIGNER)
    check_support.assert_caught(result, *shape.named, what=what, action=check_support.FLAGGED)
    check_support.assert_left_as_the_call_left_it(project, left, what)


# --------------------------------------------------------------------------
# The other side
# --------------------------------------------------------------------------

def test_an_ordinary_merge_whose_merge_commit_carries_a_test_designer_s_trailers_and_changes_nothing_is_silent(
        project, sandbox, call):
    """DP-27 speaks of the merge commit's own change. An ordinary ``git merge --no-ff`` in the orchestrator's
    own call brings a test designer's new test and an engineer's source file; the merge commit carries a test
    designer's trailers and holds nothing its parents do not hold. Every commit passes by its own trailers and
    the merge commit has no own change: silent (KPI success 2). A fix that flags every merge commit with a
    test designer's trailers fails this."""
    shape = support.ordinary_integration_merge(project, sandbox, trailers=AS_DESIGNER)
    before = check_support.git(project, "rev-parse", "HEAD").strip()
    result, left = call(project, shape.command, ORCHESTRATOR, TICKET)
    support.assert_shape(project, shape, before)
    assert support.trailer_values(project, "HEAD", "Role") == [DESIGNER], (
        "the fixture is wrong: the merge commit does not carry the test designer's Role trailer"
    )
    assert check_support.read(project, support.NEW_TEST), f"the merge did not bring in {support.NEW_TEST}"
    what = f"{shape.what}, with a test designer's trailers on the merge commit, in the orchestrator's own call"
    check_support.assert_silent(result, what)
    check_support.assert_left_as_the_call_left_it(project, left, what)

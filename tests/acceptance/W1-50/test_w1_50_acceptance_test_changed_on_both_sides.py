"""W1-50 — an acceptance test that both sides of a merge changed is the merge commit's own change.

Added after implementation; reason: delegated decision, DEC-410 (packages DP-24
option (b) and DP-26 option (a)).

DEC-410, DP-24: "under `tests/acceptance/**`, a path that more than one parent
changed against the merge base is the merge commit's own, whichever side's
content it holds. Taking one side whole is a resolution, and a resolution of
an acceptance test is a finding (DEC-269)."

DEC-410, DP-26: "git's own clean combination of two sides' edits of one
acceptance test stays flagged, as built. Branches are brought to a state where
no acceptance test is changed on both sides before they are merged."

**The shapes.** Since their one merge base, the ticket branch and ``main`` each
changed the same acceptance test, each by a test designer's commit that passes
by its own trailers. Whatever the merge commit holds for that path, the path is
in ``read_merge(...).own`` and not in ``brought``, and the orchestrator's merge
in its own call is a finding that names it:

- the merge commit holds the first parent's content of it whole;
- it holds the second parent's content whole. Until DEC-410 the second parent
  "brought" it (DEC-394) and the merge was silent;
- either order of the parents for those two: an ordinary ``git merge --no-ff``
  whose conflict is resolved with ``git checkout --ours`` or ``--theirs``, and
  a merge commit made with ``git commit-tree`` whose first parent is the branch;
- git's own clean combination of two edits in different parts of the file
  (DP-26);
- both sides made the identical change: the merge commit differs from neither
  parent, and by the words of DP-24 the path is "a path that more than one
  parent changed against the merge base" all the same. Through the check this
  is the rewritten ``test_a_merge_of_two_sides_that_made_the_same_change_of_a_test_is_flagged``
  (``test_w1_50_merge_that_takes_each_side_s_change.py``); through the helper
  it is here.

The merge commit carries the orchestrator's trailers; one case carries a test
designer's (a finding by DP-27 as well).

Other existing cases rewritten to this rule: the conflict resolved to the
merged side's content (``test_w1_50_merge_commit_own_changes.py``) and the
``-X theirs`` merge (``test_w1_50_merge_read_by_the_merge_base.py``).

**The other side.** The same shapes for a path outside ``tests/acceptance/**``
and outside ``.tickets/**`` are read as before: the path is not the merge
commit's own, the merge commit holding the second parent's changed content has
it in ``brought``, and the merge is silent. A merge in which each side changed
a *different* acceptance test has an empty ``own`` and is silent
(``test_an_integration_merge_stays_silent_when_main_got_a_test_designer_s_commit_since_the_fork``,
unchanged, through the check). With several merge bases, or none, nothing
changes: every path that differs from any parent is the merge commit's own
already (DP-23).

**Now pinned:** DEC-421 extends the both-sides rule to ``.tickets/**`` too.
The tests for that are in ``test_w1_50_ticket_file_changed_on_both_sides.py``.
"""

from __future__ import annotations

import pytest

import w1_50_own_change_support as own_change
import w1_50_support as support
import w1_50_symmetric_support as symmetric

check_support = support.check_support

ORCHESTRATOR = support.ORCHESTRATOR
TICKET = support.TICKET
AS_DESIGNER = support.AS_DESIGNER
AS_ENGINEER = support.AS_ENGINEER
AS_ORCHESTRATOR = support.AS_ORCHESTRATOR

FIRST = own_change.FIRST
SECOND = own_change.SECOND
TEST = support.ACCEPTANCE_FILE
OUTSIDE = support.SOURCE              # outside tests/acceptance/** and .tickets/**; both sides' commits an engineer's


@pytest.fixture()
def helper(monkeypatch):
    """``helper()`` -> the module ``gov.guard.containment_merge``, imported when it is first called."""
    return own_change.helper_module(monkeypatch)


# name: (the parent whose content of the test the merge commit holds whole, the parents are turned round)
ONE_SIDE_WHOLE = {
    "holds-the-first-parent-s-content-an-ordinary-merge": (FIRST, False),
    "holds-the-second-parent-s-content-an-ordinary-merge": (SECOND, False),
    "holds-the-first-parent-s-content-the-parents-turned-round": (FIRST, True),
    "holds-the-second-parent-s-content-the-parents-turned-round": (SECOND, True),
}


def _call(project, call, shape):
    """One call of the orchestrator makes the merge commit of ``shape``. Returns (result, state after, what)."""
    before = check_support.git(project, "rev-parse", "HEAD").strip()
    branch = check_support.git(project, "rev-parse", support.TICKET_BRANCH).strip()
    result, left = call(project, shape.command, ORCHESTRATOR, TICKET)
    own_change.assert_both_changed(project, shape, before, branch)
    return result, left, f"{shape.what}, in the orchestrator's own call on {TICKET}"


def _build(project, sandbox, shape):
    """Make the merge commit of ``shape`` with no hook around it. Returns the state a reading must leave."""
    before = check_support.git(project, "rev-parse", "HEAD").strip()
    branch = check_support.git(project, "rev-parse", support.TICKET_BRANCH).strip()
    state = own_change.built(project, sandbox, shape.command)
    own_change.assert_both_changed(project, shape, before, branch)
    return state


def _assert_the_test_is_named(project, shape, made):
    """A finding names the test both sides changed; the path only the branch changed is not named."""
    result, left, what = made
    check_support.assert_caught(result, shape.path, what=what, action=check_support.FLAGGED)
    check_support.assert_not_recorded(result, shape.also, what=what)
    check_support.assert_left_as_the_call_left_it(project, left, what)


def _assert_own_not_brought(reading, shape):
    assert shape.path in reading.own, (
        f"read_merge on {shape.what}: `own` is {reading.own!r}; it does not hold {shape.path}, which more than "
        f"one parent changed against the merge base (DEC-410, DP-24)"
    )
    assert shape.path not in reading.brought, (
        f"read_merge on {shape.what}: `brought` holds {shape.path}: {reading.brought!r} (DEC-410, DP-24)"
    )
    assert shape.also not in reading.own, (
        f"read_merge on {shape.what}: `own` holds {shape.also}, which only the branch changed: {reading.own!r}"
    )


# --------------------------------------------------------------------------
# The merge commit holds one side's content of the test whole
# --------------------------------------------------------------------------

@pytest.mark.parametrize("case", sorted(ONE_SIDE_WHOLE), ids=sorted(ONE_SIDE_WHOLE))
def test_a_merge_that_takes_one_side_s_content_of_a_test_both_sides_changed_is_flagged(project, sandbox, call,
                                                                                      case):
    """DEC-410, DP-24. "Taking one side whole is a resolution, and a resolution of an acceptance test is a
    finding." The test is named whichever parent's content the merge commit holds and whichever parent comes
    first; the source file only the branch changed is not named."""
    holds, turned_round = ONE_SIDE_WHOLE[case]
    shape = own_change.changed_on_both_sides(project, sandbox, TEST, AS_DESIGNER, holds, turned_round)
    _assert_the_test_is_named(project, shape, _call(project, call, shape))


@pytest.mark.parametrize("case", sorted(ONE_SIDE_WHOLE), ids=sorted(ONE_SIDE_WHOLE))
def test_read_merge_puts_a_test_both_sides_changed_in_own_whichever_side_s_content_the_merge_commit_holds(
        project, sandbox, helper, case):
    """DEC-410, DP-24, through the helper: the test is in ``own`` and not in ``brought``; the source file only
    the branch changed is not in ``own``."""
    holds, turned_round = ONE_SIDE_WHOLE[case]
    shape = own_change.changed_on_both_sides(project, sandbox, TEST, AS_DESIGNER, holds, turned_round)
    state = _build(project, sandbox, shape)
    reading = own_change.read(project, helper, "HEAD", shape.what)
    _assert_own_not_brought(reading, shape)
    own_change.assert_left(project, state, shape.what)


def test_the_same_merge_with_a_test_designer_s_trailers_on_the_merge_commit_is_flagged(project, sandbox, call):
    """DEC-410, DP-24 with DP-27. The merge commit holds the merged side's content of the test and carries a
    test designer's trailers on a ticket in progress: the path is its own change, and its own change of an
    acceptance test is a finding whatever its trailers."""
    shape = own_change.changed_on_both_sides(project, sandbox, TEST, AS_DESIGNER, SECOND, trailers=AS_DESIGNER)
    made = _call(project, call, shape)
    assert support.trailer_values(project, "HEAD", "Role") == [support.DESIGNER], (
        "the fixture is wrong: the merge commit does not carry the test designer's Role trailer"
    )
    _assert_the_test_is_named(project, shape, made)


# --------------------------------------------------------------------------
# DP-26: git's own clean combination of two edits
# --------------------------------------------------------------------------

def test_a_clean_combination_of_two_sides_edits_of_one_test_is_flagged(project, sandbox, call):
    """DEC-410, DP-26: "stays flagged, as built". A test designer changed line 2 of an acceptance test on the
    branch and line 19 on ``main``; ``git merge`` combines them without a conflict, and the merge commit holds
    content of the test neither parent holds. The test is named."""
    shape = own_change.changed_on_both_sides_in_different_parts(project, sandbox)
    _assert_the_test_is_named(project, shape, _call(project, call, shape))


def test_read_merge_puts_a_clean_combination_of_two_sides_edits_of_one_test_in_own(project, sandbox, helper):
    """DEC-410, DP-26, through the helper: the test is in ``own`` and not in ``brought``."""
    shape = own_change.changed_on_both_sides_in_different_parts(project, sandbox)
    state = _build(project, sandbox, shape)
    reading = own_change.read(project, helper, "HEAD", shape.what)
    _assert_own_not_brought(reading, shape)
    own_change.assert_left(project, state, shape.what)


# --------------------------------------------------------------------------
# Both sides made the identical change
# --------------------------------------------------------------------------

def test_read_merge_puts_a_test_both_sides_changed_in_the_same_way_in_own(project, sandbox, helper):
    """DEC-410, DP-24, read by its words: "a path that more than one parent changed against the merge base".
    A test designer made the same change of an acceptance test on the branch and on ``main``; the merge commit
    holds that content, which is each parent's. The test is in ``own`` and not in ``brought``; the engineer's
    source file the branch brings is in ``brought``."""
    shape = symmetric.both_sides_made_the_same_change(project, sandbox)
    state = own_change.built(project, sandbox, shape.command)
    assert symmetric.differing_from_any_parent(project) == [support.SOURCE], (
        f"the fixture is wrong: the merge commit differs from its parents in "
        f"{symmetric.differing_from_any_parent(project)}"
    )
    base = support.merge_bases(project, "HEAD^1", "HEAD^2")
    held = support.content_at(project, "HEAD", TEST)
    assert len(base) == 1 and held == support.content_at(project, "HEAD^1", TEST) == support.content_at(
        project, "HEAD^2", TEST) != support.content_at(project, base[0], TEST), (
        f"the fixture is wrong: the two parents did not make the same change of {TEST} against one merge base"
    )
    reading = own_change.read(project, helper, "HEAD", shape.what)
    assert reading.own == [TEST], (
        f"read_merge on {shape.what}: `own` is {reading.own!r}, not {[TEST]!r}: both parents changed the test "
        f"against the merge base (DEC-410, DP-24)"
    )
    assert reading.brought == [support.SOURCE], (
        f"read_merge on {shape.what}: `brought` is {reading.brought!r}, not {[support.SOURCE]!r}"
    )
    own_change.assert_left(project, state, shape.what)


# --------------------------------------------------------------------------
# The other side: a path outside tests/acceptance/** and .tickets/**; different tests on each side
# --------------------------------------------------------------------------

# name: the parent whose content of the source file the merge commit holds whole
OUTSIDE_ONE_SIDE_WHOLE = {
    "holds-the-first-parent-s-content": FIRST,
    "holds-the-second-parent-s-content": SECOND,
}


@pytest.mark.parametrize("case", sorted(OUTSIDE_ONE_SIDE_WHOLE), ids=sorted(OUTSIDE_ONE_SIDE_WHOLE))
def test_a_merge_that_takes_one_side_s_content_of_a_source_file_both_sides_changed_stays_silent(project, sandbox,
                                                                                               call, case):
    """DP-24 names ``tests/acceptance/**``. Both sides changed a source file by an engineer's commit inside its
    ticket's paths; the merge commit holds one side's content whole. That content is a parent's and differs
    from the merge base: it is brought, as before, and the merge is silent. A fix that takes every path both
    sides changed for the merge commit's own, and judges it, must still find nothing here; a fix that flags
    the shape fails."""
    shape = own_change.changed_on_both_sides(project, sandbox, OUTSIDE, AS_ENGINEER, OUTSIDE_ONE_SIDE_WHOLE[case])
    result, left, what = _call(project, call, shape)
    check_support.assert_silent(result, what)
    check_support.assert_left_as_the_call_left_it(project, left, what)


@pytest.mark.parametrize("case", sorted(OUTSIDE_ONE_SIDE_WHOLE), ids=sorted(OUTSIDE_ONE_SIDE_WHOLE))
def test_read_merge_reads_a_source_file_both_sides_changed_as_before(project, sandbox, helper, case):
    """The same history through the helper: the source file is not in ``own``. Where the merge commit holds
    the second parent's content of it, changed there against the merge base, it is in ``brought`` (DEC-394)."""
    holds = OUTSIDE_ONE_SIDE_WHOLE[case]
    shape = own_change.changed_on_both_sides(project, sandbox, OUTSIDE, AS_ENGINEER, holds)
    state = _build(project, sandbox, shape)
    reading = own_change.read(project, helper, "HEAD", shape.what)
    assert reading.own == [], (
        f"read_merge on {shape.what}: `own` is {reading.own!r}, not empty: DP-24 names tests/acceptance/** only"
    )
    if holds == SECOND:
        assert shape.path in reading.brought, (
            f"read_merge on {shape.what}: `brought` lacks {shape.path}: {reading.brought!r}"
        )
    own_change.assert_left(project, state, shape.what)


def test_read_merge_finds_no_own_change_where_each_side_changed_another_acceptance_test(project, sandbox, helper):
    """DP-24 speaks of one path that more than one parent changed. A test designer added a test on the branch
    and another changed a different test on ``main``; the merge commit holds both. ``own`` is empty."""
    shape = own_change.each_side_changed_another_acceptance_test(project, sandbox)
    state = own_change.built(project, sandbox, shape.command)
    symmetric.assert_taking(project, shape)
    reading = own_change.read(project, helper, "HEAD", shape.what)
    assert reading.own == [], f"read_merge on {shape.what}: `own` is {reading.own!r}, not empty"
    own_change.assert_left(project, state, shape.what)

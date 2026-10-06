"""W1-50 — what ``read_merge(...).brought`` holds: the complement of ``own`` over every parent.

Added after implementation; reason: delegated decision, DEC-410 (package DP-22).

DEC-410, DP-22: "`brought` is the complement of `own` over every parent: each
path where the merge commit differs from some parent and that is not its own."

Until DEC-410 ``brought`` held only paths where the merge commit differs from
its *first* parent: what the first parent brought against another parent was in
neither list. Now ``own`` and ``brought`` together are exactly the paths where
the merge commit differs from any parent (and, by DP-24, an acceptance test
both sides changed in the same way, which differs from none and is in
``own``); ``brought`` is sorted, holds no path twice and no path of ``own``.

Through the helper only (``from gov.guard.containment_merge import read_merge``,
DEC-398), imported inside the test when the history is built, as in the other
helper cases.

The cases here: a merge commit with a change of its own (a hand edit; a
dropped change beside a path its first parent brought), and a fail-closed
merge in which the first parent holds a change of its own.

Existing helper cases, rewritten after implementation to compare ``brought``
exactly (reason: delegated decision, DEC-410):

- an ordinary two-parent merge where each side changed its own path, and the
  same with the parents turned round:
  ``test_read_merge_finds_no_own_change_in_a_merge_that_takes_each_side_s_change``;
- an ordinary octopus merge of two branches, and the other histories of the
  seventh batch:
  ``test_read_merge_says_which_paths_are_the_merge_commit_s_own_and_which_another_parent_brought``;
- an ordinary octopus merge of eight branches:
  ``test_read_merge_finds_no_own_change_in_an_ordinary_octopus_merge_of_eight_branches``;
- the ``-s ours`` merge and the ordinary merge after it:
  ``test_read_merge_puts_what_an_ours_merge_drops_in_its_own_and_not_in_the_ordinary_merge_s_after_it``;
- an octopus whose other parents cross only each other:
  ``test_read_merge_reads_an_octopus_whose_other_parents_cross_only_each_other_parent_by_parent``.

The fail-closed shapes (several merge bases, none, an octopus with a crossing
parent) keep an empty ``brought``, as before; the existing cases of
``test_w1_50_read_merge_every_parent.py`` hold that, unchanged.
"""

from __future__ import annotations

import pytest

import w1_50_own_change_support as own_change
import w1_50_support as support
import w1_50_symmetric_support as symmetric

check_support = support.check_support

AS_ORCHESTRATOR = support.AS_ORCHESTRATOR
NO_TRAILERS = support.NO_TRAILERS
TESTS = symmetric.TESTS


@pytest.fixture()
def helper(monkeypatch):
    """``helper()`` -> the module ``gov.guard.containment_merge``, imported when it is first called."""
    return own_change.helper_module(monkeypatch)


def _assert_reading(reading, own, brought, what):
    assert reading.own == sorted(own), f"read_merge on {what}: `own` is {reading.own!r}, not {sorted(own)!r}"
    assert reading.brought == sorted(brought), (
        f"read_merge on {what}: `brought` is {reading.brought!r}, not {sorted(brought)!r}: every path where the "
        f"merge commit differs from some parent and that is not its own (DEC-410, DP-22)"
    )


def test_read_merge_puts_what_either_parent_brought_beside_a_hand_edit_in_brought(project, sandbox, helper):
    """An ordinary integration merge of a branch with a test designer's new test and an engineer's source
    file; ``main`` moved on with an orchestrator's commit; the merge commit also appends a line to
    ``README.md``. ``own`` is ``README.md``. ``brought`` is the branch's two paths and the path ``main``
    changed, which the first parent brought against the second. Together they are exactly the paths where the
    merge commit differs from a parent."""
    shape = own_change.hand_edit(project, sandbox, support.README, AS_ORCHESTRATOR)
    state = own_change.built(project, sandbox, shape.command)
    own_change.assert_content_no_parent_holds(project, support.README)
    brought = [support.BOOTSTRAP, support.NEW_TEST, support.SOURCE]
    assert symmetric.differing_from_any_parent(project) == sorted([support.README, *brought]) and (
        symmetric.differing(project, "HEAD", "HEAD^2") == sorted([support.README, support.BOOTSTRAP])), (
        f"the fixture is wrong: the merge commit differs from its parents in "
        f"{symmetric.differing_from_any_parent(project)}, from the second in "
        f"{symmetric.differing(project, 'HEAD', 'HEAD^2')}"
    )
    reading = own_change.read(project, helper, "HEAD", shape.what)
    _assert_reading(reading, [support.README], brought, shape.what)
    assert sorted(reading.own + reading.brought) == symmetric.differing_from_any_parent(project), (
        f"read_merge on {shape.what}: `own` and `brought` together are not the paths where the merge commit "
        f"differs from a parent"
    )
    own_change.assert_left(project, state, shape.what)


def test_read_merge_puts_what_the_first_parent_brought_beside_a_dropped_change_in_brought(project, sandbox,
                                                                                         helper):
    """Shape D of DEC-403: a branch cut before two test designer's commits got an orchestrator's commit of
    ``README.md`` and took ``main`` with ``git merge -s ours``. The merge commit changes nothing against its
    first parent. ``own`` is the two dropped tests; ``brought`` is ``README.md``, which the first parent
    changed against the merge base and the second parent does not hold so."""
    shape = symmetric.plain_porcelain(project, sandbox, TESTS, NO_TRAILERS)
    state = own_change.built(project, sandbox, shape.command)
    symmetric.assert_own(project, "HEAD", TESTS.paths, shape.what)
    assert symmetric.differing(project, "HEAD", "HEAD^1") == [] and symmetric.differing(
        project, "HEAD", "HEAD^2") == sorted([support.README, *TESTS.paths]), (
        "the fixture is wrong: the merge commit does not differ from its parents as the test describes"
    )
    reading = own_change.read(project, helper, "HEAD", shape.what)
    _assert_reading(reading, TESTS.paths, [support.README], shape.what)
    own_change.assert_left(project, state, shape.what)


def test_read_merge_puts_the_change_a_turned_round_merge_commit_keeps_in_brought(project, sandbox, helper):
    """Shape E of DEC-403: the parents are ``HEAD~2`` and ``HEAD`` in that order; the tree is ``HEAD``'s with
    the first of two test designer's changes set back. ``own`` is the test set back; ``brought`` is the test
    that was kept, the second parent's content."""
    shape = symmetric.turned_round_setting_one_back(project, sandbox, TESTS, AS_ORCHESTRATOR)
    state = own_change.built(project, sandbox, shape.command)
    symmetric.assert_own(project, "HEAD", [TESTS.first], shape.what)
    reading = own_change.read(project, helper, "HEAD", shape.what)
    _assert_reading(reading, [TESTS.first], [TESTS.second], shape.what)
    own_change.assert_left(project, state, shape.what)


def test_read_merge_brings_nothing_in_a_criss_cross_merge_although_each_parent_holds_a_change_of_its_own(
        project, sandbox, helper):
    """Fail closed, as before (DEC-398, DEC-403; DP-23 as built): with several merge bases nothing is brought.
    After the crossing the merged side got an engineer's source file and ``main`` an orchestrator's commit; an
    ordinary ``git merge --no-ff`` holds both. ``own`` is both paths, also the one the merge commit keeps as
    its first parent has it; ``brought`` is empty, which is the complement of ``own`` here too."""
    shape = own_change.criss_cross_after_main_moved_on(project, sandbox)
    state = own_change.built(project, sandbox, shape.command)
    assert len(support.merge_bases(project, "HEAD^1", "HEAD^2")) == 2, (
        "the fixture is wrong: the parents do not have two merge bases"
    )
    own = [support.BOOTSTRAP, support.SOURCE]
    assert symmetric.differing(project, "HEAD", "HEAD^1") == [support.SOURCE] and symmetric.differing(
        project, "HEAD", "HEAD^2") == [support.BOOTSTRAP], (
        "the fixture is wrong: the merge commit does not differ from its parents as the test describes"
    )
    reading = own_change.read(project, helper, "HEAD", shape.what)
    _assert_reading(reading, own, [], shape.what)
    own_change.assert_left(project, state, shape.what)

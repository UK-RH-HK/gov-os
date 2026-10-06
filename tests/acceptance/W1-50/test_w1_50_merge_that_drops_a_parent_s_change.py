"""W1-50 — a merge commit that keeps one parent's content and so drops what another parent changed.

Added after implementation; reason: delegated decision, DEC-403 (package DP-20,
option (a): the symmetric rule, in the one helper).

**The gap.** DEC-394 and DEC-398 read a merge commit against its first parent
alone. A merge commit that holds its first parent's content of a path, where
another parent changed that path, changes nothing against its first parent: it
was never judged, and a test designer's commit could be dropped unseen.

**DEC-403.** A merge commit is read against every parent the way it is read
against the first. A path where its content differs from any parent's is the
merge commit's own change, unless another parent brought it by the three-way
rule: that parent holds the merge commit's content of the path, and that
content differs from the merge base. With several merge bases, or none, every
path that differs from any parent is the merge commit's own change. An own
change is judged as before (DEC-269): by the merge commit's trailers, or
against the caller when it has none.

Every call here is an orchestrator session's own call (DEC-266, DEC-319). The
histories are built in ``w1_50_symmetric_support.py``; ``assert_dropping``
checks each from git's own answers: the dropping merge commit is new in the
move, its own changes by the words of DEC-403 are the ones the builder names,
and read against its first parent alone none of the named paths is its own.

**What is dropped**, one case each for every shape:

- *a test designer's tests*: a commit that edits an existing acceptance test
  and a commit that adds a new one. No trailers of a merge commit here allow a
  path under ``tests/acceptance/**``, and the caller's do not either;
- *an orchestrator's ticket files*: a commit that narrows one ticket's allowed
  paths and a commit that closes another ticket. The dropping merge commit
  carries an engineer's trailers: a change under ``.tickets/**`` in a commit
  with a worker's ``Role`` trailer is a finding (DEC-390, DP-16). A dropping
  merge commit with the orchestrator's trailers, or none, that undoes ticket
  files is a finding since DEC-410 (DP-21):
  ``test_w1_50_merge_commit_own_change_of_a_ticket_file.py``.

**Which merge commit the finding is for, in shape N.** A ticket branch takes
``main`` with ``git merge -s ours`` and is then merged into ``main`` with an
ordinary ``git merge --no-ff``. By the rule's words the own change is the
``-s ours`` merge commit's: it differs from its second parent (``main``) in
the dropped paths, and its first parent, whose content it holds, never changed
them. The final merge commit holds its second parent's content of those paths,
and that content differs from the merge base (``main`` as it was): they are
brought, and the final merge commit has no own change. The ``-s ours`` merge
commit is new to ``HEAD`` in the move whether it was made in the call (N1) or
before it (N2), so in both the finding is for that commit.
"""

from __future__ import annotations

import pytest

import w1_50_support as support
import w1_50_symmetric_support as symmetric

check_support = support.check_support

ORCHESTRATOR = support.ORCHESTRATOR
TICKET = support.TICKET
AS_ENGINEER = support.AS_ENGINEER
AS_ORCHESTRATOR = support.AS_ORCHESTRATOR
NO_TRAILERS = support.NO_TRAILERS

TESTS = symmetric.TESTS
TICKETS = symmetric.TICKETS

# name: (what is dropped, the dropping merge commit's trailers)
BY_DEFAULT = {
    TESTS.name: (TESTS, TESTS.trailers),
    TICKETS.name: (TICKETS, TICKETS.trailers),
}

# The trailers varied, on the first shape: none of them allows a path under tests/acceptance/**.
WITH_EACH_TRAILERS = {
    "a-test-designer-s-tests-orchestrator-trailers": (TESTS, AS_ORCHESTRATOR),
    "a-test-designer-s-tests-engineer-trailers": (TESTS, AS_ENGINEER),
    # No trailers: the caller decides, and the orchestrator may not write an acceptance test.
    "a-test-designer-s-tests-no-trailers": (TESTS, NO_TRAILERS),
    "an-orchestrator-s-ticket-files-engineer-trailers": (TICKETS, AS_ENGINEER),
}


def _make(project, call, shape):
    """One call of the orchestrator makes the move of ``shape``. Returns (result, state after, what, the
    dropping merge commit's id)."""
    before = check_support.git(project, "rev-parse", "HEAD").strip()
    result, left = call(project, shape.command, ORCHESTRATOR, TICKET)
    dropping = symmetric.assert_dropping(project, shape, before)
    return result, left, f"{shape.what}, in the orchestrator's own call on {TICKET}", dropping


def _assert_the_dropped_paths_are_named(project, shape, made):
    """A finding names every dropped path; what another parent brought into the dropping merge commit is not
    named; the call is flagged and nothing is reverted."""
    result, left, what, _ = made
    check_support.assert_caught(result, *shape.named, what=what, action=check_support.FLAGGED)
    if shape.kept:
        check_support.assert_not_recorded(result, *shape.kept, what=what)
    check_support.assert_left_as_the_call_left_it(project, left, what)


# --------------------------------------------------------------------------
# B, C: the parents turned round
# --------------------------------------------------------------------------

@pytest.mark.parametrize("case", sorted(WITH_EACH_TRAILERS), ids=sorted(WITH_EACH_TRAILERS))
def test_a_merge_commit_with_its_parents_turned_round_is_flagged_for_what_it_drops(project, sandbox, call, case):
    """DEC-403, DP-20; shape B. The merge commit's first parent is ``HEAD~2`` and its second parent ``HEAD``;
    its tree is ``HEAD~2``'s. Against its first parent it changes nothing. Against its second parent it changes
    the two paths of the commits in between, and its first parent never changed them: both are its own change,
    and both are named."""
    dropped, trailers = WITH_EACH_TRAILERS[case]
    shape = symmetric.parents_turned_round(project, sandbox, dropped, trailers)
    earlier = check_support.git(project, "rev-parse", "HEAD~2").strip()
    before = check_support.git(project, "rev-parse", "HEAD").strip()
    made = _make(project, call, shape)
    assert support.parents_of(project) == [earlier, before], (
        f"the fixture is wrong: the merge commit's parents are {support.parents_of(project)}"
    )
    assert symmetric.differing(project, "HEAD", "HEAD^1") == [], (
        "the fixture is wrong: the merge commit does not hold its first parent's tree"
    )
    assert check_support.git(project, "rev-list", f"{before}..HEAD").split() == [made[1][0][0]], (
        "the fixture is wrong: the move holds other new commits than the merge commit"
    )
    _assert_the_dropped_paths_are_named(project, shape, made)


@pytest.mark.parametrize("case", sorted(BY_DEFAULT), ids=sorted(BY_DEFAULT))
def test_a_turned_round_merge_commit_whose_first_parent_is_a_new_empty_commit_is_flagged(project, sandbox, call,
                                                                                       case):
    """Shape C. As B, the first parent being a new empty commit on top of ``HEAD~2``: no parent of the merge
    commit is an earlier commit of ``HEAD``'s history, and the first parent's content of the dropped paths is
    still the merge base's."""
    dropped, trailers = BY_DEFAULT[case]
    shape = symmetric.turned_round_through_a_new_empty_commit(project, sandbox, dropped, trailers)
    earlier = check_support.git(project, "rev-parse", "HEAD~2").strip()
    before = check_support.git(project, "rev-parse", "HEAD").strip()
    made = _make(project, call, shape)
    empty, second = support.parents_of(project)
    assert second == before and support.parents_of(project, empty) == [earlier] and not support.is_ancestor(
        project, empty, before), (
        "the fixture is wrong: the first parent is no new commit on top of HEAD~2, or the second is not HEAD"
    )
    assert symmetric.differing(project, empty, earlier) == [] and symmetric.differing(project, "HEAD", empty) == [], (
        "the fixture is wrong: the first parent is not empty, or the merge commit does not hold its tree"
    )
    _assert_the_dropped_paths_are_named(project, shape, made)


# --------------------------------------------------------------------------
# D: plain porcelain
# --------------------------------------------------------------------------

# The tests: the merge commit as `git merge -s ours main` alone makes it, without trailers.
PLAIN_PORCELAIN = {
    "a-test-designer-s-tests-no-trailers": (TESTS, NO_TRAILERS),
    TICKETS.name: (TICKETS, TICKETS.trailers),
}


@pytest.mark.parametrize("case", sorted(PLAIN_PORCELAIN), ids=sorted(PLAIN_PORCELAIN))
def test_a_branch_cut_before_the_changes_that_takes_main_with_ours_and_is_fast_forwarded_to_is_flagged(
        project, sandbox, call, case):
    """Shape D, with porcelain only: ``git checkout -b tmp HEAD~2``, an orchestrator's commit of a file outside
    the judged paths, ``git merge -s ours main``, and ``main`` fast-forwarded to the result. The merge commit
    holds its first parent's tree, so it drops what ``main`` got since ``HEAD~2``. The dropped paths are named;
    the orchestrator's own file is not."""
    dropped, trailers = PLAIN_PORCELAIN[case]
    shape = symmetric.plain_porcelain(project, sandbox, dropped, trailers)
    before = check_support.git(project, "rev-parse", "HEAD").strip()
    made = _make(project, call, shape)
    first, second = support.parents_of(project)
    assert second == before and symmetric.differing(project, "HEAD", first) == [], (
        "the fixture is wrong: the merge commit's second parent is not main as the call found it, or the merge "
        "commit does not hold its first parent's tree"
    )
    assert support.changed_paths(project, first) == [support.README], (
        f"the fixture is wrong: the commit on {symmetric.TEMPORARY} changes {support.changed_paths(project, first)}"
    )
    _assert_the_dropped_paths_are_named(project, shape, made)


# --------------------------------------------------------------------------
# E: only one of two changes is set back
# --------------------------------------------------------------------------

@pytest.mark.parametrize("case", sorted(BY_DEFAULT), ids=sorted(BY_DEFAULT))
def test_a_turned_round_merge_commit_that_sets_back_one_of_two_changes_is_flagged_for_that_one(project, sandbox,
                                                                                             call, case):
    """Shape E. The parents are ``HEAD~2`` and ``HEAD`` in that order; the tree is ``HEAD``'s with the first of
    the two changed paths set back to ``HEAD~2``'s content. The path set back is named. The path that was kept
    is ``HEAD``'s content, which differs from the merge base: the second parent brought it, and it is not
    named."""
    dropped, trailers = BY_DEFAULT[case]
    shape = symmetric.turned_round_setting_one_back(project, sandbox, dropped, trailers)
    made = _make(project, call, shape)
    assert symmetric.differing(project, "HEAD", "HEAD^1") == [dropped.second] and symmetric.differing(
        project, "HEAD", "HEAD^2") == [dropped.first], (
        f"the fixture is wrong: the merge commit differs from its first parent in "
        f"{symmetric.differing(project, 'HEAD', 'HEAD^1')} and from its second in "
        f"{symmetric.differing(project, 'HEAD', 'HEAD^2')}"
    )
    _assert_the_dropped_paths_are_named(project, shape, made)


# --------------------------------------------------------------------------
# J2: an octopus merge turned round
# --------------------------------------------------------------------------

@pytest.mark.parametrize("case", sorted(BY_DEFAULT), ids=sorted(BY_DEFAULT))
def test_an_octopus_merge_commit_that_holds_the_tree_of_a_side_forked_before_the_changes_is_flagged(
        project, sandbox, call, case):
    """Shape J2. The parents are ``side``, ``HEAD`` and ``HEAD~1``; the tree is ``side``'s, and ``side`` forked
    before the two changes. Every pair of parents has one merge base. No parent that holds the merge commit's
    content of a dropped path changed it against a merge base: both paths are the merge commit's own. The
    side's own file is brought by the first parent and is not named."""
    dropped, trailers = BY_DEFAULT[case]
    shape = symmetric.octopus_turned_round(project, sandbox, dropped, trailers)
    before = check_support.git(project, "rev-parse", "HEAD").strip()
    made = _make(project, call, shape)
    parents = support.parents_of(project)
    assert len(parents) == 3 and parents[1] == before and parents[2] == check_support.git(
        project, "rev-parse", f"{before}~1").strip(), (
        f"the fixture is wrong: the merge commit's parents are {parents}"
    )
    assert symmetric.differing(project, "HEAD", parents[0]) == [] and not symmetric.fails_closed(project), (
        "the fixture is wrong: the merge commit does not hold its first parent's tree, or a parent has several "
        "merge bases, or none, with the first"
    )
    _assert_the_dropped_paths_are_named(project, shape, made)


# --------------------------------------------------------------------------
# NB2: no merge base
# --------------------------------------------------------------------------

@pytest.mark.parametrize("case", sorted(BY_DEFAULT), ids=sorted(BY_DEFAULT))
def test_a_merge_commit_on_an_unrelated_first_parent_is_flagged_for_the_paths_it_deletes(project, sandbox, call,
                                                                                       case):
    """Shape NB2; DEC-403: "with several merge bases, or none, every path that differs from any parent is the
    merge commit's own change". The first parent is a new commit without a parent and with an empty tree; the
    second is ``HEAD``. The merge commit's tree is ``HEAD``'s without ``tests/acceptance/`` (the tests) or
    without the two ticket files (the tickets). The deleted paths differ from the second parent only; they are
    named."""
    dropped, trailers = BY_DEFAULT[case]
    shape = symmetric.unrelated_first_parent(project, sandbox, dropped, trailers)
    before = check_support.git(project, "rev-parse", "HEAD").strip()
    made = _make(project, call, shape)
    root, second = support.parents_of(project)
    assert second == before and support.parents_of(project, root) == [] and symmetric.tree_paths(
        project, root) == [] and support.merge_bases(project, root, second) == [], (
        "the fixture is wrong: the first parent is no commit without a parent and with an empty tree, or the "
        "second parent is not HEAD"
    )
    for path in shape.named:
        assert not support.is_tracked(project, path) and support.is_tracked(project, path, before), (
            f"the fixture is wrong: the merge commit does not delete {path}"
        )
    _assert_the_dropped_paths_are_named(project, shape, made)


# --------------------------------------------------------------------------
# N: a ticket branch takes main with `-s ours`, then an ordinary merge of the branch
# --------------------------------------------------------------------------

# name: (what is dropped, the `-s ours` merge commit's trailers, that merge is made in the call)
OURS_THEN_AN_ORDINARY_MERGE = {
    "N1-both-merges-in-the-call-a-test-designer-s-tests-orchestrator-trailers": (TESTS, AS_ORCHESTRATOR, True),
    # As `git merge -s ours main` alone makes it. No trailers: the caller decides.
    "N1-both-merges-in-the-call-a-test-designer-s-tests-no-trailers": (TESTS, NO_TRAILERS, True),
    "N1-both-merges-in-the-call-an-orchestrator-s-ticket-files": (TICKETS, TICKETS.trailers, True),
    "N2-ours-before-the-call-a-test-designer-s-tests-orchestrator-trailers": (TESTS, AS_ORCHESTRATOR, False),
    "N2-ours-before-the-call-an-orchestrator-s-ticket-files": (TICKETS, TICKETS.trailers, False),
}


@pytest.mark.parametrize("case", sorted(OURS_THEN_AN_ORDINARY_MERGE), ids=sorted(OURS_THEN_AN_ORDINARY_MERGE))
def test_a_branch_that_took_main_with_ours_and_is_then_merged_ordinarily_is_flagged_for_what_it_dropped(
        project, sandbox, call, case):
    """Shape N. The ticket branch takes ``main`` with ``git merge -s ours``, so it drops what ``main`` got
    since the fork; an ordinary ``git merge --no-ff`` then merges the branch into ``main``, and ``main`` loses
    those changes. The final merge is an ordinary one and has no own change. The ``-s ours`` merge commit is
    new to ``HEAD`` in the move, in the call that makes it (N1) and in the call that only merges the branch
    (N2); the dropped paths are its own change, they are named, and the finding names that commit (DEC-270).
    The engineer's source file of the branch is not named."""
    dropped, trailers, take_in_the_call = OURS_THEN_AN_ORDINARY_MERGE[case]
    shape = symmetric.branch_that_took_main_with_ours(project, sandbox, dropped, trailers, take_in_the_call)
    before = check_support.git(project, "rev-parse", "HEAD").strip()
    taken_before = support.is_merge(project, support.TICKET_BRANCH)
    assert taken_before != take_in_the_call, (
        f"the fixture is wrong: before the call, 'the branch has taken main' is {taken_before}"
    )
    made = _make(project, call, shape)
    result, _, what, dropping = made
    first, second = support.parents_of(project)
    assert first == before and second == dropping and support.parents_of(project, dropping)[1] == before, (
        "the fixture is wrong: the final merge commit's parents are not main and the `-s ours` merge commit, or "
        "that commit's second parent is not main as the call found it"
    )
    assert symmetric.differing(project, dropping, f"{dropping}^1") == [] and symmetric.differing(
        project, "HEAD", dropping) == [], (
        "the fixture is wrong: the `-s ours` merge commit does not hold its first parent's tree, or the final "
        "merge commit does not hold the branch's"
    )
    symmetric.assert_own(project, "HEAD", (), "the final merge commit")
    _assert_the_dropped_paths_are_named(project, shape, made)
    for path in shape.named:
        findings = support.findings_naming(result, path, what)
        assert any(support.names_commit(finding["reason"], dropping) for finding in findings), (
            f"{what}: no finding that names {path} names the `-s ours` merge commit {dropping[:12]}: "
            f"{[finding['reason'] for finding in findings]}"
        )


# --------------------------------------------------------------------------
# The follow-on: a second merge commit on top restores one of two undone tests
# --------------------------------------------------------------------------

def test_a_test_that_stays_undone_is_named_when_a_second_merge_commit_restores_the_other(project, sandbox, call):
    """The review's F2. In one call a turned-round merge commit undoes a test designer's two tests, and a
    second merge commit on top of it holds the second test again. The first test stays undone: it is the first
    merge commit's own change, and it is named. The test says nothing of the test that was restored."""
    shape = symmetric.turned_round_then_one_restored(project, sandbox)
    before = check_support.git(project, "rev-parse", "HEAD").strip()
    made = _make(project, call, shape)
    stays_undone, restored = TESTS.first, TESTS.second
    assert support.parents_of(project) == [made[3], before], (
        f"the fixture is wrong: the second merge commit's parents are {support.parents_of(project)}"
    )
    assert sorted(check_support.git(project, "rev-list", f"{before}..HEAD").split()) == sorted(
        [made[1][0][0], made[3]]), "the fixture is wrong: the move holds other commits than the two merge commits"
    assert support.content_at(project, "HEAD", restored) == support.content_at(project, before, restored), (
        f"the fixture is wrong: {restored} is not restored"
    )
    assert support.content_at(project, "HEAD", stays_undone) == support.content_at(
        project, f"{before}~2", stays_undone), f"the fixture is wrong: {stays_undone} does not stay undone"
    _assert_the_dropped_paths_are_named(project, shape, made)

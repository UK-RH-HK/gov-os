"""W1-50 — a merge commit that undoes earlier commits through a parent that is not new in the move.

Added after implementation; reason: delegated decision, DEC-390 (package
DP-15).

DEC-390, DP-15: "when a merge commit has a parent that is not among the commits
new in the move, every path it changes against its first parent is judged by
the merge commit's own trailers, or against the caller without them. An
ordinary integration merge, whose other parent is new in the move, is read as
before (DEC-269)."

**The move.** Some commits are in ``HEAD``'s history before the call. The
orchestrator's own call then makes a merge commit with ``git commit-tree`` and
moves the branch forward to it (``git merge --ff-only <the new commit>``):

- first parent: ``HEAD`` as the call found it;
- second parent: the commit before those commits. It is in ``HEAD``'s history
  already, so the merge commit brings no commit: the move is forward and holds
  one new commit, the merge commit;
- tree: the second parent's tree. The merge commit undoes those commits, and
  every path it holds has content one of its parents holds.

What the merge commit changes against its first parent is exactly the paths of
the undone commits. They are judged as any commit's paths are: by the merge
commit's own ``Role`` and ``Task`` trailers, or against the caller (the
orchestrator) when it has none. Since DEC-410 (DP-27, DP-21) a path under
``tests/acceptance/**`` or ``.tickets/**`` among them is a finding whatever
those trailers: the two cases with a test designer's trailers were rewritten
for it.

The same merge commit with a hand edit that neither parent holds is
``test_w1_50_merge_with_an_earlier_parent.py``.

**The other side.** An ordinary ``--no-ff`` integration merge, whose second
parent is new in the move, stays silent when the commits it brings stay inside
their own paths. Two existing cases of
``test_an_integration_merge_of_commits_inside_their_own_paths_is_silent`` hold
it with a test designer's commit under ``tests/acceptance/**`` and an
engineer's commit inside its ticket's paths: ``no-ff-merge-of-a-branch-that-is-ahead``
(the merge base is ``HEAD``) and ``diverged-branches`` (the branch forked from
an earlier commit of ``HEAD``'s history: the merged side's commits are new in
the move, the merge base is old). The last test here adds the form those two
do not hold: since the fork, ``main`` itself got a test designer's commit, so
the merge commit differs under ``tests/acceptance/**`` from each of its
parents.

Every call is an orchestrator session's own call (DEC-266, DEC-319).
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

DESIGNER_WORK = ((support.ACCEPTANCE_FILE, AS_DESIGNER), (support.NEW_TEST, AS_DESIGNER))


def _undo_by_a_merge_commit(project, sandbox, call, steps, trailers):
    """Commit ``steps`` before the call; then one call of the orchestrator makes the merge commit that undoes
    them and moves the branch forward to it. Returns (result, state after, a description)."""
    support.run(project, sandbox, support.commits(*steps))
    earlier_revision = f"HEAD~{len(steps)}"
    before = check_support.git(project, "rev-parse", "HEAD").strip()
    earlier = check_support.git(project, "rev-parse", earlier_revision).strip()
    merge_commit = support.commit_tree(f"{earlier_revision}^{{tree}}", ["HEAD", earlier_revision], trailers)
    command = f"git merge -q --ff-only {merge_commit}"
    result, left = call(project, command, ORCHESTRATOR, TICKET)
    parents = check_support.git(project, "rev-list", "--parents", "-n", "1", "HEAD").split()[1:]
    assert parents == [before, earlier], (
        f"the fixture is wrong: the new commit's parents are {parents}, not {[before, earlier]}"
    )
    assert support.is_ancestor(project, earlier, before), (
        "the fixture is wrong: the second parent is not in the history HEAD had before the call"
    )
    assert check_support.git(project, "rev-list", f"{before}..HEAD").split() == [left[0][0]], (
        "the fixture is wrong: the move holds other new commits than the merge commit"
    )
    assert (check_support.git(project, "rev-parse", "HEAD^{tree}")
            == check_support.git(project, "rev-parse", f"{earlier}^{{tree}}")), (
        "the fixture is wrong: the merge commit's tree is not the second parent's tree"
    )
    undone = sorted(check_support.git(project, "diff", "--name-only", before, "HEAD").split())
    assert undone == sorted(path for path, _ in steps), (
        f"the fixture is wrong: against its first parent the merge commit changes {undone}"
    )
    what = (f"a merge commit with trailers {trailers} and the parents HEAD and {earlier_revision}, whose tree is "
            f"that of {earlier_revision} and so undoes the commits of {undone}, in the orchestrator's own call "
            f"on {TICKET}")
    return result, left, what


# --------------------------------------------------------------------------
# The case found: the merge commit undoes test designer's commits under tests/acceptance/**
# --------------------------------------------------------------------------

# name: the merge commit's trailers. None of them allows a path under tests/acceptance/**.
NOT_THE_TEST_DESIGNER_S = {
    "orchestrator-trailers": AS_ORCHESTRATOR,
    "engineer-trailers": AS_ENGINEER,
    # No trailers: the caller decides, and the orchestrator may not write an acceptance test.
    "no-trailers": NO_TRAILERS,
}


@pytest.mark.parametrize("case", sorted(NOT_THE_TEST_DESIGNER_S), ids=sorted(NOT_THE_TEST_DESIGNER_S))
def test_a_merge_commit_that_undoes_test_designer_commits_through_an_earlier_parent_is_flagged(project, sandbox,
                                                                                              call, case):
    """DEC-390, DP-15. One test designer's commit edited an existing acceptance test, one added a new one. The
    merge commit puts the first back and removes the second. Both paths are named."""
    trailers = NOT_THE_TEST_DESIGNER_S[case]
    result, left, what = _undo_by_a_merge_commit(project, sandbox, call, DESIGNER_WORK, trailers)
    assert check_support.read(project, support.NEW_TEST) is None, (
        f"the fixture is wrong: {support.NEW_TEST} is still there after the call"
    )
    check_support.assert_caught(result, support.ACCEPTANCE_FILE, support.NEW_TEST, what=what,
                                action=check_support.FLAGGED)
    check_support.assert_left_as_the_call_left_it(project, left, what)


def test_the_same_merge_commit_with_a_test_designer_s_trailers_is_flagged_all_the_same(project, sandbox, call):
    """Rewritten after implementation; reason: delegated decision, DEC-410 (DP-27). Until then this case was
    ``test_the_same_merge_commit_with_a_test_designer_s_trailers_is_judged_by_those_trailers`` and pinned
    silence: the trailers are a test designer's on a ticket in progress and every path the merge commit
    changes is under ``tests/acceptance/**``.

    DEC-410, DP-27: a merge commit's own change under ``tests/acceptance/**`` is a finding whatever its
    trailers, test-designer trailers included. The same history; both undone tests are named."""
    result, left, what = _undo_by_a_merge_commit(project, sandbox, call, DESIGNER_WORK, AS_DESIGNER)
    check_support.assert_caught(result, support.ACCEPTANCE_FILE, support.NEW_TEST, what=what,
                                action=check_support.FLAGGED)
    check_support.assert_left_as_the_call_left_it(project, left, what)


def test_a_test_designer_s_merge_commit_that_also_undoes_a_source_file_is_flagged_for_every_path_it_undoes(
        project, sandbox, call):
    """Rewritten after implementation; reason: delegated decision, DEC-410 (DP-27). Until then this case was
    ``test_a_test_designer_s_merge_commit_that_also_undoes_a_source_file_is_flagged_for_that_file`` and pinned
    that the two acceptance tests are not named.

    The test designer's trailers do not allow the engineer's source file (DEC-390, DP-15), and the undone
    acceptance tests are the merge commit's own change (DEC-410, DP-27): all three paths are named."""
    steps = (*DESIGNER_WORK, (support.SOURCE, AS_ENGINEER))
    result, left, what = _undo_by_a_merge_commit(project, sandbox, call, steps, AS_DESIGNER)
    check_support.assert_caught(result, support.SOURCE, support.ACCEPTANCE_FILE, support.NEW_TEST, what=what,
                                action=check_support.FLAGGED)
    check_support.assert_left_as_the_call_left_it(project, left, what)


# --------------------------------------------------------------------------
# The same merge commit undoing only paths outside tests/acceptance/**
# --------------------------------------------------------------------------

ORCHESTRATOR_WORK = ((support.README, AS_ORCHESTRATOR), (support.NOTES, AS_ORCHESTRATOR))
ENGINEER_WORK = ((support.SOURCE, AS_ENGINEER), (support.SECOND_SOURCE, AS_ENGINEER))

# name: (the undone commits, the merge commit's trailers). The trailers, or the caller, may write every undone path.
UNDONE_INSIDE = {
    "orchestrator-trailers-undoing-orchestrator-commits": (ORCHESTRATOR_WORK, AS_ORCHESTRATOR),
    "no-trailers-undoing-orchestrator-commits": (ORCHESTRATOR_WORK, NO_TRAILERS),
    "engineer-trailers-undoing-commits-inside-the-ticket-s-paths": (ENGINEER_WORK, AS_ENGINEER),
}


@pytest.mark.parametrize("case", sorted(UNDONE_INSIDE), ids=sorted(UNDONE_INSIDE))
def test_a_merge_commit_that_undoes_only_paths_its_trailers_or_the_caller_may_write_is_silent(project, sandbox,
                                                                                             call, case):
    """DEC-390, DP-15: the paths are judged, not the form of the commit. Nothing under ``tests/acceptance/**``
    changes."""
    steps, trailers = UNDONE_INSIDE[case]
    result, left, what = _undo_by_a_merge_commit(project, sandbox, call, steps, trailers)
    check_support.assert_silent(result, what)
    check_support.assert_left_as_the_call_left_it(project, left, what)


def test_a_merge_commit_that_undoes_a_path_outside_its_own_trailers_paths_is_flagged(project, sandbox, call):
    """ "By the merge commit's own trailers", not against the caller: the orchestrator may write README.md and
    docs/notes.md itself; the engineer's trailers on DAEO-zz90 do not allow them."""
    result, left, what = _undo_by_a_merge_commit(project, sandbox, call, ORCHESTRATOR_WORK, AS_ENGINEER)
    check_support.assert_caught(result, support.README, support.NOTES, what=what, action=check_support.FLAGGED)
    check_support.assert_left_as_the_call_left_it(project, left, what)


# --------------------------------------------------------------------------
# The other side: an ordinary integration merge, whose second parent is new in the move
# --------------------------------------------------------------------------

# name: the merge commit's trailers
INTEGRATION_MERGES = {
    "orchestrator-trailers": AS_ORCHESTRATOR,
    "no-trailers": NO_TRAILERS,
}


@pytest.mark.parametrize("case", sorted(INTEGRATION_MERGES), ids=sorted(INTEGRATION_MERGES))
def test_an_integration_merge_stays_silent_when_main_got_a_test_designer_s_commit_since_the_fork(project, sandbox,
                                                                                                call, case):
    """The ticket branch forked from an earlier commit of ``HEAD``'s history and brings a test designer's commit
    and an engineer's. Since the fork ``main`` got a test designer's commit of another acceptance test.

    The merge commit differs under ``tests/acceptance/**`` from its first parent (by the merged side's test) and
    from its second parent (by ``main``'s test). Neither is the merge commit's own change: its second parent is
    new in the move, so it is read as before (DEC-269, KPI success 2).
    """
    trailers = INTEGRATION_MERGES[case]
    support.ticket_branch(project, sandbox, (support.NEW_TEST, AS_DESIGNER), (support.SOURCE, AS_ENGINEER))
    support.run(project, sandbox, support.commit(support.ACCEPTANCE_FILE, AS_DESIGNER, subject="main's own test"))
    before = check_support.git(project, "rev-parse", "HEAD").strip()
    fork = check_support.git(project, "merge-base", "HEAD", support.TICKET_BRANCH).strip()
    command = support.merge(trailers=trailers)
    result, left = call(project, command, ORCHESTRATOR, TICKET)
    assert support.is_merge(project), f"the fixture command `{command}` made no merge commit"
    second_parent = check_support.git(project, "rev-parse", "HEAD^2").strip()
    assert not support.is_ancestor(project, second_parent, before), (
        "the fixture is wrong: the merge commit's second parent was in HEAD's history before the call"
    )
    assert fork != before and support.is_ancestor(project, fork, before), (
        "the fixture is wrong: the branch did not fork from an earlier commit of HEAD's history"
    )
    for parent in ("HEAD^1", "HEAD^2"):
        differing = check_support.git(project, "diff", "--name-only", parent, "HEAD", "--", support.ACCEPTANCE)
        assert differing.strip(), f"the fixture is wrong: the merge commit holds {parent}'s acceptance tests"
    what = (f"`{command}` by the orchestrator on {TICKET}, of a branch that forked before main's own test "
            f"designer commit")
    check_support.assert_silent(result, what)
    check_support.assert_left_as_the_call_left_it(project, left, what)

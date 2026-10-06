"""W1-50 — a merge commit's own change of a ticket file is a finding whatever its trailers.

Added after implementation; reason: delegated decision, DEC-410 (package DP-21,
option (b)).

DEC-410, DP-21: "a change to a file under `.tickets/**` that a merge commit
itself makes (its own change, by the helper) is a finding whatever the merge
commit's trailers, also with orchestrator trailers or none."

Until DEC-410 such a change was judged by the merge commit's trailers, or
against the caller without them (DEC-269), and the orchestrator may write a
ticket file (DEC-156, DEC-359): a merge commit with the orchestrator's
trailers, or none, that edited a ticket file by hand, resolved a conflict in
one, or dropped one parent's change of one (and so set a ticket's status
back, or widened its paths again) was silent.

Every call here is an orchestrator session's own call (DEC-266, DEC-319), and
every merge commit carries ``Role: orchestrator`` with a ``Task`` trailer, or no
trailers. "Own" is the merge commit's own change as DEC-403 reads it: content
of the path that differs from a parent's and that no other parent brought.

**The other side.** A ticket-file change that an orchestrator's commit made on
one side only, and that an ordinary ``git merge --no-ff`` brings, is no change
of the merge commit's own: the merge is silent. The orchestrator's ordinary
(non-merge) commit of a ticket file in its own call stays silent too:
``test_an_orchestrator_s_commit_of_a_ticket_file_made_in_its_own_call_is_silent``
and
``test_a_commit_without_trailers_of_a_ticket_file_made_in_the_orchestrator_s_own_call_is_silent``,
unchanged.

**Now pinned:** a ticket file that both sides changed is the merge commit's own
change, whichever side's content it holds. DEC-421 extends the both-sides
rule of DP-24 to ``.tickets/**``. Tests:
``test_w1_50_ticket_file_changed_on_both_sides.py``.

The same dropped changes with an engineer's trailers on the merge commit are
findings since DEC-403 (DP-16):
``test_w1_50_merge_that_drops_a_parent_s_change.py``, unchanged.
"""

from __future__ import annotations

import pytest

import w1_50_own_change_support as own_change
import w1_50_support as support
import w1_50_symmetric_support as symmetric

check_support = support.check_support

ORCHESTRATOR = support.ORCHESTRATOR
TICKET = support.TICKET
AS_ORCHESTRATOR = support.AS_ORCHESTRATOR
NO_TRAILERS = support.NO_TRAILERS
ORCHESTRATOR_ON_MAIN = support.ORCHESTRATOR_ON_MAIN

TICKETS = symmetric.TICKETS
TICKET_FILE = own_change.TICKET_FILE

# name: the merge commit's trailers. Both let the orchestrator write a ticket file in an ordinary commit.
ORCHESTRATOR_S = {
    "orchestrator-trailers": AS_ORCHESTRATOR,
    # No trailers: the caller decides, and the caller is the orchestrator.
    "no-trailers": NO_TRAILERS,
}


# --------------------------------------------------------------------------
# A hand edit, and a conflict resolution
# --------------------------------------------------------------------------

@pytest.mark.parametrize("case", sorted(ORCHESTRATOR_S), ids=sorted(ORCHESTRATOR_S))
def test_a_hand_edit_of_a_ticket_file_in_an_orchestrator_s_merge_commit_is_flagged(project, sandbox, call, case):
    """DEC-410, DP-21. An ordinary integration merge whose merge commit also appends a line to a ticket file
    that neither side changed. The ticket file is named; the paths the branch brought are not."""
    shape = own_change.hand_edit(project, sandbox, TICKET_FILE, ORCHESTRATOR_S[case])
    result, left = call(project, shape.command, ORCHESTRATOR, TICKET)
    own_change.assert_content_no_parent_holds(project, TICKET_FILE)
    what = f"{shape.what}, in the orchestrator's own call on {TICKET}"
    check_support.assert_caught(result, TICKET_FILE, what=what, action=check_support.FLAGGED)
    check_support.assert_not_recorded(result, *shape.brought, what=what)
    check_support.assert_left_as_the_call_left_it(project, left, what)


@pytest.mark.parametrize("case", sorted(ORCHESTRATOR_S), ids=sorted(ORCHESTRATOR_S))
def test_a_conflict_resolution_of_a_ticket_file_in_an_orchestrator_s_merge_commit_is_flagged(project, sandbox,
                                                                                           call, case):
    """DEC-410, DP-21. An orchestrator's commit on each side appended a line to the same ticket file; the
    merge conflicts and is resolved to content neither parent holds. Each side's commit passes by its own
    trailers; the resolution is the merge commit's own change, and the ticket file is named."""
    shape = own_change.conflict_resolved_to_new_content(project, sandbox, TICKET_FILE, ORCHESTRATOR_ON_MAIN,
                                                        ORCHESTRATOR_S[case])
    result, left = call(project, shape.command, ORCHESTRATOR, TICKET)
    own_change.assert_content_no_parent_holds(project, TICKET_FILE)
    what = f"{shape.what}, in the orchestrator's own call on {TICKET}"
    check_support.assert_caught(result, TICKET_FILE, what=what, action=check_support.FLAGGED)
    check_support.assert_left_as_the_call_left_it(project, left, what)


# --------------------------------------------------------------------------
# A merge commit that drops one parent's change of a ticket file
# --------------------------------------------------------------------------

def _make(project, call, shape):
    before = check_support.git(project, "rev-parse", "HEAD").strip()
    result, left = call(project, shape.command, ORCHESTRATOR, TICKET)
    symmetric.assert_dropping(project, shape, before)
    return result, left, f"{shape.what}, in the orchestrator's own call on {TICKET}"


def _assert_the_dropped_ticket_files_are_named(project, shape, made):
    result, left, what = made
    check_support.assert_caught(result, *shape.named, what=what, action=check_support.FLAGGED)
    if shape.kept:
        check_support.assert_not_recorded(result, *shape.kept, what=what)
    check_support.assert_left_as_the_call_left_it(project, left, what)


def _assert_the_ticket_is_open_again(project, before):
    """Guard: the dropped close is undone. ``before`` held the closed status; ``HEAD`` holds it no longer."""
    ticket = symmetric.CLOSED_TICKET
    assert support.status_at(project, ticket, before) == ["status: closed"] and support.status_at(
        project, ticket) == ["status: in_progress"], (
        f"the fixture is wrong: {ticket} was {support.status_at(project, ticket, before)} before the call and is "
        f"{support.status_at(project, ticket)} after it"
    )


@pytest.mark.parametrize("case", sorted(ORCHESTRATOR_S), ids=sorted(ORCHESTRATOR_S))
def test_an_orchestrator_s_merge_commit_with_its_parents_turned_round_that_drops_ticket_file_changes_is_flagged(
        project, sandbox, call, case):
    """DEC-410, DP-21; shape B of DEC-403. An orchestrator's commits narrowed one ticket's allowed paths and
    closed another ticket. The merge commit's parents are ``HEAD~2`` and ``HEAD`` in that order and its tree is
    ``HEAD~2``'s: the paths are wide again and the ticket is in progress again. Both ticket files are the merge
    commit's own change, and both are named."""
    shape = symmetric.parents_turned_round(project, sandbox, TICKETS, ORCHESTRATOR_S[case])
    before = check_support.git(project, "rev-parse", "HEAD").strip()
    made = _make(project, call, shape)
    assert symmetric.differing(project, "HEAD", "HEAD^1") == [], (
        "the fixture is wrong: the merge commit does not hold its first parent's tree"
    )
    _assert_the_ticket_is_open_again(project, before)
    _assert_the_dropped_ticket_files_are_named(project, shape, made)


@pytest.mark.parametrize("case", sorted(ORCHESTRATOR_S), ids=sorted(ORCHESTRATOR_S))
def test_an_orchestrator_s_ours_merge_that_sets_a_ticket_s_status_back_is_flagged(project, sandbox, call, case):
    """DEC-410, DP-21; shape D of DEC-403, with porcelain only: ``git checkout -b tmp HEAD~2``, an
    orchestrator's commit of ``README.md``, ``git merge -s ours main``, and ``main`` fast-forwarded to the
    result. The merge commit drops the narrowing and the close ``main`` got since ``HEAD~2``. Both ticket files
    are named; ``README.md`` is not."""
    shape = symmetric.plain_porcelain(project, sandbox, TICKETS, ORCHESTRATOR_S[case])
    before = check_support.git(project, "rev-parse", "HEAD").strip()
    made = _make(project, call, shape)
    first, second = support.parents_of(project)
    assert second == before and symmetric.differing(project, "HEAD", first) == [], (
        "the fixture is wrong: the merge commit's second parent is not main as the call found it, or the merge "
        "commit does not hold its first parent's tree"
    )
    _assert_the_ticket_is_open_again(project, before)
    _assert_the_dropped_ticket_files_are_named(project, shape, made)


def test_an_orchestrator_s_merge_commit_that_drops_one_of_two_ticket_file_changes_is_flagged_for_that_one(
        project, sandbox, call):
    """DEC-410, DP-21; shape E of DEC-403. The parents are ``HEAD~2`` and ``HEAD`` in that order; the tree is
    ``HEAD``'s with the narrowed ticket file set back to ``HEAD~2``'s content. That file is the merge commit's
    own change and is named. The closed ticket's file is ``HEAD``'s content, which an orchestrator's commit
    changed against the merge base: the second parent brought it, and it is not named."""
    shape = symmetric.turned_round_setting_one_back(project, sandbox, TICKETS, AS_ORCHESTRATOR)
    made = _make(project, call, shape)
    assert symmetric.differing(project, "HEAD", "HEAD^1") == [TICKETS.second] and symmetric.differing(
        project, "HEAD", "HEAD^2") == [TICKETS.first], (
        "the fixture is wrong: the merge commit does not differ from its parents as the test describes"
    )
    _assert_the_dropped_ticket_files_are_named(project, shape, made)


# --------------------------------------------------------------------------
# The other side: an ordinary merge that brings an orchestrator's ticket-file change
# --------------------------------------------------------------------------

# name: (the orchestrator's ticket-file commits are on the ticket branch, the merge commit's trailers)
BROUGHT = {
    "the-ticket-file-commits-on-the-branch-orchestrator-trailers": (True, AS_ORCHESTRATOR),
    "the-ticket-file-commits-on-the-branch-no-trailers": (True, NO_TRAILERS),
    "the-ticket-file-commits-on-main-orchestrator-trailers": (False, AS_ORCHESTRATOR),
}


@pytest.mark.parametrize("case", sorted(BROUGHT), ids=sorted(BROUGHT))
def test_an_ordinary_merge_that_brings_an_orchestrator_s_ticket_file_changes_from_one_side_is_silent(
        project, sandbox, call, case):
    """An orchestrator's two commits changed two ticket files on one side only; the other side did not touch
    them since the fork. The merge commit holds that side's content of both, which differs from the merge
    base: the files are brought, the merge commit has no own change, and every commit passes by its own
    trailers. Must stay silent: a fix that flags every merge commit that differs from a parent in a ticket
    file fails these."""
    on_the_branch, trailers = BROUGHT[case]
    shape = own_change.ticket_files_on_one_side(project, sandbox, on_the_branch, trailers)
    before = check_support.git(project, "rev-parse", "HEAD").strip()
    result, left = call(project, shape.command, ORCHESTRATOR, TICKET)
    symmetric.assert_taking(project, shape)
    changed_by = "HEAD^2" if on_the_branch else "HEAD^1"
    untouched_by = "HEAD^1" if on_the_branch else "HEAD^2"
    assert support.parents_of(project)[0] == before, "the fixture is wrong: the first parent is not main"
    base = support.merge_bases(project, "HEAD^1", "HEAD^2")[0]
    for path in TICKETS.paths:
        held = support.content_at(project, "HEAD", path)
        assert held == support.content_at(project, changed_by, path) and support.content_at(
            project, untouched_by, path) == support.content_at(project, base, path) != held, (
            f"the fixture is wrong: {path} is not changed on one side only and held as that side has it"
        )
    what = f"{shape.what}, in the orchestrator's own call on {TICKET}"
    check_support.assert_silent(result, what)
    check_support.assert_left_as_the_call_left_it(project, left, what)

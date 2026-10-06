"""W1-50 — a ticket file that both sides of a merge changed is the merge commit's own change.

Added after implementation; reason: owner decision, DEC-421.

DEC-421 extends the both-sides rule of DEC-410 DP-24 to ``.tickets/**``:
"under `.tickets/**` too, a path that more than one parent changed against
the merge base is the merge commit's own, whichever side's content it
holds. Stricter-only."

**The shapes.** Since their one merge base, the ticket branch and ``main``
each changed the same ticket file, each by an orchestrator's commit that
passes by its own trailers. Whatever the merge commit holds for that path,
the path is in ``read_merge(...).own`` and not in ``brought``, and the
orchestrator's merge in its own call is a finding that names it:

- the merge commit holds the first parent's content of it whole;
- it holds the second parent's content whole;
- both sides made the identical change: the ticket file is in ``own`` (as
  for acceptance tests, DP-24).

**The other side.** A merge in which each side changed a *different* ticket
file: ``own`` is empty and the merge is silent.
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

FIRST = own_change.FIRST
SECOND = own_change.SECOND
TICKET_FILE = own_change.TICKET_FILE           # .tickets/DAEO-zz94.md
SECOND_TICKET_FILE = symmetric.CLOSED_FILE     # .tickets/DAEO-zz96.md


@pytest.fixture()
def helper(monkeypatch):
    """``helper()`` -> the module ``gov.guard.containment_merge``, imported when it is first called."""
    return own_change.helper_module(monkeypatch)


ONE_SIDE_WHOLE = {
    "holds-the-first-parent-s-content": FIRST,
    "holds-the-second-parent-s-content": SECOND,
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


# --------------------------------------------------------------------------
# Through the check (the hook): both sides changed the same ticket file
# --------------------------------------------------------------------------

@pytest.mark.parametrize("case", sorted(ONE_SIDE_WHOLE), ids=sorted(ONE_SIDE_WHOLE))
def test_a_merge_that_takes_one_side_s_content_of_a_ticket_file_both_sides_changed_is_flagged(project, sandbox, call,
                                                                                              case):
    """DEC-421. A ticket file that more than one parent changed against the merge base is the merge commit's
    own change, whichever side's content it holds. The ticket file is named."""
    holds = ONE_SIDE_WHOLE[case]
    shape = own_change.changed_on_both_sides(project, sandbox, TICKET_FILE, AS_ORCHESTRATOR, holds)
    result, left, what = _call(project, call, shape)
    check_support.assert_caught(result, shape.path, what=what, action=check_support.FLAGGED)
    check_support.assert_not_recorded(result, shape.also, what=what)
    check_support.assert_left_as_the_call_left_it(project, left, what)


# --------------------------------------------------------------------------
# Through the helper (read_merge): the ticket file is in own, not brought
# --------------------------------------------------------------------------

@pytest.mark.parametrize("case", sorted(ONE_SIDE_WHOLE), ids=sorted(ONE_SIDE_WHOLE))
def test_read_merge_puts_a_ticket_file_both_sides_changed_in_own(project, sandbox, helper, case):
    """DEC-421, through the helper: the ticket file is in ``own`` and not in ``brought``; the source file only
    the branch changed is not in ``own``."""
    holds = ONE_SIDE_WHOLE[case]
    shape = own_change.changed_on_both_sides(project, sandbox, TICKET_FILE, AS_ORCHESTRATOR, holds)
    state = _build(project, sandbox, shape)
    reading = own_change.read(project, helper, "HEAD", shape.what)
    assert shape.path in reading.own, (
        f"read_merge on {shape.what}: `own` is {reading.own!r}; it does not hold {shape.path}, which more than "
        f"one parent changed against the merge base (DEC-421)"
    )
    assert shape.path not in reading.brought, (
        f"read_merge on {shape.what}: `brought` holds {shape.path}: {reading.brought!r} (DEC-421)"
    )
    assert shape.also not in reading.own, (
        f"read_merge on {shape.what}: `own` holds {shape.also}, which only the branch changed: {reading.own!r}"
    )
    own_change.assert_left(project, state, shape.what)


# --------------------------------------------------------------------------
# Both sides made the identical change to a ticket file
# --------------------------------------------------------------------------

def test_read_merge_puts_a_ticket_file_both_sides_changed_in_the_same_way_in_own(project, sandbox, helper):
    """DEC-421, read by the words of DP-24: "a path that more than one parent changed against the merge base".
    An orchestrator's commit made the same change of a ticket file on the branch and on ``main``; the merge
    commit holds that content, which is each parent's. The ticket file is in ``own``."""
    also = support.SECOND_SOURCE
    support.ticket_branch(project, sandbox, (TICKET_FILE, AS_ORCHESTRATOR), (also, support.AS_ENGINEER),
                          main_moves_on=False)
    support.run(project, sandbox, support.commit(TICKET_FILE, AS_ORCHESTRATOR, subject="the same change on main"))
    fork = support.merge_bases(project, "HEAD", support.TICKET_BRANCH)
    held = support.content_at(project, "HEAD", TICKET_FILE)
    assert len(fork) == 1 and held == support.content_at(project, support.TICKET_BRANCH, TICKET_FILE) and (
        held != support.content_at(project, fork[0], TICKET_FILE)), (
        f"the fixture is wrong: the two sides did not make the same change of {TICKET_FILE}"
    )
    command = support.merge(trailers=AS_ORCHESTRATOR)
    what = (f"an ordinary --no-ff merge of {support.TICKET_BRANCH} into main after an orchestrator made the "
            f"same change of {TICKET_FILE} on both; the branch also brings an engineer's {also}")
    state = own_change.built(project, sandbox, command)
    assert symmetric.differing_from_any_parent(project) == [also], (
        f"the fixture is wrong: the merge commit differs from its parents in "
        f"{symmetric.differing_from_any_parent(project)}"
    )
    base = support.merge_bases(project, "HEAD^1", "HEAD^2")
    assert len(base) == 1 and held == support.content_at(project, "HEAD^1", TICKET_FILE) == support.content_at(
        project, "HEAD^2", TICKET_FILE) != support.content_at(project, base[0], TICKET_FILE), (
        f"the fixture is wrong: the two parents did not make the same change of {TICKET_FILE} against one merge base"
    )
    reading = own_change.read(project, helper, "HEAD", what)
    assert reading.own == [TICKET_FILE], (
        f"read_merge on {what}: `own` is {reading.own!r}, not {[TICKET_FILE]!r}: both parents changed the ticket "
        f"file against the merge base (DEC-421)"
    )
    assert reading.brought == [also], (
        f"read_merge on {what}: `brought` is {reading.brought!r}, not {[also]!r}"
    )
    own_change.assert_left(project, state, what)


# --------------------------------------------------------------------------
# The other side: each side changed a different ticket file
# --------------------------------------------------------------------------

def test_a_merge_where_each_side_changed_a_different_ticket_file_is_silent(project, sandbox, call):
    """DEC-421 speaks of one path that more than one parent changed. An orchestrator's commit changed one
    ticket file on the branch and another orchestrator's commit changed a different ticket file on ``main``
    since the fork; the merge commit holds both. ``own`` is empty and the merge is silent."""
    support.ticket_branch_of(project, sandbox,
                             support.commit(TICKET_FILE, AS_ORCHESTRATOR,
                                            subject="the branch's ticket-file change"),
                             main_moves_on=False)
    support.run(project, sandbox, support.commit(SECOND_TICKET_FILE, support.ORCHESTRATOR_ON_MAIN,
                                                 subject="main's ticket-file change"))
    command = support.merge(trailers=AS_ORCHESTRATOR)
    shape = symmetric.TakingMerge(command, (TICKET_FILE, SECOND_TICKET_FILE),
                                  what=f"an ordinary --no-ff merge of {support.TICKET_BRANCH} (an orchestrator's "
                                       f"change of {TICKET_FILE}) into main, which got an orchestrator's change of "
                                       f"{SECOND_TICKET_FILE} since the fork")
    result, left = call(project, shape.command, ORCHESTRATOR, TICKET)
    symmetric.assert_taking(project, shape)
    what = f"{shape.what}, in the orchestrator's own call on {TICKET}"
    check_support.assert_silent(result, what)
    check_support.assert_left_as_the_call_left_it(project, left, what)

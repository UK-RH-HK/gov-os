"""W1-50 — a commit with a worker's ``Role`` trailer that changes a ticket file is a finding.

Added after implementation; reason: delegated decision, DEC-390 (package
DP-16), on a finding of the review after the suite went green (DEC-136,
DEC-137).

DEC-390, DP-16: "a change under `.tickets/**` in a commit that carries a
worker's `Role:` trailer is a finding."

A ticket's ``allowed_paths`` say what its worker may write (CAP-58.a). A commit
is judged by the ticket its ``Task`` trailer names (KPI success 1), and the
ticket's state and paths are read from ``HEAD`` and from the working tree
(DEC-390, DP-14). A commit that rewrites the ticket it is judged by, or adds
the ticket it names, makes both agree with whatever it wants: after the move
``HEAD`` and the working tree hold the widened file.

**The commits found by review.** Each carries an engineer's trailers:

- one commit adds ``**`` to its own ticket's ``allowed_paths`` and changes
  ``README.md``, outside the ticket's former paths;
- a first commit widens the ticket, a second changes ``README.md``;
- one commit creates a ticket file ``DAEO-zz99`` with ``status: in_progress``
  and ``**``, names that ticket, and changes ``README.md``.

Each is made in an orchestrator session's own call, or arrives there by an
integration merge. Each test asserts the finding that names the ticket file,
and nothing about ``README.md``: whether that path is a finding of its own is
not what DP-16 decides.

"A worker's ``Role:``" is every role that is not the orchestrator. The engineer
is tested in full, the product-spec role and the test designer with one case
each.

**The other side.** A commit with ``Role: orchestrator`` that changes a ticket
file stays silent: the orchestrator may write every path outside
``tests/acceptance/**`` (DEC-156, DEC-359). Existing cases hold it for commits
that arrive in the call: the close commits and status commits in the moves of
``test_a_closed_ticket_s_commits_before_its_close_commit_pass_inside_that_ticket_s_paths``,
``test_work_between_two_closes_is_judged_by_the_ticket_because_the_latest_close_commit_counts``
and ``test_a_close_inside_a_larger_commit_is_the_close_commit``. The last two
tests here hold it for a commit made in the call itself, and for the worker's
commit that follows an orchestrator's committed widening.

``Role: owner`` and commits without trailers are judged as already decided
(KPI success 5, KPI success 4); nothing is added for them.
"""

from __future__ import annotations

import pytest

import w1_50_support as support

check_support = support.check_support

ORCHESTRATOR = support.ORCHESTRATOR
ENGINEER = support.ENGINEER
DESIGNER = support.DESIGNER
PRODUCT_SPEC = check_support.PRODUCT_SPEC
TICKET = support.TICKET
SPEC_TICKET = support.SPEC_TICKET
NEW_TICKET = support.NEW_TICKET
AS_ENGINEER = support.AS_ENGINEER
AS_DESIGNER = support.AS_DESIGNER
AS_ORCHESTRATOR = support.AS_ORCHESTRATOR

README = support.README
TICKET_FILE = support.ticket_file(TICKET)
NEW_TICKET_FILE = support.ticket_file(NEW_TICKET)


def _widening_commit_with_work(trailers=AS_ENGINEER, ticket=TICKET, path=README):
    """Shell: one commit that adds ``**`` to the ticket's ``allowed_paths`` and changes ``path``."""
    return (support.widen_paths(ticket) + " && " + support.change(path) + " && "
            + support.commit_paths([support.ticket_file(ticket), path], trailers, subject="widen and work"))


def _widening_commit_then_work(trailers=AS_ENGINEER):
    """Shell: a commit that only widens the ticket, then a commit of README.md."""
    return (support.widen_paths(TICKET) + " && "
            + support.commit_paths([TICKET_FILE], trailers, subject="widen") + " && "
            + support.commit(README, trailers, subject="work under the widened paths"))


def _new_ticket_commit_with_work():
    """Shell: one commit that creates DAEO-zz99 (engineer, in progress, ``**``), names it, and changes README.md."""
    return (support.new_ticket_file() + " && " + support.change(README) + " && "
            + support.commit_paths([NEW_TICKET_FILE, README], (ENGINEER, NEW_TICKET), subject="a ticket and work"))


# name: (the shell command that makes the commits, the ticket file they change)
ENGINEER_COMMITS = {
    "one-commit-widens-its-ticket-and-works-under-it": (_widening_commit_with_work, TICKET_FILE),
    "a-first-commit-widens-a-second-works-under-it": (_widening_commit_then_work, TICKET_FILE),
    "one-commit-creates-a-ticket-in-progress-and-works-under-it": (_new_ticket_commit_with_work, NEW_TICKET_FILE),
}


def _assert_the_ticket_file_allows_everything(project, ticket_file):
    """Guard against an empty test: after the move ``HEAD`` and the working tree hold the same, widened file."""
    committed = check_support.git(project, "show", f"HEAD:{ticket_file}")
    assert check_support.read(project, ticket_file) == committed, (
        f"the fixture is wrong: {ticket_file} differs between HEAD and the working tree"
    )
    assert f"\n- {support.EVERYTHING}\n" in committed and "\nstatus: in_progress\n" in committed, (
        f"the fixture is wrong: {ticket_file} at HEAD is not in progress with the entry {support.EVERYTHING}"
    )


def _assert_changed_by_a_commit_with_role(project, ticket_file, role):
    """Guard against an empty test: the latest commit that changes the ticket file carries ``Role: <role>``."""
    commit_id = support.commit_of(project, ticket_file)
    assert support.trailer_values(project, commit_id, "Role") == [role], (
        f"the fixture is wrong: the commit that changes {ticket_file} carries the Role trailer "
        f"{support.trailer_values(project, commit_id, 'Role')}"
    )
    assert ticket_file in support.changed_paths(project, commit_id), (
        f"the fixture is wrong: commit {commit_id[:12]} does not change {ticket_file}"
    )


# --------------------------------------------------------------------------
# An engineer's commit, made in an orchestrator session's own call
# --------------------------------------------------------------------------

@pytest.mark.parametrize("case", sorted(ENGINEER_COMMITS), ids=sorted(ENGINEER_COMMITS))
def test_an_engineer_s_commit_of_a_ticket_file_made_in_the_orchestrator_s_call_is_flagged(project, call, case):
    """DEC-390, DP-16. The finding names the ticket file."""
    make, ticket_file = ENGINEER_COMMITS[case]
    command = make()
    result, left = call(project, command, ORCHESTRATOR, TICKET)
    _assert_the_ticket_file_allows_everything(project, ticket_file)
    _assert_changed_by_a_commit_with_role(project, ticket_file, ENGINEER)
    what = f"`{command[:200]}…` in the orchestrator's own call on {TICKET}"
    check_support.assert_caught(result, ticket_file, what=what, action=check_support.FLAGGED)
    check_support.assert_left_as_the_call_left_it(project, left, what)


# --------------------------------------------------------------------------
# The same commits, arriving by the orchestrator's integration merge
# --------------------------------------------------------------------------

@pytest.mark.parametrize("case", sorted(ENGINEER_COMMITS), ids=sorted(ENGINEER_COMMITS))
def test_an_engineer_s_commit_of_a_ticket_file_brought_by_an_integration_merge_is_flagged(project, sandbox, call,
                                                                                         case):
    """DEC-390, DP-16. The commits are on the ticket branch; the orchestrator merges it with ``--no-ff``. After
    the merge ``HEAD`` and the working tree hold the widened file."""
    make, ticket_file = ENGINEER_COMMITS[case]
    support.ticket_branch_of(project, sandbox, make())
    command = support.merge()
    result, left = call(project, command, ORCHESTRATOR, TICKET)
    assert support.is_merge(project), f"the fixture command `{command}` made no merge commit"
    _assert_the_ticket_file_allows_everything(project, ticket_file)
    _assert_changed_by_a_commit_with_role(project, ticket_file, ENGINEER)
    what = f"`{command}` by the orchestrator on {TICKET}, bringing the engineer's commits of the case {case}"
    check_support.assert_caught(result, ticket_file, what=what, action=check_support.FLAGGED)
    check_support.assert_left_as_the_call_left_it(project, left, what)


# --------------------------------------------------------------------------
# The rule is about the commit's Role trailer, whatever the ticket's paths say
# --------------------------------------------------------------------------

def test_an_engineer_s_commit_of_a_ticket_file_is_flagged_although_the_ticket_s_paths_allow_it(project, sandbox,
                                                                                              call):
    """Before the call, a commit of the orchestrator gave the ticket ``**``: the widening is the orchestrator's
    and is in ``HEAD``'s history. The engineer's commit then changes the ticket's file (a line in its body) and
    README.md. README.md is inside the ticket's paths; the ticket file is a finding all the same."""
    support.run(project, sandbox,
                support.widen_paths(TICKET) + " && "
                + support.commit_paths([TICKET_FILE], AS_ORCHESTRATOR, subject="the orchestrator widens the ticket"))
    command = (f"echo 'A note by the worker.' >> {TICKET_FILE} && " + support.change(README) + " && "
               + support.commit_paths([TICKET_FILE, README], AS_ENGINEER))
    result, left = call(project, command, ORCHESTRATOR, TICKET)
    _assert_the_ticket_file_allows_everything(project, TICKET_FILE)
    assert support.EVERYTHING in support.allowed_paths_at(project, TICKET, "HEAD~1"), (
        "the fixture is wrong: the ticket did not allow every path before the engineer's commit"
    )
    assert support.trailer_values(project, "HEAD~1", "Role") == [ORCHESTRATOR], (
        "the fixture is wrong: the commit that widened the ticket is not the orchestrator's"
    )
    _assert_changed_by_a_commit_with_role(project, TICKET_FILE, ENGINEER)
    what = (f"an engineer's commit of {TICKET_FILE} and {README}, in the orchestrator's own call on {TICKET}; "
            f"the ticket's committed allowed_paths hold {support.EVERYTHING}")
    check_support.assert_caught(result, TICKET_FILE, what=what, action=check_support.FLAGGED)
    check_support.assert_left_as_the_call_left_it(project, left, what)


def test_an_engineer_s_commit_that_widens_its_own_ticket_in_its_own_call_is_flagged(project, call):
    """DP-16 names the commit's trailer, not the caller. An engineer session's call makes the commit, with the
    engineer's own trailers: it adds ``**`` to the ticket the session works on and changes README.md."""
    command = _widening_commit_with_work()
    result, left = call(project, command, ENGINEER, TICKET)
    _assert_the_ticket_file_allows_everything(project, TICKET_FILE)
    _assert_changed_by_a_commit_with_role(project, TICKET_FILE, ENGINEER)
    what = (f"a commit with trailers {AS_ENGINEER} that widens {TICKET_FILE} and changes {README}, in a call of "
            f"the engineer on {TICKET}")
    check_support.assert_caught(result, TICKET_FILE, what=what, action=check_support.FLAGGED)
    check_support.assert_left_as_the_call_left_it(project, left, what)


# --------------------------------------------------------------------------
# Other worker roles, one case each
# --------------------------------------------------------------------------

def test_a_product_spec_commit_that_widens_its_own_ticket_is_flagged(project, call):
    """``Role: product-spec`` on the product-spec ticket DAEO-zz92: the commit adds ``**`` to that ticket and
    changes README.md."""
    ticket_file = support.ticket_file(SPEC_TICKET)
    command = _widening_commit_with_work(trailers=(PRODUCT_SPEC, SPEC_TICKET), ticket=SPEC_TICKET)
    result, left = call(project, command, ORCHESTRATOR, TICKET)
    _assert_the_ticket_file_allows_everything(project, ticket_file)
    _assert_changed_by_a_commit_with_role(project, ticket_file, PRODUCT_SPEC)
    what = (f"a commit with trailers {(PRODUCT_SPEC, SPEC_TICKET)} that widens {ticket_file} and changes {README}, "
            f"in the orchestrator's own call on {TICKET}")
    check_support.assert_caught(result, ticket_file, what=what, action=check_support.FLAGGED)
    check_support.assert_left_as_the_call_left_it(project, left, what)


def test_a_test_designer_s_commit_of_a_ticket_file_is_flagged(project, call):
    """``Role: independent-test-designer``: the commit widens the engineer ticket and adds an acceptance test."""
    command = _widening_commit_with_work(trailers=AS_DESIGNER, path=support.NEW_TEST)
    result, left = call(project, command, ORCHESTRATOR, TICKET)
    _assert_the_ticket_file_allows_everything(project, TICKET_FILE)
    _assert_changed_by_a_commit_with_role(project, TICKET_FILE, DESIGNER)
    what = (f"a commit with trailers {AS_DESIGNER} that widens {TICKET_FILE} and adds {support.NEW_TEST}, in the "
            f"orchestrator's own call on {TICKET}")
    check_support.assert_caught(result, TICKET_FILE, what=what, action=check_support.FLAGGED)
    check_support.assert_not_recorded(result, support.NEW_TEST, what=what)
    check_support.assert_left_as_the_call_left_it(project, left, what)


# --------------------------------------------------------------------------
# The other side: the orchestrator's own commit of a ticket file
# --------------------------------------------------------------------------

def test_an_orchestrator_s_commit_of_a_ticket_file_made_in_its_own_call_is_silent(project, call):
    """``Role: orchestrator``: the same widening of the engineer ticket, with README.md, in the orchestrator's
    own call. The orchestrator may write every path outside ``tests/acceptance/**`` (DEC-156)."""
    command = _widening_commit_with_work(trailers=AS_ORCHESTRATOR)
    result, left = call(project, command, ORCHESTRATOR, TICKET)
    _assert_the_ticket_file_allows_everything(project, TICKET_FILE)
    _assert_changed_by_a_commit_with_role(project, TICKET_FILE, ORCHESTRATOR)
    what = (f"a commit with trailers {AS_ORCHESTRATOR} that widens {TICKET_FILE} and changes {README}, in the "
            f"orchestrator's own call on {TICKET}")
    check_support.assert_silent(result, what)
    check_support.assert_left_as_the_call_left_it(project, left, what)


def test_an_engineer_s_commit_under_paths_an_orchestrator_s_commit_gave_the_ticket_is_silent(project, call):
    """One call: the orchestrator's commit widens the ticket (it changes only the ticket file); the engineer's
    commit then changes README.md and no ticket file. The ticket allows README.md at ``HEAD`` and in the working
    tree, and no commit with a worker's trailer touches ``.tickets/**``.

    This is also the guard of this file's fixtures: the entry the tests add to ``allowed_paths`` is one the
    check reads as allowing README.md.
    """
    command = (support.widen_paths(TICKET) + " && "
               + support.commit_paths([TICKET_FILE], AS_ORCHESTRATOR, subject="the orchestrator widens the ticket")
               + " && " + support.commit(README, AS_ENGINEER, subject="work under the widened paths"))
    result, left = call(project, command, ORCHESTRATOR, TICKET)
    _assert_the_ticket_file_allows_everything(project, TICKET_FILE)
    _assert_changed_by_a_commit_with_role(project, TICKET_FILE, ORCHESTRATOR)
    assert support.changed_paths(project, "HEAD") == [README], (
        f"the fixture is wrong: the engineer's commit changes {support.changed_paths(project, 'HEAD')}"
    )
    what = f"`{command[:200]}…` in the orchestrator's own call on {TICKET}"
    check_support.assert_silent(result, what)
    check_support.assert_left_as_the_call_left_it(project, left, what)

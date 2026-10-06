"""W1-50 — in a worker's call, a commit that changes a ticket file is a finding, with or without trailers.

Added after implementation; reason: delegated decision, DEC-394 (package
DP-17).

DEC-394, DP-17: "in a worker's call, any commit of the move that changes a path
under `.tickets/**` is a finding, with or without trailers."

DEC-390 (DP-16) already makes a ticket-file change a finding in a commit that
carries a worker's ``Role`` trailer. What it left open: a commit *without*
trailers is judged against the caller (KPI success 4), and the caller's paths
are read from the ticket, so a worker whose commit widens its own ticket is
judged by the file that commit has just written. The commit of these cases
is that one: it adds ``**`` to the calling session's own ticket and changes
``README.md``, outside the ticket's former paths. After the move ``HEAD`` and
the working tree agree on the widened file.

A worker's call is a session of a worker's role, or a subagent of a worker's
role inside an orchestrator session (DEC-117); the fixture ``call`` models the
second with ``subagent``. Each test asserts the finding that names the ticket
file, and nothing about ``README.md``.

The commit with a worker's own trailers in its own call is
``test_an_engineer_s_commit_that_widens_its_own_ticket_in_its_own_call_is_flagged``
(DP-16).

**The other side.** In an orchestrator session's own call the same commits are
silent: the orchestrator may write every path outside ``tests/acceptance/**``
(DEC-156). With orchestrator trailers that is the existing
``test_an_orchestrator_s_commit_of_a_ticket_file_made_in_its_own_call_is_silent``;
the commit without trailers is the last test here.
"""

from __future__ import annotations

import pytest

import w1_50_support as support

check_support = support.check_support

ORCHESTRATOR = support.ORCHESTRATOR
ENGINEER = support.ENGINEER
TICKET = support.TICKET
AS_ORCHESTRATOR = support.AS_ORCHESTRATOR
NO_TRAILERS = support.NO_TRAILERS

README = support.README
TICKET_FILE = support.ticket_file(TICKET)


def _widening_commit_with_work(trailers):
    """Shell: one commit that adds ``**`` to the ticket's ``allowed_paths`` and changes README.md."""
    return (support.widen_paths(TICKET) + " && " + support.change(README) + " && "
            + support.commit_paths([TICKET_FILE, README], trailers, subject="widen and work"))


def _assert_the_commit_widened_the_ticket(project, trailers):
    """Guard against an empty test: one new commit changed the ticket file and README.md, with ``trailers``;
    ``HEAD`` and the working tree hold the same, widened file."""
    committed = check_support.git(project, "show", f"HEAD:{TICKET_FILE}")
    assert check_support.read(project, TICKET_FILE) == committed, (
        f"the fixture is wrong: {TICKET_FILE} differs between HEAD and the working tree"
    )
    assert f"\n- {support.EVERYTHING}\n" in committed and "\nstatus: in_progress\n" in committed, (
        f"the fixture is wrong: {TICKET_FILE} at HEAD is not in progress with the entry {support.EVERYTHING}"
    )
    assert sorted(support.changed_paths(project, "HEAD")) == sorted([TICKET_FILE, README]), (
        f"the fixture is wrong: the commit changes {support.changed_paths(project, 'HEAD')}"
    )
    roles = support.trailer_values(project, "HEAD", "Role")
    tasks = support.trailer_values(project, "HEAD", "Task")
    expected = ([], []) if trailers is None else ([trailers[0]], [trailers[1]])
    assert (roles, tasks) == expected, (
        f"the fixture is wrong: the commit carries the Role trailers {roles} and the Task trailers {tasks}"
    )


# name: (GOV_ROLE, subagent type)
WORKER_CALLS = {
    "engineer-session": (ENGINEER, None),
    "engineer-subagent-of-an-orchestrator-session": (ORCHESTRATOR, ENGINEER),
}

# name: the commit's trailers
COMMITS = {
    "commit-without-trailers": NO_TRAILERS,
    "commit-with-orchestrator-trailers": AS_ORCHESTRATOR,
}

FLAGGED = sorted((caller, commit) for caller in WORKER_CALLS for commit in COMMITS)


@pytest.mark.parametrize("caller,commit", FLAGGED, ids=[f"{caller}-{commit}" for caller, commit in FLAGGED])
def test_a_commit_of_a_ticket_file_made_in_a_worker_s_call_is_flagged(project, call, caller, commit):
    """DEC-394, DP-17. The finding names the ticket file, whatever the commit's trailers and whatever the
    ticket's file allows after the commit."""
    role, subagent = WORKER_CALLS[caller]
    trailers = COMMITS[commit]
    command = _widening_commit_with_work(trailers)
    result, left = call(project, command, role, TICKET, subagent=subagent)
    _assert_the_commit_widened_the_ticket(project, trailers)
    what = (f"a commit with trailers {trailers} that widens {TICKET_FILE} and changes {README}, in a call with "
            f"GOV_ROLE={role!r} and subagent {subagent!r} on {TICKET}")
    check_support.assert_caught(result, TICKET_FILE, what=what, action=check_support.FLAGGED)
    check_support.assert_left_as_the_call_left_it(project, left, what)


def test_a_commit_without_trailers_of_a_ticket_file_made_in_the_orchestrator_s_own_call_is_silent(project, call):
    """DP-17 speaks of a worker's call. In an orchestrator session's own call the commit without trailers is
    judged against the caller (KPI success 4), and the orchestrator may write the ticket file and README.md
    (DEC-156)."""
    command = _widening_commit_with_work(NO_TRAILERS)
    result, left = call(project, command, ORCHESTRATOR, TICKET)
    _assert_the_commit_widened_the_ticket(project, NO_TRAILERS)
    what = (f"a commit without trailers that widens {TICKET_FILE} and changes {README}, in the orchestrator's own "
            f"call on {TICKET}")
    check_support.assert_silent(result, what)
    check_support.assert_left_as_the_call_left_it(project, left, what)

"""W1-50 — a ticket's state and paths are read from ``HEAD`` and from the working tree, and both must allow.

Added after implementation; reason: delegated decision, DEC-390 (package
DP-14). Expected to pass on the implementation as it stands: DEC-390 fixes
the reading the check already has.

DEC-390, DP-14: "a ticket's state and `allowed_paths` are read from `HEAD` and
from the working tree, and both must allow."

In each test the ticket's file differs between the commit at ``HEAD`` and the
working tree, and one of the two would let the commit pass. The commit carries
an engineer's trailers and changes a path the orchestrator may write itself.
The edit of the ticket's file is the orchestrator's own uncommitted change of
a path outside ``tests/acceptance/**``; it is no finding (DEC-156) and the
check leaves it in the working tree.

The fifth case of the decision's ground, a ticket closed at ``HEAD`` and
reopened only in the working tree, is
``test_w1_50_uncommitted_ticket_state.py`` (fourth batch).

Where both agree and allow, the commit passes: every silent case of the suite.

Every call is an orchestrator session's own call (DEC-319).
"""

from __future__ import annotations

import w1_50_support as support

check_support = support.check_support

ORCHESTRATOR = support.ORCHESTRATOR
ENGINEER = support.ENGINEER
TICKET = support.TICKET
CLOSED = support.CLOSED_TICKET          # in progress in these tests until a test closes it
OPEN = support.OPEN_TICKET
NEW_TICKET = support.NEW_TICKET
AS_ENGINEER = support.AS_ENGINEER

TICKET_FILE = support.ticket_file(TICKET)


def test_a_ticket_closed_only_in_the_working_tree_is_closed_for_a_commit_that_names_it(project, sandbox,
                                                                                      call_leaving_changes):
    """In progress at ``HEAD``; the call sets ``status: closed`` in the working tree, does not commit it, and
    makes an engineer's commit inside the ticket's paths. The working tree does not allow: a finding."""
    path = support.CLOSED_SOURCE
    ticket_file = support.ticket_file(CLOSED)
    support.two_more_tickets(project, sandbox)
    command = support.set_status_in_the_working_tree(CLOSED, "closed") + " && " + support.commit(path,
                                                                                                 (ENGINEER, CLOSED))
    result, left = call_leaving_changes(project, command, ORCHESTRATOR, TICKET, uncommitted=[ticket_file])
    assert support.status_at(project, CLOSED) == ["status: in_progress"], (
        "the fixture is wrong: the ticket is not in progress at HEAD"
    )
    assert support.status_in_tree(project, CLOSED) == ["status: closed"], (
        "the fixture is wrong: the ticket is not closed in the working tree"
    )
    what = (f"`{command}` by the orchestrator on {TICKET}: {CLOSED} is in progress at HEAD and closed only in the "
            f"working tree")
    check_support.assert_caught(result, path, what=what, action=check_support.FLAGGED)
    check_support.assert_left_as_the_call_left_it(project, left, what)


def test_a_ticket_started_only_in_the_working_tree_is_not_started_for_a_commit_that_names_it(project, sandbox,
                                                                                            call_leaving_changes):
    """``status: open`` at ``HEAD``; the call sets ``status: in_progress`` in the working tree, does not commit
    it, and makes an engineer's commit inside the ticket's paths. ``HEAD`` does not allow: a finding."""
    path = support.OPEN_SOURCE
    ticket_file = support.ticket_file(OPEN)
    support.two_more_tickets(project, sandbox)
    command = support.set_status_in_the_working_tree(OPEN, "in_progress") + " && " + support.commit(path,
                                                                                                    (ENGINEER, OPEN))
    result, left = call_leaving_changes(project, command, ORCHESTRATOR, TICKET, uncommitted=[ticket_file])
    assert support.status_at(project, OPEN) == ["status: open"], "the fixture is wrong: the ticket is not open at HEAD"
    assert support.status_in_tree(project, OPEN) == ["status: in_progress"], (
        "the fixture is wrong: the ticket is not in progress in the working tree"
    )
    what = (f"`{command}` by the orchestrator on {TICKET}: {OPEN} is open at HEAD and in progress only in the "
            f"working tree")
    check_support.assert_caught(result, path, what=what, action=check_support.FLAGGED)
    check_support.assert_left_as_the_call_left_it(project, left, what)


def test_a_path_only_the_working_tree_s_ticket_file_allows_is_flagged(project, call_leaving_changes):
    """The call adds ``**`` to the ticket's ``allowed_paths`` in the working tree, does not commit it, and makes
    an engineer's commit of README.md. The committed file does not allow README.md: a finding."""
    path = support.README
    command = support.widen_paths(TICKET) + " && " + support.commit(path, AS_ENGINEER)
    result, left = call_leaving_changes(project, command, ORCHESTRATOR, TICKET, uncommitted=[TICKET_FILE])
    assert support.EVERYTHING not in support.allowed_paths_at(project, TICKET), (
        "the fixture is wrong: the committed ticket file allows every path"
    )
    assert support.EVERYTHING in support.allowed_paths_in_tree(project, TICKET), (
        "the fixture is wrong: the working tree's ticket file does not allow every path"
    )
    what = (f"`{command}` by the orchestrator on {TICKET}: only the working tree's ticket file allows {path}")
    check_support.assert_caught(result, path, what=what, action=check_support.FLAGGED)
    check_support.assert_left_as_the_call_left_it(project, left, what)


def test_a_path_only_the_committed_ticket_file_allows_is_flagged(project, call_leaving_changes):
    """The call takes ``pyproject.toml`` out of the ticket's ``allowed_paths`` in the working tree, does not
    commit that, and makes an engineer's commit of ``pyproject.toml``. The working tree's file does not allow
    the path: a finding."""
    path = support.SECOND_SOURCE
    command = support.drop_path(TICKET, path) + " && " + support.commit(path, AS_ENGINEER)
    result, left = call_leaving_changes(project, command, ORCHESTRATOR, TICKET, uncommitted=[TICKET_FILE])
    assert path in support.allowed_paths_at(project, TICKET), (
        f"the fixture is wrong: the committed ticket file does not allow {path}"
    )
    assert path not in support.allowed_paths_in_tree(project, TICKET), (
        f"the fixture is wrong: the working tree's ticket file still allows {path}"
    )
    what = f"`{command}` by the orchestrator on {TICKET}: only the committed ticket file allows {path}"
    check_support.assert_caught(result, path, what=what, action=check_support.FLAGGED)
    check_support.assert_left_as_the_call_left_it(project, left, what)


def test_a_ticket_file_that_is_only_in_the_working_tree_names_no_ticket(project, call_leaving_changes):
    """The call writes a ticket file ``DAEO-zz99`` (engineer, in progress, ``**``), does not commit it, and
    makes an engineer's commit of README.md that names that ticket. No commit holds the ticket: the trailers
    name no ticket and allow nothing (DEC-268)."""
    path = support.README
    ticket_file = support.ticket_file(NEW_TICKET)
    command = support.new_ticket_file() + " && " + support.commit(path, (ENGINEER, NEW_TICKET))
    result, left = call_leaving_changes(project, command, ORCHESTRATOR, TICKET, uncommitted=[ticket_file])
    assert not support.is_tracked(project, ticket_file), "the fixture is wrong: HEAD holds the new ticket's file"
    assert support.status_in_tree(project, NEW_TICKET) == ["status: in_progress"], (
        "the fixture is wrong: the working tree's ticket file is not in progress"
    )
    what = (f"`{command[-160:]}` by the orchestrator on {TICKET}: {ticket_file} exists only in the working tree")
    check_support.assert_caught(result, path, what=what, action=check_support.FLAGGED)
    check_support.assert_left_as_the_call_left_it(project, left, what)

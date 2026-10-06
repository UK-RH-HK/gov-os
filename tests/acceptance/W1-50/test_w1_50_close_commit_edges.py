"""W1-50 — three edges of "the ticket's close commit".

Added after implementation; reason: delegated decision, DEC-390 (package
DP-13). Expected to pass on the implementation as it stands: DEC-390 fixes
the reading the check already has.

DEC-390, DP-13: "a ticket file whose first version is already `closed` is not a
close commit; the close commit itself is not "before" itself when it carries a
worker's trailers; a close made by a merge commit does not count."

DEC-358 (owner): "A ticket's close commit is the latest commit in HEAD's
history in which the ticket's status becomes `closed`. When no such commit is
found for a ticket whose status is `closed`, that is a finding."

DEC-318 (owner): "A commit whose trailers name a closed ticket is judged by
that ticket's role and `allowed_paths` only if it is an ancestor of the
ticket's close commit; otherwise it is a finding."

The closed ticket is ``DAEO-zz97`` (engineer, ``lib/closed/**``). Every commit
judged here carries an engineer's trailers that name it and changes a file
inside its paths, which the orchestrator may write itself: under the other
reading of each edge the call would be silent. Every call is an orchestrator
session's own call (DEC-319).

Each test asserts the finding for the commit's work path. A ticket file changed
by a commit with a worker's trailers is a finding of its own (DEC-390, DP-16):
``test_w1_50_worker_commit_of_a_ticket_file.py``.
"""

from __future__ import annotations

import w1_50_support as support

check_support = support.check_support

ORCHESTRATOR = support.ORCHESTRATOR
ENGINEER = support.ENGINEER
TICKET = support.TICKET
CLOSED = support.CLOSED_TICKET
CLOSED_FILE = support.ticket_file(CLOSED)
AS_ORCHESTRATOR = support.AS_ORCHESTRATOR

BEHIND = "behind"                # a branch left where ``main`` was before the ticket's history
TAKE_MAIN = "git merge -q --ff-only main"
WORK = (support.CLOSED_SOURCE, (ENGINEER, CLOSED))


def test_a_commit_older_than_a_ticket_file_that_begins_closed_is_flagged(project, sandbox, call):
    """ "A ticket file whose first version is already `closed` is not a close commit."

    The engineer's commit that names the ticket is made first; the commit after it adds the ticket's file,
    already holding ``status: closed``. The work is an ancestor of the commit that brought the status. That
    commit is no close commit, so the ticket is closed without one and the work is a finding. A branch that is
    behind takes both in.
    """
    path = support.CLOSED_SOURCE
    check_support.git(project, "branch", BEHIND)
    support.run(project, sandbox, support.commits(WORK))
    work = support.commit_of(project, path)
    assert not support.is_tracked(project, CLOSED_FILE), "the fixture is wrong: the ticket's file exists already"
    support.two_more_tickets(project, sandbox, closed_status="closed")
    first_version = support.status_changes(project)
    assert len(first_version) == 1 and support.status_at(project, CLOSED) == ["status: closed"], (
        "the fixture is wrong: the ticket's file has more than one version, or its first version is not closed"
    )
    assert support.is_ancestor(project, work, first_version[0]) and work != first_version[0], (
        "the fixture is wrong: the work is not older than the ticket's file"
    )
    check_support.git(project, "checkout", "-q", BEHIND)
    result, left = call(project, TAKE_MAIN, ORCHESTRATOR, TICKET)
    what = (f"`{TAKE_MAIN}` by the orchestrator on {TICKET}, bringing a commit of {path} with trailers "
            f"{(ENGINEER, CLOSED)} and, after it, the commit that adds {CLOSED_FILE} with status closed")
    check_support.assert_caught(result, path, what=what, action=check_support.FLAGGED)
    check_support.assert_left_as_the_call_left_it(project, left, what)


def test_the_work_paths_of_a_close_commit_with_a_worker_s_trailers_are_flagged(project, sandbox, call):
    """ "The close commit itself is not "before" itself when it carries a worker's trailers."

    One commit with the engineer's trailers sets ``status: closed`` and adds a file inside the ticket's paths.
    It is the ticket's close commit (the latest commit in which the status becomes ``closed``) and it names a
    closed ticket; it is no ancestor of itself, so its work path is a finding.
    """
    path = support.CLOSED_LATE_SOURCE
    support.two_more_tickets(project, sandbox)
    support.run(project, sandbox, support.commits(WORK))
    command = (support.set_status_in_the_working_tree(CLOSED, "closed") + " && " + support.change(path) + " && "
               + support.commit_paths([CLOSED_FILE, path], (ENGINEER, CLOSED), subject="work, and the close"))
    result, left = call(project, command, ORCHESTRATOR, TICKET)
    close_commit = check_support.git(project, "rev-parse", "HEAD").strip()
    assert support.status_at(project, CLOSED) == ["status: closed"] and support.status_at(
        project, CLOSED, "HEAD~1") == ["status: in_progress"], (
        "the fixture is wrong: the commit does not move the ticket's status from in_progress to closed"
    )
    assert sorted(support.changed_paths(project, close_commit)) == sorted([CLOSED_FILE, path]), (
        f"the fixture is wrong: the close commit changes {support.changed_paths(project, close_commit)}"
    )
    assert support.trailer_values(project, close_commit, "Role") == [ENGINEER], (
        "the fixture is wrong: the close commit does not carry the engineer's Role trailer"
    )
    what = (f"a commit with trailers {(ENGINEER, CLOSED)} that sets {CLOSED} to closed and adds {path}, in the "
            f"orchestrator's own call on {TICKET}")
    check_support.assert_caught(result, path, what=what, action=check_support.FLAGGED)
    check_support.assert_left_as_the_call_left_it(project, left, what)


def test_a_close_made_by_a_merge_commit_is_no_close_commit(project, sandbox, call):
    """ "A close made by a merge commit does not count."

    The ticket's work is on ``main``. Then a merge commit of the orchestrator, by its own hand edit, sets the
    ticket's status to ``closed``; neither of its parents holds that status. The work is an ancestor of the
    merge commit. The merge commit is no close commit, so the ticket is closed without one and the work is a
    finding. A branch that is behind takes the whole history in.
    """
    path = support.CLOSED_SOURCE
    support.two_more_tickets(project, sandbox)
    support.run(project, sandbox, support.commits(WORK))
    work = support.commit_of(project, path)
    support.ticket_branch(project, sandbox, (support.SECOND_SOURCE, support.AS_ENGINEER))
    support.run(project, sandbox,
                f"git merge -q --no-ff --no-commit {support.TICKET_BRANCH} && "
                + support.set_status_in_the_working_tree(CLOSED, "closed") + " && "
                + support.commit_paths([CLOSED_FILE], (ORCHESTRATOR, CLOSED),
                                       subject=f"Merge {support.TICKET_BRANCH}; {support.CLOSED_WBS} closed"))
    merge_commit = check_support.git(project, "rev-parse", "HEAD").strip()
    assert support.is_merge(project), "the fixture is wrong: the commit that closes the ticket is no merge commit"
    assert support.status_at(project, CLOSED) == ["status: closed"], "the fixture is wrong: the ticket is not closed"
    for parent in ("HEAD^1", "HEAD^2"):
        assert support.status_at(project, CLOSED, parent) == ["status: in_progress"], (
            f"the fixture is wrong: {parent} already holds the closed status"
        )
    assert support.is_ancestor(project, work, merge_commit), (
        "the fixture is wrong: the work is no ancestor of the merge commit"
    )
    check_support.git(project, "checkout", "-q", support.LEAD_BRANCH)
    result, left = call(project, TAKE_MAIN, ORCHESTRATOR, TICKET)
    what = (f"`{TAKE_MAIN}` by the orchestrator on {TICKET}, bringing a commit of {path} with trailers "
            f"{(ENGINEER, CLOSED)} and, after it, a merge commit whose own change closes {CLOSED}")
    check_support.assert_caught(result, path, what=what, action=check_support.FLAGGED)
    check_support.assert_not_recorded(result, support.SECOND_SOURCE, what=what)
    check_support.assert_left_as_the_call_left_it(project, left, what)

"""W1-50 — a forward ``HEAD`` move is judged commit by commit, each commit by its own trailers.

KPI success 1 [CAP-58.h]: "A forward HEAD move, including an integration merge
by the orchestrator, is judged commit by commit: each commit's paths against
the allowed paths of its own Role and Task trailers, not against the caller".

KPI failure 2: "A commit that changes a path outside the allowed paths of its
own Role and Task trailers raises no finding, whoever the caller is".

Each test makes one whole Bash call (PreToolUse hook, command, PostToolUse
hook) that makes one or more commits on the same branch. Integration merges
are in ``test_w1_50_integration_merge.py``.
"""

from __future__ import annotations

import pytest

import w1_50_support as support

check_support = support.check_support

ORCHESTRATOR = support.ORCHESTRATOR
ENGINEER = support.ENGINEER
DESIGNER = support.DESIGNER
TICKET = support.TICKET
AS_DESIGNER = support.AS_DESIGNER
AS_ENGINEER = support.AS_ENGINEER


# --------------------------------------------------------------------------
# Commits inside the paths of their own trailers: no finding
# --------------------------------------------------------------------------

def _fast_forward(project, sandbox):
    support.ticket_branch(project, sandbox, (support.NEW_TEST, AS_DESIGNER), (support.SOURCE, AS_ENGINEER),
                          main_moves_on=False)
    return f"git merge -q --ff-only {support.TICKET_BRANCH}"


# name: the command of the call, or a function that prepares the project and returns the command
INSIDE = {
    "one-test-designer-commit": support.commits((support.NEW_TEST, AS_DESIGNER)),
    "a-test-designer-commit-then-an-engineer-commit": support.commits(
        (support.NEW_TEST, AS_DESIGNER), (support.SOURCE, AS_ENGINEER)),
    "three-commits-of-two-roles": support.commits(
        (support.NEW_TEST, AS_DESIGNER), (support.SOURCE, AS_ENGINEER), (support.ACCEPTANCE_FILE, AS_DESIGNER)),
    "fast-forward-to-a-ticket-branch": _fast_forward,
    # Green before W1-50 too: the orchestrator may write docs/notes.md itself.
    "an-engineer-commit-of-another-ticket": support.commits((support.NOTES, (ENGINEER, support.DOCS_TICKET))),
}


@pytest.mark.parametrize("case", sorted(INSIDE), ids=sorted(INSIDE))
def test_commits_inside_the_paths_of_their_own_trailers_are_silent(project, sandbox, call, case):
    """The caller is the orchestrator, which may not write ``tests/acceptance/**`` itself (DEC-156)."""
    command = INSIDE[case]
    if callable(command):
        command = command(project, sandbox)
    result, left = call(project, command, ORCHESTRATOR, TICKET)
    what = f"`{command}` in a call of the orchestrator on {TICKET}"
    check_support.assert_silent(result, what)
    check_support.assert_left_as_the_call_left_it(project, left, what)


# --------------------------------------------------------------------------
# A commit outside the paths of its own trailers: a finding, whoever the caller is
# --------------------------------------------------------------------------

# name: (the commit's trailers, the path it changes)
OUTSIDE = {
    "engineer-commit-outside-its-ticket-paths": (AS_ENGINEER, support.README),
    "engineer-commit-of-an-acceptance-test": (AS_ENGINEER, support.ACCEPTANCE_FILE),
    "test-designer-commit-of-a-source-file": (AS_DESIGNER, support.SOURCE),
}

# name: (GOV_ROLE, GOV_TICKET). Each of them may write one of the three paths itself.
CALLERS = {
    "orchestrator": (ORCHESTRATOR, TICKET),
    "engineer": (ENGINEER, TICKET),
    "test-designer": (DESIGNER, TICKET),
}


@pytest.mark.parametrize("caller", sorted(CALLERS), ids=sorted(CALLERS))
@pytest.mark.parametrize("case", sorted(OUTSIDE), ids=sorted(OUTSIDE))
def test_a_commit_outside_the_paths_of_its_own_trailers_is_flagged_whoever_the_caller_is(project, call, case,
                                                                                         caller):
    trailers, path = OUTSIDE[case]
    role, ticket = CALLERS[caller]
    command = support.commit(path, trailers)
    result, left = call(project, command, role, ticket)
    what = f"a commit of {path} with trailers {trailers}, in a call with GOV_ROLE={role!r} on {ticket}"
    check_support.assert_caught(result, path, what=what, action=check_support.FLAGGED)
    check_support.assert_left_as_the_call_left_it(project, left, what)


def test_each_commit_is_judged_by_its_own_trailers_not_the_move_as_a_whole(project, call):
    """Four commits of two roles. Every path is in one role's scope; two commits hold the other role's path."""
    command = support.commits(
        (support.SOURCE, AS_DESIGNER),            # outside the test designer's paths
        (support.NEW_TEST, AS_ENGINEER),          # outside the engineer's paths
        (support.SECOND_NEW_TEST, AS_DESIGNER),   # inside
        (support.SECOND_SOURCE, AS_ENGINEER),     # inside
    )
    result, left = call(project, command, ORCHESTRATOR, TICKET)
    what = f"`{command}` in a call of the orchestrator on {TICKET}"
    check_support.assert_caught(result, support.SOURCE, support.NEW_TEST, what=what, action=check_support.FLAGGED)
    check_support.assert_not_recorded(result, support.SECOND_NEW_TEST, support.SECOND_SOURCE, what=what)
    for path in (support.SECOND_NEW_TEST, support.SECOND_SOURCE):
        assert path not in result.report, f"{what}: the report names {path}, a commit inside its own paths"
    check_support.assert_left_as_the_call_left_it(project, left, what)


def test_one_commit_outside_its_paths_among_commits_inside_theirs_is_the_only_finding(project, call):
    command = support.commits(
        (support.NEW_TEST, AS_DESIGNER), (support.SOURCE, AS_ENGINEER), (support.README, AS_ENGINEER))
    result, left = call(project, command, ORCHESTRATOR, TICKET)
    what = f"`{command}` in a call of the orchestrator on {TICKET}"
    check_support.assert_caught(result, support.README, what=what, action=check_support.FLAGGED)
    check_support.assert_not_recorded(result, support.NEW_TEST, support.SOURCE, what=what)
    check_support.assert_left_as_the_call_left_it(project, left, what)


def test_a_commit_outside_its_paths_is_flagged_although_a_later_commit_undoes_it(project, call):
    """ "Commit by commit": the two revisions of ``HEAD`` hold the same files, and one commit still left its paths."""
    command = (
        support.commit(support.README, AS_ENGINEER, subject="outside")
        + f" && git checkout -q HEAD~1 -- {support.README}"
        + " && git commit -q -m undo --trailer 'Task: " + TICKET + "' --trailer 'Role: engineer'"
    )
    result, left = call(project, command, ENGINEER, TICKET)
    what = f"`{command}` in a call of the engineer on {TICKET}"
    assert check_support.git(project, "diff", "--name-only", "HEAD~2", "HEAD") == "", (
        "the fixture is wrong: the two commits together change a file"
    )
    check_support.assert_caught(result, support.README, what=what, action=check_support.FLAGGED)
    check_support.assert_left_as_the_call_left_it(project, left, what)

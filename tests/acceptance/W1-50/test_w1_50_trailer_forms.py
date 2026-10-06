"""W1-50 — which trailers count, and what trailers that name nothing valid allow.

DEC-267: "A commit is judged by its own trailers only when its final trailer
block carries both `Role` and `Task`. A commit with one of the two, or with
`Role:` and `Task:` lines only in the message body, is judged against the
caller, as today."

DEC-268: "When a commit's trailers name an unknown role, an unknown ticket, a
role that is not the ticket's, or several different `Role` or `Task` values,
the commit has no allowed paths and every path it changes is a finding. A
ticket is found by its `id` or its `wbs_id`, as the guard does."

Every call here is an orchestrator session's own call (DEC-319). The
orchestrator may write everything outside ``tests/acceptance/**`` itself
(DEC-156) and nothing under it.
"""

from __future__ import annotations

import pytest

import w1_50_support as support

check_support = support.check_support

ORCHESTRATOR = support.ORCHESTRATOR
ENGINEER = support.ENGINEER
DESIGNER = support.DESIGNER
TICKET = support.TICKET

ROLE_DESIGNER = f"Role: {DESIGNER}"
ROLE_ENGINEER = f"Role: {ENGINEER}"
TASK = f"Task: {TICKET}"
BODY_ONLY = ("-m", TASK, "-m", "{role}", "-m", "The trailer lines above are not in the last paragraph.")


def _body_only(role_line):
    return tuple(role_line if word == "{role}" else word for word in BODY_ONLY)


# name: (arguments of `git commit`, the path, the caller may write that path itself)
NOT_BOTH_TRAILERS = {
    # The trailers would allow the path; the caller does not.
    "role-only-of-an-acceptance-test": (support.trailer_arguments(ROLE_DESIGNER), support.NEW_TEST, False),
    "task-only-of-an-acceptance-test": (support.trailer_arguments(TASK), support.NEW_TEST, False),
    "body-lines-only-of-an-acceptance-test": (_body_only(ROLE_DESIGNER), support.NEW_TEST, False),
    # The trailers would not allow the path; the caller does.
    "role-only-outside-that-role-s-paths": (support.trailer_arguments(ROLE_ENGINEER), support.README, True),
    "body-lines-only-outside-that-role-s-paths": (_body_only(ROLE_ENGINEER), support.README, True),
}


@pytest.mark.parametrize("case", sorted(NOT_BOTH_TRAILERS), ids=sorted(NOT_BOTH_TRAILERS))
def test_a_commit_without_both_trailers_in_the_final_block_is_judged_against_the_caller(project, call, case):
    """DEC-267. Green before W1-50 and after it: today every commit is judged against the caller."""
    arguments, path, allowed = NOT_BOTH_TRAILERS[case]
    command = support.commit_with(path, *arguments)
    result, left = call(project, command, ORCHESTRATOR, TICKET)
    message = check_support.git(project, "log", "-1", "--format=%B")
    found = check_support.git(project, "log", "-1", "--format=%(trailers:only,key=Role)%(trailers:only,key=Task)")
    assert len(found.split()) <= 2, (
        f"the fixture is wrong: git reads both trailers from the final block of {message!r}: {found!r}"
    )
    what = f"`{command}` in a call of the orchestrator on {TICKET}"
    if allowed:
        check_support.assert_silent(result, what)
    else:
        check_support.assert_caught(result, path, what=what, action=check_support.FLAGGED)
    check_support.assert_left_as_the_call_left_it(project, left, what)


def test_both_trailers_in_the_final_block_next_to_other_trailers_are_the_commit_s_own(project, call):
    """DEC-182 puts ``Task:``, ``Implements:`` and ``Role:`` in one block; a co-author line stands there too."""
    arguments = support.trailer_arguments(TASK, "Implements: CAP-58.h", ROLE_DESIGNER,
                                          "Co-Authored-By: Someone <someone@example.invalid>")
    command = support.commit_with(support.NEW_TEST, "-m", "A body paragraph.", *arguments)
    result, left = call(project, command, ORCHESTRATOR, TICKET)
    what = f"`{command}` in a call of the orchestrator on {TICKET}"
    check_support.assert_silent(result, what)
    check_support.assert_left_as_the_call_left_it(project, left, what)


# --------------------------------------------------------------------------
# DEC-268: trailers that name nothing valid allow nothing
# --------------------------------------------------------------------------

# name: (the trailer lines, the path). The orchestrator may write every one of these paths itself.
ALLOW_NOTHING = {
    "unknown-role": (("Task: " + TICKET, "Role: wizard"), support.SOURCE),
    "unknown-ticket": (("Task: DAEO-none", ROLE_ENGINEER), support.SOURCE),
    # DAEO-zz92 is a product-spec ticket; the path is inside its allowed paths.
    "role-that-is-not-the-ticket-s": (("Task: " + support.SPEC_TICKET, ROLE_ENGINEER), support.SPEC_FILE),
    "two-different-roles": ((TASK, ROLE_ENGINEER, ROLE_DESIGNER), support.SOURCE),
    # Both are engineer tickets in progress; the path is inside the second one's allowed paths.
    "two-different-tickets": ((TASK, "Task: " + support.DOCS_TICKET, ROLE_ENGINEER), support.NOTES),
}


@pytest.mark.parametrize("case", sorted(ALLOW_NOTHING), ids=sorted(ALLOW_NOTHING))
def test_trailers_that_name_nothing_valid_allow_nothing(project, call, case):
    """The path is one the caller may write and, but for the fault in the trailers, the named role too."""
    lines, path = ALLOW_NOTHING[case]
    command = support.commit_with(path, *support.trailer_arguments(*lines))
    result, left = call(project, command, ORCHESTRATOR, TICKET)
    what = f"a commit of {path} with the trailers {lines}, in a call of the orchestrator on {TICKET}"
    check_support.assert_caught(result, path, what=what, action=check_support.FLAGGED)
    check_support.assert_left_as_the_call_left_it(project, left, what)


def test_among_valid_commits_only_the_one_with_invalid_trailers_is_a_finding(project, call):
    command = (
        support.commit(support.NEW_TEST, support.AS_DESIGNER)
        + " && " + support.commit_with(support.SOURCE, *support.trailer_arguments(TASK, "Role: wizard"))
        + " && " + support.commit(support.SECOND_SOURCE, support.AS_ENGINEER)
    )
    result, left = call(project, command, ORCHESTRATOR, TICKET)
    what = f"`{command}` in a call of the orchestrator on {TICKET}"
    check_support.assert_caught(result, support.SOURCE, what=what, action=check_support.FLAGGED)
    check_support.assert_not_recorded(result, support.NEW_TEST, support.SECOND_SOURCE, what=what)
    check_support.assert_left_as_the_call_left_it(project, left, what)


def test_a_ticket_named_by_its_wbs_id_is_found(project, call):
    """``Task: W1-90`` names DAEO-zz90, as ``GOV_TICKET=W1-90`` does for the guard."""
    by_wbs_id = support.trailer_arguments("Task: " + support.WBS, ROLE_DESIGNER)
    command = support.commit_with(support.NEW_TEST, *by_wbs_id)
    result, left = call(project, command, ORCHESTRATOR, TICKET)
    what = f"`{command}` in a call of the orchestrator on {TICKET}"
    check_support.assert_silent(result, what)
    check_support.assert_left_as_the_call_left_it(project, left, what)


def test_a_ticket_named_by_its_wbs_id_gives_that_ticket_s_paths_and_no_more(project, call):
    by_wbs_id = support.trailer_arguments("Task: " + support.WBS, ROLE_ENGINEER)
    command = support.commit_with(support.README, *by_wbs_id)
    result, left = call(project, command, ORCHESTRATOR, TICKET)
    what = f"`{command}` in a call of the orchestrator on {TICKET}"
    check_support.assert_caught(result, support.README, what=what, action=check_support.FLAGGED)
    check_support.assert_left_as_the_call_left_it(project, left, what)

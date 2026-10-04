"""W1-50 — a path the merge commit itself changes is judged by the merge commit's own trailers.

DEC-269: "A path a merge commit changes beyond what its parents hold (a
conflict resolution, a hand edit) is judged by the merge commit's own trailers,
or against the caller when it has none. An orchestrator's conflict resolution
under `tests/acceptance/**` is therefore a finding, and elsewhere it is not."

Every merge here is made in an orchestrator session's own call (DEC-266), and
every commit the merge brings stays inside the paths of its own trailers. What
differs is the content the merge commit holds that none of its parents holds.
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

GOOD_COMMITS = ((support.NEW_TEST, AS_DESIGNER), (support.SOURCE, AS_ENGINEER))


def _own_change(project, path):
    """Guard against an empty test: the merge commit holds content of ``path`` that neither parent holds."""
    merged = check_support.git(project, "show", f"HEAD:{path}")
    for parent in ("HEAD^1", "HEAD^2"):
        held = check_support.git(project, "show", f"{parent}:{path}")
        assert merged != held, f"the fixture is wrong: {parent} already holds the merge commit's content of {path}"


# name: (the merge commit's trailers, the path the merge commit changes by hand)
HAND_EDITS_FLAGGED = {
    "orchestrator-trailers-acceptance-test": (AS_ORCHESTRATOR, support.ACCEPTANCE_FILE),
    # No trailers: the caller decides, and the orchestrator may not write an acceptance test.
    "no-trailers-acceptance-test": (NO_TRAILERS, support.ACCEPTANCE_FILE),
    # The caller may write README.md; the merge commit's own trailers do not allow it.
    "engineer-trailers-outside-the-ticket-paths": (AS_ENGINEER, support.README),
}


@pytest.mark.parametrize("case", sorted(HAND_EDITS_FLAGGED), ids=sorted(HAND_EDITS_FLAGGED))
def test_a_merge_commit_s_own_change_outside_its_trailers_paths_is_flagged(project, sandbox, call, case):
    """The finding names the path the merge commit changed, and none of the paths of the commits it brings."""
    trailers, path = HAND_EDITS_FLAGGED[case]
    support.ticket_branch(project, sandbox, *GOOD_COMMITS)
    command = support.merge_with_own_change(path, trailers=trailers)
    result, left = call(project, command, ORCHESTRATOR, TICKET)
    assert support.is_merge(project), f"the fixture command `{command}` made no merge commit"
    _own_change(project, path)
    what = f"`{command}` by the orchestrator on {TICKET}"
    check_support.assert_caught(result, path, what=what, action=check_support.FLAGGED)
    check_support.assert_not_recorded(result, support.NEW_TEST, support.SOURCE, what=what)
    check_support.assert_left_as_the_call_left_it(project, left, what)


# name: (the merge commit's trailers, the path the merge commit changes by hand)
HAND_EDITS_SILENT = {
    "orchestrator-trailers-outside-acceptance-tests": (AS_ORCHESTRATOR, support.README),
    "no-trailers-outside-acceptance-tests": (NO_TRAILERS, support.README),
}


@pytest.mark.parametrize("case", sorted(HAND_EDITS_SILENT), ids=sorted(HAND_EDITS_SILENT))
def test_an_orchestrator_s_own_change_in_a_merge_commit_outside_acceptance_tests_is_silent(project, sandbox, call,
                                                                                         case):
    trailers, path = HAND_EDITS_SILENT[case]
    support.ticket_branch(project, sandbox, *GOOD_COMMITS)
    command = support.merge_with_own_change(path, trailers=trailers)
    result, left = call(project, command, ORCHESTRATOR, TICKET)
    assert support.is_merge(project), f"the fixture command `{command}` made no merge commit"
    _own_change(project, path)
    what = f"`{command}` by the orchestrator on {TICKET}"
    check_support.assert_silent(result, what)
    check_support.assert_left_as_the_call_left_it(project, left, what)


# --------------------------------------------------------------------------
# Conflict resolutions
# --------------------------------------------------------------------------

def _conflict(project, sandbox, path, trailers):
    """``main`` and the ticket branch each change ``path``, both with ``trailers``: merging them conflicts."""
    check_support.git(project, "checkout", "-q", "-b", support.TICKET_BRANCH)
    support.run(project, sandbox, support.commit(path, trailers, subject="the ticket branch's change"))
    check_support.git(project, "checkout", "-q", "main")
    support.run(project, sandbox, f"echo main-side >> {path} && git add -- {path} && git commit -q -m 'main side'"
                                  f" --trailer 'Task: {trailers[1]}' --trailer 'Role: {trailers[0]}'")


def test_an_orchestrator_s_conflict_resolution_under_acceptance_tests_is_flagged(project, sandbox, call):
    """Both sides' commits are the test designer's; the resolution is content neither side holds."""
    path = support.ACCEPTANCE_FILE
    _conflict(project, sandbox, path, AS_DESIGNER)
    command = support.merge_resolving(path, "new")
    result, left = call(project, command, ORCHESTRATOR, TICKET)
    assert support.is_merge(project), f"the fixture command `{command}` made no merge commit"
    _own_change(project, path)
    what = f"`{command}` by the orchestrator on {TICKET}"
    check_support.assert_caught(result, path, what=what, action=check_support.FLAGGED)
    check_support.assert_left_as_the_call_left_it(project, left, what)


def test_an_orchestrator_s_conflict_resolution_outside_acceptance_tests_is_silent(project, sandbox, call):
    path = support.SOURCE
    _conflict(project, sandbox, path, AS_ENGINEER)
    command = support.merge_resolving(path, "new")
    result, left = call(project, command, ORCHESTRATOR, TICKET)
    assert support.is_merge(project), f"the fixture command `{command}` made no merge commit"
    _own_change(project, path)
    what = f"`{command}` by the orchestrator on {TICKET}"
    check_support.assert_silent(result, what)
    check_support.assert_left_as_the_call_left_it(project, left, what)


def test_a_conflict_resolved_to_the_merged_side_s_content_is_not_the_merge_commit_s_own_change(project, sandbox,
                                                                                             call):
    """ "Beyond what its parents hold": the merge commit holds the test designer's content from the merged side."""
    path = support.ACCEPTANCE_FILE
    _conflict(project, sandbox, path, AS_DESIGNER)
    command = support.merge_resolving(path, "theirs")
    result, left = call(project, command, ORCHESTRATOR, TICKET)
    assert support.is_merge(project), f"the fixture command `{command}` made no merge commit"
    merged = check_support.git(project, "show", f"HEAD:{path}")
    assert merged == check_support.git(project, "show", f"HEAD^2:{path}"), (
        "the fixture is wrong: the merge commit does not hold the merged side's content"
    )
    what = f"`{command}` by the orchestrator on {TICKET}"
    check_support.assert_silent(result, what)
    check_support.assert_left_as_the_call_left_it(project, left, what)

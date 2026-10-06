"""W1-50 — a commit carrying ``Role: owner`` that is made during an agent session's call is a finding.

KPI success 5 [CAP-58.h]: "A commit carrying a Role: owner trailer that is made
during any agent session's call is a finding (DEC-360)".

DEC-360 (owner): "The owner's approval fact for a decision is the `Role: owner`
trailer on the commit that sets the decision `ACTIVE`. [...] Safeguard: W1-50
gets a KPI line, in its own commit, so that a commit carrying `Role: owner`
made during any agent session's call is a finding."

"Made during a call" is what the check can observe (README, "Made during an
agent session's call"): the commit is new between the call's PreToolUse hook
and its PostToolUse hook. Every commit judged here is created inside that
window, on the checked branch. An owner commit that existed before the call
and only arrives in the call's move (a merge, a fast-forward) is package
DP-11 and is not tested.

In every flagged case the path is one the caller may write itself, so only
the ``Role: owner`` trailer makes the commit a finding.
"""

from __future__ import annotations

import pytest

import w1_50_support as support

check_support = support.check_support

ORCHESTRATOR = support.ORCHESTRATOR
ENGINEER = support.ENGINEER
TICKET = support.TICKET
AS_DESIGNER = support.AS_DESIGNER
AS_ENGINEER = support.AS_ENGINEER

ROLE_OWNER = f"Role: {support.OWNER}"
TASK = f"Task: {TICKET}"

# name: the commit's trailer lines, in its final trailer block
OWNER_TRAILERS = {
    "task-and-role-owner": (TASK, ROLE_OWNER),
    "role-owner-alone": (ROLE_OWNER,),
}

# name: (GOV_ROLE, subagent type, a path that caller may write itself)
CALLERS = {
    "orchestrator-session": (ORCHESTRATOR, None, support.README),
    "engineer-session": (ENGINEER, None, support.SOURCE),
    "engineer-subagent-of-an-orchestrator-session": (ORCHESTRATOR, ENGINEER, support.SOURCE),
}


def _owner_commit(path, lines):
    return support.commit_with(path, *support.trailer_arguments(*lines))


def _assert_carries_role_owner(project, path):
    """Guard against an empty test: git reads ``Role: owner`` from the commit's final trailer block."""
    found = check_support.git(project, "log", "-1", "--format=%(trailers:key=Role,valueonly)",
                              support.commit_of(project, path))
    assert found.split() == [support.OWNER], f"the fixture is wrong: the commit's Role trailer is {found!r}"


@pytest.mark.parametrize("trailers", sorted(OWNER_TRAILERS), ids=sorted(OWNER_TRAILERS))
@pytest.mark.parametrize("caller", sorted(CALLERS), ids=sorted(CALLERS))
def test_a_role_owner_commit_made_in_an_agent_s_call_is_flagged(project, call, caller, trailers):
    """An orchestrator's call and a worker's call, with and without a ``Task`` trailer next to ``Role: owner``."""
    role, subagent, path = CALLERS[caller]
    lines = OWNER_TRAILERS[trailers]
    command = _owner_commit(path, lines)
    result, left = call(project, command, role, TICKET, subagent=subagent)
    _assert_carries_role_owner(project, path)
    what = (f"a commit of {path} with the trailers {lines}, made in a call with GOV_ROLE={role!r} "
            f"and subagent {subagent!r} on {TICKET}")
    check_support.assert_caught(result, path, what=what, action=check_support.FLAGGED)
    check_support.assert_left_as_the_call_left_it(project, left, what)


def test_among_commits_inside_their_paths_only_the_role_owner_commit_is_a_finding(project, call):
    command = (
        support.commit(support.NEW_TEST, AS_DESIGNER)
        + " && " + _owner_commit(support.README, (TASK, ROLE_OWNER))
        + " && " + support.commit(support.SOURCE, AS_ENGINEER)
    )
    result, left = call(project, command, ORCHESTRATOR, TICKET)
    _assert_carries_role_owner(project, support.README)
    what = f"`{command}` in a call of the orchestrator on {TICKET}"
    check_support.assert_caught(result, support.README, what=what, action=check_support.FLAGGED)
    check_support.assert_not_recorded(result, support.NEW_TEST, support.SOURCE, what=what)
    check_support.assert_left_as_the_call_left_it(project, left, what)


def test_a_role_owner_commit_made_by_someone_else_during_an_agent_s_call_is_flagged(project, sandbox,
                                                                                   during_a_call):
    """ "During any agent session's call": the commit appears while a lead's call waits, with no hook around the
    command that makes it. The check of the waiting call finds it."""
    command = _owner_commit(support.README, (TASK, ROLE_OWNER))
    result, left = during_a_call(project, ORCHESTRATOR, TICKET, lambda: support.run(project, sandbox, command))
    _assert_carries_role_owner(project, support.README)
    what = f"the orchestrator's call on {TICKET}, during which `{command}` ran"
    check_support.assert_caught(result, support.README, what=what, action=check_support.FLAGGED)
    check_support.assert_left_as_the_call_left_it(project, left, what)


# --------------------------------------------------------------------------
# The same trailer on a commit that was in the history before the call
# --------------------------------------------------------------------------

# name: (GOV_ROLE, the commit the call itself makes: path and trailers, inside that commit's own paths)
LATER_CALLS = {
    "orchestrator-call-with-a-test-designer-commit": (ORCHESTRATOR, support.NEW_TEST, AS_DESIGNER),
    # Green before W1-50 too: the engineer may write the source file itself.
    "engineer-call-with-its-own-commit": (ENGINEER, support.SOURCE, AS_ENGINEER),
}


@pytest.mark.parametrize("case", sorted(LATER_CALLS), ids=sorted(LATER_CALLS))
def test_a_role_owner_commit_already_in_the_history_before_the_call_is_no_finding(project, sandbox, call, case):
    """The owner committed README.md before the call began; ``HEAD`` was on that commit at the PreToolUse hook."""
    role, path, trailers = LATER_CALLS[case]
    support.run(project, sandbox, _owner_commit(support.README, (TASK, ROLE_OWNER)))
    _assert_carries_role_owner(project, support.README)
    owner_commit = support.commit_of(project, support.README)
    command = support.commit(path, trailers)
    result, left = call(project, command, role, TICKET)
    assert check_support.git(project, "rev-parse", "HEAD~1").strip() == owner_commit, (
        "the fixture is wrong: the owner's commit is not the commit HEAD was on before the call"
    )
    what = f"`{command}` in a call with GOV_ROLE={role!r} on {TICKET}, the commit before it carrying {ROLE_OWNER!r}"
    check_support.assert_silent(result, what)
    check_support.assert_left_as_the_call_left_it(project, left, what)

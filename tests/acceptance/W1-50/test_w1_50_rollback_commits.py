"""W1-50 — a revert commit in the shape of ``gov pause --rollback`` is judged like any other commit.

Added after implementation; reason: delegated decision, DEC-390 (package
DP-12). Expected to pass on the implementation as it stands: DEC-390 fixes
the reading the check already has.

DEC-390, DP-12: "as built until the owner says otherwise: the revert commits
and the record commit of `gov pause --rollback` are judged like any other
commit; where they are findings, the findings are records."

The shape (README, "The commits of `gov pause --rollback`"): a revert commit
carries ``Role: <role>`` and ``Reverts-Task: <ticket>`` and no ``Task``. Its
final trailer block does not hold both ``Role`` and ``Task``, so it is judged
against the caller (KPI success 4, DEC-267); ``Reverts-Task`` is no trailer
the check reads.

The commits are built by hand with ``git revert --no-commit`` and
``git commit``. No test runs ``gov pause``.

The record commit changes only a ticket's file. With ``Role: orchestrator`` it
is an orchestrator's commit of a ticket file, held by the close commits of the
suite and by
``test_an_orchestrator_s_commit_of_a_ticket_file_made_in_its_own_call_is_silent``;
nothing is added for it.
"""

from __future__ import annotations

import pytest

import w1_50_support as support

check_support = support.check_support

ORCHESTRATOR = support.ORCHESTRATOR
TICKET = support.TICKET

REVERT_TRAILERS = (f"Role: {ORCHESTRATOR}", f"Reverts-Task: {TICKET}")

# name: (the reverted commit: its path and trailers, the orchestrator may write that path itself)
REVERTS = {
    "of-an-engineer-s-commit-of-a-source-file": (support.SOURCE, support.AS_ENGINEER, True),
    "of-a-test-designer-s-commit-of-an-acceptance-test": (support.ACCEPTANCE_FILE, support.AS_DESIGNER, False),
}


@pytest.mark.parametrize("case", sorted(REVERTS), ids=sorted(REVERTS))
def test_a_revert_commit_with_role_and_reverts_task_is_judged_against_the_caller(project, sandbox, call, case):
    """In an orchestrator session's own call: the revert of a source file passes (DEC-156); the revert of a test
    designer's commit changes a path under ``tests/acceptance/**`` and is a finding."""
    path, trailers, allowed = REVERTS[case]
    support.run(project, sandbox, support.commit(path, trailers))
    command = ("git revert --no-commit HEAD && git commit -q -m 'Revert \"work\"'"
               + "".join(f" --trailer '{line}'" for line in REVERT_TRAILERS))
    result, left = call(project, command, ORCHESTRATOR, TICKET)
    found = [line.decode("utf-8") for line in support.final_block(project, "HEAD")]
    assert found == list(REVERT_TRAILERS), f"the fixture is wrong: the revert commit's final block is {found}"
    assert support.changed_paths(project, "HEAD") == [path], (
        f"the fixture is wrong: the revert commit changes {support.changed_paths(project, 'HEAD')}"
    )
    assert check_support.git(project, "diff", "--name-only", "HEAD~2", "HEAD") == "", (
        "the fixture is wrong: the revert does not undo the commit before it"
    )
    what = (f"a revert of the commit of {path}, with the trailers {REVERT_TRAILERS} and no Task trailer, in the "
            f"orchestrator's own call on {TICKET}")
    if allowed:
        check_support.assert_silent(result, what)
    else:
        check_support.assert_caught(result, path, what=what, action=check_support.FLAGGED)
    check_support.assert_left_as_the_call_left_it(project, left, what)

"""W2-72, KPI success 1 — a merge-back acceptance file equal to git's own merge is no change (DEC-918 item 1).

DEC-918 (a1): "containment's merge rule matches DEC-912. A merge-back file under ``tests/acceptance/`` equal to
git's own merge of its parents (``git merge-tree --write-tree``) is neither reverted, refused nor counted as a
change, by the live hook or by the close's gate."

The KPI line: under ``tests/acceptance/``, a path both parents of a merge commit changed against their merge base
is not the merge commit's own change when the merge holds exactly git's own merge of that file (the blob
``git merge-tree --write-tree <first parent> <other parent>`` writes for it, with no conflict on that file):
containment's live post-command check neither restores, refuses nor flags it, and ``judge_commits`` returns no
finding for it.

**The cases.** Each history is a real one in a throw-away project; the guard ``assert_shape`` shows from git's
own answers that both parents changed the acceptance test against their one merge base, and that the merge
commit holds exactly the blob git's own merge writes for it, with no conflict on it:

- a clean combination of two sides' edits of one acceptance test (it equals neither parent);
- two sides that made the same edit (it equals both parents);
- per file, the shape of ``03f470a5``: git reports a conflict on a source file, resolved by hand, and merges the
  acceptance test cleanly. The hand resolution of the source file is an orchestrator's own change outside
  ``tests/acceptance/`` and ``.tickets/``, inside the ticket's paths: silent as before (DEC-269).

Every merge is a forward move of ``main`` made in an orchestrator session's own call (DEC-266), the merge commit
carrying ``Task: DAEO-zz90`` and ``Role: orchestrator``. Each case runs twice: once through the live check, once
through ``judge_commits`` on the same history made with no hook around it.

**Not (a2)** (DEC-918 item 2): no condition is put on the commits that brought the edits. Where the merged side's
edit of the test is an engineer's commit, the merge commit itself is still no change of that file; the engineer's
commit is judged by its own trailers, as before (the last two cases).

Red reason now: DEC-410 DP-24 reads every path both parents changed under ``tests/acceptance/**`` as the merge
commit's own, so the check flags the test ("a merge commit's own change to a ticket file or an acceptance test")
and ``judge_commits`` returns that finding.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_72_support as support  # noqa: E402
from w2_72_support import call, guard_hook, hook, judge, project, sandbox  # noqa: E402,F401  fixtures

check_support = support.check_support

ORCHESTRATOR = support.ORCHESTRATOR
TICKET = support.TICKET


def _in_the_call(project, sandbox, call, build):
    """The orchestrator's own call makes the merge commit of ``build``. Returns (shape, result, state, merge id)."""
    shape = build(project, sandbox)
    before = support.full_id(project, "HEAD")
    result, left = call(project, shape.command, ORCHESTRATOR, TICKET)
    merge_id = support.full_id(project, "HEAD")
    support.assert_shape(project, shape, before, merge_id)
    assert support.trailer_values(project, merge_id, "Role") == [ORCHESTRATOR] and support.trailer_values(
        project, merge_id, "Task") == [TICKET], "the fixture is wrong: the merge commit's trailers"
    return shape, result, left, merge_id


def _with_no_hook(project, sandbox, build):
    """The same history, the merge commit made with no hook around it. Returns (shape, merge id)."""
    shape = build(project, sandbox)
    before = support.full_id(project, "HEAD")
    support.support.run(project, sandbox, shape.command)
    merge_id = support.full_id(project, "HEAD")
    support.assert_shape(project, shape, before, merge_id)
    return shape, merge_id


@pytest.mark.parametrize("case", sorted(support.SUCCESS), ids=sorted(support.SUCCESS))
def test_the_live_check_neither_restores_refuses_nor_flags_an_acceptance_file_equal_to_git_s_own_merge(
        project, sandbox, call, case):
    """DEC-918 item 1, through the live hook: the call is silent (no report to the agent, no finding, exit 0) and
    the check moves nothing (HEAD, index, working tree as the call left them)."""
    shape, result, left, _ = _in_the_call(project, sandbox, call, support.SUCCESS[case])
    what = f"{shape.what}, in the orchestrator's own call on {TICKET}"
    check_support.assert_silent(result, what)
    check_support.assert_left_as_the_call_left_it(project, left, what)


@pytest.mark.parametrize("case", sorted(support.SUCCESS), ids=sorted(support.SUCCESS))
def test_judge_commits_returns_no_finding_for_an_acceptance_file_equal_to_git_s_own_merge(project, sandbox, judge,
                                                                                         case):
    """DEC-918 item 1, through the close's containment gate: ``judge_commits`` on the merge commit alone returns
    no finding."""
    shape, merge_id = _with_no_hook(project, sandbox, support.SUCCESS[case])
    findings = judge(project, [merge_id])
    assert findings == [], (
        f"{shape.what}: judge_commits on the merge commit returns "
        f"{[(f.commit[:12], f.paths, f.reason) for f in findings]}, not no finding (DEC-918 item 1)"
    )


# --------------------------------------------------------------------------
# Not (a2): the merged side's edit of the test is an engineer's commit
# --------------------------------------------------------------------------

def test_the_live_check_names_the_engineer_s_commit_and_not_the_merge_commit(project, sandbox, call):
    """The clean combination, where the merged side's edit of the acceptance test is an engineer's commit. The
    merge commit holds git's own merge of the test: no finding is the merge commit's. The engineer's commit is
    new in the move and judged by its own trailers, as before: a finding for it names the test."""
    shape, result, left, merge_id = _in_the_call(project, sandbox, call, support.brought_by_an_engineer)
    engineer = support.support.commit_of(project, support.MERGED_TEST, support.BRANCH)
    assert support.trailer_values(project, engineer, "Role") == [support.support.ENGINEER], (
        "the fixture is wrong: the merged side's commit of the test is not an engineer's"
    )
    what = f"{shape.what}, in the orchestrator's own call on {TICKET}"
    for_the_engineer = support.findings_for(result, engineer, what)
    assert any(support.MERGED_TEST in check_support.finding_paths(result, f) for f in for_the_engineer), (
        f"{what}: no finding for the engineer's commit {engineer[:12]} names {support.MERGED_TEST}; findings: "
        f"{[f['reason'] for f in check_support.new_findings(result, what)]}"
    )
    for_the_merge = support.findings_for(result, merge_id, what)
    assert for_the_merge == [], (
        f"{what}: the merge commit {merge_id[:12]} holds git's own merge of {support.MERGED_TEST} and has the "
        f"findings {[(f['paths'], f['reason']) for f in for_the_merge]} (DEC-918 items 1 and 2)"
    )
    check_support.assert_left_as_the_call_left_it(project, left, what)


def test_judge_commits_finds_nothing_in_the_merge_commit_and_still_judges_the_engineer_s_commit(project, sandbox,
                                                                                                judge):
    """The same history through ``judge_commits``: the merge commit alone is no finding (no condition on the
    bringing commits, DEC-918 item 2); the engineer's commit alone is a finding that names the test."""
    shape, merge_id = _with_no_hook(project, sandbox, support.brought_by_an_engineer)
    engineer = support.support.commit_of(project, support.MERGED_TEST, support.BRANCH)
    of_the_engineer = judge(project, [engineer])
    assert [f.commit for f in of_the_engineer] == [engineer] and support.MERGED_TEST in of_the_engineer[0].paths, (
        f"{shape.what}: judge_commits on the engineer's commit {engineer[:12]} returns "
        f"{[(f.commit[:12], f.paths) for f in of_the_engineer]}, not one finding that names {support.MERGED_TEST}"
    )
    findings = judge(project, [merge_id])
    assert findings == [], (
        f"{shape.what}: judge_commits on the merge commit returns "
        f"{[(f.commit[:12], f.paths, f.reason) for f in findings]}, not no finding (DEC-918 items 1 and 2)"
    )

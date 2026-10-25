"""W2-72, review 1, F1 — a merge-back made over two Bash calls keeps git's own merge (DEC-918 item 1).

Every merge of the first batch is made in one Bash call. A ticket lead often makes it in two: ``git merge --no-ff
--no-commit w2/integrate``, which may stop on a conflict, and later ``git commit``. Each call runs between the
kernel's PreToolUse and PostToolUse hooks (PostToolUseFailure when the call fails, as ``git merge`` does on a
conflict), in an orchestrator session's own calls (``GOV_ROLE=orchestrator``, ``GOV_TICKET=DAEO-zz90``; DEC-266),
the merge commit carrying ``Task: DAEO-zz90`` and ``Role: orchestrator``.

DEC-918 item 1: a merge-back file under ``tests/acceptance/`` equal to git's own merge of its parents "is neither
reverted, refused nor counted as a change, by the live hook or by the close's gate". Between the two calls the
merge is in progress (``MERGE_HEAD``); git's own merge of the acceptance tests is in the tree and the index, and
it is the same merge: ``git merge-tree --write-tree`` of ``HEAD`` and ``MERGE_HEAD``.

**Kept (KPI 1; red now).** Two histories, as the review drove them:

- *a conflict on the source file* (the shape of ``03f470a5``): the first call's merge stops on a conflict in
  ``src/gov/guard/decide.py``, which both sides' engineers changed, while git combines an acceptance test both
  sides' test designers changed and brings a new acceptance test only the merged side added. The second call
  resolves the source file by hand, stages it and commits the merge;
- *no conflict*: the first call is ``git merge --no-ff --no-commit``, the second ``git commit``.

Expected: neither call's check restores, flags or reports either test (silent, and the tree and the index as the
call left them); the merge commit holds git's own merge of both tests (the combined test as ``git merge-tree
--write-tree`` writes it, the new test present); the tree and the index equal the merge commit; ``judge_commits``
returns no finding for it. A failure shows both calls' agent-facing text and the findings recorded.

Red reason now: after the first call the check reports "Acceptance test restored from HEAD" for both tests: it
sets the combined test back to the first parent's version and deletes the new one; the merge commit then holds
the first parent's versions, the second call's check flags it, and ``judge_commits`` returns a finding.

**Still caught (KPI 2; pass now and must keep passing).** In the same flow:

- a hand write of the acceptance test (line 10, content that differs from git's own merge of ``HEAD`` and the
  merge being made) in the first call after the merge, in a call of its own between, or in the commit's call
  before the commit: the check of the call that makes it catches it (reported and recorded, restored or flagged),
  and the committed merge, when its test differs from git's own merge (it holds the hand write, or a restore that
  is not git's merge), is a finding of the commit's check for the merge commit and of ``judge_commits``;
- a conflict in the acceptance test itself (git reports the test as conflicted), whatever the second call stages
  for it (the first parent's version whole, the merged side's, the blob git's own merge writes with its
  markers): the first call's check catches the conflicted test, and the merge commit is a finding of the
  commit's check and of ``judge_commits``;
- the same two-call flow of the clean history in an engineer's session (DEC-266): today's behaviour, the first
  call's check restores both tests from ``HEAD`` (recorded as ``reverted``), the second call's merge is flagged
  with nothing reverted (W1-03's default for a merge that is not a fast-forward).
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_72_support as support  # noqa: E402
from w2_72_support import guard_hook, hook, judge, project, sandbox  # noqa: E402,F401  fixtures

check_support = support.check_support

ORCHESTRATOR = support.ORCHESTRATOR
TICKET = support.TICKET
MERGED_TEST = support.MERGED_TEST
NEW_TEST = support.NEW_TEST


def _told(observed):
    return ". ".join(seen.told(f"Call {number}") for number, seen in enumerate(observed, 1))


def _committed(project, observed, before, side, what):
    """Guard: the last call exited 0 and committed the merge of ``side`` on top of ``before``. Returns the merge
    commit's id."""
    merge_id = support.full_id(project, "HEAD")
    assert observed[-1].exit_code == 0 and support.parents_of(project, merge_id) == [before, side], (
        f"the fixture is wrong: {what}: the last call did not commit the merge. {_told(observed)}"
    )
    return merge_id


def _assert_a_finding_for_the_merge(project, judge, result, merge_id, path, what):
    """The commit's check has a finding for the merge commit that names ``path``, and ``judge_commits`` on the
    merge commit alone returns one finding, for it, naming ``path``."""
    for_the_merge = support.findings_for(result, merge_id, what)
    assert any(path in check_support.finding_paths(result, f) for f in for_the_merge), (
        f"{what}: the commit's check has no finding for the merge commit {merge_id[:12]} that names {path}; "
        f"findings: {[f['reason'] for f in check_support.new_findings(result, what)]}"
    )
    findings = judge(project, [merge_id])
    assert [f.commit for f in findings] == [merge_id] and path in findings[0].paths, (
        f"{what}: judge_commits on the merge commit returns "
        f"{[(f.commit[:12], f.paths, f.reason) for f in findings]}, not one finding that names {path}"
    )


# --------------------------------------------------------------------------
# Kept: git's own merge over two calls (KPI 1, DEC-918 item 1)
# --------------------------------------------------------------------------

@pytest.mark.parametrize("case", sorted(support.TWO_CALLS), ids=sorted(support.TWO_CALLS))
def test_a_merge_back_over_two_calls_keeps_git_s_own_merge_of_the_acceptance_tests(project, sandbox, judge, case):
    """Neither call's check restores, flags or reports either test; the merge commit holds git's own merge of
    both, the tree and the index equal it, and ``judge_commits`` returns no finding for it."""
    shape = support.TWO_CALLS[case](project, sandbox)
    problems, told = support.merge_back_over_two_calls(project, sandbox, judge, shape)
    assert not problems, (
        f"{shape.what}, in the orchestrator's own calls on {TICKET} (DEC-918 item 1): " + "; ".join(problems)
        + f". {told}"
    )


# --------------------------------------------------------------------------
# Still caught: a hand write, a conflicted test, another caller (KPI 2)
# --------------------------------------------------------------------------

@pytest.mark.parametrize("case", sorted(support.HAND_WRITES), ids=sorted(support.HAND_WRITES))
def test_a_hand_write_of_an_acceptance_test_in_a_merge_over_two_calls_stays_caught(project, sandbox, judge, case):
    """The check of the call that makes the hand write catches it; the committed merge, when its test differs
    from git's own merge, is a finding of the commit's check and of ``judge_commits``."""
    support.history_of_two_calls_with_no_conflict(project, sandbox)
    flow = support.HAND_WRITES[case]
    before, side = support.full_id(project, "HEAD"), support.full_id(project, support.BRANCH)
    own = support.git_s_own_merge(project, before, side)
    assert own.conflicted == (), f"the fixture is wrong: git's own merge reports the conflicts {own.conflicted}"
    observed = [support.bash_call(project, sandbox, command, ORCHESTRATOR, TICKET) for command in flow.calls]
    what = (f"the merge of {support.BRANCH} (git combines two sides' edits of {MERGED_TEST} and brings {NEW_TEST}) "
            f"over {len(flow.calls)} calls of the orchestrator on {TICKET}: {flow.words}")
    assert all(seen.exit_code == 0 for seen in observed) and observed[0].merging == side, (
        f"the fixture is wrong: {what}. {_told(observed)}"
    )
    merge_id = _committed(project, observed, before, side, what)
    held = support.content_at(project, merge_id, MERGED_TEST)
    if flow.caught_in == len(flow.calls) - 1:
        assert 'LINE_10 = "by-hand"' in check_support.git(project, "show", f"{merge_id}:{MERGED_TEST}"), (
            f"the fixture is wrong: {what}: the merge commit does not hold the hand write"
        )
    told = _told(observed)
    check_support.assert_caught(observed[flow.caught_in].result, MERGED_TEST,
                                what=f"{what}: call {flow.caught_in + 1}, which makes the hand write. {told}")
    if held != support.content_at(project, own.tree, MERGED_TEST):
        _assert_a_finding_for_the_merge(project, judge, observed[-1].result, merge_id, MERGED_TEST,
                                        f"{what}: the merge commit's {MERGED_TEST} differs from git's own merge "
                                        f"({held}). {told}")


@pytest.mark.parametrize("resolution", support.RESOLUTIONS_OVER_TWO_CALLS, ids=support.RESOLUTIONS_OVER_TWO_CALLS)
def test_a_conflict_in_an_acceptance_test_over_two_calls_stays_caught(project, sandbox, judge, resolution):
    """Git reports the acceptance test as conflicted: the first call's check catches it, and the merge commit,
    whatever the second call stages for the test, is a finding of the commit's check and of ``judge_commits``."""
    support.history_of_a_conflict_in_the_test(project, sandbox)
    before, side = support.full_id(project, "HEAD"), support.full_id(project, support.BRANCH)
    own = support.git_s_own_merge(project, before, side)
    assert own.conflicted == (MERGED_TEST,), f"the fixture is wrong: git's own merge reports {own.conflicted}"
    resolve = support.resolution_of_the_conflicted_test(project, resolution)
    first = support.bash_call(project, sandbox, support.START_THE_MERGE, ORCHESTRATOR, TICKET)
    what = (f"the merge of {support.BRANCH} over two calls of the orchestrator on {TICKET}; both sides' test "
            f"designers changed line 2 of {MERGED_TEST}, git reports the conflict, and the second call stages "
            f"{resolution} and commits")
    assert (first.exit_code, first.merging, first.unmerged) == (1, side, (MERGED_TEST,)), (
        f"the fixture is wrong: {what}: {_told([first])}; unmerged {first.unmerged}"
    )
    second = support.bash_call(project, sandbox,
                               support.commit_the_merge(before_the_commit=f"{resolve} && git add -- {MERGED_TEST}"),
                               ORCHESTRATOR, TICKET)
    merge_id = _committed(project, [first, second], before, side, what)
    told = _told([first, second])
    check_support.assert_caught(first.result, MERGED_TEST, what=f"{what}: the first call. {told}")
    check_support.assert_caught(second.result, MERGED_TEST, what=f"{what}: the commit's call. {told}")
    _assert_a_finding_for_the_merge(project, judge, second.result, merge_id, MERGED_TEST, f"{what}. {told}")


def test_the_same_merge_over_two_calls_in_an_engineer_s_session_keeps_today_s_behaviour(project, sandbox):
    """DEC-266: only a merge in an orchestrator session's own call is judged commit by commit. In an engineer's
    session (``GOV_ROLE=engineer`` on ``DAEO-zz90``, the merge commit with the engineer's trailers), the first
    call's check restores both acceptance tests from ``HEAD`` as today, and the second call's merge is flagged
    with nothing reverted."""
    support.history_of_two_calls_with_no_conflict(project, sandbox)
    engineer = support.support.ENGINEER
    before, side = support.full_id(project, "HEAD"), support.full_id(project, support.BRANCH)
    first = support.bash_call(project, sandbox, support.START_THE_MERGE, engineer, TICKET)
    what = (f"the merge of {support.BRANCH} (git combines two sides' edits of {MERGED_TEST} and brings {NEW_TEST}) "
            f"over two calls of an engineer's session on {TICKET}")
    assert (first.exit_code, first.merging, first.unmerged) == (0, side, ()), (
        f"the fixture is wrong: {what}: {_told([first])}"
    )
    after_the_first = (check_support.read(project, MERGED_TEST), check_support.read(project, NEW_TEST),
                       check_support.porcelain_all(project, support.ACCEPTANCE))
    second = support.bash_call(project, sandbox, support.commit_the_merge(trailers=support.AS_ENGINEER),
                               engineer, TICKET)
    _committed(project, [first, second], before, side, what)
    told = _told([first, second])
    findings = check_support.assert_caught(first.result, MERGED_TEST, NEW_TEST,
                                           what=f"{what}: the first call. {told}")
    assert {f["action"] for f in findings} == {check_support.REVERTED}, (
        f"{what}: the first call's findings have the actions {[f['action'] for f in findings]}, not "
        f"{check_support.REVERTED!r} as today. {told}"
    )
    assert after_the_first == (check_support.git(project, "show", f"{before}:{MERGED_TEST}"), None, ""), (
        f"{what}: after the first call's check the tests are not as HEAD holds them ({after_the_first}). {told}"
    )
    check_support.assert_reported(second.result, what=f"{what}: the second call. {told}")
    actions = [f["action"] for f in check_support.new_findings(second.result, what)]
    assert check_support.FLAGGED in actions and check_support.REVERTED not in actions and second.kept(), (
        f"{what}: the second call's merge is not flagged with nothing reverted ({actions}; "
        f"{'' if second.kept() else second.change()}). {told}"
    )

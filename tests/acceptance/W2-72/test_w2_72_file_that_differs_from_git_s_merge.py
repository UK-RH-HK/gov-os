"""W2-72, KPI success 2 — any file that differs from git's own merge is still caught as before (DEC-918 item 1).

DEC-918 (a1): "Any file that differs from git's own merge (a hand edit, a conflict resolution) is still caught as
before." The KPI line: a hand edit of a clean merge, a conflict resolution in the file, a file git reports as
conflicted, an octopus merge, and a merge whose parents have several merge bases or none stay the merge commit's
own change.

**The cases** (each an orchestrator's merge in its own call with orchestrator trailers, as in the success file;
``assert_shape`` shows the history from git's own answers):

- a hand edit on top of a clean merge: one more line of the acceptance test changed before the commit;
- git's content of the file in another mode (``100755``): equal blob, not equal entry;
- a conflict git reports on the file (both sides changed its line 2), resolved by hand, by taking the merged
  side's version whole, by taking the first parent's version whole, or held exactly as git's own merge writes
  it, with its conflict markers: git reports the conflict, so it is no clean merge of the file;
- an octopus merge (three parents) of clean edits of the file: DEC-912's merge is of two parents;
- a criss-cross history (two merge bases), whose merge commit holds git's own clean merge of the file;
- unrelated histories (no merge base), whose merge commit holds git's own clean merge of the file
  (``git merge-tree --write-tree --allow-unrelated-histories``).

In each, the live check flags the acceptance test in a finding for the merge commit and moves nothing, and
``judge_commits`` on the merge commit alone returns one finding that names it.

Red reason now: none; every case passes today (DEC-410 DP-24, DP-23 and DP-27 read each as the merge commit's own
change) and must keep passing: a fix that lifts more than git's own clean two-parent merge on one merge base
fails them.
"""

from __future__ import annotations

import pytest

import w2_72_support as support

check_support = support.check_support

ORCHESTRATOR = support.ORCHESTRATOR
TICKET = support.TICKET


@pytest.mark.parametrize("case", sorted(support.FAILURE), ids=sorted(support.FAILURE))
def test_the_live_check_still_flags_an_acceptance_file_that_differs_from_git_s_own_merge(project, sandbox, call,
                                                                                         case):
    """The check reports and records the acceptance test as flagged, in a finding for the merge commit, and
    moves nothing."""
    shape = support.FAILURE[case](project, sandbox)
    before = support.full_id(project, "HEAD")
    result, left = call(project, shape.command, ORCHESTRATOR, TICKET)
    merge_id = support.full_id(project, "HEAD")
    support.assert_shape(project, shape, before, merge_id)
    what = f"{shape.what}, in the orchestrator's own call on {TICKET}"
    check_support.assert_caught(result, shape.path, what=what, action=check_support.FLAGGED)
    for_the_merge = support.findings_for(result, merge_id, what)
    assert any(shape.path in check_support.finding_paths(result, f) for f in for_the_merge), (
        f"{what}: no finding for the merge commit {merge_id[:12]} names {shape.path}; findings: "
        f"{[f['reason'] for f in check_support.new_findings(result, what)]}"
    )
    check_support.assert_left_as_the_call_left_it(project, left, what)


@pytest.mark.parametrize("case", sorted(support.FAILURE), ids=sorted(support.FAILURE))
def test_judge_commits_still_finds_an_acceptance_file_that_differs_from_git_s_own_merge(project, sandbox, judge,
                                                                                        case):
    """``judge_commits`` on the merge commit alone returns one finding, for it, that names the acceptance test."""
    shape = support.FAILURE[case](project, sandbox)
    before = support.full_id(project, "HEAD")
    support.support.run(project, sandbox, shape.command)
    merge_id = support.full_id(project, "HEAD")
    support.assert_shape(project, shape, before, merge_id)
    findings = judge(project, [merge_id])
    assert [f.commit for f in findings] == [merge_id] and shape.path in findings[0].paths, (
        f"{shape.what}: judge_commits on the merge commit returns "
        f"{[(f.commit[:12], f.paths, f.reason) for f in findings]}, not one finding that names {shape.path}"
    )

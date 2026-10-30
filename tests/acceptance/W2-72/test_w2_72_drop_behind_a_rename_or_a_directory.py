"""W2-72, review 1, F2 and F3 — a drop hidden behind a rename or a file replaced by a directory stays caught.

DEC-918 item 1: "Any file that differs from git's own merge (a hand edit, a conflict resolution) is still caught
as before." The KPI line: a conflict resolution in the file and a file git reports as conflicted stay the merge
commit's own change. Git's own merge is read for the test whatever its names: the new name of a rename, and the
moved-aside name (``<path>~<commit>``) under which git reports a conflict when a directory took the file's place.

**F2, a rename on the first parent.** A test designer renamed the acceptance test on ``main`` (``git mv``) and
the merged side changed one of its lines:

- *a clean rename*: git's own merge is clean, with the merged side's edit at the new name; the merge commit
  instead holds ``main``'s renamed file whole (the merged side's edit dropped);
- *a conflict at the new name*: ``main`` changed the same line in its rename, so git reports a conflict at the new
  name; it is resolved by taking ``main``'s version whole.

**F3, a file replaced by a directory.** The base holds the acceptance test; one side deletes it and adds a
directory of the same name holding one file (a test designer's commit); the other side changes one of its lines.
Git reports the conflict only under the moved-aside name. The merge commit keeps the directory and drops the
moved-aside edited copy, in both directions:

- the directory on ``main``: the merged side's edit dropped;
- the directory on the merged side: ``main``'s edit dropped.

Each merge is an orchestrator's in its own call with orchestrator trailers (DEC-266); ``assert_moved_shape`` shows
the history from git's own answers: the conflicts git's own merge reports, that the merge commit does not hold
git's own merge of the folder, and which side's version of the folder it holds whole. Expected: the live check
reports and records the drop as flagged, in a finding for the merge commit that names at least one path of the
test (its old or new name, the directory's file, or the moved-aside name), and moves nothing; ``judge_commits`` on
the merge commit alone returns one finding, for it, naming such a path.

Red reason now: both checks are silent on all four: the drop passes as git's own merge.
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


@pytest.mark.parametrize("case", sorted(support.DROPPED), ids=sorted(support.DROPPED))
def test_the_live_check_flags_a_drop_behind_a_rename_or_a_directory(project, sandbox, call, case):
    """Reported and recorded as flagged, in a finding for the merge commit that names a path of the test;
    nothing moved."""
    shape = support.DROPPED[case](project, sandbox)
    before = support.full_id(project, "HEAD")
    result, left = call(project, shape.command, ORCHESTRATOR, TICKET)
    merge_id = support.full_id(project, "HEAD")
    support.assert_moved_shape(project, shape, before, merge_id)
    what = f"{shape.what}, in the orchestrator's own call on {TICKET}"
    findings = check_support.new_findings(result, what)
    assert result.outcome == "report" and any(path in result.report for path in shape.paths), (
        f"{what}: the agent is told nothing of {shape.paths}: {result.describe()}; findings: "
        f"{[(f['paths'], f['action'], f['reason']) for f in findings]}"
    )
    for_the_merge = support.findings_for(result, merge_id, what)
    named = [path for f in for_the_merge for path in check_support.finding_paths(result, f)
             if support.is_the_test_s(path, shape.paths)]
    assert named and all(f["action"] == check_support.FLAGGED for f in for_the_merge), (
        f"{what}: no finding for the merge commit {merge_id[:12]}, flagged, names a path of the test "
        f"{shape.paths}; findings: {[(f['paths'], f['action'], f['reason']) for f in findings]}"
    )
    check_support.assert_left_as_the_call_left_it(project, left, what)


@pytest.mark.parametrize("case", sorted(support.DROPPED), ids=sorted(support.DROPPED))
def test_judge_commits_finds_a_drop_behind_a_rename_or_a_directory(project, sandbox, judge, case):
    """``judge_commits`` on the merge commit alone returns one finding, for it, naming a path of the test."""
    shape = support.DROPPED[case](project, sandbox)
    before = support.full_id(project, "HEAD")
    support.support.run(project, sandbox, shape.command)
    merge_id = support.full_id(project, "HEAD")
    support.assert_moved_shape(project, shape, before, merge_id)
    findings = judge(project, [merge_id])
    assert [f.commit for f in findings] == [merge_id] and any(
        support.is_the_test_s(path, shape.paths) for path in findings[0].paths), (
        f"{shape.what}: judge_commits on the merge commit returns "
        f"{[(f.commit[:12], f.paths, f.reason) for f in findings]}, not one finding that names a path of the "
        f"test {shape.paths}"
    )

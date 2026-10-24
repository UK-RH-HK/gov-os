"""W2-72, KPI success 3 — nothing else changes (DEC-918 item 4).

The KPI line: "Nothing else changes: ticket files keep DEC-421's and DEC-572's rule, every other path keeps
read_merge's rule, and the approval check's reading of merges is unchanged."

**Ticket files (DEC-421).** Orchestrator's commits changed one ticket file on both sides (a line near its top on
``main``, a line appended on the merged side) and git combined them without a conflict; the merge commit holds
exactly git's own merge of it. It stays the merge commit's own change: the live check flags it and
``judge_commits`` returns a finding naming it. DEC-918 speaks of ``tests/acceptance/`` only. The other half of
the ticket files' rule, DEC-572's lift for a ticket file held exactly as one parent has it, is shown by W1-50's
cases, unchanged (``test_w1_50_merge_commit_file_that_equals_one_parent_s_version.py``).

**Every other path (read_merge's rule, DEC-269).** ``README.md`` is cleanly combined by git from two sides'
orchestrator commits; the merge commit, made in the orchestrator's own call, carries an engineer's trailers whose
ticket does not allow ``README.md``. The path is the merge commit's own change by ``read_merge`` and is judged by
the merge commit's trailers, as before: flagged, and a finding of ``judge_commits``. A fix that lifts git's own
merge for every path, not only under ``tests/acceptance/``, fails here.

**The approval check's reading (read_merge).** For every merge of this suite, ``read_merge``'s answer is exactly
what it is today: ``own`` and ``brought`` as DEC-410 (DP-21 to DP-24) and DEC-403 give them. In particular an
acceptance test git merged cleanly is still in ``own``: DEC-918 changes containment's use of the reading, not
the reading (``src/gov/decisions/checker.py`` is not changed).

Red reason now: none; every case passes today and must keep passing.
"""

from __future__ import annotations

import pytest

import w2_72_support as support

check_support = support.check_support

ORCHESTRATOR = support.ORCHESTRATOR
TICKET = support.TICKET


@pytest.mark.parametrize("case", sorted(support.UNCHANGED), ids=sorted(support.UNCHANGED))
def test_the_live_check_still_flags_a_clean_merge_of_a_path_outside_the_acceptance_tests(project, sandbox, call,
                                                                                         case):
    shape = support.UNCHANGED[case](project, sandbox)
    before = support.full_id(project, "HEAD")
    result, left = call(project, shape.command, ORCHESTRATOR, TICKET)
    merge_id = support.full_id(project, "HEAD")
    support.assert_shape(project, shape, before, merge_id)
    what = f"{shape.what}, in the orchestrator's own call on {TICKET}"
    check_support.assert_caught(result, shape.path, what=what, action=check_support.FLAGGED)
    for_the_merge = support.findings_for(result, merge_id, what)
    assert any(shape.path in check_support.finding_paths(result, f) for f in for_the_merge), (
        f"{what}: no finding for the merge commit {merge_id[:12]} names {shape.path}"
    )
    check_support.assert_not_recorded(result, support.ALSO, what=what)
    check_support.assert_left_as_the_call_left_it(project, left, what)


@pytest.mark.parametrize("case", sorted(support.UNCHANGED), ids=sorted(support.UNCHANGED))
def test_judge_commits_still_finds_a_clean_merge_of_a_path_outside_the_acceptance_tests(project, sandbox, judge,
                                                                                        case):
    shape = support.UNCHANGED[case](project, sandbox)
    before = support.full_id(project, "HEAD")
    support.support.run(project, sandbox, shape.command)
    merge_id = support.full_id(project, "HEAD")
    support.assert_shape(project, shape, before, merge_id)
    findings = judge(project, [merge_id])
    assert [f.commit for f in findings] == [merge_id] and shape.path in findings[0].paths, (
        f"{shape.what}: judge_commits on the merge commit returns "
        f"{[(f.commit[:12], f.paths, f.reason) for f in findings]}, not one finding that names {shape.path}"
    )
    assert support.ALSO not in findings[0].paths, f"{shape.what}: the finding names {support.ALSO}"


@pytest.mark.parametrize("case", sorted(support.EVERY_MERGE), ids=sorted(support.EVERY_MERGE))
def test_read_merge_reads_every_merge_of_this_suite_as_it_does_today(project, sandbox, read_merge, case):
    """``own`` and ``brought`` of the merge commit are exactly today's. With several merge bases or none, every
    path that differs from any parent is ``own`` (DP-23): for the unrelated histories, every path of the tree."""
    shape = support.EVERY_MERGE[case](project, sandbox)
    before = support.full_id(project, "HEAD")
    support.support.run(project, sandbox, shape.command)
    merge_id = support.full_id(project, "HEAD")
    support.assert_shape(project, shape, before, merge_id)
    reading = read_merge(project, merge_id)
    own = support.expected_own(project, shape, merge_id)
    assert (list(reading.own), list(reading.brought)) == (own, sorted(shape.brought)), (
        f"read_merge on {shape.what}: (own, brought) is ({reading.own!r}, {reading.brought!r}), not "
        f"({own!r}, {sorted(shape.brought)!r}): the approval check's reading of merges is to stay as it is "
        f"(DEC-918 item 4)"
    )

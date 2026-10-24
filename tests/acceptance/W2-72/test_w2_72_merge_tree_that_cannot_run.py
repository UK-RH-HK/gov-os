"""W2-72, KPI success 2 — a merge-tree run that cannot run gives no allowance: the path stays caught (DEC-918).

The KPI line: "a merge-tree run that cannot run gives no allowance (fails closed)".

**The seam.** A ``git`` put first on ``PATH`` (``w2_72_support.failing_merge_tree``) fails every call whose
words hold ``merge-tree`` and passes every other call to the real git, unchanged. It fails in one of two ways:

- ``a-fatal-error``: exit 128 and a ``fatal:`` line, as git fails when it cannot run a command;
- ``a-git-without-write-tree``: exit 129 and a usage line, as a git older than 2.38 answers ``--write-tree``.

Each refused call adds one line to a log file in the test's own temporary folder.

**The history** is the clean combination of the success file: without the seam, the merge commit holds exactly
git's own merge of the acceptance test and is no change of it. With the seam:

- the live check runs with the failing ``git`` first on its ``PATH`` (only the PostToolUse hook: the call itself
  and the PreToolUse hook use the real git) and must still flag the test in a finding for the merge commit;
- ``judge_commits`` runs in a new Python process of this worktree's ``src`` with the failing ``git`` first on its
  ``PATH`` (a new process, so that nothing a module resolved earlier in the test run reaches past the seam) and
  must return one finding for the merge commit that names the test.

**How each case shows that the check met the failure:** the log holds at least one refused ``merge-tree`` call
made by the check under test (the hook run, or the judging process). A check that never asks git's own merge
leaves the log empty and the case fails: it would show nothing about failing closed.

Red reason now: the log stays empty (today's check asks no ``merge-tree``); the flag and the finding are there
already (DEC-410 DP-24).
"""

from __future__ import annotations

import json

import pytest

import w2_72_support as support

check_support = support.check_support

ORCHESTRATOR = support.ORCHESTRATOR
TICKET = support.TICKET


def _assert_met(shim, who):
    refused = shim.refused()
    assert refused and all("merge-tree" in line for line in refused), (
        f"{who} never ran `git merge-tree` while it could not run (exit {shim.exit_code}): the log of refused "
        f"calls is empty, so this case shows nothing about failing closed"
    )


@pytest.mark.parametrize("case", sorted(support.CANNOT_RUN), ids=sorted(support.CANNOT_RUN))
def test_the_live_check_still_flags_the_file_when_git_merge_tree_cannot_run(project, sandbox, call, tmp_path, case):
    shape = support.clean_combination(project, sandbox)
    shim = support.failing_merge_tree(tmp_path / "failing-git", case)
    before = support.full_id(project, "HEAD")
    result, left = call(project, shape.command, ORCHESTRATOR, TICKET,
                        check_environment={"PATH": shim.path_variable()})
    merge_id = support.full_id(project, "HEAD")
    support.assert_shape(project, shape, before, merge_id)
    what = f"{shape.what}, in the orchestrator's own call on {TICKET}, `git merge-tree` failing ({case})"
    _assert_met(shim, "the live check")
    check_support.assert_caught(result, shape.path, what=what, action=check_support.FLAGGED)
    for_the_merge = support.findings_for(result, merge_id, what)
    assert any(shape.path in check_support.finding_paths(result, f) for f in for_the_merge), (
        f"{what}: no finding for the merge commit {merge_id[:12]} names {shape.path}"
    )
    check_support.assert_left_as_the_call_left_it(project, left, what)


@pytest.mark.parametrize("case", sorted(support.CANNOT_RUN), ids=sorted(support.CANNOT_RUN))
def test_judge_commits_still_finds_the_file_when_git_merge_tree_cannot_run(project, sandbox, tmp_path, case):
    shape = support.clean_combination(project, sandbox)
    before = support.full_id(project, "HEAD")
    support.support.run(project, sandbox, shape.command)
    merge_id = support.full_id(project, "HEAD")
    support.assert_shape(project, shape, before, merge_id)
    shim = support.failing_merge_tree(tmp_path / "failing-git", case)
    proc = support.judge_in_a_process(project, [merge_id], {"PATH": shim.path_variable()})
    what = f"{shape.what}, judged with `git merge-tree` failing ({case})"
    _assert_met(shim, "judge_commits")
    assert proc.returncode == 0, (
        f"{what}: judge_commits did not return findings; the path is to stay caught as a finding: "
        f"exit {proc.returncode}, {proc.stderr.strip()[-800:]!r}"
    )
    findings = json.loads(proc.stdout.strip().splitlines()[-1])
    assert [commit for commit, _, _ in findings] == [merge_id] and shape.path in findings[0][1], (
        f"{what}: judge_commits on the merge commit returns {findings}, not one finding that names {shape.path}"
    )

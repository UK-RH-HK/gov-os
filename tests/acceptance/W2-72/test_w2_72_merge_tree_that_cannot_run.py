"""W2-72, KPI success 2 — a merge-tree run that cannot run gives no allowance: the path stays caught (DEC-918).

The KPI line: "a merge-tree run that cannot run gives no allowance (fails closed)".

**The seam** (Rewrite-Reason: DEC-802 (P-B1-2)). Containment takes git by absolute path from the system's own
folders, the tuple ``gov.util.gitenv.GIT_DIRS`` read at each call, never by name from the inherited ``PATH``; a
``git`` first on ``PATH`` (these cases' seam before) is no longer started. So the process that runs the check names,
in ``GIT_DIRS``, a folder holding a ``git`` of the case's own (``w2_72_support.git_seam``), and ``git merge-tree
--write-tree`` fails in one of two ways:

- ``a-fatal-error``: the real git fails. The merge base's blob of the test is taken out of the object store
  (``remove_the_merge_base_s_blob``; no tree of the merge commit or of its parents holds it), so git answers
  ``fatal: unable to read blob object <id>`` and 128. The folder's ``git`` only records: it passes every call to
  the real git by its absolute path;
- ``a-git-without-write-tree``: the folder's ``git`` answers ``merge-tree --write-tree`` with 129 and a usage line,
  as a git older than 2.38 answers, and passes every other call to the real git by its absolute path.

Either way the folder's ``git`` logs each ``merge-tree`` call it answered, with the exit code and git's ``fatal:``
line on stderr (past any ``hint:``), or the stand-in's usage line.

**The history** is the clean combination of the success file: with git's own merge there, the merge commit holds
exactly git's own merge of the acceptance test and is no change of it. Then:

- the live check: only the PostToolUse hook's process gets the folder (a ``sitecustomize`` first on its
  ``PYTHONPATH`` sets ``GIT_DIRS`` before the hook runs, as W1-03's ``clock`` sets its clock); the call itself and
  the PreToolUse hook use the real git. For ``a-fatal-error`` the blob is taken out after the call's command and
  before the check. The test must still be flagged in a finding for the merge commit;
- ``judge_commits`` runs in a new Python process of this worktree's ``src`` that sets ``GIT_DIRS`` before it
  imports containment (a new process, so that nothing a module resolved earlier in the test run reaches past the
  seam). First the control: through a recording git with nothing failing, it asks git's own merge (answered 0) and
  returns no finding. Then, with merge-tree failing, it must return one finding for the merge commit that names the
  test.

**How each case shows that the check met the failure:** the log holds at least one ``merge-tree --write-tree`` call
made by the check under test (the hook run, or the judging process), and every one was answered as the case fails
it: 128 with a ``fatal:`` line naming the missing blob, or 129 with the usage line. A check that never asks git's
own merge, or takes git from elsewhere, leaves the log empty and the case fails: it would show nothing about failing
closed.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_72_support as support  # noqa: E402
from w2_72_support import call, guard_hook, hook, project, sandbox  # noqa: E402,F401  fixtures

check_support = support.check_support

ORCHESTRATOR = support.ORCHESTRATOR
TICKET = support.TICKET


def _assert_met(seam, who, what, missing=None, installed=None):
    """The check under test asked ``git merge-tree --write-tree`` through the case's ``git``, and each such call
    was answered as the case fails it: 128 and a ``fatal:`` line naming ``missing`` (the real git), or 129 and the
    usage line (the stand-in)."""
    answered = seam.answered()
    seen = "\n".join(f"  exit {a.exit_code}: {a.stderr!r} <- git {a.words}" for a in answered) or "  (none)"
    assert answered, (
        f"{what}: {who} never ran `git merge-tree` through the git of {seam.directory.name} (named in "
        f"gov.util.gitenv.GIT_DIRS): the log of answered calls is empty, so this case shows nothing about failing "
        f"closed" + (f"\nthe hook process's sitecustomize: {installed}" if installed else "")
    )
    assert all("--write-tree" in a.words.split() for a in answered), (
        f"{what}: {who}'s merge-tree calls are not `--write-tree` calls:\n{seen}"
    )
    if missing:
        met = all(a.exit_code == 128 and a.stderr.startswith("fatal:") and missing in a.stderr for a in answered)
        expected = f"128 and a `fatal:` line naming the missing blob {missing[:12]}"
    else:
        met = all(a.exit_code == seam.exit_code and a.stderr == support.USAGE for a in answered)
        expected = f"{seam.exit_code} and the usage line"
    assert met, f"{what}: {who}'s `git merge-tree --write-tree` was not answered with {expected}:\n{seen}"


@pytest.mark.parametrize("case", sorted(support.CANNOT_RUN), ids=sorted(support.CANNOT_RUN))
def test_the_live_check_still_flags_the_file_when_git_merge_tree_cannot_run(project, sandbox, call, tmp_path, case):
    """Rewrite-Reason: DEC-802 (P-B1-2): containment takes git by absolute path, so a ``git`` first on the hook's
    ``PATH`` no longer reaches merge-tree. The hook process's ``GIT_DIRS`` names the case's ``git`` now; for
    ``a-fatal-error`` the real git fails, on the merge base's missing blob. Expected as before: the failing
    merge-tree was met, the test is flagged in a finding for the merge commit, and nothing moved."""
    shape = support.clean_combination(project, sandbox)
    seam = support.git_seam(tmp_path / "the-check-s-git", case)
    before = support.full_id(project, "HEAD")
    missing = []

    def before_the_check():
        merge_id = support.full_id(project, "HEAD")
        support.assert_shape(project, shape, before, merge_id)   # git's own merge, read while it still runs
        if case == "a-fatal-error":
            missing.append(support.remove_the_merge_base_s_blob(project, merge_id, shape.path))

    result, left = call(project, shape.command, ORCHESTRATOR, TICKET,
                        check_environment=seam.hook_environment(), before_the_check=before_the_check)
    merge_id = support.full_id(project, "HEAD")
    what = f"{shape.what}, in the orchestrator's own call on {TICKET}, `git merge-tree` failing ({case})"
    _assert_met(seam, "the live check", what, missing=missing[0] if missing else None, installed=seam.installed())
    check_support.assert_caught(result, shape.path, what=what, action=check_support.FLAGGED)
    for_the_merge = support.findings_for(result, merge_id, what)
    assert any(shape.path in check_support.finding_paths(result, f) for f in for_the_merge), (
        f"{what}: no finding for the merge commit {merge_id[:12]} names {shape.path}"
    )
    check_support.assert_left_as_the_call_left_it(project, left, what)


@pytest.mark.parametrize("case", sorted(support.CANNOT_RUN), ids=sorted(support.CANNOT_RUN))
def test_judge_commits_still_finds_the_file_when_git_merge_tree_cannot_run(project, sandbox, tmp_path, case):
    """Rewrite-Reason: DEC-802 (P-B1-2): containment takes git by absolute path, so a ``git`` first on the judging
    process's ``PATH`` no longer reaches merge-tree. That process sets ``GIT_DIRS`` to the case's ``git`` now; for
    ``a-fatal-error`` the real git fails, on the merge base's missing blob. The control (nothing failing: merge-tree
    answered 0, no finding) is new. Expected as before: the failing merge-tree was met, the process exits 0, and one
    finding, for the merge commit, names the test."""
    shape = support.clean_combination(project, sandbox)
    before = support.full_id(project, "HEAD")
    support.support.run(project, sandbox, shape.command)
    merge_id = support.full_id(project, "HEAD")
    support.assert_shape(project, shape, before, merge_id)

    control = support.git_seam(tmp_path / "the-control-s-git", support.NOTHING_FAILING)
    proc = support.judge_in_a_process(project, [merge_id], git_dirs=[control.directory])
    assert proc.returncode == 0 and json.loads(proc.stdout.strip().splitlines()[-1]) == [], (
        f"{shape.what}: the control: with nothing failing, judge_commits on the merge commit is to find nothing "
        f"(KPI 1): exit {proc.returncode}, {proc.stdout.strip()[-400:]!r} {proc.stderr.strip()[-800:]!r}"
    )
    assert control.answered() and all(a.exit_code in (0, 1) for a in control.answered()), (
        f"{shape.what}: the control: judge_commits asked no `git merge-tree` through the git GIT_DIRS names, or "
        f"git failed it: {control.answered()}"
    )

    seam = support.git_seam(tmp_path / "the-check-s-git", case)
    missing = (support.remove_the_merge_base_s_blob(project, merge_id, shape.path)
               if case == "a-fatal-error" else None)
    proc = support.judge_in_a_process(project, [merge_id], git_dirs=[seam.directory])
    what = f"{shape.what}, judged with `git merge-tree` failing ({case})"
    _assert_met(seam, "judge_commits", what, missing=missing)
    assert proc.returncode == 0, (
        f"{what}: judge_commits did not return findings; the path is to stay caught as a finding: "
        f"exit {proc.returncode}, {proc.stderr.strip()[-800:]!r}"
    )
    findings = json.loads(proc.stdout.strip().splitlines()[-1])
    assert [commit for commit, _, _ in findings] == [merge_id] and shape.path in findings[0][1], (
        f"{what}: judge_commits on the merge commit returns {findings}, not one finding that names {shape.path}"
    )

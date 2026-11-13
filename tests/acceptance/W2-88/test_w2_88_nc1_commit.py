"""Run 6 (P1-W2-88-NC-1 (a)): NC-1, A9's own record commit is refused, and NC-2, an interrupt inside the copy step (success-16; Case C
is reached through success-3's refusals too).

The narrow independent check after review round 2 (``docs/probes/DAEO-2bdu/PR-DAEO-2bdu.md`` at ``01ec6d2a7``) found that run 5's undo
(``test_w2_88_rv2_undo.py``) missed two paths. The interface (the lead's statement of NC-1 and NC-2, the owner's decision
P1-W2-88-NC-1 (a); "the start commit" is the commit HEAD named when A9 began, before its copy step; run 5's interface, RV2-1 items 1
to 6 and ``HEAD_MOVED``, stands unchanged):

NC-1. A9's last act is one commit holding its copies and its record (``governance/adoption/A9-<title>.md``). W2-23's ``project.commit``
and ``project.restore`` are not on A9's path and stay unchanged.
  1. When that commit is refused (git commit exits non-zero: a ``pre-commit`` or ``commit-msg`` hook, commit signing), or the record's
     write or ``git add`` fails, or an interrupt comes during it: **no ``git reset --hard``, no checkout**. A9's undo runs as run 5's
     items 1 to 5 state it, with A9's record counted among what A9 wrote and staged (unstaged only while its index entry is still the
     blob A9 staged, deleted only while its bytes are still A9's; A9's copies likewise).
  2. A tracked file edited during the run keeps its edit; a file staged during the run stays staged; an untracked file made during the
     run stays; HEAD and the branch do not move; the reflog gains no ``reset``.
  3. Where HEAD did not move A9 is refused ``ADOPT_GIT_FAILED``: the message names the refused ``git commit`` and carries git's own error
     text (a hook's message is in it), ``details.exit_code`` is the commit's exit code (1 for a refusing hook); ``gov adopt`` exits as for any
     refusal (the lead wrote "2"; every refusal of this suite exits 1, 2 being argparse's usage error: read as "as any refusal") with
     ``ok: false``. Where HEAD moved, ``HEAD_MOVED`` holds with ``cause: "ADOPT_GIT_FAILED"``. An interrupt stays an interrupt.
  4. When the commit succeeds nothing changes (one commit, ``gov adopt --lite A9: <title>``); an untracked file at the record's path is
     still refused ``ADOPT_WOULD_OVERWRITE`` before anything is written there, and that refusal runs A9's undo too.

NC-2. An interrupt (or any exception) at **any point after A9's ``git add`` of its copies has begun** leaves none of A9's copies in the
index (and, as run 5, none in the tree where the bytes are still A9's; a replaced tracked file gets its start-commit content back). An
index entry whose blob is the blob of A9's own bytes for that path counts as staged by A9.

The plants (A9 in a child process on a fork of the planted adoption at A8, the suite's A9 cases):

* **Case C** (``standin_nc1/``): a ``pre-commit`` hook in the planted repository's ``.git/hooks/`` (installed after A8's commit, so only
  A9's record commit meets it) writes a marker file outside the repository, prints a unique word to stderr and exits 1. A stand-in for
  ``gov.rebuild.command.run`` rewrites the tracked ``docs/notes.txt`` (not staged) and stages a new ``staged-during-run.md``, then calls
  the real rebuild, so A9 reaches its record commit.
* **Case D** (``standin_nc2/``): a ``sitecustomize`` wrapping ``subprocess.Popen`` lets the first ``git`` call whose arguments hold ``add``
  and a path of A9's copy plan run to its end and raises ``KeyboardInterrupt`` the moment it returns to its caller. It reports on stderr
  that it fired; a case where it never fired fails as "the plant did not take".
"""

from __future__ import annotations

import json
import os
import shlex

import pytest

import w2_88_support as W
from test_w2_88_rv2_undo import TARGETS, EDITED, EDITED_BYTES, STAGED, folders, indexed, porcelain, assert_interrupt

STANDIN_C = W.HERE / "standin_nc1"
STANDIN_D = W.HERE / "standin_nc2"
HOOK_WORD = "quokka-refuses-the-record-commit-9c1e"
RECORD_DIR = "governance/adoption"
RETRIEVAL = W.RETRIEVAL_REL


def stderr_line(run, prefix: str, why: str) -> dict:
    lines = [line for line in run.stderr.splitlines() if line.startswith(prefix + ": ")]
    assert lines, f"the plant did not take: no `{prefix}` line on stderr ({why})\n{run.describe()}"
    return json.loads(lines[-1].split(": ", 1)[1])


def record_paths(project) -> tuple:
    """(in the tree, in the index): A9's record, the file under ``governance/adoption/`` named ``A9-...`` (A1 to A8 have their own)."""
    folder = project / RECORD_DIR
    in_tree = sorted(p.name for p in folder.glob("A9*")) if folder.is_dir() else []
    in_index = sorted(n for n in indexed(project) if n.startswith(f"{RECORD_DIR}/A9"))
    return in_tree, in_index


def assert_none_of_a9(project, targets, folders_before, what: str) -> None:
    """None of A9's copies is in the tree or in the index, and no folder A9 made is left."""
    left = [t for t in targets if (project / t).exists()]
    assert not left, f"{what}: A9's copies are left in the tree: {left}"
    staged = [t for t in targets if t in indexed(project)]
    assert not staged, f"{what}: A9's copies are left in the index: {staged}"
    made = sorted(folders(project) - folders_before)
    assert not made, f"{what}: folders A9 made are left (an empty folder is deleted): {made}"


def plant_hook(project, marker) -> None:
    """A ``pre-commit`` hook that notes it ran (a file outside the repository), prints a unique word to stderr and refuses."""
    hook = project / ".git" / "hooks" / "pre-commit"
    hook.parent.mkdir(parents=True, exist_ok=True)
    hook.write_text(f"#!/bin/sh\necho ran >> {shlex.quote(str(marker))}\necho {HOOK_WORD} >&2\nexit 1\n", encoding="utf-8")
    hook.chmod(0o755)


# ---- Case C: A9's own record commit is refused by a hook --------------------------------------------------------------------------

def test_s16_nc1_c_a_refused_record_commit_resets_nothing_and_a9_takes_back_only_its_copies_and_its_record(worlds):
    """NC-1 (items 1, 2, 3): a refusing ``pre-commit`` hook; during the run a tracked file is rewritten (not staged) and a new file is
    staged; A9 reaches its record commit and is refused. Afterwards: the refusal is ``ADOPT_GIT_FAILED`` (exit 2, ``ok: false``),
    ``details.exit_code == 1``, the message names the ``git commit`` and holds the hook's word; HEAD is the start commit on its branch;
    no reflog entry since the start is a ``reset``; the edited file holds the edited bytes; the new file is still staged (``git diff
    --cached --name-status`` is exactly that file); none of A9's copies and not A9's record is in the tree or the index; no folder A9
    made is left; ``git status --porcelain --untracked-files=all`` shows exactly the edit and the staged file."""
    nine = worlds.a9("a8-for-forks", run_a9=False)
    nine.need_chain()
    adoption = W.fork(nine, "nc1-c-hook")
    project = adoption.project
    marker = adoption.box.base / "nc1-hook-ran.txt"
    plant_hook(project, marker)
    start = W.head(project)
    reflog_before = W.git(project, "reflog", "--format=%gs").splitlines()
    folders_before = folders(project)
    adoption.extra_env.update({"PYTHONPATH": f"{STANDIN_C}{os.pathsep}{W.SRC}", "W2_88_NC1_COPIES": json.dumps(TARGETS)})
    run = adoption.a9(adoption.box.base / "nc1-c-out")
    W.assert_offered(run, "A9")

    # the plant took: the stand-in ran with A9's copies written and staged, the real rebuild returned (A9 went on to its record commit),
    # and the hook, which only A9's record commit meets, ran
    seen = stderr_line(run, "nc1-standin", "A9 did not reach the rebuild, or did not call it in this process, I3")
    assert seen["head"] == start, f"HEAD was {seen['head']} when the rebuild began, the start commit is {start}"
    assert seen["in_tree"] == TARGETS and seen["in_index"] == TARGETS, \
        ("the copy step had not written and staged every kernel file when the rebuild began: "
         f"in the tree {sorted(set(TARGETS) - set(seen['in_tree']))} missing, in the index {sorted(set(TARGETS) - set(seen['in_index']))} missing")
    stderr_line(run, "nc1-standin-returned", "the real rebuild did not return: A9 never reached its record commit")
    assert marker.is_file(), f"the plant did not take: the pre-commit hook never ran (A9 made no commit)\n{run.describe()}"

    W.assert_refused(run, "ADOPT_GIT_FAILED", "A9's record commit was refused by a pre-commit hook")
    error = run.error
    assert run.returncode == 1, (f"gov adopt exits {run.returncode}; a refusal exits as every other refusal of gov adopt does, 1 "
                                 f"(exit 2 is argparse's usage error: W.assert_refused)\n{run.describe()}")
    assert error.get("code") == "ADOPT_GIT_FAILED", f"the refusal is {error.get('code')!r}, not ADOPT_GIT_FAILED (HEAD did not move)\n{run.describe()}"
    message = str(error.get("message", ""))
    assert "commit" in message.lower(), f"the message does not name the refused git commit: {message!r}"
    assert HOOK_WORD in message, f"the message does not carry git's own error text (the hook's word {HOOK_WORD!r} is not in it): {message!r}"
    details = error.get("details") or {}
    assert details.get("exit_code") == 1, f"details.exit_code is {details.get('exit_code')!r}, the refused commit's exit code is 1 (details: {details})"

    assert W.head(project) == start, f"the branch moved from the start commit {start} to {W.head(project)}"
    assert W.git(project, "symbolic-ref", "--short", "HEAD").strip() == "main", "HEAD is no longer on the branch"
    edited = (project / EDITED).read_text(encoding="utf-8") if (project / EDITED).is_file() else None
    assert edited == EDITED_BYTES, f"the edit made during the run to the tracked {EDITED} was thrown away (it holds {edited!r})"
    assert (project / STAGED).is_file(), f"{STAGED}, a new file made and staged during the run, was deleted from the tree"
    assert W.git(project, "diff", "--cached", "--name-status").splitlines() == [f"A\t{STAGED}"], \
        ("the index is not the new file staged during the run alone: "
         f"{W.git(project, 'diff', '--cached', '--name-status').splitlines()} (the staged file lost, or A9's copies or record left)")
    now = W.git(project, "reflog", "--format=%gs").splitlines()
    assert now[len(now) - len(reflog_before):] == reflog_before, "the reflog's older entries changed"
    fresh = now[:len(now) - len(reflog_before)]
    assert not [entry for entry in fresh if "reset" in entry.lower()], f"A9's undo reset the branch (the reflog since the run began): {fresh}"
    assert_none_of_a9(project, TARGETS, folders_before, "after the refused record commit")
    in_tree, in_index = record_paths(project)
    assert not in_tree, f"A9's record is left in the tree: {in_tree}"
    assert not in_index, f"A9's record is left in the index: {in_index}"
    assert porcelain(project) == [f" M {EDITED}", f"A  {STAGED}"], \
        f"git status --porcelain is {porcelain(project)}, exactly the edit and the staged file expected"


# ---- Case D: an interrupt the moment A9's `git add` of its copies returns -----------------------------------------------------------

@pytest.mark.parametrize("tracked", ["retrieval-tracked", "retrieval-not-tracked"])
def test_s16_nc2_d_an_interrupt_the_moment_the_git_add_of_the_copies_returns_leaves_no_copy_in_the_index_or_the_tree(worlds, tracked):
    """NC-2: ``KeyboardInterrupt`` is raised the moment A9's ``git add`` of its copies has returned (the call is let run to its end). The
    interrupt stays an interrupt (non-zero exit, ``KeyboardInterrupt`` in stderr, no ``HEAD_MOVED``); HEAD is the start commit; none of A9's
    copies is in the index or the tree (``governance/project/retrieval.yaml`` too, in the second parameter, where the repository tracks
    none and A9 installs Gov OS's); ``git status --porcelain --untracked-files=all`` is empty."""
    if tracked == "retrieval-tracked":
        nine = worlds.a9("a8-for-forks", run_a9=False)
        targets = list(TARGETS)
    else:
        nine = worlds.a9("a8-no-retrieval-for-forks", run_a9=False, plant_options={"no_retrieval": True})
        targets = sorted([*TARGETS, RETRIEVAL])
    nine.need_chain()
    adoption = W.fork(nine, f"nc2-d-{tracked}")
    project = adoption.project
    assert W.git(project, "status", "--porcelain", "--untracked-files=all").strip() == "", "the plant: the repository at A8 is not clean"
    start = W.head(project)
    folders_before = folders(project)
    adoption.extra_env.update({"PYTHONPATH": f"{STANDIN_D}{os.pathsep}{W.SRC}", "W2_88_NC2_COPIES": json.dumps(targets)})
    run = adoption.a9(adoption.box.base / f"nc2-d-{tracked}-out")
    W.assert_offered(run, "A9")

    calls = [line for line in run.stderr.splitlines() if line.startswith("nc2-git: ")]
    fired = [line for line in run.stderr.splitlines() if line.startswith("nc2-plant: fired")]
    assert fired, ("the plant did not take: no git call with `add` and a path of A9's copy plan ran in the child, so the interrupt never fired "
                   f"(git calls seen: {calls[-12:]})\n{run.describe()}")
    assert_interrupt(run, "A9 interrupted the moment its git add of its copies returned")
    assert W.head(project) == start, f"the branch moved from the start commit {start} to {W.head(project)}"
    assert W.git(project, "symbolic-ref", "--short", "HEAD").strip() == "main", "HEAD is no longer on the branch"
    assert_none_of_a9(project, targets, folders_before, "after the interrupt that came as the git add of the copies returned")
    assert porcelain(project) == [], f"git status --porcelain --untracked-files=all is {porcelain(project)}, empty expected"

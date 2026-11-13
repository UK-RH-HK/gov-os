"""Run 5 (P1-W2-88-RV2-1 (a)): RV2-1, A9's undo touches only what A9 itself did (success-16; reached through success-3's refusals).

Review round 2 (``docs/probes/DAEO-2bdu/PR-DAEO-2bdu-round-2.md``) found that a refused or interrupted A9 threw away work done in the
repository while it ran. The interface (the lead's statement of RV2-1; "the start commit" is the commit HEAD named when A9 began,
before its copy step). When A9 refuses or is interrupted (any exception, Ctrl-C included) **after** its copy step (the kernel files
written and staged), its undo touches only what A9 did:

1. the index: only the paths A9 staged, and only where the entry is still the blob A9 staged (a path someone else staged during the
   run, a new file or a re-staged edit, stays staged);
2. the tree: only the files A9 wrote whose bytes are still A9's are deleted, then the folders A9 made when empty (a file A9 wrote
   whose bytes changed during the run is left as it is; a copy that replaced a file the start commit tracks, its bytes still A9's,
   gets that file's content at the start commit back and is never deleted);
3. nothing else: no ``git reset --hard``, no checkout of another path; a tracked file edited during the run keeps its edit, an
   untracked file made during the run stays, the branch is never moved by the undo;
4. HEAD moved (it no longer names the start commit when the undo runs): ``HEAD_MOVED``, the message naming the start commit and the
   new one and saying nothing was reset, ``details {started, now, cause}`` (``cause``: the original refusal's code, or the exception's
   class name); the branch stays at the new commit; 1 to 3 still run, judged against the new HEAD (a copy the new HEAD tracks is
   left in the index and the tree);
5. HEAD did not move: the refusal keeps its own code (an interrupt stays an interrupt).

The plant is the review's: A9 in a child process on a planted adoption (the suite's A9 cases), with a stand-in for
``gov.rebuild.command.run`` (I3: A9 runs it in full) installed first on the child's ``PYTHONPATH`` (``standin_rv2/sitecustomize.py``),
which acts on the repository and raises. The stand-in builds no store, so each case ends the moment A9's undo has run.
"""

from __future__ import annotations

import json
import os
import re

import pytest

import w2_88_support as W

STANDIN = W.HERE / "standin_rv2"
PLAN = W.copy_plan()                          # (path in the adopted repository, path in Gov OS)
TARGETS = sorted(target for target, _ in PLAN)
KERNEL_BYTES = {target: (W.REPO_ROOT / source).read_bytes() for target, source in PLAN}
EDITED = "docs/notes.txt"                      # tracked in the planted adoption
EDITED_BYTES = "Edited during the run by the stand-in.\n"
STAGED = "staged-during-run.md"
COPY = ".claude/skills/retrieval/SKILL.md"
TWO_REFUSALS = ["REBUILD_FAILED", "KeyboardInterrupt"]


def folders(root) -> set:
    found = set()
    for folder, dirs, _ in os.walk(root):
        dirs[:] = [d for d in dirs if d not in (".git", ".gov-runtime")]
        found.update(os.path.relpath(os.path.join(folder, d), root) for d in dirs)
    return found


def porcelain(project) -> list:
    return sorted(W.git(project, "status", "--porcelain", "--untracked-files=all").splitlines())


def indexed(project) -> set:
    return set(W.git(project, "ls-files").splitlines())


class Undone:
    """One planted A9 run with the stand-in, and what the repository was before it and is after it."""

    def __init__(self, project, run, start, seen, after, reflog_before, folders_before):
        self.project, self.run, self.start, self.seen, self.after = project, run, start, seen, after
        self.reflog_before, self.folders_before = reflog_before, folders_before

    def new_reflog(self) -> list:
        """The reflog subjects of HEAD written since the run began (newest first)."""
        now = W.git(self.project, "reflog", "--format=%gs").splitlines()
        assert now[len(now) - len(self.reflog_before):] == self.reflog_before, "the reflog's older entries changed"
        return now[:len(now) - len(self.reflog_before)]


def stand_in_line(run, prefix: str) -> dict:
    lines = [line for line in run.stderr.splitlines() if line.startswith(prefix + ": ")]
    assert lines, (f"the plant did not take: no `{prefix}` line from the stand-in for gov.rebuild.command.run (A9 did not reach "
                   f"the rebuild, or did not call it in this process, I3)\n{run.describe()}")
    return json.loads(lines[-1].split(": ", 1)[1])


def undone(worlds, name: str, action: str, raising: str = "REBUILD_FAILED", *, tracked: dict | None = None) -> Undone:
    """A fork of the planted adoption at A8 (with ``tracked`` files committed on top), A9 run in a child whose
    ``gov.rebuild.command.run`` is the stand-in doing ``action`` and raising ``raising``."""
    nine = worlds.a9("a8-for-forks", run_a9=False)
    nine.need_chain()
    adoption = W.fork(nine, name)
    project = adoption.project
    for rel, text in (tracked or {}).items():
        W.write(project, rel, text)
    if tracked:
        W.commit_all(project, "the repository tracks its own copy of what A9 installs")
    start = W.head(project)
    reflog_before = W.git(project, "reflog", "--format=%gs").splitlines()
    folders_before = folders(project)
    adoption.extra_env.update({"PYTHONPATH": f"{STANDIN}{os.pathsep}{W.SRC}", "W2_88_RV2_ACTION": action,
                               "W2_88_RV2_RAISE": raising, "W2_88_RV2_COPIES": json.dumps(TARGETS)})
    run = adoption.a9(adoption.box.base / f"{name}-out")
    W.assert_offered(run, "A9")
    seen = stand_in_line(run, "rv2-standin")
    after = stand_in_line(run, "rv2-standin-after")["head"]
    assert seen["head"] == start, f"HEAD was {seen['head']} when the rebuild began, the start commit is {start}"
    assert seen["in_tree"] == TARGETS and seen["in_index"] == TARGETS, \
        ("the copy step had not written and staged every kernel file when the rebuild began (the undo is judged on copies that "
         f"were there): in the tree {sorted(set(TARGETS) - set(seen['in_tree']))} missing, in the index "
         f"{sorted(set(TARGETS) - set(seen['in_index']))} missing")
    return Undone(project, run, start, seen, after, reflog_before, folders_before)


def assert_interrupt(run, what: str) -> None:
    """An interrupt stays an interrupt: the child ends non-zero with the traceback of ``KeyboardInterrupt``, no refusal's envelope
    and no ``HEAD_MOVED``."""
    assert run.returncode not in (0, 2), f"{what}: the child ended with exit {run.returncode}\n{run.describe()}"
    assert "KeyboardInterrupt" in run.stderr, f"{what}: the interrupt did not stay an interrupt (no KeyboardInterrupt in stderr)\n{run.describe()}"
    assert "HEAD_MOVED" not in run.stdout + run.stderr, f"{what}: HEAD did not move, yet the run says HEAD_MOVED\n{run.describe()}"


def assert_own_refusal(run, code: str, what: str) -> None:
    W.assert_refused(run, code, what)
    assert run.error.get("code") == code, f"{what}: the refusal is {run.error.get('code')!r}, the stand-in's own is {code!r} (HEAD did not move)\n{run.describe()}"


def assert_refused_as_raised(world: Undone, raising: str, what: str) -> None:
    if raising == "KeyboardInterrupt":
        assert_interrupt(world.run, what)
    else:
        assert_own_refusal(world.run, raising, what)


def assert_no_copies(world: Undone, what: str, keep: tuple = ()) -> None:
    """None of A9's copies (but those of ``keep``) is in the tree or in the index, and no folder A9 made is left."""
    project = world.project
    left = [t for t in TARGETS if t not in keep and (project / t).exists()]
    assert not left, f"{what}: A9's copies are left in the tree: {left}"
    staged = [t for t in TARGETS if t not in keep and t in indexed(project)]
    assert not staged, f"{what}: A9's copies are left in the index: {staged}"
    made = sorted(folders(project) - world.folders_before)
    assert not made, f"{what}: folders A9 made are left (an empty folder is deleted): {made}"


# ---- Case A: the repository's work during the run survives a refusal or an interrupt ---------------------------------------------

@pytest.mark.parametrize("raising", TWO_REFUSALS)
def test_s16_rv2_1_a_refused_or_interrupted_a9_keeps_a_tracked_edit_and_a_staged_new_file_and_takes_back_only_its_copies(worlds, raising):
    """RV2-1 (items 1, 2, 3, 5): the stand-in rewrites the tracked ``docs/notes.txt`` (not staged) and stages a new file, then raises
    (a ``GovError`` ``REBUILD_FAILED``, and a ``KeyboardInterrupt``). Afterwards: the refusal is the stand-in's own code (the interrupt
    stays an interrupt); HEAD is the start commit; the edited file holds the edited bytes; the new file is still staged; none of A9's
    copies is in the tree or the index; ``git status --porcelain`` shows exactly the edit and the staged file."""
    world = undone(worlds, f"rv2-a-{raising.lower()}", "edit-and-stage", raising)
    project = world.project
    assert_refused_as_raised(world, raising, f"A9 refused with {raising} after its copy step")
    assert W.head(project) == world.start, f"the branch moved from the start commit {world.start} to {W.head(project)}"
    assert W.git(project, "symbolic-ref", "--short", "HEAD").strip() == "main", "HEAD is no longer on the branch"
    edited = (project / EDITED).read_text(encoding="utf-8") if (project / EDITED).is_file() else None
    assert edited == EDITED_BYTES, f"the edit made during the run to the tracked {EDITED} was thrown away (it holds {edited!r})"
    assert (project / STAGED).is_file(), f"{STAGED}, a new file made and staged during the run, was deleted from the tree"
    assert W.git(project, "diff", "--cached", "--name-status").splitlines() == [f"A\t{STAGED}"], \
        ("the index is not the new file staged during the run alone: "
         f"{W.git(project, 'diff', '--cached', '--name-status').splitlines()} (the staged file lost, or A9's copies left)")
    assert_no_copies(world, f"after the {raising} refusal")
    assert porcelain(project) == [f" M {EDITED}", f"A  {STAGED}"], \
        f"git status --porcelain is {porcelain(project)}, exactly the edit and the staged file expected"


# ---- Case B: HEAD moved during the run ------------------------------------------------------------------------------------------

def commits(token_text: str) -> list:
    return re.findall(r"(?<![0-9a-f])[0-9a-f]{7,40}(?![0-9a-f])", token_text)


def names(text: str, commit: str) -> bool:
    return any(commit.startswith(token) for token in commits(text))


def is_commit(value, commit: str) -> bool:
    return isinstance(value, str) and len(value) >= 7 and commit.startswith(value)


def test_s16_rv2_1_b_a_commit_made_during_the_run_is_refused_head_moved_naming_both_commits_and_nothing_is_reset(worlds):
    """RV2-1 (item 4): the stand-in commits a new file (``git commit -- notes.md``), then raises ``REBUILD_FAILED``. Afterwards A9 is
    refused ``HEAD_MOVED``: the message names the start commit and that commit and says nothing was reset, ``details`` hold
    ``{started, now, cause: "REBUILD_FAILED"}``; the branch head is that commit (its parent the start commit); ``notes.md`` is in the
    tree; A9's copies are in neither the tree nor the index; the newest reflog entry is the stand-in's commit and none since the run
    began is a ``reset``."""
    world = undone(worlds, "rv2-b-head-moved", "commit-notes")
    project, new = world.project, world.after
    assert new != world.start and W.git(project, "rev-parse", f"{new}^").strip() == world.start, "the plant did not move HEAD by one commit"
    W.assert_refused(world.run, "HEAD_MOVED", "A9 refused after a commit made during the run")
    error = world.run.error
    assert error.get("code") == "HEAD_MOVED", f"the refusal is {error.get('code')!r}, not HEAD_MOVED (HEAD moved from {world.start[:12]} to {new[:12]})"
    message = str(error.get("message", ""))
    assert names(message, world.start) and names(message, new), \
        f"the message does not name both the start commit ({world.start[:12]}) and the new one ({new[:12]}): {message!r}"
    assert "reset" in message.lower(), f"the message does not say nothing was reset: {message!r}"
    details = error.get("details") or {}
    assert is_commit(details.get("started"), world.start), f"details.started is {details.get('started')!r}, the start commit is {world.start}"
    assert is_commit(details.get("now"), new), f"details.now is {details.get('now')!r}, the new commit is {new}"
    assert details.get("cause") == "REBUILD_FAILED", f"details.cause is {details.get('cause')!r}, the original refusal's code is REBUILD_FAILED"
    assert W.head(project) == new, f"the branch is not at the commit made during the run: it is at {W.head(project)[:12]}, the commit is {new[:12]}"
    assert W.git(project, "rev-parse", "main").strip() == new, "the branch main is not at the new commit"
    notes = project / "notes.md"
    assert notes.is_file() and "Committed during the run" in notes.read_text(encoding="utf-8"), "notes.md, committed during the run, is not in the tree"
    assert_no_copies(world, "after HEAD_MOVED")
    assert porcelain(project) == [], f"git status --porcelain is not clean: {porcelain(project)}"
    fresh = world.new_reflog()
    assert fresh and fresh[0].startswith("commit"), f"the newest reflog entry is {fresh[:1]}, the stand-in's commit expected (the branch was moved after it)"
    assert not [entry for entry in fresh if "reset" in entry.lower()], f"the undo reset the branch: {fresh}"


def test_s16_rv2_1_b_a_copy_the_new_head_tracks_is_left_in_the_index_and_the_tree(worlds):
    """RV2-1 (item 4, the last sentence): the stand-in commits the whole index, so A9's staged copies are in the commit made during the
    run, then raises. A9 is refused ``HEAD_MOVED``; steps 1 to 3 are judged against the new HEAD: every copy the new HEAD tracks is
    left in the tree (A9's bytes) and in the index, the tree is clean, and the branch is at the new commit with no ``reset`` in the
    reflog."""
    world = undone(worlds, "rv2-b-copies-committed", "commit-all")
    project, new = world.project, world.after
    tracked_at_new = set(W.git(project, "ls-tree", "-r", "--name-only", new).splitlines())
    assert set(TARGETS) <= tracked_at_new, f"the plant did not commit A9's copies: {sorted(set(TARGETS) - tracked_at_new)}"
    W.assert_refused(world.run, "HEAD_MOVED", "A9 refused after a commit of its own copies made during the run")
    assert world.run.error.get("code") == "HEAD_MOVED", f"the refusal is {world.run.error.get('code')!r}, not HEAD_MOVED"
    assert world.run.error.get("details", {}).get("cause") == "REBUILD_FAILED", f"details: {world.run.error.get('details')}"
    assert W.head(project) == new, f"the branch is not at the new commit {new[:12]}: it is at {W.head(project)[:12]}"
    gone = [t for t in TARGETS if not (project / t).is_file()]
    assert not gone, f"copies the new HEAD tracks were deleted from the tree: {gone}"
    changed = [t for t in TARGETS if (project / t).read_bytes() != KERNEL_BYTES[t]]
    assert not changed, f"copies the new HEAD tracks were changed in the tree: {changed}"
    unstaged = [t for t in TARGETS if t not in indexed(project)]
    assert not unstaged, f"copies the new HEAD tracks were removed from the index: {unstaged}"
    assert porcelain(project) == [], f"git status --porcelain is not clean: {porcelain(project)}"
    fresh = world.new_reflog()
    assert fresh and fresh[0].startswith("commit") and not [e for e in fresh if "reset" in e.lower()], f"the reflog since the run began: {fresh}"


# ---- Case C: a file A9 wrote whose bytes changed during the run ------------------------------------------------------------------

def test_s16_rv2_1_c_a_copy_edited_during_the_run_is_left_in_the_tree_and_the_other_copies_are_taken_back(worlds):
    """RV2-1 (items 1, 2): the stand-in appends a line to A9's ``.claude/skills/retrieval/SKILL.md`` (not staged), then raises. The file
    A9 wrote whose bytes changed is left as it is (A9's bytes and the appended line); its index entry is still the blob A9 staged, so
    it is removed from the index (the file is untracked); every other copy is gone from the tree and the index; HEAD is the start
    commit; ``git status --porcelain`` shows that one untracked file."""
    world = undone(worlds, "rv2-c-edited-copy", "edit-copy")
    project = world.project
    assert_own_refusal(world.run, "REBUILD_FAILED", "A9 refused with REBUILD_FAILED after its copy was edited")
    assert W.head(project) == world.start, "the branch moved"
    path = project / COPY
    assert path.is_file(), f"{COPY}, a copy A9 wrote that was edited during the run, was deleted"
    assert path.read_bytes().startswith(KERNEL_BYTES[COPY]) and b"edited during the run by the stand-in" in path.read_bytes(), \
        f"{COPY} is not A9's bytes with the line appended during the run"
    assert COPY not in indexed(project), f"{COPY} is still in the index: its entry is the blob A9 staged and the undo removes it"
    left = [t for t in TARGETS if t != COPY and (project / t).exists()]
    assert not left, f"A9's other copies are left in the tree: {left}"
    staged = [t for t in TARGETS if t in indexed(project)]
    assert not staged, f"A9's copies are left in the index: {staged}"
    assert porcelain(project) == [f"?? {COPY}"], f"git status --porcelain is {porcelain(project)}, the one untracked edited copy expected"


def test_s16_rv2_1_c_a_copy_edited_and_restaged_during_the_run_stays_staged_with_its_edit(worlds):
    """RV2-1 (items 1, 2): the stand-in appends a line to A9's ``.claude/skills/retrieval/SKILL.md`` and stages the edit, then raises.
    The index entry is no longer the blob A9 staged, so it stays in the index (the edited blob); the file stays in the tree; every
    other copy is gone from the tree and the index; HEAD is the start commit; ``git status --porcelain`` shows that file added."""
    world = undone(worlds, "rv2-c-restaged-copy", "edit-copy-restaged")
    project = world.project
    assert_own_refusal(world.run, "REBUILD_FAILED", "A9 refused with REBUILD_FAILED after its copy was edited and re-staged")
    assert W.head(project) == world.start, "the branch moved"
    path = project / COPY
    assert path.is_file() and b"edited during the run by the stand-in" in path.read_bytes(), f"{COPY}, edited and staged during the run, is not in the tree as edited"
    entry = W.git(project, "ls-files", "-s", "--", COPY).split()
    assert entry, f"{COPY}, re-staged during the run, was removed from the index"
    assert entry[1] == W.git(project, "hash-object", COPY).strip(), f"the index holds {entry[1]} for {COPY}, not the blob staged during the run"
    left = [t for t in TARGETS if t != COPY and (project / t).exists()]
    assert not left, f"A9's other copies are left in the tree: {left}"
    staged = [t for t in TARGETS if t != COPY and t in indexed(project)]
    assert not staged, f"A9's other copies are left in the index: {staged}"
    assert porcelain(project) == [f"A  {COPY}"], f"git status --porcelain is {porcelain(project)}, the one re-staged copy expected"


# ---- Case D: a copy that replaced a file the start commit tracks ------------------------------------------------------------------

def test_s16_rv2_1_d_a_copy_that_replaced_a_tracked_file_gets_the_start_commits_content_back_and_is_never_deleted(worlds):
    """RV2-1 (item 2): the repository tracks its own ``.claude/skills/retrieval/SKILL.md`` (committed at the start commit), A9's copy
    step replaces it, and the stand-in raises ``REBUILD_FAILED`` with the copy's bytes still A9's. The undo puts that file's content at
    the start commit back (it is never deleted), the other copies are gone, HEAD is the start commit and the tree and the index are
    clean."""
    own = "# The repository's own retrieval skill\n\nKept as the repository wrote it.\n"
    world = undone(worlds, "rv2-d-tracked-copy", "none", tracked={COPY: own})
    project = world.project
    assert (W.git(project, "show", f"{world.start}:{COPY}")) == own, "the plant did not commit the repository's own copy"
    assert_own_refusal(world.run, "REBUILD_FAILED", "A9 refused with REBUILD_FAILED after replacing a tracked file")
    assert W.head(project) == world.start, "the branch moved"
    path = project / COPY
    assert path.is_file(), f"{COPY}, tracked at the start commit and replaced by A9's copy, was deleted by the undo"
    assert path.read_text(encoding="utf-8") == own, f"{COPY} does not hold its content at the start commit: {path.read_text(encoding='utf-8')[:80]!r}"
    left = [t for t in TARGETS if t != COPY and (project / t).exists()]
    assert not left, f"A9's other copies are left in the tree: {left}"
    assert [t for t in TARGETS if t != COPY and t in indexed(project)] == [], "A9's other copies are left in the index"
    assert porcelain(project) == [], f"git status --porcelain is not clean: {porcelain(project)}"


# ---- Case E: an untracked file and a re-staged edit made during the run -----------------------------------------------------------

def test_s16_rv2_1_e_an_untracked_file_stays_and_a_restaged_edit_stays_staged(worlds):
    """RV2-1 (items 1, 3): the stand-in writes an untracked ``scratch-untracked.txt`` and re-stages an edit of the tracked
    ``lib/util.py``, then raises ``REBUILD_FAILED``. The untracked file stays; the edit stays staged (the index entry is the edited
    blob, not HEAD's); A9's copies are gone; HEAD is the start commit; ``git status --porcelain`` shows exactly the two."""
    world = undone(worlds, "rv2-e-untracked", "untracked-and-restaged")
    project = world.project
    assert_own_refusal(world.run, "REBUILD_FAILED", "A9 refused with REBUILD_FAILED after an untracked file and a re-staged edit")
    assert W.head(project) == world.start, "the branch moved"
    assert (project / "scratch-untracked.txt").is_file(), "scratch-untracked.txt, an untracked file made during the run, was deleted"
    assert "return 42" in (project / "lib/util.py").read_text(encoding="utf-8"), "the edit of lib/util.py made during the run was thrown away"
    assert_no_copies(world, "after the refusal")
    assert porcelain(project) == ["?? scratch-untracked.txt", "M  lib/util.py"], \
        f"git status --porcelain is {porcelain(project)}, the untracked file and the staged edit expected"

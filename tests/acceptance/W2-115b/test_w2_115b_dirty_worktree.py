"""``gov queue`` never leaves uncommitted work behind (W2-115b's fix, audit N-01; README, "Fix: a dirty worktree").

The queue merges a branch's tip, the branch's committed head. A worktree that holds that branch (a linked one, or the
main tree) with modified, staged, deleted or untracked-but-not-ignored work would be left holding changes the landing
does not contain, so the queue refuses before any merge: ``QUEUE_WORKTREE_DIRTY``, its message naming the worktree and
every dirty file. Public interface only: ``gov queue <ticket>=<branch> [--onto <branch>] --root <project> --json`` (the
envelope, stderr, exit code), the planted repository's refs and the worktrees' own ``git status``.

Each case plants a fresh project (``w2_115b_support.Planted``, A and B on ``main``), A's branch ``topic/aa`` (one
commit changing the widget, which A's suite and ``tests/unit/test_uses_widget.py`` guard), and a worktree.
"""

from __future__ import annotations

import pytest

import w2_115b_support as support
from w2_115b_support import A, module_rel

CHANGED = "# CHANGED by the ticket\nVALUE = 2\n"
WIDGET = {module_rel("widget"): CHANGED}
IGNORES = ".gov-runtime/\n__pycache__/\n*.pyc\nbuild/\n"

HELPER = module_rel("helper")          # tracked, mapped (a unit test imports it)
NOTES = support.NOTES_REL              # tracked, a plain file
NEW_FILE = "src/app/newmod.py"         # a new file in a directory the repository tracks
CODE = "QUEUE_WORKTREE_DIRTY"
REFUSED_EXITS = (support.EXIT_REFUSED_TO_RUN, support.EXIT_NOT_ALL_LANDED)   # 1 as a refused candidate, 3 as the run's


def _plant(planted):
    p = planted(extra={".gitignore": IGNORES})
    p.plant_branch(A, "topic/aa", [(WIDGET, "engineer", True)])
    return p


def _worktree(p, branch="topic/aa", name="wt-aa"):
    path = p.root.parent / name
    support.git(p.root, "worktree", "add", "-q", str(path), branch)
    return path


def _modify(wt):
    (wt / HELPER).write_text("# DIRTY, not committed\nVALUE = 5\n", encoding="utf-8")


def _stage(wt):
    _modify(wt)
    support.git(wt, "add", HELPER)


def _untracked(wt):
    (wt / NEW_FILE).write_text("# a new file nobody committed\nVALUE = 1\n", encoding="utf-8")


def _delete(wt):
    (wt / NOTES).unlink()


def _dirty_status(wt):
    return support.git(wt, "status", "--porcelain")


def _ready(p):
    """The state to compare a refusal with, taken after the worktree is dirty."""
    return {"state": p.state(), "main": support.rev(p.root, "main"),
            "refs": support.git(p.root, "for-each-ref", "--format=%(refname) %(objectname)")}


def assert_refused_dirty(p, run, wt, files, before):
    env = support.envelope(run)
    assert env.get("ok") is False, f"the queue did not refuse\n{support.describe(run)}"
    error = env.get("error") or {}
    assert error.get("code") == CODE, f"refused with {error.get('code')!r}, not {CODE}\n{support.describe(run)}"
    assert run["code"] in REFUSED_EXITS, f"exit {run['code']}, not one of {REFUSED_EXITS}\n{support.describe(run)}"
    assert f"{CODE}:" in run["stderr"], f"stderr does not say {CODE}\n{support.describe(run)}"
    message = error.get("message") or ""
    named = {str(wt), str(wt.resolve())}
    assert any(n in message for n in named), f"the message does not name the worktree {wt}\n{message}"
    missing = [f for f in files if f not in message]
    assert not missing, f"the message does not name {missing}\n{message}"
    assert p.state() == before["state"], "the refused queue changed the project's root (refs, HEAD, files, status)"
    assert support.rev(p.root, "main") == before["main"], "the integration branch moved"
    assert support.git(p.root, "for-each-ref", "--format=%(refname) %(objectname)") == before["refs"]
    assert len(support.parents(p.root, support.rev(p.root, "main"))) <= 1, "main's head is a merge commit"
    assert not (p.root / "docs" / "close").exists(), "a close record was written"
    assert support.status_at(p.root, "main", A.id) == "open", "the ticket was closed"
    assert not support.is_ancestor(p.root, p.tips[A.id], "main"), "the branch was merged"


def _dirty_case(planted, make, files):
    p = _plant(planted)
    wt = _worktree(p)
    make(wt)
    assert _dirty_status(wt), "fixture: the worktree is not dirty"
    before, wt_before = _ready(p), _dirty_status(wt)
    run = support.run_queue(p, f"{A.id}=topic/aa")
    assert_refused_dirty(p, run, wt, files, before)
    assert _dirty_status(wt) == wt_before, "the refusal changed the dirty worktree"
    return p, wt


# -- success-14: a worktree holding the branch with uncommitted work refuses the queue ------------------------------

def test_a_modified_tracked_file_in_the_branch_s_worktree_refuses(planted):
    _dirty_case(planted, _modify, [HELPER])


def test_a_staged_change_in_the_branch_s_worktree_refuses(planted):
    _dirty_case(planted, _stage, [HELPER])


def test_an_untracked_new_file_in_a_tracked_directory_refuses(planted):
    _dirty_case(planted, _untracked, [NEW_FILE])


def test_a_deleted_tracked_file_in_the_branch_s_worktree_refuses(planted):
    _dirty_case(planted, _delete, [NOTES])


def test_two_dirty_files_are_both_named(planted):
    def both(wt):
        _modify(wt)
        _untracked(wt)
    _dirty_case(planted, both, [HELPER, NEW_FILE])


def test_the_main_tree_holding_the_branch_dirty_refuses(planted):
    p = _plant(planted)
    p.checkout("topic/aa")
    _modify(p.root)
    before = _ready(p)
    run = support.run_queue(p, f"{A.id}=topic/aa", "--onto", "main")
    assert_refused_dirty(p, run, p.root, [HELPER], before)


# -- success-14: the entry is not poisoned by the refusal ------------------------------------------------------------

def test_after_the_change_is_discarded_the_same_entry_lands(planted):
    p, wt = _dirty_case(planted, _modify, [HELPER])
    support.git(wt, "checkout", "-q", "--", HELPER)
    assert _dirty_status(wt) == ""
    support.self_check(p, {p.tips[A.id]: {A.node: "passed", support.USES_WIDGET_NODE: "passed"}})
    old_head = support.rev(p.root, "main")
    result = support.answer(support.run_queue(p, f"{A.id}=topic/aa"), support.EXIT_LANDED)
    assert result.get("landed") == [A.id], f"landed: {result.get('landed')}"
    support.assert_landed_through_close_commits(p, result, "main", old_head)
    support.assert_closed_iff_merged(p, "main")


def test_after_the_change_is_committed_the_same_entry_lands_with_it(planted):
    p, wt = _dirty_case(planted, _modify, [HELPER])
    support.git(wt, "add", HELPER)
    support.git(wt, "commit", "-q", "--no-gpg-sign", "-m", "the work, committed", "--trailer", f"Task: {A.id}",
                "--trailer", "Role: engineer")
    p.record_branch(A, "topic/aa")
    old_head = support.rev(p.root, "main")
    result = support.answer(support.run_queue(p, f"{A.id}=topic/aa"), support.EXIT_LANDED)
    assert result.get("landed") == [A.id], f"landed: {result.get('landed')}"
    support.assert_landed_through_close_commits(p, result, "main", old_head)
    assert HELPER in support.git(p.root, "diff", "--name-only", old_head, result["tested"]).split()
    support.assert_closed_iff_merged(p, "main")


# -- failure-4: honest work is not refused (controls) -----------------------------------------------------------------

def _lands(p, *args):
    support.self_check(p, {p.tips[A.id]: {A.node: "passed", support.USES_WIDGET_NODE: "passed"}})
    old_head = support.rev(p.root, "main")
    result = support.answer(support.run_queue(p, f"{A.id}=topic/aa", *args), support.EXIT_LANDED)
    assert result.get("landed") == [A.id], f"landed: {result.get('landed')}"
    support.assert_landed_through_close_commits(p, result, "main", old_head)
    support.assert_closed_iff_merged(p, "main")
    return result


def test_a_clean_worktree_holding_the_branch_lands(planted):
    p = _plant(planted)
    wt = _worktree(p)
    assert _dirty_status(wt) == ""
    _lands(p)


def test_a_clean_main_tree_holding_the_branch_lands(planted):
    p = _plant(planted)
    p.checkout("topic/aa")
    assert support.git(p.root, "status", "--porcelain") == ""
    _lands(p, "--onto", "main")


def test_files_the_gitignore_ignores_are_not_dirty(planted):
    p = _plant(planted)
    wt = _worktree(p)
    for rel, text in {"src/app/__pycache__/widget.cpython-312.pyc": "\0", "src/app/stray.pyc": "\0",
                      "build/out.bin": "output\n"}.items():
        (wt / rel).parent.mkdir(parents=True, exist_ok=True)
        (wt / rel).write_text(text, encoding="utf-8")
    assert _dirty_status(wt) == "", f"fixture: ignored files show as dirty: {_dirty_status(wt)}"
    _lands(p)


def test_a_branch_checked_out_in_no_worktree_lands(planted):
    p = _plant(planted)
    assert support.git(p.root, "worktree", "list", "--porcelain").count("worktree ") == 1
    _lands(p)


def test_another_branch_s_dirty_worktree_does_not_refuse(planted):
    p = _plant(planted)
    support.git(p.root, "branch", "topic/other", p.base)
    other = _worktree(p, "topic/other", "wt-other")
    _modify(other)
    _untracked(other)
    assert _dirty_status(other)
    _lands(p)

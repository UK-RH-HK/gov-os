"""W2-111 success-8 and failure-4 (DEC-1184 (3)): with 150 worktrees, every decision is the same as before.

The fails-open check: a speed-up that judges a call against fewer trees must never let a read of a hidden part
through. On the planted repository (150 worktrees and the main tree, each holding the planted evaluation set's hidden
part, which measures the engineer, DEC-820 (d), DEC-845, W2-84), the engineer's reads of the hidden part are refused
wherever it lies: in the last-listed tree, in the first, in the session's own tree, a file not there yet, by the Read
tool, by a Bash ``cat`` or ``ls``, by a search from the folder above every worktree (``grep -r``, ``find -exec cat``),
by a shell glob over every worktree, by the Grep tool from that folder (with and without a glob), through a link, and
from a session in the last tree. And the allows still allow: the engineer's reads outside the hidden part in any tree,
a session no set measures reading the hidden part, and a listing of names alone from the folder above (``find``, the
Glob tool), which opens no file and is allowed today. The expected answers are the rule's (DEC-820 (d)): refused to a
session the set measures, "whether or not it exists"; a search from above takes a part in where its files exist.
"""

from __future__ import annotations

import pytest

import w2_111_support as support

q = support.q
H, F, W = support.HIDDEN_FILE, support.HIDDEN_FOLDER, support.HIDDEN_WORD


def last(w):
    return w.trees[-1]


# id: a call on the world (returns a HookResult)
REFUSED = {
    "Read-of-the-hidden-file-in-the-last-listed-tree": lambda w: w.read(last(w) / H),
    "Read-of-the-hidden-file-in-the-first-listed-worktree": lambda w: w.read(w.trees[1] / H),
    "Read-of-the-hidden-file-in-the-session-s-own-tree": lambda w: w.read(w.trees[0] / H),
    "Read-of-a-file-not-there-under-the-last-tree-s-hidden-folder": lambda w: w.read(last(w) / F / "new.yaml"),
    "Bash-cat-of-the-hidden-file-in-the-last-tree": lambda w: w.bash(f"cat {q(last(w) / H)}"),
    "Bash-ls-of-the-hidden-folder-in-the-last-tree": lambda w: w.bash(f"ls {q(last(w) / F)}"),
    "Bash-grep-r-from-the-folder-above-every-worktree": lambda w: w.bash(f"grep -r {W} {q(w.above)}"),
    "Bash-find-exec-cat-from-the-folder-above-every-worktree": lambda w: w.bash(
        f"find {q(w.above)} -name answers.yaml -exec cat {{}} +"),
    "Bash-cat-of-a-shell-glob-over-every-worktree": lambda w: w.bash(f"cat {q(w.above)}/*/{H}"),
    "Grep-tool-from-the-folder-above-every-worktree": lambda w: w.call(
        "Grep", {"pattern": W, "path": str(w.above), "output_mode": "content"}),
    "Grep-tool-with-a-glob-for-the-hidden-files-from-the-folder-above": lambda w: w.call(
        "Grep", {"pattern": W, "path": str(w.above), "glob": "**/hidden/*.yaml", "output_mode": "content"}),
    "Read-through-a-link-to-the-last-tree-s-hidden-folder": lambda w: w.read(
        w.trees[0] / support.LINK_NAME / "answers.yaml"),
    "Read-of-the-main-tree-s-hidden-file-from-a-session-in-the-last-tree": lambda w: w.read(
        w.trees[0] / H, project=last(w)),
}

ALLOWED = {
    "Read-of-the-visible-file-in-the-last-tree": lambda w: w.read(last(w) / support.VISIBLE_FILE),
    "Read-of-a-source-file-in-the-session-s-own-tree": lambda w: w.read(w.trees[0] / "src/app/main.py"),
    "Bash-cat-of-a-file-outside-the-hidden-part-in-the-last-tree": lambda w: w.bash(
        f"cat {q(last(w) / 'docs/notes.md')}"),
    "Bash-grep-r-in-a-folder-of-the-last-tree-outside-the-hidden-part": lambda w: w.bash(
        f"grep -r {support.WORD} {q(last(w) / 'docs')}"),
    "Grep-tool-in-a-folder-of-the-last-tree-outside-the-hidden-part": lambda w: w.call(
        "Grep", {"pattern": support.WORD, "path": str(last(w) / "docs"), "output_mode": "content"}),
    "Read-of-the-hidden-file-in-the-last-tree-by-a-session-no-set-measures": lambda w: w.read(
        last(w) / H, role=None, ticket=None),
    # A listing of names from above opens no file: allowed today (names may be seen, DEC-820), and pinned so.
    "Bash-find-listing-names-from-the-folder-above-every-worktree": lambda w: w.bash(f"find {q(w.above)}"),
    "Glob-tool-listing-names-from-the-folder-above-every-worktree": lambda w: w.call(
        "Glob", {"pattern": "**/hidden/*.yaml", "path": str(w.above)}),
}


@pytest.mark.parametrize("name", list(REFUSED), ids=list(REFUSED))
def test_a_read_of_the_hidden_part_is_still_refused_with_150_worktrees(trees_world, name):
    result = REFUSED[name](trees_world)
    support.guard.assert_denied(result, f"{name} (the engineer, {len(trees_world.trees)} trees)")


@pytest.mark.parametrize("name", list(ALLOWED), ids=list(ALLOWED))
def test_a_read_outside_the_hidden_part_is_still_allowed_with_150_worktrees(trees_world, name):
    result = ALLOWED[name](trees_world)
    support.guard.assert_allowed(result, f"{name} ({len(trees_world.trees)} trees)")

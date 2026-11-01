"""W2-84 -- no git route shows a hidden file from the object store the worktrees share.

KPI success 3: "No git route shows a hidden file's content to a measured
session from another tree or from the object store the worktrees share: git
show <rev>:<path>, git -C <tree> show or grep, and a patch (git show <rev>, git
log -p, git diff <rev>) of a revision that holds the hidden part, whether or
not the session's own tree holds it [DEC-950 item 1, DEC-873]".
KPI failure 3: "A git route that shows a hidden file's content to a measured
session from another tree or from the shared object store."

The store world (``w2_84_support.make_store_world``): neither the main tree
(on ``main``) nor the worktree W2-81 holds a hidden file. The branch
``w2/W2-88`` holds two commits the trees do not: ``hidden``, which adds the
hidden part, then ``after``, which changes ``docs/notes.md`` only. ``main``
ends with ``unrelated``, which changes ``docs/notes.md`` only.

``git show <rev>:<path>``, ``git -C <tree> show`` and ``git -C <tree> grep``
across the trees are in ``test_w2_84_every_tree.py``.

Not tested as refused: the design note's residual R1, a hidden blob printed by
its object id (``git cat-file -p <blob id>``, ``--batch``), which must be
looked up first and printed by hand (W2-L374's class); see the README.
"""

from __future__ import annotations

import pytest

import w2_84_support as s

SESSIONS = (s.STORE_MAIN, s.STORE_WT)

REFUSED_IDS = ("show-rev", "log-p-branch", "log-p-all", "diff-rev", "grep-rev", "archive-rev", "cat-file-rev-path",
               "show-rev-path")


def _refused(store):
    hidden = store.revs["hidden"]
    return [
        s.bash(f"git show {hidden}"),
        s.bash(f"git log -p {s.HIDDEN_BRANCH}"),
        s.bash("git log -p --all"),
        s.bash(f"git diff {hidden}"),
        s.bash(f"git grep -n {s.HIDDEN_WORD} {hidden}"),
        s.bash(f"git archive {hidden}"),
        s.bash(f"git cat-file -p {hidden}:{s.HIDDEN_FILE}"),
        s.bash(f"git show {hidden}:{s.HIDDEN_FILE}"),
    ]


@pytest.mark.parametrize("index", range(len(REFUSED_IDS)), ids=REFUSED_IDS)
@pytest.mark.parametrize("session", SESSIONS)
def test_a_revision_that_holds_the_hidden_part_is_not_shown(store, session, index):
    call = _refused(store)[index]
    result = store.ask(call, s.ENGINEER, s.ENG, store.tree(session))
    s.assert_refused(result, call, f"engineer rooted in the store's {session} (no hidden file on disk): ")


ALLOWED_IDS = ("show-unrelated-rev", "show-rev-after-the-hidden-part", "log-p-head", "log-p-all-visible-folder")


def _allowed(store):
    return [
        s.bash(f"git show {store.revs['unrelated']}"),
        s.bash(f"git show {store.revs['after']}"),
        s.bash("git log -p"),
        s.bash(f"git log -p --all -- {s.VISIBLE_FOLDER}"),
    ]


@pytest.mark.parametrize("index", range(len(ALLOWED_IDS)), ids=ALLOWED_IDS)
@pytest.mark.parametrize("session", SESSIONS)
def test_a_patch_that_shows_no_hidden_path_stays_allowed(store, session, index):
    """The converse (the design note's item 5): a patch of a commit that touches no hidden path stays open, even
    when the commit's tree holds the hidden part (``after``), and a pathspec that keeps to the visible part."""
    call = _allowed(store)[index]
    result = store.ask(call, s.ENGINEER, s.ENG, store.tree(session))
    s.assert_allowed(result, call, f"engineer rooted in the store's {session}: ")


def test_the_store_world_is_as_the_cases_say(store):
    """The fixture's own check: the hidden commit adds the hidden part; the others touch only docs/notes.md."""
    repo = store.tree(s.STORE_MAIN)
    names = {rev: s.git(store.sandbox, repo, "show", "--name-only", "--format=", rev).split()
             for rev in store.revs.values()}
    assert set(names[store.revs["hidden"]]) >= {s.HIDDEN_FILE, s.HIDDEN_EXTRA}, names
    assert names[store.revs["after"]] == ["docs/notes.md"], names
    assert names[store.revs["unrelated"]] == ["docs/notes.md"], names
    tree = s.git(store.sandbox, repo, "ls-tree", "-r", "--name-only", store.revs["after"]).split()
    assert s.HIDDEN_FILE in tree, "the commit after the hidden part does not hold it"

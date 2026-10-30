"""Builder tests for W2-72's review round (DEC-918): the merge commit is
compared with git's own merge over the whole of ``tests/acceptance/``,
and a merge-back over two calls keeps git's own merge.

Regression evidence only, in temporary repositories built from scratch.
"""

from __future__ import annotations

from gov.guard.containment import (
    _git_merge_diff, _git_merged, _held_by_merges, _merging)

from .test_w2_72_merge_rule import (
    ACC, LINES, commit_all, edit, git, judge, merge, merge_commit,
    repo_with_sides, write)

NEW = "tests/acceptance/T/test_renamed.py"


def renamed(tmp_path, renamer):
    """A base with ACC; *renamer* (``main`` or ``side``) renames it to
    NEW, the other branch edits it; main is checked out."""
    repo = tmp_path / "r"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "main")
    git(repo, "config", "user.email", "t@example.com")
    git(repo, "config", "user.name", "t")
    write(repo, ACC, LINES)
    commit_all(repo, "base")
    git(repo, "branch", "side")
    for branch in ("side", "main"):
        git(repo, "checkout", "-q", branch)
        if branch == renamer:
            git(repo, "mv", ACC, NEW)
        else:
            write(repo, ACC, edit(LINES, 8, branch))
        commit_all(repo, branch + " again")
    return repo


def test_an_edit_merged_across_a_rename_on_the_merged_side_passes(tmp_path):
    repo = renamed(tmp_path, "side")
    merge(repo, "side")
    c = merge_commit(repo)
    assert ACC in c[4] and NEW in c[4]
    assert _git_merge_diff(str(repo), c, {}) == set()
    assert _git_merged(str(repo), c, {}) == {ACC, NEW}
    assert judge(repo, c) is None


def test_a_drop_behind_a_rename_gives_no_allowance(tmp_path):
    repo = renamed(tmp_path, "main")
    merge(repo, "-s", "ours", "side")  # main's renamed file whole
    c = merge_commit(repo)
    assert NEW not in c[4] and ACC in c[4]
    assert NEW in _git_merge_diff(str(repo), c, {})
    assert _git_merged(str(repo), c, {}) == set()
    res = judge(repo, c)
    assert res is not None and ACC in res[0]


def test_a_merge_in_progress_holds_git_s_own_merge(tmp_path):
    repo = repo_with_sides(tmp_path, edit(LINES, 1, "ours"),
                           edit(LINES, 8, "theirs"))
    git(repo, "checkout", "-q", "side")
    write(repo, "tests/acceptance/T/test_new.py", "new\n")
    commit_all(repo, "side new")
    git(repo, "checkout", "-q", "main")
    head = git(repo, "rev-parse", "HEAD")
    both = [ACC, "tests/acceptance/T/test_new.py"]
    assert _merging(str(repo), both, head) == set()  # no merge yet
    merge(repo, "--no-commit", "side")
    assert _merging(str(repo), both, head) == set(both)
    write(repo, ACC, "by hand\n")
    assert _merging(str(repo), both, head) == {both[1]}
    git(repo, "add", ACC)
    assert _merging(str(repo), both, head) == {both[1]}


def test_a_conflicted_acceptance_test_in_progress_stays_caught(tmp_path):
    repo = repo_with_sides(tmp_path, edit(LINES, 1, "ours"),
                           edit(LINES, 1, "theirs"))
    head = git(repo, "rev-parse", "HEAD")
    merge(repo, "--no-commit", "side")
    assert _merging(str(repo), [ACC], head) == set()


def test_the_commit_of_a_merge_in_progress_holds_what_was_dirty(tmp_path):
    repo = repo_with_sides(tmp_path, edit(LINES, 1, "ours"),
                           edit(LINES, 8, "theirs"))
    merge(repo, "--no-commit", "side")
    git(repo, "commit", "-q", "--no-edit")
    c = merge_commit(repo)
    assert _held_by_merges(str(repo), [ACC, "tests/acceptance/x.py"],
                           [c], {}) == {ACC}

    # A merge commit that differs from git's own merge holds nothing.
    other = tmp_path / "o"
    other.mkdir()
    repo = repo_with_sides(other, edit(LINES, 1, "ours"),
                           edit(LINES, 8, "theirs"))
    merge(repo, "--no-commit", "side")
    write(repo, ACC, "by hand\n")
    git(repo, "add", ACC)
    git(repo, "commit", "-q", "--no-edit")
    c = merge_commit(repo)
    assert _held_by_merges(str(repo), [ACC], [c], {}) == set()

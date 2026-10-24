"""Builder tests for W2-72 (DEC-918): an acceptance test a merge commit
holds exactly as git's own merge of its parents writes it is not judged.

Regression evidence only, in temporary repositories built from scratch.
"""

from __future__ import annotations

import subprocess

from gov.guard import containment
from gov.guard.containment import _LIFT_LEFT, _git_merged, _judge_commit
from gov.guard.containment_merge import read_merge

ACC = "tests/acceptance/T/test_t.py"
LINES = "".join(f"line {i}\n" for i in range(10))


def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], check=True,
                          capture_output=True, text=True).stdout.strip()


def write(repo, path, text):
    f = repo / path
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(text)


def commit_all(repo, msg):
    git(repo, "add", "-A")
    git(repo, "commit", "-qm", msg)
    return git(repo, "rev-parse", "HEAD")


def edit(text, i, new):
    lines = text.splitlines(keepends=True)
    lines[i] = new + "\n"
    return "".join(lines)


def repo_with_sides(tmp_path, ours, theirs, path=ACC):
    """A base with *path*, a side branch changing it to *theirs* and
    main changing it to *ours*; main is checked out."""
    repo = tmp_path / "r"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "main")
    git(repo, "config", "user.email", "t@example.com")
    git(repo, "config", "user.name", "t")
    write(repo, path, LINES)
    commit_all(repo, "base")
    git(repo, "checkout", "-qb", "side")
    write(repo, path, theirs)
    commit_all(repo, "side")
    git(repo, "checkout", "-q", "main")
    write(repo, path, ours)
    commit_all(repo, "main")
    return repo


def merge(repo, *more):
    subprocess.run(["git", "-C", str(repo), "merge", "-q", "--no-edit",
                    "--no-ff", *more], capture_output=True, text=True)


def merge_commit(repo):
    sha = git(repo, "rev-parse", "HEAD")
    parents = git(repo, "rev-list", "--no-walk", "--parents", sha).split()[1:]
    return (sha, parents, [], [], list(read_merge(str(repo), sha).own))


def deny_all(*_args):
    return "deny", ""


def judge(repo, c, closes=None):
    return _judge_commit(str(repo), c, "orchestrator", None, None, True,
                         c[0], deny_all, {} if closes is None else closes)


def clean_merge(tmp_path):
    repo = repo_with_sides(tmp_path, edit(LINES, 1, "ours"),
                           edit(LINES, 8, "theirs"))
    merge(repo, "side")
    return repo


def test_a_clean_merge_of_a_both_changed_acceptance_test_is_not_judged(tmp_path):
    repo = clean_merge(tmp_path)
    c = merge_commit(repo)
    assert ACC in c[4]  # read_merge's own reading is unchanged (DP-24)
    assert _git_merged(str(repo), c, {}) == {ACC}
    assert judge(repo, c) is None


def uncommitted_clean_merge(tmp_path):
    repo = repo_with_sides(tmp_path, edit(LINES, 1, "ours"),
                           edit(LINES, 8, "theirs"))
    merge(repo, "--no-commit", "side")
    return repo


def test_a_hand_edit_of_a_clean_merge_stays_a_finding(tmp_path):
    repo = uncommitted_clean_merge(tmp_path)
    write(repo, ACC, edit(edit(LINES, 1, "ours"), 8, "theirs") + "extra\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "--no-edit")
    c = merge_commit(repo)
    assert _git_merged(str(repo), c, {}) == set()
    res = judge(repo, c)
    assert res is not None and ACC in res[0]


def test_another_mode_stays_a_finding(tmp_path):
    repo = uncommitted_clean_merge(tmp_path)
    git(repo, "update-index", "--chmod=+x", ACC)
    git(repo, "commit", "-q", "--no-edit")
    c = merge_commit(repo)
    assert _git_merged(str(repo), c, {}) == set()
    assert judge(repo, c) is not None


def test_a_conflicted_file_stays_a_finding_resolved_or_with_markers(tmp_path):
    for resolved in ("resolved\n", None):
        root = tmp_path / ("a" if resolved else "b")
        root.mkdir()
        repo = repo_with_sides(root, edit(LINES, 1, "ours"),
                               edit(LINES, 1, "theirs"))
        merge(repo, "side")
        if resolved:
            write(repo, ACC, resolved)
        git(repo, "add", "-A")
        git(repo, "commit", "-q", "--no-edit")
        c = merge_commit(repo)
        assert _git_merged(str(repo), c, {}) == set()
        res = judge(repo, c)
        assert res is not None and ACC in res[0]


def test_a_ticket_file_keeps_its_rule(tmp_path):
    path = ".tickets/T-1.md"
    repo = repo_with_sides(tmp_path, edit(LINES, 1, "ours"),
                           edit(LINES, 8, "theirs"), path=path)
    merge(repo, "side")
    c = merge_commit(repo)
    assert _git_merged(str(repo), c, {}) == set()
    assert path in _judge_commit(str(repo), c, "orchestrator", None, None,
                                 True, c[0], deny_all, {}, lift=False)[0]


def test_an_octopus_merge_gives_no_allowance(tmp_path):
    repo = repo_with_sides(tmp_path, edit(LINES, 1, "ours"),
                           edit(LINES, 8, "theirs"))
    git(repo, "checkout", "-qb", "third", "main~1")
    write(repo, "other.txt", "x\n")
    commit_all(repo, "third")
    git(repo, "checkout", "-q", "main")
    merge(repo, "side", "third")
    c = merge_commit(repo)
    assert len(c[1]) == 3
    assert _git_merged(str(repo), c, {}) == set()
    assert judge(repo, c) is not None


def test_several_merge_bases_give_no_allowance(tmp_path):
    repo = repo_with_sides(tmp_path, edit(LINES, 1, "ours"),
                           edit(LINES, 8, "theirs"))
    a1 = git(repo, "rev-parse", "main")
    merge(repo, "side")  # main: a merge of the side's first commit
    git(repo, "checkout", "-q", "side")
    git(repo, "merge", "-q", "--no-edit", "--no-ff", "-s", "ours", a1)
    write(repo, ACC, edit(edit(LINES, 1, "ours"), 8, "theirs2"))
    commit_all(repo, "side again")
    git(repo, "checkout", "-q", "main")
    write(repo, ACC, edit(edit(LINES, 1, "ours2"), 8, "theirs"))
    commit_all(repo, "main again")
    merge(repo, "side")
    assert len(git(repo, "merge-base", "--all", "main^1", "main^2").split()) == 2
    c = merge_commit(repo)
    assert _git_merged(str(repo), c, {}) == set()
    assert judge(repo, c) is not None


def test_a_merge_tree_that_fails_gives_no_allowance(tmp_path, monkeypatch):
    repo = clean_merge(tmp_path)
    c = merge_commit(repo)
    real = containment._git

    def failing(root, *args, ok=(0,)):
        if "merge-tree" in args:
            raise containment._GitError("merge-tree failed")
        return real(root, *args, ok=ok)

    monkeypatch.setattr(containment, "_git", failing)
    assert _git_merged(str(repo), c, {}) == set()
    assert judge(repo, c) is not None

    # Exit 1 with no tree id (a parent git cannot merge) is no answer.
    monkeypatch.setattr(containment, "_git", lambda root, *a, ok=(0,): (
        "" if "merge-tree" in a else real(root, *a, ok=ok)))
    assert _git_merged(str(repo), c, {}) == set()


def test_the_git_processes_are_counted_against_the_lift_budget(tmp_path):
    repo = clean_merge(tmp_path)
    c = merge_commit(repo)
    closes: dict = {}
    assert _git_merged(str(repo), c, closes) == {ACC}
    assert closes[_LIFT_LEFT] == containment._LIFT_PROCESSES - 5
    closes = {_LIFT_LEFT: 4}
    assert _git_merged(str(repo), c, closes) == set()
    assert judge(repo, c, {_LIFT_LEFT: 4}) is not None


def test_a_merge_with_no_own_acceptance_test_starts_no_git(tmp_path):
    repo = repo_with_sides(tmp_path, edit(LINES, 1, "ours"),
                           edit(LINES, 8, "theirs"), path="src/x.py")
    merge(repo, "side")
    c = merge_commit(repo)
    closes: dict = {}
    assert _git_merged(str(repo), c, closes) == set()
    assert closes == {}

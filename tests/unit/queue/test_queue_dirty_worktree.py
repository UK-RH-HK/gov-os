"""W2-115b fix (audit N-01): ``checks.dirty_files`` lists what ``git status`` says is uncommitted or untracked-and-not-
ignored in a worktree, and ``command._candidate`` refuses a branch whose worktree holds any (``QUEUE_WORKTREE_DIRTY``)."""
from __future__ import annotations

import subprocess

import pytest

from gov.cli.errors import GovError
from gov.queue import checks, command


def _git(cwd, *args):
    done = subprocess.run(["git", "-C", str(cwd), "-c", "user.name=t", "-c", "user.email=t@t", *args],
                          capture_output=True, text=True)
    assert done.returncode == 0, done.stderr
    return done.stdout


@pytest.fixture
def repo(tmp_path):
    root = tmp_path / "repo"
    root.mkdir()
    _git(root, "init", "-q", "-b", "main")
    (root / ".gitignore").write_text("build/\n*.pyc\n", encoding="utf-8")
    (root / "src").mkdir()
    (root / "src" / "a.py").write_text("A = 1\n", encoding="utf-8")
    (root / "notes.txt").write_text("n\n", encoding="utf-8")
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "--no-gpg-sign", "-m", "base")
    return root


def test_a_clean_worktree_lists_nothing(repo):
    assert checks.dirty_files(repo) == []


def test_modified_staged_deleted_and_untracked_files_are_listed(repo):
    (repo / "src" / "a.py").write_text("A = 2\n", encoding="utf-8")
    (repo / "notes.txt").unlink()
    (repo / "src" / "new.py").write_text("N = 1\n", encoding="utf-8")
    (repo / "staged.py").write_text("S = 1\n", encoding="utf-8")
    _git(repo, "add", "staged.py")
    assert checks.dirty_files(repo) == ["notes.txt", "src/a.py", "src/new.py", "staged.py"]


def test_ignored_files_are_not_dirty(repo):
    (repo / "build").mkdir()
    (repo / "build" / "out.bin").write_text("x", encoding="utf-8")
    (repo / "src" / "a.pyc").write_text("x", encoding="utf-8")
    assert checks.dirty_files(repo) == []


def test_a_file_in_an_untracked_folder_is_named_itself(repo):
    (repo / "fresh").mkdir()
    (repo / "fresh" / "x.py").write_text("X = 1\n", encoding="utf-8")
    assert checks.dirty_files(repo) == ["fresh/x.py"]


def test_a_renamed_file_names_both_paths_as_a_delete_and_an_add(repo):
    _git(repo, "mv", "notes.txt", "memo.txt")
    assert checks.dirty_files(repo) == ["memo.txt", "notes.txt"]


def test_the_check_does_not_write_the_worktree_s_index(repo):
    before = (repo / ".git" / "index").stat().st_mtime_ns
    checks.dirty_files(repo)
    assert (repo / ".git" / "index").stat().st_mtime_ns == before


def test_the_refusal_names_the_worktree_and_each_file(repo):
    (repo / "notes.txt").write_text("changed\n", encoding="utf-8")
    (repo / "src" / "new.py").write_text("N = 1\n", encoding="utf-8")
    with pytest.raises(GovError) as raised:
        command._refuse_dirty(repo, "topic/aa")
    error = raised.value
    assert error.code == "QUEUE_WORKTREE_DIRTY" and error.exit_code == 1
    assert str(repo) in error.message and "notes.txt" in error.message and "src/new.py" in error.message
    assert error.details["worktree"] == str(repo) and error.details["files"] == ["notes.txt", "src/new.py"]


def test_a_clean_worktree_is_not_refused(repo):
    command._refuse_dirty(repo, "topic/aa")

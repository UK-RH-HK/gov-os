"""Builder tests for gov.util.gitenv (W2-05, regression evidence only; the acceptance tests are W2-05's own)."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

from gov.util.gitenv import git_env

CLEAN = {"PATH": "/usr/bin:/bin", "HOME": "/nonexistent", "LC_ALL": "C", "GIT_CONFIG_NOSYSTEM": "1",
         "GIT_CONFIG_GLOBAL": os.devnull, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@example.invalid",
         "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@example.invalid"}


def _git(cwd, *args):
    return subprocess.run(["git", "-C", str(cwd), *args], capture_output=True, text=True, check=True,
                          env=CLEAN).stdout


def _repo(path: Path) -> Path:
    path.mkdir(parents=True)
    _git(path, "init", "-q", "-b", "main")
    (path / "a.txt").write_text("a\n")
    _git(path, "add", "-A")
    _git(path, "commit", "-q", "-m", "a")
    return path


@pytest.fixture()
def repo(tmp_path):
    return _repo(tmp_path / "repo")


@pytest.fixture()
def decoy(tmp_path):
    return _repo(tmp_path / "decoy")


def test_every_git_variable_is_cleared_and_lazy_fetch_is_off(repo, decoy):
    base = {"PATH": "/usr/bin:/bin", "GIT_DIR": str(decoy / ".git"), "GIT_INDEX_FILE": str(decoy / ".git/index"),
            "GIT_WORK_TREE": str(decoy), "GIT_TRACE": "/tmp/x", "GIT_TRACE2_EVENT": "/tmp/y",
            "GIT_CONFIG_COUNT": "1", "GIT_CONFIG_KEY_0": "core.pager", "GIT_CONFIG_VALUE_0": "cat", "OTHER": "kept"}
    env = git_env(repo, base=base)
    assert {k for k in env if k.startswith("GIT_")} == {"GIT_NO_LAZY_FETCH"}
    assert env["GIT_NO_LAZY_FETCH"] == "1" and env["OTHER"] == "kept" and env["PATH"] == "/usr/bin:/bin"


def test_without_a_root_nothing_is_kept(repo):
    env = git_env(None, base={"GIT_INDEX_FILE": str(repo / ".git/index")})
    assert "GIT_INDEX_FILE" not in env


def test_the_index_git_gives_the_call_for_its_own_repository_is_kept(repo):
    lock = repo / ".git" / "index.lock"
    env = git_env(repo, base={"PATH": "/usr/bin:/bin", "GIT_INDEX_FILE": str(lock)})
    assert env["GIT_INDEX_FILE"] == os.path.realpath(lock)


def test_a_relative_index_is_read_from_the_caller_s_folder(repo, monkeypatch):
    monkeypatch.chdir(repo)
    env = git_env(repo, base={"PATH": "/usr/bin:/bin", "GIT_INDEX_FILE": ".git/index"})
    assert env["GIT_INDEX_FILE"] == os.path.realpath(repo / ".git" / "index")


def test_an_index_of_another_repository_or_beside_the_git_directory_is_cleared(repo, decoy, tmp_path):
    for value in (str(decoy / ".git" / "index"), str(tmp_path / "index"), str(repo / ".gitx" / "index")):
        assert "GIT_INDEX_FILE" not in git_env(repo, base={"PATH": "/usr/bin:/bin", "GIT_INDEX_FILE": value})


def test_a_linked_worktree_keeps_its_own_index_and_another_tree_does_not(repo, tmp_path):
    tree = tmp_path / "wt"
    _git(repo, "worktree", "add", "-q", str(tree), "-b", "side")
    own = Path(_git(tree, "rev-parse", "--absolute-git-dir").strip()) / "index.lock"
    base = {"PATH": "/usr/bin:/bin", "GIT_DIR": str(own.parent), "GIT_INDEX_FILE": str(own)}
    assert git_env(tree, base=base)["GIT_INDEX_FILE"] == os.path.realpath(own)
    assert "GIT_DIR" not in git_env(tree, base=base)
    assert "GIT_INDEX_FILE" not in git_env(repo, base=base)
    assert "GIT_INDEX_FILE" not in git_env(tmp_path / "elsewhere", base=base)


def test_pinned_reads_no_global_or_xdg_configuration(repo, tmp_path):
    home, xdg = tmp_path / "home", tmp_path / "xdg"
    (xdg / "git").mkdir(parents=True)
    home.mkdir()
    (home / ".gitconfig").write_text("[w2]\n\thome = yes\n")
    (xdg / "git" / "config").write_text("[w2]\n\txdg = yes\n")
    base = {"PATH": "/usr/bin:/bin", "HOME": str(home), "XDG_CONFIG_HOME": str(xdg)}

    def read(env, key):
        return subprocess.run(["git", "-C", str(repo), "config", "--get", key], capture_output=True, text=True,
                              env=env).stdout.strip()

    plain = git_env(repo, base=base)
    assert read(plain, "w2.home") == "yes" and read(plain, "w2.xdg") == "yes"
    pinned = git_env(repo, base=base, pinned=True)
    assert read(pinned, "w2.home") == "" and read(pinned, "w2.xdg") == ""


def test_the_caller_s_environment_is_not_changed(repo, decoy, monkeypatch):
    monkeypatch.setenv("GIT_DIR", str(decoy / ".git"))
    git_env(repo)
    assert os.environ["GIT_DIR"] == str(decoy / ".git")

"""W2-94 (a fix, 2026-11-19): B3's `git archive` that is still running when the tar's last member has been read.

tarfile's stream mode stops at the tar's end-of-archive marker; a `git archive` that has not yet exited (a loaded
machine, descheduled between its last write and its exit) was then killed by build_tree's clean-up and its status
-9 was refused as 14 "archive": a good build refused, at random, under load. Here a stand-in `git` runs the real one
and holds its exit for half a second, which makes that moment certain.
"""
import os
import stat
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "governance" / "project" / "orchestration" / "tools"))
import indep_launch  # noqa: E402


def _git(repo, *a):
    return subprocess.run(["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@t", *a],
                          capture_output=True, text=True, check=True).stdout.strip()


@pytest.fixture
def repo(tmp_path):
    r = tmp_path / "repo"
    r.mkdir()
    _git(r, "init", "-q", "-b", "main")
    (r / "a.txt").write_text("a\n")
    (r / "d").mkdir()
    (r / "d" / "b.txt").write_text("b\n")
    _git(r, "add", "-A")
    _git(r, "commit", "-q", "-m", "x")
    return r


def _slow_git_on_path(tmp_path, monkeypatch, delay, rc=None):
    real = subprocess.run(["which", "git"], capture_output=True, text=True, check=True).stdout.strip()
    b = tmp_path / "slowbin"
    b.mkdir()
    g = b / "git"
    g.write_text(f'#!/bin/sh\n{real} "$@"\nrc=$?\nsleep {delay}\nexit {"$rc" if rc is None else rc}\n')
    g.chmod(g.stat().st_mode | stat.S_IEXEC)
    monkeypatch.setenv("PATH", f"{b}:{os.environ['PATH']}")


def _tree(tmp_path, repo):
    st = indep_launch.State()
    st.tree = str(tmp_path / "tree")
    return st, _git(repo, "rev-parse", "HEAD")


def test_a_git_archive_that_exits_after_its_last_byte_is_read_still_builds_the_tree(tmp_path, repo, monkeypatch):
    st, commit = _tree(tmp_path, repo)
    _slow_git_on_path(tmp_path, monkeypatch, "0.5")
    files = indep_launch.build_tree(st, str(repo), commit, lambda name, is_dir=False: False)
    assert files == 2
    assert (Path(st.tree) / "d" / "b.txt").read_text() == "b\n"


def test_a_git_archive_that_ends_with_an_error_is_still_refused_14_archive(tmp_path, repo, monkeypatch):
    st, commit = _tree(tmp_path, repo)
    _slow_git_on_path(tmp_path, monkeypatch, "0.2", rc=3)
    with pytest.raises(indep_launch.Refuse) as e:
        indep_launch.build_tree(st, str(repo), commit, lambda name, is_dir=False: False)
    assert (e.value.code, e.value.word) == (14, "archive")

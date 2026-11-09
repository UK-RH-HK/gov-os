"""Unit tests for gov.util.gitrun, the one git runner of the close and the store (W2-150 S6; DEC-500, DEC-136).

A planted repository only. ``gov.close.repo.git`` keeps its cases in tests/unit/close.
"""

from __future__ import annotations

import subprocess

import pytest

from gov.cli.errors import GovError
from gov.util import gitrun


def _plain(root, *args):
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, check=True,
                          stdin=subprocess.DEVNULL).stdout


@pytest.fixture
def repo(tmp_path):
    _plain(tmp_path, "init", "-q", "-b", "main")
    (tmp_path / "a").write_text("a\n", encoding="utf-8")
    _plain(tmp_path, "add", "a")
    _plain(tmp_path, "-c", "user.name=t", "-c", "user.email=t@localhost", "commit", "-q", "-m", "one")
    return tmp_path


def test_the_close_and_the_store_share_this_runner():
    from gov.close import repo as close_repo
    from gov.store import loader

    assert close_repo.git is gitrun.git
    assert loader._commit_git is gitrun.git


def test_output_exit_code_and_standard_input(repo):
    head = _plain(repo, "rev-parse", "HEAD")
    assert gitrun.git(repo, "rev-parse", "HEAD") == head
    assert gitrun.git(repo, "cat-file", "-e", "HEAD", code=True) == 0
    assert gitrun.git(repo, "check-ignore", "--stdin", "-z", given="a\0", ok=(0, 1), code=True) == 1


def test_an_exit_code_outside_ok_is_git_failure_with_the_arguments(repo):
    with pytest.raises(GovError) as raised:
        gitrun.git(repo, "rev-parse", "--verify", "no-such-ref")
    assert raised.value.code == "GIT_FAILURE"
    assert raised.value.message.startswith("git rev-parse failed: ")


def test_the_callers_git_variables_do_not_reach_git(repo, tmp_path_factory, monkeypatch):
    other = tmp_path_factory.mktemp("other")
    _plain(other, "init", "-q")
    monkeypatch.setenv("GIT_DIR", str(other / ".git"))
    # Without the stripping git would answer for the other, empty repository and fail.
    assert gitrun.git(repo, "rev-parse", "HEAD").strip() == _plain(repo, "--git-dir", str(repo / ".git"),
                                                                    "rev-parse", "HEAD").strip()


def test_replacement_refs_are_not_followed(repo, tmp_path):
    commit = _plain(repo, "rev-parse", "HEAD").strip()
    body = _plain(repo, "cat-file", "commit", commit).replace("one", "replaced")
    (tmp_path / "replacement").write_text(body, encoding="utf-8")
    replacement = _plain(repo, "hash-object", "-t", "commit", "-w", str(tmp_path / "replacement")).strip()
    _plain(repo, "replace", commit, replacement)
    assert "replaced" in _plain(repo, "log", "-1", "--format=%s", commit)
    assert gitrun.git(repo, "log", "-1", "--format=%s", commit).strip() == "one"

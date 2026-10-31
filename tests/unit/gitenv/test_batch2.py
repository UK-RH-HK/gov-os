"""Builder tests for W2-05's batch 2: git by absolute path from the helper, the close's calls, the decisions
checker, the record store and ``gov --version`` (regression evidence only; the acceptance tests are W2-05's own)."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from gov.close import batch, nightly, repo, tool, traceability
from gov.close.command import _started
from gov.decisions import checker
from gov.guard import containment, decide
from gov.store import loader
from gov.util import gitenv
from gov.util.gitenv import git_binary

CLEAN = {"PATH": "/usr/bin:/bin", "HOME": "/nonexistent", "LC_ALL": "C", "GIT_CONFIG_NOSYSTEM": "1",
         "GIT_CONFIG_GLOBAL": os.devnull, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@example.invalid",
         "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@example.invalid"}
PLANTED = ("GIT_DIR", "GIT_INDEX_FILE", "GIT_TRACE", "GIT_TRACE2", "GIT_TRACE2_EVENT", "GIT_TRACE_PACKET",
           "GIT_TRACE_SETUP")


def _init(path: Path, message: str = "first") -> str:
    path.mkdir(parents=True)
    for args in (["init", "-q", "-b", "main"], ["commit", "-q", "--allow-empty", "-m", f"{message}\n\nTask: T-1"]):
        subprocess.run(["git", "-C", str(path), *args], check=True, env=CLEAN)
    return subprocess.run(["git", "-C", str(path), "rev-parse", "HEAD"], check=True, env=CLEAN,
                          capture_output=True, text=True).stdout.strip()


@pytest.fixture()
def project(tmp_path):
    return tmp_path / "project", _init(tmp_path / "project")


@pytest.fixture()
def planted(tmp_path, monkeypatch):
    """A decoy repository named by every planted variable, the trace variables writing into ``traces``."""
    _init(tmp_path / "decoy", "decoy")
    traces = tmp_path / "traces"
    traces.mkdir()
    monkeypatch.setenv("GIT_DIR", str(tmp_path / "decoy" / ".git"))
    monkeypatch.setenv("GIT_INDEX_FILE", str(tmp_path / "decoy" / ".git" / "index"))
    for name in PLANTED[2:]:
        monkeypatch.setenv(name, str(traces / name))
    return traces


@pytest.fixture()
def person(tmp_path, monkeypatch):
    """The person's own configuration: an identity, and a trace setting that writes ``trace2``."""
    home = tmp_path / "home"
    home.mkdir()
    (home / ".gitconfig").write_text(f"[user]\n\tname = Person\n\temail = person@example.invalid\n"
                                     f"[trace2]\n\teventTarget = {tmp_path / 'trace2'}\n")
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("XDG_CONFIG_HOME", str(home / ".config"))
    for name in ("GIT_AUTHOR_NAME", "GIT_AUTHOR_EMAIL", "GIT_COMMITTER_NAME", "GIT_COMMITTER_EMAIL",
                 "GIT_CONFIG_COUNT", "GIT_CONFIG_GLOBAL", "GIT_CONFIG_NOSYSTEM"):
        monkeypatch.delenv(name, raising=False)
    return tmp_path / "trace2"


# -- git by absolute path (W2-L160) ---------------------------------------------------------------------------

def test_git_is_resolved_from_the_system_folders_never_from_path(tmp_path, monkeypatch):
    planted_bin = tmp_path / "bin"
    planted_bin.mkdir()
    (planted_bin / "git").write_text("#!/bin/sh\nexit 1\n")
    (planted_bin / "git").chmod(0o755)
    monkeypatch.setenv("PATH", str(planted_bin))
    found = git_binary()
    assert found is not None and os.path.isabs(found)
    assert os.path.dirname(found) in gitenv.GIT_DIRS
    assert git_binary(dirs=(str(tmp_path / "none"),)) is None


def test_the_freeze_look_up_and_containment_take_the_helper_s_git(monkeypatch):
    assert decide._git_binary() == git_binary() and decide._GIT_DIRS is gitenv.GIT_DIRS
    assert containment.git_binary is git_binary
    monkeypatch.setattr(decide, "_GIT_DIRS", ())
    assert decide._git_binary() is None


def test_containment_refuses_when_no_git_is_resolved(project, monkeypatch):
    root, _head = project
    assert containment._git(str(root), "rev-parse", "HEAD").strip() == _head
    monkeypatch.setattr(containment, "git_binary", lambda: None)
    with pytest.raises(containment._GitError, match="no git"):
        containment._git(str(root), "rev-parse", "HEAD")
    with pytest.raises(containment._GitError, match="no git"):
        containment._is_ancestor(str(root), _head, _head)
    with pytest.raises(containment.ContainmentError):
        containment.judge_commits(str(root), [_head])


# -- the close (W2-M161) --------------------------------------------------------------------------------------

def test_the_close_s_git_reads_its_own_repository_under_planted_variables(project, planted):
    root, head = project
    assert repo.git(root, "rev-parse", "HEAD").strip() == head
    assert [c["sha"] for c in traceability._commits_for_ticket(root, "T-1")] == [head]
    assert traceability._read_trailers(root, head) == {"Task": ["T-1"]}
    assert not list(planted.iterdir())


def test_the_close_s_reads_are_pinned_and_its_commits_keep_the_person_s_identity(project, person):
    root, _head = project
    repo.git(root, "rev-parse", "HEAD")
    traceability._commits_for_ticket(root, "T-1")
    assert not person.exists()  # the person's trace setting was not read
    (root / "a.txt").write_text("a\n")
    commit = batch._commit(root, "a record", ["a.txt"], task="T-1")
    author = repo.git(root, "log", "-1", "--format=%an <%ae>", commit).strip()
    assert author == "Person <person@example.invalid>"


def test_the_close_s_commits_without_an_identity_are_gov_s(project, tmp_path, monkeypatch):
    root, _head = project
    home = tmp_path / "empty-home"
    home.mkdir()
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("XDG_CONFIG_HOME", str(home / ".config"))
    monkeypatch.setenv("GIT_AUTHOR_EMAIL", "caller@example.invalid")  # the caller's: not passed on (DEC-500)
    (root / "b.txt").write_text("b\n")
    commit = batch._commit(root, "b record", ["b.txt"])
    assert repo.git(root, "log", "-1", "--format=%ae %ce", commit).strip() == "gov@localhost gov@localhost"


def test_the_close_s_started_programs_get_no_git_variable_of_the_caller(project, planted):
    root, _head = project
    show = [sys.executable, "-c", "import json, os; print(json.dumps(dict(os.environ)))"]
    env = {**os.environ, "PYTHONPATH": str(root / "src"), "GOV_SOME_CHECK_RESULT": "x"}
    seen = json.loads(_started(root, show, env).stdout)
    assert not [name for name in PLANTED if name in seen]
    assert seen["PYTHONPATH"] == str(root / "src") and seen["GOV_SOME_CHECK_RESULT"] == "x"
    assert seen["GIT_NO_LAZY_FETCH"] == "1"


def test_the_ticket_tool_runs_in_the_root_with_its_tickets_folder(project, planted, tmp_path, monkeypatch):
    root, _head = project
    tk = tmp_path / "tk"
    tk.write_text("#!/bin/sh\nenv\n")
    tk.chmod(0o755)
    monkeypatch.setattr(tool, "find", lambda _root: tk)
    lines = tool.tk(root, "show").splitlines()
    assert f"TICKETS_DIR={root / '.tickets'}" in lines
    assert not [line for line in lines if line.split("=", 1)[0] in PLANTED]


def test_the_nightly_removes_its_clone_under_a_planted_git_dir(project, planted, tmp_path):
    root, head = project
    tree = tmp_path / "clone"
    subprocess.run(["git", "-C", str(root), "worktree", "add", "-q", "--detach", str(tree), head], check=True,
                   env=CLEAN)
    entry = nightly._entry_of(tree)
    assert nightly._remove_clone(root, tree, entry) is None
    assert not tree.exists()
    assert not list(planted.iterdir())


# -- the decisions checker, the record store, gov --version ---------------------------------------------------

def test_the_checker_and_the_store_read_their_own_repository_pinned(project, planted, person):
    root, head = project
    assert checker._git(root, "rev-parse", "HEAD").decode().strip() == head
    assert loader._git(root, "rev-parse", "HEAD").decode().strip() == head
    reader = checker._Objects(root)
    try:
        assert reader.read(head)[0] == head
    finally:
        reader.close()
    env = checker._environment(root)
    assert env["GIT_CONFIG_GLOBAL"] == os.devnull and env["GIT_GRAFT_FILE"] == os.devnull
    assert not [name for name in PLANTED if name in env]
    assert not person.exists() and not list(planted.iterdir())


def test_the_version_names_this_tree_s_commit_under_a_planted_git_dir(planted):
    from gov.cli import main
    tree = Path(main.__file__).resolve().parents[2]
    head = subprocess.run(["git", "-C", str(tree), "rev-parse", "HEAD"], capture_output=True, text=True,
                          env={k: v for k, v in os.environ.items() if not k.startswith("GIT_")}).stdout.strip()
    assert main._version().endswith(f"(commit {head})")
    assert not list(planted.iterdir())

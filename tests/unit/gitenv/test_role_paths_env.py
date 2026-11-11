"""Builder tests for the git calls of gov.util.role_paths (W2-05 S1 and F1, sweep row 71; DEC-710, DEC-712, DEC-580).

``main_tree``, ``linked_tests``, ``changed`` and ``engineer_side`` each start git in a folder they name (``-C``). Each
takes its environment from ``gov.util.gitenv.git_env(<that folder>, pinned=True)`` and starts git by
``git_binary()``: no inherited location, index, trace or configuration variable reaches it, lazy fetching is off,
the system's and the person's configuration are unread, and no ``git`` that comes first on ``PATH`` is run. With no
git in the system's folders each takes its "git cannot say" route (``main_tree``: the folder given; the others:
None), never a git from ``PATH``. Every repository here is built in ``tmp_path`` from scratch.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov.util import gitenv, role_paths  # noqa: E402

GIT = gitenv.git_binary()
NAMES = {"DAEO-pier", "W2-99"}
WBS = "W2-99"
CHANGED = {"src/a.py", "tests/acceptance/W2-99/test_x.py", "tests/acceptance/W2-98/test_y.py", "scratch.py"}
CARRIED = {"src/a.py"}
LINKED = {"tests/acceptance/W2-98/test_y.py"}


def _build_env(home: Path) -> dict:
    return {"PATH": os.environ.get("PATH", ""), "HOME": str(home), "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_CONFIG_GLOBAL": os.devnull}


def _git(where: Path, *args, home: Path) -> str:
    return subprocess.run([GIT, "-c", "user.name=t", "-c", "user.email=t@example.invalid", "-C", str(where), *args],
                          check=True, capture_output=True, text=True, env=_build_env(home)).stdout


def _write(at: Path, rel: str, text: str = "x\n") -> None:
    (at / rel).parent.mkdir(parents=True, exist_ok=True)
    (at / rel).write_text(text, encoding="utf-8")


def _repository(at: Path, home: Path) -> Path:
    """w2/integrate (one commit); w2/W2-99 from it (src/a.py); w2/W2-99-tests from that, checked out, with the test
    designer's commit for DAEO-pier (its own folder and another ticket's); one untracked file."""
    at.mkdir()
    _git(at, "init", "-q", "-b", "w2/integrate", home=home)
    _write(at, "README", "base\n")
    _git(at, "add", "README", home=home)
    _git(at, "commit", "-q", "-m", "base", home=home)
    _git(at, "checkout", "-q", "-b", "w2/W2-99", home=home)
    _write(at, "src/a.py")
    _git(at, "add", "src/a.py", home=home)
    _git(at, "commit", "-q", "-m", "engineer", home=home)
    _git(at, "checkout", "-q", "-b", "w2/W2-99-tests", home=home)
    _write(at, "tests/acceptance/W2-99/test_x.py")
    _write(at, "tests/acceptance/W2-98/test_y.py")
    _git(at, "add", "tests", home=home)
    _git(at, "commit", "-q", "-m", "cases\n\nTask: DAEO-pier\nRole: independent-test-designer\n", home=home)
    _write(at, "scratch.py")
    return at


def _foreign(at: Path, home: Path) -> Path:
    at.mkdir()
    _git(at, "init", "-q", "-b", "main", home=home)
    _write(at, "f.txt")
    _git(at, "add", "f.txt", home=home)
    _git(at, "commit", "-q", "-m", "foreign", home=home)
    return at


def _state(repo: Path) -> dict:
    git_dir = repo / ".git"
    return {"index": (git_dir / "index").read_bytes(), "head": (git_dir / "HEAD").read_text(),
            "refs": sorted(str(p.relative_to(git_dir)) for p in (git_dir / "refs").rglob("*")),
            "config": (git_dir / "config").read_text()}


@pytest.fixture()
def world(tmp_path, monkeypatch):
    """A repository, a foreign one, a HOME and XDG folder of the test's own, no GIT_* variable, a fresh link cache."""
    home = tmp_path / "home"
    (home / ".config").mkdir(parents=True)
    for key in list(os.environ):
        if key.startswith("GIT_"):
            monkeypatch.delenv(key)
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("XDG_CONFIG_HOME", str(home / ".config"))
    monkeypatch.setattr(role_paths, "LINK_CACHE", str(tmp_path / "link-cache"))
    build_home = tmp_path / "build-home"
    build_home.mkdir()
    repo = _repository(tmp_path / "repo", build_home)
    foreign = _foreign(tmp_path / "foreign", build_home)
    return {"tmp": tmp_path, "home": home, "repo": repo, "foreign": foreign}


def _answers(repo: Path) -> dict:
    return {"main_tree": role_paths.main_tree(repo / "src"), "changed": role_paths.changed(str(repo)),
            "engineer_side": role_paths.engineer_side(str(repo), WBS),
            "linked_tests": role_paths.linked_tests(str(repo), NAMES, WBS)}


def _expected(repo: Path) -> dict:
    return {"main_tree": os.path.realpath(repo), "changed": CHANGED, "engineer_side": CARRIED, "linked_tests": LINKED}


def test_the_four_calls_answer_as_before_on_an_ordinary_repository(world):
    assert _answers(world["repo"]) == _expected(world["repo"])


def test_a_planted_location_index_trace_or_global_configuration_reaches_no_call(world, monkeypatch):
    tmp, foreign = world["tmp"], world["foreign"]
    before = _state(foreign)
    (tmp / "global").write_text(f"[trace2]\n\teventTarget = {tmp / 'global-trace2'}\n", encoding="utf-8")
    monkeypatch.setenv("GIT_DIR", str(foreign / ".git"))
    monkeypatch.setenv("GIT_INDEX_FILE", str(foreign / ".git" / "index"))
    monkeypatch.setenv("GIT_TRACE", str(tmp / "trace.log"))
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", str(tmp / "global"))
    assert _answers(world["repo"]) == _expected(world["repo"])
    assert not (tmp / "trace.log").exists()
    assert not (tmp / "global-trace2").exists()
    assert _state(foreign) == before


def test_the_persons_own_configuration_is_unread(world):
    """A ~/.gitconfig of the caller's HOME that sets a trace2 target: no call writes it (the configuration pinned)."""
    tmp, home = world["tmp"], world["home"]
    (home / ".gitconfig").write_text(f"[trace2]\n\teventTarget = {tmp / 'home-trace2'}\n", encoding="utf-8")
    (home / ".config" / "git").mkdir()
    (home / ".config" / "git" / "config").write_text(f"[trace2]\n\tperfTarget = {tmp / 'xdg-trace2'}\n",
                                                      encoding="utf-8")
    assert _answers(world["repo"]) == _expected(world["repo"])
    assert not (tmp / "home-trace2").exists()
    assert not (tmp / "xdg-trace2").exists()


def test_every_call_has_lazy_fetch_off_the_configuration_pinned_and_git_by_absolute_path(world, monkeypatch):
    monkeypatch.setenv("GIT_DIR", str(world["foreign"] / ".git"))
    monkeypatch.setenv("GIT_TRACE", str(world["tmp"] / "trace.log"))
    seen = []
    real = subprocess.run

    def spy(argv, *args, **kwargs):
        if "-C" in argv:
            seen.append((list(argv), dict(kwargs.get("env") or {})))
        return real(argv, *args, **kwargs)
    monkeypatch.setattr(role_paths.subprocess, "run", spy)
    counts = {}
    for name, call in (("main_tree", lambda: role_paths.main_tree(world["repo"])),
                       ("changed", lambda: role_paths.changed(str(world["repo"]))),
                       ("engineer_side", lambda: role_paths.engineer_side(str(world["repo"]), WBS)),
                       ("linked_tests", lambda: role_paths.linked_tests(str(world["repo"]), NAMES, WBS))):
        start = len(seen)
        call()
        counts[name] = len(seen) - start
    assert all(counts.values()), counts
    for argv, env in seen:
        assert argv[0] == GIT and os.path.isabs(argv[0]), argv
        assert env.get("GIT_NO_LAZY_FETCH") == "1", argv
        assert env.get("GIT_CONFIG_NOSYSTEM") == "1" and env.get("GIT_CONFIG_GLOBAL") == os.devnull, argv
        assert not {"GIT_DIR", "GIT_TRACE", "GIT_INDEX_FILE"} & set(env), argv


def _logging_git(world) -> Path:
    """A ``git`` first on ``PATH`` that writes each call to a log and then runs the system's git."""
    bin_dir, log = world["tmp"] / "bin", world["tmp"] / "path-git.log"
    bin_dir.mkdir()
    (bin_dir / "git").write_text(f'#!/bin/sh\necho "$@" >> "{log}"\nexec "{GIT}" "$@"\n', encoding="utf-8")
    (bin_dir / "git").chmod(0o755)
    return log


def test_a_git_first_on_path_is_never_run(world, monkeypatch):
    log = _logging_git(world)
    monkeypatch.setenv("PATH", f"{world['tmp'] / 'bin'}{os.pathsep}{os.environ['PATH']}")
    assert _answers(world["repo"]) == _expected(world["repo"])
    assert not log.exists(), log.read_text()


def test_no_git_in_the_systems_folders_is_git_cannot_say_never_a_git_from_path(world, monkeypatch):
    log = _logging_git(world)
    monkeypatch.setenv("PATH", f"{world['tmp'] / 'bin'}{os.pathsep}{os.environ['PATH']}")
    empty = world["tmp"] / "no-git"
    empty.mkdir()
    monkeypatch.setattr(gitenv, "GIT_DIRS", (str(empty),))
    assert gitenv.git_binary() is None
    repo = world["repo"]
    assert role_paths.main_tree(repo / "src") == os.path.realpath(repo / "src")
    assert role_paths.changed(str(repo)) is None
    assert role_paths.engineer_side(str(repo), WBS) is None
    assert role_paths.linked_tests(str(repo), NAMES, WBS) is None
    assert not log.exists(), log.read_text()


def test_changed_lists_a_file_only_the_persons_configured_ignore_file_hides(world):
    """Row 71's decision: ``changed``'s ``ls-files --others --exclude-standard`` is pinned too, so an ignore file the
    person names in ~/.gitconfig (``core.excludesFile``) is unread and an untracked file it alone hides is counted as
    changed (withheld, never handed out); the repository's own ``.gitignore`` still applies."""
    home, repo = world["home"], world["repo"]
    (home / "person-ignore").write_text("*.secret\n", encoding="utf-8")
    (home / ".gitconfig").write_text(f"[core]\n\texcludesFile = {home / 'person-ignore'}\n", encoding="utf-8")
    _write(repo, "hidden.secret")
    _write(repo, ".gitignore", "*.repo\n")
    _write(repo, "ignored.repo")
    assert role_paths.changed(str(repo)) == CHANGED | {"hidden.secret", ".gitignore"}

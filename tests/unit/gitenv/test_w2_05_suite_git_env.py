"""The tests' half of the ``core.bare`` fix (W2-05, DAEO-0z8c; DEC-1074 (8), DEC-1083, DEC-1109 (2)).

On 2026-11-04 the project's ``.git/config`` went to ``core.bare = true`` one second after a ``git bisect run`` of a
test in a linked worktree: ``git bisect run`` (and git's hooks) export ``GIT_DIR`` and git's other repository-local
variables to what they start, and a case's ``git init`` in a folder of its own, with an environment of
``{**os.environ}``, then re-initialises the repository they name. ``tests/conftest.py`` removes those variables
from every process of a run; these cases start a nested pytest with this repository's ``tests/conftest.py`` in
force (as a plugin, from its own file) and git's variables in its environment, on a sacrificial repository.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

CONFTEST_DIR = Path(__file__).resolve().parents[2]  # this repository's tests/, holding conftest.py
IDENTITY = ["-c", "user.name=Sacrifice", "-c", "user.email=sacrifice@example.invalid"]

# git 2.43's ``git rev-parse --local-env-vars``.
LOCAL = ["GIT_ALTERNATE_OBJECT_DIRECTORIES", "GIT_CONFIG", "GIT_CONFIG_PARAMETERS", "GIT_CONFIG_COUNT",
         "GIT_OBJECT_DIRECTORY", "GIT_DIR", "GIT_WORK_TREE", "GIT_IMPLICIT_WORK_TREE", "GIT_GRAFT_FILE",
         "GIT_INDEX_FILE", "GIT_NO_REPLACE_OBJECTS", "GIT_REPLACE_REF_BASE", "GIT_PREFIX", "GIT_SHALLOW_FILE",
         "GIT_COMMON_DIR"]

try:
    import xdist  # noqa: F401
    MODES = ["alone", "xdist"]
except ImportError:
    MODES = ["alone"]

INIT_TEST = '''
import os, subprocess


def test_init_in_a_folder_of_its_own(tmp_path):
    done = subprocess.run(["git", "init", "-q"], cwd=tmp_path, env={**os.environ}, capture_output=True, text=True)
    assert done.returncode == 0, done.stderr
'''

ENV_TEST = '''
import json, os


def test_record_the_environment():
    with open({record!r}, "w", encoding="utf-8") as handle:
        json.dump(sorted(name for name in os.environ if name.startswith("GIT_")), handle)
'''


def _clean_env() -> dict:
    """This process's environment less every ``GIT_*``, git's system and global config cut off."""
    env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    env.update({"GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull})
    return env


def _git(*args: str) -> str:
    return subprocess.run(["git", *IDENTITY, *args], check=True, capture_output=True, text=True,
                          env=_clean_env()).stdout


def _sacrifice(tmp_path: Path) -> tuple[Path, Path]:
    """A sacrificial repository with one commit and a linked worktree: its git folder and the worktree's."""
    project, tree = tmp_path / "project", tmp_path / "tree"
    project.mkdir()
    _git("-C", str(project), "init", "-q", "-b", "main")
    (project / "a.txt").write_text("one\n", encoding="utf-8")
    _git("-C", str(project), "add", "a.txt")
    _git("-C", str(project), "commit", "-q", "-m", "one")
    _git("-C", str(project), "worktree", "add", "-q", "-b", "side", str(tree))
    gitdir = project / ".git" / "worktrees" / "tree"
    assert (gitdir / "commondir").is_file()
    return project / ".git", gitdir


def _state(common: Path, gitdir: Path) -> dict:
    """The sacrificial repository's core.bare, its config, its refs and both HEADs, read from its files."""
    return {"bare": _git("config", "-f", str(common / "config"), "--get", "core.bare").strip(),
            "config": (common / "config").read_text(encoding="utf-8"),
            "refs": _git(f"--git-dir={common}", "for-each-ref", "--format=%(refname) %(objectname)"),
            "head": (common / "HEAD").read_text(encoding="utf-8"),
            "tree head": (gitdir / "HEAD").read_text(encoding="utf-8")}


def _nested(tmp_path: Path, test: str, env_extra: dict, mode: str = "alone", path: str | None = None) -> None:
    """Run ``test`` (a test file's text) in a nested pytest with this repository's conftest in force."""
    planted = tmp_path / "planted"
    planted.mkdir()
    (planted / "pytest.ini").write_text("[pytest]\n", encoding="utf-8")
    (planted / "test_planted.py").write_text(test, encoding="utf-8")
    nested_tmp = tmp_path / "nested-tmp"
    nested_tmp.mkdir()
    env = _clean_env()
    # The conftest needs no gov: only its own folder is on the path.
    env.update({"PYTHONPATH": str(CONFTEST_DIR), "TMPDIR": str(nested_tmp), **env_extra})
    if path is not None:
        env["PATH"] = path
    args = [sys.executable, "-m", "pytest", "-c", str(planted / "pytest.ini"), "-p", "conftest",
            "-p", "no:cacheprovider", "-q", "-o", "tmp_path_retention_policy=failed", str(planted / "test_planted.py")]
    if mode == "xdist":
        args[3:3] = ["-p", "xdist", "-n", "2"]
    done = subprocess.run(args, cwd=planted, env=env, capture_output=True, text=True, timeout=180)
    assert done.returncode == 0, done.stdout + done.stderr
    assert "1 passed" in done.stdout, done.stdout


@pytest.mark.parametrize("mode", MODES)
def test_a_case_s_git_init_never_reaches_the_repository_git_dir_names(tmp_path, mode):
    common, gitdir = _sacrifice(tmp_path)
    before = _state(common, gitdir)
    assert before["bare"] == "false"

    _nested(tmp_path, INIT_TEST, {"GIT_DIR": str(gitdir)}, mode)

    after = _state(common, gitdir)
    assert after["bare"] == "false", f"the sacrificial repository's core.bare is now {after['bare']}"
    assert after == before


@pytest.mark.parametrize("git_answers", [True, False], ids=["git-answers", "no-git-on-path"])
def test_every_repository_local_variable_is_gone_and_no_other(tmp_path, git_answers):
    common, gitdir = _sacrifice(tmp_path)
    record = tmp_path / "seen.json"
    planted = {name: str(gitdir) for name in LOCAL}
    planted.update({"GIT_CONFIG_COUNT": "1", "GIT_CONFIG_KEY_0": "core.bare", "GIT_CONFIG_VALUE_0": "true",
                    "GIT_CONFIG_KEY_7": "user.name", "GIT_CONFIG_VALUE_7": "x",
                    "GIT_AUTHOR_NAME": "kept", "GIT_TRACE2_EVENT_NESTING": "2"})
    empty = tmp_path / "no-git"
    empty.mkdir()
    _nested(tmp_path, ENV_TEST.format(record=str(record)), planted, path=None if git_answers else str(empty))
    seen = json.loads(record.read_text(encoding="utf-8"))
    # Kept: the variables that are not repository-local, and those _clean_env sets.
    assert seen == ["GIT_AUTHOR_NAME", "GIT_CONFIG_GLOBAL", "GIT_CONFIG_NOSYSTEM", "GIT_TRACE2_EVENT_NESTING"]
    assert _state(common, gitdir)["bare"] == "false"


def test_a_case_may_set_a_local_variable_itself(monkeypatch, tmp_path):
    monkeypatch.setenv("GIT_DIR", str(tmp_path / "own.git"))
    assert os.environ["GIT_DIR"] == str(tmp_path / "own.git")

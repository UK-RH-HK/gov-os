"""Builder tests for W2-05's package I (b) (DEC-970): the test runs get the person's ``user.name``, ``user.email``
and ``init.defaultBranch``, and nothing else of the person's git configuration (regression evidence only; the
acceptance tests are W2-05's own)."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from gov.close import nightly
from gov.close.command import _started
from gov.util.gitenv import runner_env

KEYS = ["init.defaultbranch=trunk", "user.email=xdg@example.invalid", "user.name=Person"]
SHOW = [sys.executable, "-c", "import json, os; print(json.dumps(dict(os.environ)))"]


def _listed(path: str) -> list[str]:
    """Every setting of the file at ``path``, read with nothing else of git's configuration."""
    env = {"PATH": "/usr/bin:/bin", "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull}
    return sorted(subprocess.run(["git", "config", "--file", path, "--list"], capture_output=True, text=True,
                                 env=env).stdout.splitlines())


@pytest.fixture()
def home(tmp_path, monkeypatch):
    """A stand-in home: the three keys between its XDG file and its ``.gitconfig`` (the later winning), and a trace
    setting, a hook path, an include and an alias that must not reach a test run."""
    home = tmp_path / "home"
    (home / ".config" / "git").mkdir(parents=True)
    (home / ".config" / "git" / "config").write_text(
        "[user]\n\tname = Xdg\n\temail = xdg@example.invalid\n[init]\n\tdefaultBranch = trunk\n")
    (tmp_path / "included").write_text("[user]\n\temail = included@example.invalid\n")
    (home / ".gitconfig").write_text(
        f"[user]\n\tname = Person\n[include]\n\tpath = {tmp_path / 'included'}\n"
        f"[trace2]\n\teventTarget = {tmp_path / 'trace2'}\n[core]\n\thooksPath = {tmp_path / 'hooks'}\n"
        "[alias]\n\tco = checkout\n")
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("XDG_CONFIG_HOME", str(home / ".config"))
    for name in [name for name in os.environ if name.startswith("GIT_")]:
        monkeypatch.delenv(name)
    return home


def test_the_file_holds_the_three_keys_and_nothing_else(home, tmp_path):
    with runner_env() as env:
        assert _listed(env["GIT_CONFIG_GLOBAL"]) == KEYS
        text = Path(env["GIT_CONFIG_GLOBAL"]).read_text()
    for word in ("trace2", "hooksPath", "include", "alias", "Xdg"):
        assert word not in text
    assert env["GIT_CONFIG_NOSYSTEM"] == "1" and env["GIT_NO_LAZY_FETCH"] == "1"
    assert not (tmp_path / "trace2").exists()  # reading the person's files wrote nothing


def test_the_xdg_file_is_found_under_home_without_xdg_config_home(home, monkeypatch):
    monkeypatch.delenv("XDG_CONFIG_HOME")
    with runner_env() as env:
        assert _listed(env["GIT_CONFIG_GLOBAL"]) == KEYS


def test_home_and_xdg_are_taken_from_the_base(home, tmp_path):
    empty = tmp_path / "empty"
    empty.mkdir()
    with runner_env(base={"PATH": "/usr/bin:/bin", "HOME": str(empty)}) as env:
        assert _listed(env["GIT_CONFIG_GLOBAL"]) == []
    with runner_env(base={"PATH": "/usr/bin:/bin", "HOME": str(empty), "XDG_CONFIG_HOME": str(home / ".config")}) \
            as env:
        assert _listed(env["GIT_CONFIG_GLOBAL"]) == ["init.defaultbranch=trunk", "user.email=xdg@example.invalid",
                                                     "user.name=Xdg"]


def test_no_identity_found_invents_none(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path / "nobody"))
    monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
    with runner_env() as env:
        assert _listed(env["GIT_CONFIG_GLOBAL"]) == []


def test_a_value_is_written_as_given(tmp_path, monkeypatch):
    home = tmp_path / "home"
    home.mkdir()
    (home / ".gitconfig").write_text('[user]\n\tname = "A \\"Q\\" \\\\ B ; #x"\n')
    monkeypatch.setenv("HOME", str(home))
    with runner_env() as env:
        assert _listed(env["GIT_CONFIG_GLOBAL"]) == ['user.name=A "Q" \\ B ; #x']


def test_a_git_run_commits_with_the_person_s_identity_and_default_branch(home, tmp_path):
    repo = tmp_path / "repo"
    with runner_env() as env:
        for args in (["init", "-q", str(repo)], ["-C", str(repo), "commit", "-q", "--allow-empty", "-m", "x"]):
            subprocess.run(["git", *args], check=True, env=env)
        shown = subprocess.run(["git", "-C", str(repo), "log", "-1", "--format=%an <%ae>%n%D"], check=True,
                               env=env, capture_output=True, text=True).stdout.split("\n")
    assert shown[:2] == ["Person <xdg@example.invalid>", "HEAD -> trunk"]
    assert not (tmp_path / "trace2").exists()


def test_the_repository_s_own_identity_wins(home, tmp_path):
    repo = tmp_path / "repo"
    with runner_env() as env:
        for args in (["init", "-q", str(repo)], ["-C", str(repo), "config", "user.name", "Own"],
                     ["-C", str(repo), "commit", "-q", "--allow-empty", "-m", "x"]):
            subprocess.run(["git", *args], check=True, env=env)
        author = subprocess.run(["git", "-C", str(repo), "log", "-1", "--format=%an"], check=True, env=env,
                                capture_output=True, text=True).stdout.strip()
    assert author == "Own"


def test_the_file_is_gone_once_the_run_ends(home, tmp_path):
    root = tmp_path / "project"
    root.mkdir()
    probe = [sys.executable, "-c", "import os; p = os.environ['GIT_CONFIG_GLOBAL']; print(p, os.path.isfile(p))"]
    path, there = _started(root, probe, dict(os.environ)).stdout.split()
    assert there == "True" and not os.path.exists(path) and not os.path.exists(os.path.dirname(path))
    assert not Path(path).resolve().is_relative_to(root.resolve())
    assert not list(root.iterdir())


def test_the_caller_s_git_variables_reach_nothing(home, tmp_path, monkeypatch):
    root = tmp_path / "project"
    root.mkdir()
    planted = {"GIT_DIR": str(tmp_path / "decoy" / ".git"), "GIT_INDEX_FILE": str(tmp_path / "decoy" / "index"),
               "GIT_TRACE2_EVENT": str(tmp_path / "trace-event"), "GIT_CONFIG_GLOBAL": str(tmp_path / "planted")}
    (tmp_path / "planted").write_text(f"[trace2]\n\teventTarget = {tmp_path / 'trace-planted'}\n")
    for name, value in planted.items():
        monkeypatch.setenv(name, value)
    seen = json.loads(_started(root, SHOW, dict(os.environ)).stdout)
    assert sorted(name for name in seen if name.startswith("GIT_")) == [
        "GIT_CONFIG_GLOBAL", "GIT_CONFIG_NOSYSTEM", "GIT_NO_LAZY_FETCH"]
    assert seen["GIT_CONFIG_GLOBAL"] not in (planted["GIT_CONFIG_GLOBAL"], os.devnull)
    with runner_env() as env:
        assert not [name for name in planted if env.get(name) == planted[name]]
        assert _listed(env["GIT_CONFIG_GLOBAL"]) == KEYS
    for name in ("trace2", "trace-event", "trace-planted"):
        assert not (tmp_path / name).exists()


def test_the_bisect_runs_in_a_test_run_s_environment(home, tmp_path, monkeypatch):
    root = tmp_path / "project"
    root.mkdir()
    monkeypatch.setenv("GIT_DIR", str(tmp_path / "decoy"))
    env = {**os.environ, "PYTHONPATH": str(root / "src")}
    run = json.loads(_started(root, SHOW, env).stdout)
    seen, real = [], subprocess.run

    def fake(args, *rest, **kwargs):
        if args[:1] == ["git"] and "bisect" in args:
            given = kwargs["env"]
            seen.append((args[4], dict(given), _listed(given["GIT_CONFIG_GLOBAL"])))
            return subprocess.CompletedProcess(args, 0, "", "")
        return real(args, *rest, **kwargs)

    monkeypatch.setattr(nightly.subprocess, "run", fake)
    monkeypatch.setattr(nightly, "_git", lambda *args, **kwargs: "")
    assert nightly._bisect(root, "a" * 40, "b" * 40, "tests/t.py::t", [], env) is None
    assert [step for step, _env, _keys in seen] == ["start", "run", "reset"]
    for step, given, keys in seen:
        handed = given.pop(nightly._STEP_ENV, None)
        # Only ``bisect run`` hands the step the run's environment for its tests (R4-1): that same environment.
        assert (handed is not None) == (step == "run")
        assert handed is None or json.loads(handed) == given
        assert keys == KEYS
        assert {k: v for k, v in given.items() if k != "GIT_CONFIG_GLOBAL"} == \
            {k: v for k, v in run.items() if k != "GIT_CONFIG_GLOBAL"}
        assert not os.path.exists(given["GIT_CONFIG_GLOBAL"])  # removed once the bisect ended

"""Emergency 2 (CAP-05; audit 7 C-1): with the guard gone, gov launch honours gov pause's freeze flag itself."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from gov.cli.errors import GovError
from gov.launch import launcher


def _git(*args, cwd):
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True)


@pytest.fixture
def repo(tmp_path):
    main = tmp_path / "main"
    main.mkdir()
    _git("init", "-q", "-b", "main", cwd=main)
    _git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty", "-m", "base", cwd=main)
    tree = tmp_path / "tree"
    _git("worktree", "add", "-q", "-b", "w", str(tree), cwd=main)
    return main.resolve(), tree.resolve()


def _freeze(root: Path, text: str = "FROZEN owner 2026-11-17T22:00:00Z\n") -> None:
    (root / ".gov-runtime").mkdir(exist_ok=True)
    (root / ".gov-runtime/freeze").write_text(text, encoding="utf-8")


def test_no_flag_lets_the_launch_go_on(repo):
    main, tree = repo
    launcher._check_not_paused(main)
    launcher._check_not_paused(tree)


def test_the_main_checkouts_flag_refuses_a_launch_in_a_worktree(repo):
    main, tree = repo
    _freeze(main)
    with pytest.raises(GovError) as refused:
        launcher._check_not_paused(tree)
    assert refused.value.code == "LAUNCH_REFUSED" and "paused" in refused.value.message


def test_the_worktrees_own_flag_refuses(repo):
    _, tree = repo
    _freeze(tree)
    with pytest.raises(GovError):
        launcher._check_not_paused(tree)


def test_an_empty_flag_is_no_pause(repo):
    main, tree = repo
    _freeze(main, "")
    launcher._check_not_paused(tree)


def test_a_worker_launch_is_refused_while_paused(repo, monkeypatch):
    """The check runs in launch() itself, before any session or record is made."""
    main, _ = repo
    _freeze(main)
    monkeypatch.setattr(launcher, "_check_ticket", lambda *a: None)
    started = []
    monkeypatch.setattr(launcher, "_run", lambda *a, **k: started.append(a) or 0)
    with pytest.raises(GovError) as refused:
        launcher.launch(main, "engineer", "DAEO-x", [])
    assert "paused" in refused.value.message and not started


# Emergency 2 (2.3): the launcher passes the no-prompt mode unless the caller names a mode
@pytest.mark.parametrize("args, expected", [
    ([], ["--permission-mode", "bypassPermissions"]),
    (["-p", "x"], ["--permission-mode", "bypassPermissions"]),
    (["--permission-mode", "acceptEdits"], []),
    (["--permission-mode=plan"], []),
    (["--dangerously-skip-permissions"], []),
])
def test_the_no_prompt_mode_is_the_default(args, expected):
    assert launcher._mode_args(args) == expected

"""``run_backup`` on a small repository: the caller's GIT_* variables, the temporary name, a dest inside (W2-198; regression)."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov.backup import bundle  # noqa: E402


def _git(cwd, *args):
    subprocess.run(["git", "-C", str(cwd), "-c", "user.name=t", "-c", "user.email=t@t", *args], check=True,
                   capture_output=True)


@pytest.fixture
def repo(tmp_path):
    root = tmp_path / "proj"
    root.mkdir()
    _git(root, "init", "-q", "-b", "main")
    _git(root, "commit", "-q", "--allow-empty", "-m", "one")
    return root


def test_a_caller_git_dir_does_not_redirect_the_bundle(repo, tmp_path, monkeypatch):
    other = tmp_path / "other"
    other.mkdir()
    _git(other, "init", "-q")
    monkeypatch.setenv("GIT_DIR", str(other / ".git"))
    result = bundle.run_backup(repo, str(tmp_path / "dest"), None, 48, 30)
    assert result["refs"] >= 2 and result["verified"] is True
    assert Path(result["file"]).name.startswith("proj-")


def test_only_the_bundle_remains_in_dest_after_a_run(repo, tmp_path):
    dest = tmp_path / "dest"
    made = bundle.run_backup(repo, str(dest), None, 48, 30)
    assert [p.name for p in dest.iterdir()] == [Path(made["file"]).name]


def test_a_dest_inside_the_repository_is_refused_and_nothing_is_written(repo):
    with pytest.raises(bundle.BackupError) as raised:
        bundle.run_backup(repo, str(repo / "sub" / "deep"), None, 48, 30)
    assert raised.value.code == "BACKUP_DEST_INSIDE"
    assert not (repo / "sub").exists()


def test_a_repository_without_a_commit_is_refused_before_dest_exists(tmp_path):
    empty = tmp_path / "empty"
    empty.mkdir()
    _git(empty, "init", "-q")
    with pytest.raises(bundle.BackupError) as raised:
        bundle.run_backup(empty, str(tmp_path / "dest"), None, 48, 30)
    assert raised.value.code == "BACKUP_FAILED"
    assert not (tmp_path / "dest").exists()

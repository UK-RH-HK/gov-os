"""W2-213 slice 1: what the check reads of a repository (SL-6, SL-7, SL-10). Regression evidence only (DEC-136)."""
from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from gov.layout import CannotRun, standard
from gov.layout.repo import Repo

REPO = Path(__file__).resolve().parents[3]


def _git(root: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(root), "-c", "user.name=t", "-c", "user.email=t@example.org", *args], check=True,
                   capture_output=True)


def _write(root: Path, rel: str, text: str = "x\n") -> None:
    (root / rel).parent.mkdir(parents=True, exist_ok=True)
    (root / rel).write_text(text)


@pytest.fixture
def planted(tmp_path):
    _git(tmp_path, "init", "-q")
    _write(tmp_path, ".gitignore", "cache/\nnode_modules/\n")
    _write(tmp_path, "governance/project/path-map.yaml",
           'sets_root_hidden:\n  root: "~/x"\n  hidden: ["cache/sets/*/hidden/**"]\n')
    _git(tmp_path, "add", "-A")
    _git(tmp_path, "commit", "-qm", "base")
    _write(tmp_path, "cache/sets/a/hidden/q.yaml")
    _write(tmp_path, "node_modules/lib/index.js")
    return tmp_path


def test_a_hidden_file_below_an_ignored_root_is_found_by_its_name(planted):
    repo = Repo(planted, standard.load(REPO), None)
    assert repo.items["cache"] == repo.items["node_modules"] == "ignored-root"
    assert repo.hidden_ignored == ["cache/sets/a/hidden/q.yaml"]


def test_a_changed_tracked_file_cannot_run_but_the_plan_file_may_change(planted):
    std = standard.load(REPO)
    _write(planted, ".gitignore", "cache/\nnode_modules/\nmore/\n")
    assert Repo(planted, std, ".gitignore").commit
    with pytest.raises(CannotRun, match="uncommitted"):
        Repo(planted, std, None)

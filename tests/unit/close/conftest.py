"""Fixtures for the unit tests of ``gov close``: a temporary git repository and the project's ticket tool."""
from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
TK = REPO_ROOT / "template" / "governance" / "kernel" / "bin" / "tk"
TICKET = "T-0001"


class Repo:
    def __init__(self, root: Path):
        self.root = root
        root.mkdir()
        self.git("init", "-q", "-b", "main")

    def git(self, *args: str) -> str:
        env = {"PATH": os.environ["PATH"], "HOME": str(self.root.parent), "GIT_CONFIG_NOSYSTEM": "1",
               "GIT_CONFIG_GLOBAL": os.devnull, "GIT_AUTHOR_NAME": "A", "GIT_AUTHOR_EMAIL": "a@example.invalid",
               "GIT_COMMITTER_NAME": "A", "GIT_COMMITTER_EMAIL": "a@example.invalid"}
        return subprocess.run(["git", "-C", str(self.root), *args], env=env, check=True,
                              capture_output=True, text=True).stdout

    def commit(self, message: str = "work", *trailers: str, files: dict | None = None) -> str:
        for rel, text in (files or {}).items():
            path = self.root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
        self.git("add", "-A")
        args = ["commit", "-q", "--allow-empty", "--no-gpg-sign", "-m", message]
        for trailer in trailers:
            args += ["--trailer", trailer]
        self.git(*args)
        return self.git("rev-parse", "HEAD").strip()


@pytest.fixture
def repo(tmp_path):
    return Repo(tmp_path / "project")


@pytest.fixture
def root(tmp_path):
    """A project folder with one ticket in progress and the project's ticket tool."""
    root = tmp_path / "project"
    (root / ".tickets").mkdir(parents=True)
    (root / ".tickets" / f"{TICKET}.md").write_text(
        f"---\nid: {TICKET}\nstatus: in_progress\ndeps: []\nlinks: []\ncreated: 2026-10-07T00:00:00Z\n"
        "type: task\npriority: 2\n---\n# A ticket\n", encoding="utf-8")
    tool = root / "governance" / "kernel" / "bin" / "tk"
    tool.parent.mkdir(parents=True)
    shutil.copy2(TK, tool)
    tool.chmod(0o755)
    return root

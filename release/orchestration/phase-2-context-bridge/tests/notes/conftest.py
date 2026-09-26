"""A tiny, self-contained synthetic Git repository for tests/notes/**. Kept entirely inside this node's own
mutation_scope (R1-RN: govbridge/notes/**, config/notes-schema.yaml, tests/notes/**) rather than reusing
tests/fixtures/core or tests/fixtures/authority, which belong to other REPAIR-1 nodes. Generic, unrelated content
only (OC-BR-02): no Review-8 item, F-finding, Phase-2 file or symbol from those chains.
"""
from __future__ import annotations

import subprocess
from pathlib import Path
from typing import NamedTuple

import pytest


def _git(root: Path, *args: str) -> subprocess.CompletedProcess:
    r = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"git {args} failed: {r.stderr}")
    return r


def _commit(root: Path, message: str) -> str:
    _git(root, "add", "-A")
    _git(root, "-c", "user.email=t@example.com", "-c", "user.name=t", "commit", "-q", "-m", message)
    return _git(root, "rev-parse", "HEAD").stdout.strip()


def _write(root: Path, rel: str, content: str) -> None:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")


NOTES_PATH_A = "widgets/gadget.py"
NOTES_PATH_B = "widgets/sprocket.py"


class NotesFixtureRepo(NamedTuple):
    root: Path
    commit: str
    path_a: str
    path_b: str
    blob_a: str
    blob_b: str
    lines_a_1_2: list  # [1, 2] -- the first two lines of path_a
    text_a_1_2: str
    lines_b_1_1: list  # [1, 1] -- the first line of path_b
    text_b_1_1: str


@pytest.fixture
def notes_repo(tmp_path) -> NotesFixtureRepo:
    root = tmp_path / "repo"
    root.mkdir(parents=True)
    _git(root, "init", "-q", "-b", "main")

    _write(root, NOTES_PATH_A,
           "def make_gadget():\n"
           "    return Gadget()\n"
           "\n"
           "class Gadget:\n"
           "    pass\n")
    _write(root, NOTES_PATH_B,
           "def make_sprocket():\n"
           "    return Sprocket()\n")

    commit = _commit(root, "add widgets")

    blob_a = _git(root, "rev-parse", f"{commit}:{NOTES_PATH_A}").stdout.strip()
    blob_b = _git(root, "rev-parse", f"{commit}:{NOTES_PATH_B}").stdout.strip()

    return NotesFixtureRepo(
        root=root, commit=commit, path_a=NOTES_PATH_A, path_b=NOTES_PATH_B,
        blob_a=blob_a, blob_b=blob_b,
        lines_a_1_2=[1, 2], text_a_1_2="def make_gadget():\n    return Gadget()",
        lines_b_1_1=[1, 1], text_b_1_1="def make_sprocket():",
    )


@pytest.fixture(autouse=True)
def _no_env_leak(monkeypatch):
    # matches tests/core, tests/authority and tests/compile's own autouse fixture: never inherit the developer's
    # real cache store into a test.
    monkeypatch.delenv("GOVBRIDGE_STORE", raising=False)

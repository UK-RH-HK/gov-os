"""Builder tests for the lexical index's git calls (W2-05, W2-M161, review R6-2; regression evidence only, the
acceptance tests are W2-05's own).

Every git call of the index only reads (``rev-parse``, ``ls-files``, ``hash-object`` without ``-w``) and runs
pinned: a trace setting in the person's ``~/.gitconfig`` or XDG file is never written by them, under the refresh, the
freshness key W2-108 added or the freshness itself, and the answers are those of an unpinned run.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

from gov.retrieval import lexical
from gov.util import gitenv

CLEAN = {"PATH": "/usr/bin:/bin", "HOME": "/nonexistent", "LC_ALL": "C", "GIT_CONFIG_NOSYSTEM": "1",
         "GIT_CONFIG_GLOBAL": os.devnull, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@example.invalid",
         "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@example.invalid"}
FILES = {".gitignore": ".gov-runtime/\n", "notes/a.md": "# A\n\nSome words.\n", "app/pool.py": "size = 1\n"}


def _git(root: Path, *args: str, env: dict | None = None) -> str:
    return subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True, text=True,
                          env=env or CLEAN).stdout


@pytest.fixture()
def project(tmp_path, monkeypatch):
    """A small project, the secret filter letting every path through, the index's process caches empty and no file
    taken for too recent to stamp."""
    root = tmp_path / "project"
    root.mkdir()
    _git(root, "init", "-q", "-b", "main")
    for rel, text in FILES.items():
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_text(text, encoding="utf-8")
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "-m", "first")
    monkeypatch.setattr(lexical, "indexable", lambda _root, paths: list(paths))
    monkeypatch.setattr(lexical, "_FRESHNESS", {})
    monkeypatch.setattr(lexical, "_LISTED", {})
    monkeypatch.setattr(lexical, "RACY_NS", 0)  # the key is taken right after a commit
    return root


@pytest.fixture()
def person(tmp_path, monkeypatch):
    """The person's own configuration: ``trace2.eventTarget`` in ``~/.gitconfig`` and ``trace2.perfTarget`` in the
    XDG file, each naming a file of the test's; the targets are returned."""
    home = tmp_path / "home"
    (home / ".config" / "git").mkdir(parents=True)
    targets = (tmp_path / "trace-home", tmp_path / "trace-xdg")
    (home / ".gitconfig").write_text(f"[trace2]\n\teventTarget = {targets[0]}\n")
    (home / ".config" / "git" / "config").write_text(f"[trace2]\n\tperfTarget = {targets[1]}\n")
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("XDG_CONFIG_HOME", str(home / ".config"))
    return targets


def _answers(root: Path) -> tuple:
    """The freshness key's tree, the listing with its blob ids, the refresh's digest and the freshness, from caches
    emptied first."""
    lexical._FRESHNESS.clear()
    lexical._LISTED.clear()
    tree = lexical._tree(root, root.resolve())
    tracked = lexical._tracked(root)
    digest = lexical.refresh(root)["digest"]
    return (tree[0][0], tree[1]), tracked, digest, lexical.freshness(root)


def test_the_index_s_git_calls_write_no_trace_the_person_set(project, person):
    """W2-M161, R6-2: the refresh, the freshness key and the freshness, before and after a change."""
    lexical.refresh(project)
    assert lexical.freshness(project)["status"] == "fresh"
    (project / "notes" / "a.md").write_text("# A\n\nOther words.\n", encoding="utf-8")
    _git(project, "add", "-A")
    _git(project, "commit", "-q", "-m", "second")
    assert lexical.freshness(project) == {"status": "stale", "stale": ["notes/a.md"]}
    assert lexical.refresh(project)["indexed"] == ["notes/a.md"]
    assert lexical.freshness(project)["status"] == "fresh"
    assert [target.name for target in person if target.exists()] == []


def test_the_answers_are_those_of_an_unpinned_run(project, person, monkeypatch):
    """The key, the listing, the blob ids and the digest are what they were before the calls were pinned."""
    pinned = _answers(project)
    monkeypatch.setattr(lexical, "git_env", lambda root, **_kw: gitenv.git_env(root))
    (project / lexical.STORE_REL).unlink()
    unpinned = _answers(project)
    assert pinned == unpinned
    head = _git(project, "rev-parse", "HEAD").strip()
    assert pinned[0][0].decode() == head and pinned[0][1] == _git(project, "ls-files", "-z").encode()
    blobs = _git(project, "hash-object", *sorted(FILES)).split()
    assert pinned[1] == dict(zip(sorted(FILES), blobs)) and pinned[3]["status"] == "fresh"


def test_an_inherited_index_of_the_root_s_own_git_directory_is_still_used(project, person, monkeypatch):
    """DEC-804 item 3: an index git gives the call for its own repository (``git commit -a``'s) is the one read."""
    (project / "staged.txt").write_text("only in the other index\n", encoding="utf-8")
    other = project / ".git" / "next-index-1.lock"
    _git(project, "read-tree", "HEAD", env={**CLEAN, "GIT_INDEX_FILE": str(other)})
    _git(project, "add", "staged.txt", env={**CLEAN, "GIT_INDEX_FILE": str(other)})
    monkeypatch.setenv("GIT_INDEX_FILE", str(other))
    assert "staged.txt" in lexical._tracked(project)
    tree = lexical._tree(project, project.resolve())
    assert b"staged.txt" in tree[1].split(b"\0")
    assert [target.name for target in person if target.exists()] == []

"""A fix in gov doctor's path compliance (found at W2-200's land, 2026-11-19): a path that was once renamed away and
exists again at HEAD (renamed back, or made anew) is no moved path, and a reference to it is no stale reference. A path
renamed away that HEAD does not hold is still reported. Builder tests on a small repository of their own."""

from __future__ import annotations

import subprocess

import pytest

from gov.doctor import command

ENV = {"PATH": "/usr/bin:/bin", "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@example.invalid",
       "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@example.invalid", "HOME": "/nonexistent"}


def git(root, *args):
    subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True, env=ENV, timeout=60)


@pytest.fixture
def repo(tmp_path):
    root = tmp_path / "project"
    root.mkdir()
    git(root, "init", "-q", "-b", "main")
    (root / "lists").mkdir()
    (root / "lists" / "lifted-breadth.txt").write_text("one\ntwo\nthree\nfour\nfive\n", encoding="utf-8")
    (root / "gone-old.txt").write_text("alpha\nbeta\ngamma\ndelta\nepsilon\n", encoding="utf-8")
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "base")
    git(root, "mv", "lists/lifted-breadth.txt", "lists/breadth.txt")
    git(root, "mv", "gone-old.txt", "gone-new.txt")
    git(root, "commit", "-q", "-m", "renamed away")
    git(root, "mv", "lists/breadth.txt", "lists/lifted-breadth.txt")
    (root / "notes.md").write_text("see lists/lifted-breadth.txt and gone-old.txt\n", encoding="utf-8")
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "one renamed back, and a note naming both old paths")
    return root


def _references(root):
    return {(ref["old_path"], ref["referenced_in"])
            for ref in command._check_path_compliance(root)["moved_references"]}


def test_a_path_renamed_away_and_back_is_no_moved_reference(repo):
    assert ("lists/lifted-breadth.txt", "notes.md") not in _references(repo)


def test_a_path_renamed_away_that_head_does_not_hold_is_still_reported(repo):
    assert ("gone-old.txt", "notes.md") in _references(repo)

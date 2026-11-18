"""W2-17 (DAEO-sdhj): ``gov update``'s plan, its rollback journal, its regeneration and its refusals. Builder evidence.

The plan compares, for every path of the two renders, release A's render (O), the project's file (P) and release B's
render (N); the overlay (``governance/project/``) is never written where the project has the file.
"""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import pytest

from gov.adapters import merge
from gov.update import core


def git(repo: Path, *args: str) -> str:
    env = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@example.invalid",
           "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@example.invalid"}
    return subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True, text=True,
                          env=env).stdout


F = lambda text: ("file", text.encode(), False)  # noqa: E731
LINES = "".join(f"line {n}\n" for n in range(1, 21))


# --------------------------------------------------------------------------
# The three-way table
# --------------------------------------------------------------------------

@pytest.mark.parametrize("rel,old,own,new,outcome,action", [
    ("k/a.md", F("a"), F("a"), F("a"), None, None),
    ("k/a.md", F("a"), F("b"), F("b"), None, None),
    ("k/a.md", F("a"), F("a"), F("b"), "updated", "write"),
    ("k/a.md", None, None, F("b"), "added", "write"),
    ("k/a.md", F("a"), F("a"), None, "removed", "delete"),
    ("k/a.md", F("a"), F("mine"), F("a"), "kept", None),
    ("k/a.md", F("a"), None, F("a"), "kept", None),
    ("governance/project/x.yaml", F("a"), F("mine"), F("b"), "overlay", None),
    ("governance/project/x.yaml", F("a"), F("a"), F("b"), "overlay", None),
    ("governance/project/x.yaml", F("a"), F("mine"), F("a"), None, None),
    ("governance/project/x.yaml", None, None, F("b"), "added", "write"),
    ("k/a.md", F("a"), None, F("b"), "conflicts", "aside"),
    ("k/a.md", F("a"), F("mine"), None, "conflicts", None),
])
def test_the_three_way_table(rel, old, own, new, outcome, action):
    got_outcome, got_action = core.classify(rel, old, own, new)
    assert got_outcome == outcome
    assert (got_action[0] if got_action else None) == action


def test_changes_in_different_lines_merge_cleanly():
    base = LINES
    own = base.replace("line 2\n", "line 2 (project)\n")
    new = base.replace("line 12\n", "line 12 (release B)\n")
    outcome, action = core.classify("k/m.md", F(base), F(own), F(new))
    assert outcome == "merged" and action[0] == "write"
    assert b"line 2 (project)" in action[1] and b"line 12 (release B)" in action[1] and b"<<<<<<<" not in action[1]


def test_changes_in_the_same_line_conflict_and_write_release_b_aside():
    base = LINES
    outcome, action = core.classify("k/c.md", F(base), F(base.replace("line 3\n", "mine\n")),
                                    F(base.replace("line 3\n", "theirs\n")))
    assert outcome == "conflicts" and action[0] == "aside" and action[1] == base.replace("line 3\n", "theirs\n").encode()


def test_a_binary_file_changed_on_both_sides_is_a_conflict():
    outcome, action = core.classify("k/b.bin", ("file", b"\0a", False), ("file", b"\0b", False),
                                    ("file", b"\0c", False))
    assert outcome == "conflicts" and action[0] == "aside"


def test_the_plan_walks_both_renders_and_skips_the_answers_file(tmp_path):
    old, project, new = tmp_path / "o", tmp_path / "p", tmp_path / "n"
    for root, files in ((old, {"k/u.md": "a", "k/r.md": "r", ".copier-answers.yml": "_commit: v1"}),
                        (project, {"k/u.md": "a", "k/r.md": "r", ".copier-answers.yml": "_commit: v1"}),
                        (new, {"k/u.md": "b", "k/n.md": "n", ".copier-answers.yml": "_commit: v2"})):
        for rel, text in files.items():
            (root / rel).parent.mkdir(parents=True, exist_ok=True)
            (root / rel).write_text(text, encoding="utf-8")
    files, actions = core.plan(old, project, new)
    assert files["updated"] == ["k/u.md"] and files["added"] == ["k/n.md"] and files["removed"] == ["k/r.md"]
    assert ".copier-answers.yml" not in actions


# --------------------------------------------------------------------------
# The journal: what the update wrote or deleted goes back
# --------------------------------------------------------------------------

def test_the_journal_restores_written_created_and_deleted_files(tmp_path):
    (tmp_path / "a.txt").write_text("before", encoding="utf-8")
    (tmp_path / "gone.txt").write_text("keep me", encoding="utf-8")
    (tmp_path / "gone.txt").chmod(0o755)
    journal = core.Journal(tmp_path)
    journal.write("a.txt", b"after")
    journal.write("new/deep/b.txt", b"new")
    journal.delete("gone.txt")
    journal.write("a.txt", b"after again")
    journal.restore()
    assert (tmp_path / "a.txt").read_text() == "before"
    assert not (tmp_path / "new").exists()
    assert (tmp_path / "gone.txt").read_text() == "keep me" and os.access(tmp_path / "gone.txt", os.X_OK)


# --------------------------------------------------------------------------
# Regeneration in the update's path (gov.adapters.merge)
# --------------------------------------------------------------------------

def test_unmerge_takes_out_what_the_old_generation_added_and_keeps_the_project_s_own():
    own = {"permissions": {"allow": ["Bash(ls)", "Bash(gen-a)"]},
           "hooks": {"Stop": [{"hooks": [{"command": "old stop"}]}], "Mine": [1]}, "model": "x", "same": 1}
    generated = {"permissions": {"allow": ["Bash(gen-a)"]}, "hooks": {"Stop": [{"hooks": [{"command": "old stop"}]}]},
                 "same": 1}
    assert merge.unmerge_value(own, generated) == {"permissions": {"allow": ["Bash(ls)"]}, "hooks": {"Mine": [1]},
                                                   "model": "x"}


def test_forget_generated_removes_old_output_and_keeps_what_the_project_changed(tmp_path):
    (tmp_path / ".claude/skills/a").mkdir(parents=True)
    (tmp_path / ".claude/skills/a/SKILL.md").write_text("old a", encoding="utf-8")
    (tmp_path / ".claude/skills/b").mkdir(parents=True)
    (tmp_path / ".claude/skills/b/SKILL.md").write_text("changed by the project", encoding="utf-8")
    (tmp_path / ".claude/settings.json").write_text(json.dumps(
        {"own": 1, "hooks": {"Stop": ["old line"]}}), encoding="utf-8")
    (tmp_path / "CLAUDE.md").write_text("mine\n", encoding="utf-8")
    previous = {".claude/skills/a/SKILL.md": b"old a", ".claude/skills/b/SKILL.md": b"old b",
                ".claude/settings.json": json.dumps({"hooks": {"Stop": ["old line"]}}).encode(),
                "CLAUDE.md": b"generated"}
    written, deleted = {}, []
    kept = merge.forget_generated(tmp_path, previous, written.__setitem__, deleted.append)
    assert deleted == [".claude/skills/a/SKILL.md"] and kept == [".claude/skills/b/SKILL.md"]
    assert json.loads(written[".claude/settings.json"]) == {"own": 1}
    assert "CLAUDE.md" not in written


# --------------------------------------------------------------------------
# Refusals before anything is written
# --------------------------------------------------------------------------

def _project(tmp_path: Path, lock_text: str | None) -> Path:
    project = tmp_path / "p"
    project.mkdir()
    git(project, "init", "-q", "-b", "main")
    (project / ".copier-answers.yml").write_text("_commit: v1.0.0\n_src_path: /nowhere\n", encoding="utf-8")
    if lock_text is not None:
        (project / "governance").mkdir()
        (project / "governance/framework.lock").write_text(lock_text, encoding="utf-8")
    git(project, "add", "-A")
    git(project, "commit", "-q", "-m", "adopted")
    return project


@pytest.mark.parametrize("lock_text", [None, "release: null\n", "- not a map\n"])
def test_a_project_without_a_lock_naming_a_release_is_refused(tmp_path, lock_text):
    project = _project(tmp_path, lock_text)
    with pytest.raises(core.UpdateRefused) as refused:
        core.update(project, "1.0.1")
    assert refused.value.reason == "not_adopted" and "governance/framework.lock" in str(refused.value)


def test_a_project_already_at_the_release_is_refused(tmp_path):
    project = _project(tmp_path, "release:\n  version: 1.0.1\n")
    with pytest.raises(core.UpdateRefused) as refused:
        core.update(project, "1.0.1")
    assert refused.value.reason == "same" and "already at release 1.0.1" in str(refused.value)


def test_an_uncommitted_change_is_refused_naming_it_and_check_goes_on(tmp_path):
    project = _project(tmp_path, "release:\n  version: 1.0.0\n")
    (project / "stray.txt").write_text("x", encoding="utf-8")
    with pytest.raises(core.UpdateRefused) as refused:
        core.update(project, "1.0.1")
    assert refused.value.reason == "dirty" and "stray.txt" in str(refused.value)
    with pytest.raises(core.UpdateRefused) as refused:  # --check goes on to the source, which is not there
        core.update(project, "1.0.1", check=True)
    assert refused.value.reason == "no_release"

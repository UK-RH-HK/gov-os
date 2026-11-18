"""W2-88 run 7, S26 (F-3): stages MA and A0 ask ``git check-ignore`` about every path ``gov adopt`` writes and commits,
and refuse at once (``ADOPT_PATH_IGNORED``) when the repository's ignore rules ignore one the index does not track.

Regression evidence only (DEC-136). Planted repositories in ``tmp_path`` (``test_adopt``'s ``root`` fixture). Before
the refusal nothing is written, staged or committed, and no ignore file is edited.
"""
from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

from gov.adopt import assess, project, safety, stages

from .test_adopt import commit, refused, root, sh, stage, write  # noqa: F401  (root is a fixture)

F3 = ".claude/skills/*"  # grafana's rule: .gitignore:84:.claude/skills/*


def snapshot(root: Path) -> dict:
    """Everything a refusal must leave as it is: HEAD, the refs, the status, and every file's bytes outside .git."""
    files = {}
    for folder, names, listed in os.walk(root):
        names[:] = [name for name in names if name != ".git"]
        files.update({str(Path(folder, name).relative_to(root)): Path(folder, name).read_bytes() for name in listed})
    return {"head": sh(root, "rev-parse", "HEAD"), "refs": sh(root, "for-each-ref"),
            "status": sh(root, "status", "--porcelain", "--ignored"), "files": files}


def ignoring(root: Path, rule: str, where: str = ".gitignore") -> int:
    """Add ``rule`` to the ignore file ``where`` (committed, unless it is under .git); the rule's line number."""
    path = root / where
    text = path.read_text() if path.is_file() else ""
    write(root, where, text + rule + "\n")
    if not where.startswith(".git/"):
        commit(root, f"ignore {rule}")
    return text.count("\n") + 1


def ma(root: Path, tmp_path: Path):
    return stage(root, "MA", out=str(tmp_path / "out"))


def test_the_f3_rule_refuses_ma_and_a0_at_once_naming_each_path_with_its_rule(root, tmp_path, monkeypatch):
    line = ignoring(root, F3)
    monkeypatch.setattr(assess, "assess", lambda *args: pytest.fail("MA's long step ran"))
    monkeypatch.setattr(safety, "setup", lambda *args: pytest.fail("A0 began its work"))
    before = snapshot(root)
    for name in ("MA", "A0"):
        more = {"out": str(tmp_path / "out")} if name == "MA" else {}
        caught = refused("PATH_IGNORED", root, name, **more)
        found = {item["path"]: item for item in caught.details["ignored"]}
        assert set(found) >= {".claude/skills/retrieval/SKILL.md", ".claude/skills/discovery/SKILL.md",
                              ".claude/skills/judging-work/SKILL.md"}
        assert all(item["source"] == ".gitignore" and item["line"] == line and item["pattern"] == F3
                   for item in found.values())
        assert all(path.startswith(".claude/skills/") for path in found)  # this rule ignores nothing else A0 to A9 write
        assert all(f".gitignore:{line}:{F3}" in caught.message and path in caught.message for path in found)
        assert snapshot(root) == before and not (tmp_path / "out").exists()  # nothing written, staged or committed


def test_the_message_gives_git_check_ignores_own_form_for_each_path(root):
    line = ignoring(root, F3)
    caught = refused("PATH_IGNORED", root, "A0")
    shown = subprocess.run(["git", "-C", str(root), "check-ignore", "-v", ".claude/skills/retrieval/SKILL.md"],
                           capture_output=True, text=True).stdout.split("\t")[0]
    assert shown == f".gitignore:{line}:{F3}" and shown in caught.message


def test_a_rule_that_ignores_the_stage_records_is_refused_with_the_records_named(root, tmp_path):
    ignoring(root, "governance/adoption/")
    for name in ("MA", "A0"):
        caught = refused("PATH_IGNORED", root, name, **({"out": str(tmp_path / "out")} if name == "MA" else {}))
        paths = [item["path"] for item in caught.details["ignored"]]
        assert "governance/adoption/A0-safety-baseline.md" in paths and "governance/adoption/A9-memory-fabric.md" in paths
        assert all(item["pattern"] == "governance/adoption/" for item in caught.details["ignored"])


def test_each_place_a_rule_can_come_from_is_found(root, tmp_path):
    # .git/info/exclude
    ignoring(root, F3, ".git/info/exclude")
    caught = refused("PATH_IGNORED", root, "A0")
    assert {item["source"] for item in caught.details["ignored"]} == {".git/info/exclude"}
    (root / ".git/info/exclude").write_text("")
    # core.excludesFile
    excludes = tmp_path / "global-ignore"
    excludes.write_text(F3 + "\n")
    sh(root, "config", "core.excludesFile", str(excludes))
    caught = refused("PATH_IGNORED", root, "A0")
    assert {item["source"] for item in caught.details["ignored"]} == {str(excludes)}
    sh(root, "config", "--unset", "core.excludesFile")
    # a .gitignore in a folder
    ignoring(root, "skills/*", ".claude/.gitignore")
    caught = refused("PATH_IGNORED", root, "A0")
    assert {item["source"] for item in caught.details["ignored"]} == {".claude/.gitignore"}
    assert all(item["pattern"] == "skills/*" and item["line"] == 1 for item in caught.details["ignored"])


def test_a_path_the_index_tracks_is_no_refusal_and_neither_is_a_negated_rule(root, tmp_path):
    ignoring(root, ".gitleaks.toml")  # an ignored name ...
    write(root, ".gitleaks.toml", "title = 'x'\n")
    sh(root, "add", "-f", ".gitleaks.toml")  # ... that the index tracks (the test, not gov, forces it)
    commit(root, "track it")
    ignoring(root, F3)
    ignoring(root, "!.claude/skills/retrieval")
    ignoring(root, "!.claude/skills/discovery")
    ignoring(root, "!.claude/skills/judging-work")
    result = stage(root, "A0")  # the rule's negations leave both skill folders alone
    assert result["stage"] == "A0" and sh(root, "log", "-1", "--format=%s").startswith("gov adopt --lite A0")


def test_a_repository_whose_rules_ignore_none_goes_on_as_today(root, tmp_path):
    made = ma(root, tmp_path)
    assert made["stage"] == "MA" and (tmp_path / "out" / assess.FILE).is_file()
    done = stage(root, "A0")
    assert done["stage"] == "A0" and done["record"] == project.record_path("A0")


def test_a0_asks_again_for_a_run_that_skipped_ma(root, tmp_path):
    ma(root, tmp_path)  # MA ran while nothing was ignored
    ignoring(root, F3)  # then the rule came
    refused("PATH_IGNORED", root, "A0")


def test_the_one_list_names_every_stage_record_the_kernel_copies_and_a0s_files(root):
    listed = safety.written_paths(root)
    for stage_name in project.STAGES:
        assert project.record_path(stage_name) in listed
    assert {".gitleaks.toml", ".gitignore", "governance/project/retrieval.yaml",
            ".claude/skills/retrieval/SKILL.md", ".claude/skills/discovery/SKILL.md",
            ".claude/skills/judging-work/SKILL.md", "governance/kernel/templates/brief.md", "governance/kernel/templates/role-cto.md"} <= set(listed)
    assert len(listed) == len(set(listed))

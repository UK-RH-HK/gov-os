"""W2-192 F1: AS writes nothing outside governance/adoption/, changes no spec or code, and leaves every gap's answer
empty. Builder tests, regression evidence only (DEC-136)."""
from __future__ import annotations

from pathlib import Path

from gov.adopt import project

from .test_adopt import sh
from .test_w2_192_support import audited, record, repo, stage, through_a2, keep_all  # noqa: F401


def outside(root: Path) -> dict[str, bytes]:
    """Every file of the working tree outside governance/adoption/ and .git, by path."""
    return {path.relative_to(root).as_posix(): path.read_bytes() for path in sorted(root.rglob("*"))
            if path.is_file() and ".git" not in path.relative_to(root).parts
            and not path.relative_to(root).as_posix().startswith(project.FOLDER + "/")}


def head_outside(root: Path) -> dict[str, str]:
    return {rel: blob for rel, blob in project.tree(root).items() if not rel.startswith(project.FOLDER + "/")}


def test_as_changes_no_byte_outside_governance_adoption(repo):  # noqa: F811
    through_a2(repo)
    before, tree = outside(repo), head_outside(repo)
    stage(repo, "AS")
    assert outside(repo) == before and head_outside(repo) == tree
    assert [line for line in sh(repo, "status", "--porcelain").splitlines()] == []
    assert sh(repo, "show", "--name-only", "--format=", "HEAD").split() == [project.record_path("AS")]


def test_every_gap_answer_is_empty_after_as_and_after_a3(repo):  # noqa: F811
    audited(repo)
    assert record(repo)["gaps"] and all(gap["answer"] is None for gap in record(repo)["gaps"])
    stage(repo, "A3", map=keep_all(repo))
    assert all(gap["answer"] is None for gap in record(repo)["gaps"])
    assert "answer" not in record(repo, "A3")

"""W2-88 I1, I2: the stage MA, and A3's ``--assessment`` (R1 (b)): a bare A3 as before, a given assessment cited."""
from __future__ import annotations

import json

import pytest

from gov.adopt import assess, command, project
from gov.cli.errors import GovError

from .test_adopt import MOVES, config, proposal, record, root, sh, stage  # noqa: F401  (root is a fixture)


def test_the_commands_name_the_new_stages_and_flags():
    assert {"MA", "A9"} <= set(command.STAGES)
    assert project.STAGES[-2:] == ("A8", "A9") and project.record_path("A9").endswith("A9-memory-fabric.md")


def test_ma_writes_files_under_out_and_nothing_in_the_repository(root, tmp_path):  # noqa: F811
    out = tmp_path / "assessment"
    before = (sh(root, "rev-parse", "HEAD"), sh(root, "status", "--porcelain"), sh(root, "ls-files", "-s"),
              sh(root, "for-each-ref"))
    result = stage(root, "MA", out=str(out))
    assert (sh(root, "rev-parse", "HEAD"), sh(root, "status", "--porcelain"), sh(root, "ls-files", "-s"),
            sh(root, "for-each-ref")) == before
    assert result["stage"] == "MA" and (out / assess.FILE).is_file() and (out / "refactor-plan").is_dir()
    assert json.loads((out / assess.FILE).read_text())["commit"] == sh(root, "rev-parse", "HEAD")


def test_ma_refuses_an_out_folder_inside_the_project_and_needs_one(root):  # noqa: F811
    with pytest.raises(GovError) as raised:
        stage(root, "MA", out=str(root / "assessment"))
    assert raised.value.code == "OUT_INSIDE_PROJECT" and not (root / "assessment").exists()
    with pytest.raises(GovError) as bare:
        stage(root, "MA")
    assert bare.value.code == "ADOPT_NO_OUT"


def test_a_bare_a3_runs_as_before_and_says_no_assessment(root):  # noqa: F811
    for name in ("A0", "A1", "A2"):
        stage(root, name)
    stage(root, "A3", map=proposal(root, *MOVES))
    assert record(root, "A3")["assessment"] == "none"


def test_a3_with_an_assessment_cites_its_sha256_and_copies_no_proposal(root, tmp_path):  # noqa: F811
    for name in ("A0", "A1", "A2"):
        stage(root, name)
    out = tmp_path / "assessment"
    stage(root, "MA", out=str(out))
    stage(root, "A3", map=proposal(root, *MOVES), assessment=str(out))
    head = record(root, "A3")
    assert head["assessment"] == "sha256:" + project.sha256((out / assess.FILE).read_bytes())
    assert head["assessment_commit"] == sh(root, "rev-parse", "HEAD~1")  # the commit A3 stood on
    assert "refactor-plan" not in (root / project.record_path("A3")).read_text()


def test_a3_given_an_assessment_of_another_commit_or_none_refuses(root, tmp_path):  # noqa: F811
    for name in ("A0", "A1", "A2"):
        stage(root, name)
    for where in (tmp_path / "empty", None):
        folder = tmp_path / "empty"
        folder.mkdir(exist_ok=True)
        with pytest.raises(GovError) as raised:
            stage(root, "A3", map=proposal(root, *MOVES), assessment=str(folder))
        assert raised.value.code == "ASSESSMENT_MISSING"
    stage(root, "MA", out=str(tmp_path / "old"))
    (root / "extra.md").write_text("x\n")
    sh(root, "add", "-A")
    sh(root, "commit", "-q", "-m", "moves on")
    with pytest.raises(GovError) as stale:
        stage(root, "A3", map=proposal(root, *MOVES), assessment=str(tmp_path / "old"))
    assert stale.value.code == "ASSESSMENT_MISSING"

"""Builder tests for the launch record (W2-60a).

Regression evidence only (DEC-136). They cover what the acceptance tests leave
to the builder: the folder found from a worktree's ``.git`` file, the exclusive
write, the resumed session's record and the CLI's version read from its link.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov.cli.errors import GovError  # noqa: E402
from gov.launch import record  # noqa: E402

SID = "1ecc24ab-3710-4228-8258-619022e4b679"


def test_a_worktree_finds_the_main_checkout_s_folder(tmp_path):
    main, tree = tmp_path / "main", tmp_path / "tree"
    (main / ".git" / "worktrees" / "tree").mkdir(parents=True)
    (main / ".git" / "worktrees" / "tree" / "commondir").write_text("../..\n", encoding="utf-8")
    tree.mkdir()
    (tree / ".git").write_text(f"gitdir: {main}/.git/worktrees/tree\n", encoding="utf-8")
    assert record.folder(tree) == main / ".gov-runtime" / "launches"
    assert (main / ".gov-runtime" / "launches").is_dir() and not (tree / ".gov-runtime").exists()


def test_a_bare_common_directory_refuses(tmp_path):
    (tmp_path / "repo.git").mkdir()
    (tmp_path / "tree").mkdir()
    (tmp_path / "tree" / ".git").write_text(f"gitdir: {tmp_path}/repo.git\n", encoding="utf-8")
    with pytest.raises(GovError):
        record.folder(tmp_path / "tree")


def test_a_record_is_written_once_and_never_over_another(tmp_path):
    path = record.write(tmp_path, {"session_id": SID, "role": "engineer"})
    assert json.loads(path.read_text(encoding="utf-8")) == {"session_id": SID, "role": "engineer"}
    with pytest.raises(GovError):
        record.write(tmp_path, {"session_id": SID, "role": "research"})
    assert json.loads(path.read_text(encoding="utf-8"))["role"] == "engineer"


@pytest.mark.parametrize("data, refused", (
    (None, True),
    ("not json", True),
    ({"record": "gov-launch", "role": "engineer", "ticket": "T-1", "role_text": {}, "skills": []}, False),
    ({"record": "gov-launch", "role": "engineer", "ticket": "T-2", "role_text": {}, "skills": []}, True),
    ({"record": "gov-launch", "role": "engineer", "ticket": "T-1"}, True),
))
def test_a_resume_needs_the_original_s_record_of_this_role_and_ticket(tmp_path, data, refused):
    if data is not None:
        (tmp_path / f"{SID}.json").write_text(data if isinstance(data, str) else json.dumps(data), encoding="utf-8")
    if refused:
        with pytest.raises(GovError):
            record.original(tmp_path, SID, "engineer", "T-1")
    else:
        assert record.original(tmp_path, SID, "engineer", "T-1")["ticket"] == "T-1"


def test_the_cli_s_version_is_the_name_its_link_resolves_to(tmp_path):
    (tmp_path / "versions").mkdir()
    (tmp_path / "versions" / "2.1.292").write_text("", encoding="utf-8")
    (tmp_path / "claude").symlink_to(tmp_path / "versions" / "2.1.292")
    (tmp_path / "plain").write_text("", encoding="utf-8")
    assert record.cli_version(tmp_path / "claude") == "2.1.292"
    assert record.cli_version(tmp_path / "plain").startswith("not measured: ")

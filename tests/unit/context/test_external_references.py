"""Unit tests for the reader of the external references file (W1-41; DEC-520; read from HEAD since DEC-552)."""

from __future__ import annotations

import subprocess

import pytest

from gov.cli.errors import GovError
from gov.context import EXTERNAL_REFERENCES_REL, external_references

GOOD = ("references:\n"
        "  - id: S0a-G-12\n    location: the archive\n    reason: kept outside\n")
_ENV = {"PATH": "/usr/bin:/bin", "GIT_CONFIG_NOSYSTEM": "1", "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t.invalid",
        "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t.invalid"}


def commit(root, message="files"):
    """Commit everything under ``root`` (a repository is made on the first call)."""
    for args in (["init", "-q", "-b", "main"], ["add", "-A"], ["commit", "-q", "--allow-empty", "-m", message]):
        subprocess.run(["git", "-C", str(root), *args], capture_output=True, check=True,
                       env={**_ENV, "HOME": str(root)})


def _project(tmp_path, text):
    path = tmp_path / EXTERNAL_REFERENCES_REL
    path.parent.mkdir(parents=True)
    path.write_text(text, encoding="utf-8")
    commit(tmp_path)
    return tmp_path


def test_a_project_without_the_file_lists_nothing(tmp_path):
    commit(tmp_path)
    assert external_references(tmp_path) == {}


def test_the_entries_are_returned_by_id(tmp_path):
    listed = external_references(_project(tmp_path, GOOD))
    assert listed == {"S0a-G-12": {"id": "S0a-G-12", "location": "the archive", "reason": "kept outside"}}


def test_an_empty_list_is_of_the_shape(tmp_path):
    assert external_references(_project(tmp_path, "references: []\n")) == {}


def test_the_file_is_read_from_the_commit_not_from_the_working_tree(tmp_path):
    project = _project(tmp_path, "references: []\n")
    (project / EXTERNAL_REFERENCES_REL).write_text(GOOD, encoding="utf-8")
    assert external_references(project) == {}
    commit(project, "listed")
    (project / EXTERNAL_REFERENCES_REL).unlink()
    assert list(external_references(project)) == ["S0a-G-12"]


def test_a_project_whose_commit_cannot_be_read_is_blocked(tmp_path):
    with pytest.raises(GovError) as raised:
        external_references(tmp_path)
    assert raised.value.code == "BLOCKED" and EXTERNAL_REFERENCES_REL in raised.value.message


@pytest.mark.parametrize("text", [
    "",
    "references: [unclosed\n",
    "- id: A\n",
    "references:\n  A: {}\n",
    "references:\n  - A\n",
    "references:\n  - id: A\n    location: x\n",
    "references:\n  - id: A\n    location: '  '\n    reason: y\n",
    "references:\n  - id: 12\n    location: x\n    reason: y\n",
    GOOD + GOOD.split("\n", 1)[1],
    "references:\n  - id: DEC-086\n    location: x\n    reason: y\n",
    "references:\n  - id: CAP-13.a\n    location: x\n    reason: y\n",
])
def test_a_defective_file_is_blocked_and_named(tmp_path, text):
    with pytest.raises(GovError) as raised:
        external_references(_project(tmp_path, text))
    assert raised.value.code == "BLOCKED"
    assert EXTERNAL_REFERENCES_REL in raised.value.message
    assert raised.value.details["file"] == EXTERNAL_REFERENCES_REL


def test_a_path_that_is_not_a_file_is_blocked(tmp_path):
    (tmp_path / EXTERNAL_REFERENCES_REL).parent.mkdir(parents=True)
    (tmp_path / EXTERNAL_REFERENCES_REL).symlink_to("elsewhere.yaml")
    commit(tmp_path)
    with pytest.raises(GovError) as raised:
        external_references(tmp_path)
    assert raised.value.code == "BLOCKED" and "cannot be read" in raised.value.message

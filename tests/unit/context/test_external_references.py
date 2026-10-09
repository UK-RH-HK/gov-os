"""Unit tests for the reader of the external references file (W1-41; DEC-520)."""

from __future__ import annotations

import pytest

from gov.cli.errors import GovError
from gov.context import EXTERNAL_REFERENCES_REL, external_references

GOOD = ("references:\n"
        "  - id: S0a-G-12\n    location: the archive\n    reason: kept outside\n")


def _project(tmp_path, text):
    path = tmp_path / EXTERNAL_REFERENCES_REL
    path.parent.mkdir(parents=True)
    path.write_text(text, encoding="utf-8")
    return tmp_path


def test_a_project_without_the_file_lists_nothing(tmp_path):
    assert external_references(tmp_path) == {}


def test_the_entries_are_returned_by_id(tmp_path):
    listed = external_references(_project(tmp_path, GOOD))
    assert listed == {"S0a-G-12": {"id": "S0a-G-12", "location": "the archive", "reason": "kept outside"}}


def test_an_empty_list_is_of_the_shape(tmp_path):
    assert external_references(_project(tmp_path, "references: []\n")) == {}


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
])
def test_a_defective_file_is_blocked_and_named(tmp_path, text):
    with pytest.raises(GovError) as raised:
        external_references(_project(tmp_path, text))
    assert raised.value.code == "BLOCKED"
    assert EXTERNAL_REFERENCES_REL in raised.value.message
    assert raised.value.details["file"] == EXTERNAL_REFERENCES_REL


def test_a_path_that_is_not_a_file_is_blocked(tmp_path):
    (tmp_path / EXTERNAL_REFERENCES_REL).mkdir(parents=True)
    with pytest.raises(GovError) as raised:
        external_references(tmp_path)
    assert raised.value.code == "BLOCKED" and "cannot be read" in raised.value.message

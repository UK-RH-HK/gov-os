"""Unit tests for gov.retrieval.synthesis (W1-23 regression evidence)."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from gov.retrieval.synthesis import NOTES_REL, synthesize, validate_notes


@pytest.fixture
def repo(tmp_path):
    path = tmp_path / "repo"
    path.mkdir()
    (path / "a").mkdir()
    (path / "b").mkdir()
    (path / "a" / "one.md").write_text("line1\nline2\nline3\n")
    (path / "b" / "two.md").write_text("alpha\nbeta\n")
    return path


def _item(root, rel, start, end, item_id):
    body = b"".join((root / rel).read_bytes().splitlines(keepends=True)[start - 1:end])
    return {"id": item_id, "sha256": hashlib.sha256(body).hexdigest(),
            "path": rel, "start_line": start, "end_line": end,
            "text": body.decode()}


def test_groups_by_directory(repo):
    ev = [_item(repo, "a/one.md", 1, 3, "a1"), _item(repo, "b/two.md", 1, 2, "b1")]
    result = synthesize(repo, ev, 10)
    groups = [n["group"] for n in result["notes"]]
    assert groups == ["a", "b"]


def test_deterministic_bytes(repo):
    ev = [_item(repo, "a/one.md", 1, 3, "a1"), _item(repo, "b/two.md", 1, 2, "b1")]
    synthesize(repo, ev, 10)
    first = (repo / NOTES_REL).read_bytes()
    (repo / NOTES_REL).unlink()
    (repo / NOTES_REL).parent.rmdir()
    synthesize(repo, ev, 10)
    assert (repo / NOTES_REL).read_bytes() == first


def test_validate_clean(repo):
    ev = [_item(repo, "a/one.md", 1, 3, "a1")]
    synthesize(repo, ev, 10)
    result = validate_notes(repo)
    assert result["valid"] is True
    assert result["errors"] == []


def test_validate_detects_file_change(repo):
    ev = [_item(repo, "a/one.md", 1, 3, "a1")]
    synthesize(repo, ev, 10)
    (repo / "a" / "one.md").write_text("changed\n")
    result = validate_notes(repo)
    assert result["valid"] is False


def test_unresolved_from_gaps(repo):
    ev = [_item(repo, "a/one.md", 1, 3, "a1")]
    gaps = [{"id": "g1", "reason": "NOT_GATHERED"}]
    result = synthesize(repo, ev, 10, gaps=gaps)
    assert result["unresolved"] == [{"id": "g1", "reason": "NOT_GATHERED"}]


def test_no_unresolved_without_gaps(repo):
    ev = [_item(repo, "a/one.md", 1, 3, "a1")]
    result = synthesize(repo, ev, 10)
    assert result["unresolved"] == []


def test_validate_missing_notes(repo):
    result = validate_notes(repo)
    assert result["valid"] is False

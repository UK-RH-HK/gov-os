"""Unit tests for gov.util.frontmatter, the one parser of the check, close, adopt and tasks modules (DEC-1039 (2))."""

from __future__ import annotations

import pytest

from gov.util import frontmatter as fm


def test_parse_reads_the_mapping():
    assert fm.parse("---\nid: X-1\ntitle: a\n---\nbody\n") == {"id": "X-1", "title": "a"}


def test_parse_none_without_an_opening_line():
    assert fm.parse("# a heading\n---\n") is None


@pytest.mark.parametrize("text,kind", [
    ("---\nid: X-1\n", fm.UNCLOSED),
    ("---\nid: [X-1\n---\n", fm.NOT_YAML),
    ("---\n- a\n- b\n---\n", fm.NOT_MAPPING),
])
def test_parse_says_why(text, kind):
    with pytest.raises(fm.FrontmatterError) as raised:
        fm.parse(text)
    assert raised.value.kind == kind


def test_parse_rstrip_reads_trailing_white_space():
    with pytest.raises(fm.FrontmatterError):  # without rstrip the closing line must be exactly ``---``
        fm.parse("---\nid: X-1\n---  \n")
    assert fm.parse("--- \nid: X-1\n---  \n", rstrip=True) == {"id": "X-1"}


def test_quiet_answers_none():
    assert fm.quiet("---\nid: X-1\n") is None
    assert fm.quiet("---\nid: X-1\n---\n") == {"id": "X-1"}


def test_of_file(tmp_path):
    path = tmp_path / "T-1.md"
    path.write_text("---\nid: T-1\n---\n# T-1\n", encoding="utf-8")
    assert fm.of_file(path) == {"id": "T-1"}
    assert fm.of_file(tmp_path / "missing.md") is None
    path.write_bytes(b"---\nid: \xff\n---\n")
    assert fm.of_file(path) is None


def test_with_body():
    assert fm.with_body("---\nname: s\n---\n\n# Body\n") == ({"name": "s"}, "# Body")
    assert fm.with_body("no frontmatter") == (None, "no frontmatter")
    assert fm.with_body("---\n- a\n---\nx") == (None, "---\n- a\n---\nx")


def test_ids():
    assert fm.ids("DEC-1") == ["DEC-1"]
    assert fm.ids(["DEC-1", "", 2]) == ["DEC-1", "2"]
    assert fm.ids(None) == []

"""W2-213 slice 1: how a text names a path (SL-11, SL-14). Regression evidence only (DEC-136)."""
from __future__ import annotations

from gov.layout.references import mentions

TARGETS = {"docs/plans/old.md": False, "notes": True, "design/specs": True, "My Notes.md": False}


def _found(text: str, source: str = "docs/index.md", document: bool = True) -> set[str]:
    return {item for _, item in mentions(text, source, TARGETS, document=document, exists=lambda path: True)}


def test_a_path_in_text_front_matter_or_code_is_a_mention():
    assert _found("see docs/plans/old.md.") == {"docs/plans/old.md"}
    assert _found("superseded_by: ./docs/plans/old.md\n") == {"docs/plans/old.md"}
    assert _found('OPEN("design/specs/a.md")', "src/a.py", False) == {"design/specs"}
    assert _found("read `My Notes.md` first") == {"My Notes.md"}


def test_a_longer_path_is_no_mention():
    assert _found("archive/legacy/docs/plans/old.md and docs/plans/old.md.bak and docs/plans/old.mdx") == set()


def test_a_one_word_folder_is_named_only_with_its_slash():
    assert _found("these notes are old") == set()
    assert _found("see notes/ and notes/a.md") == {"notes"}


def test_a_relative_link_is_resolved_from_its_document():
    assert _found("[old](plans/old.md#top)") == {"docs/plans/old.md"}
    assert _found("[old]: ../plans/old.md", "docs/a/index.md") == {"docs/plans/old.md"}
    assert _found("[web](https://example.org/docs/plans/old.md)") == set()

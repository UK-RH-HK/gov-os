"""Builder tests for W2-92 S11 (DEC-1109 (2)): a verbless change label names only its clauses' heads as changers.

Regression evidence only (DEC-136). A planted register: each verbless label (**Changed by:**, **Amended by:**,
**Lifted by:**, **Superseded by:**, **Amended:**) gives as changers only the ids at the head of its clauses: the value
ends at " · " and at a list item's line break at any indentation; clauses split at ";" outside parentheses; a head is
the text before the first ":" outside parentheses; an id in parentheses is never a changer. Labels with a verb and
every other statement form give what they gave before.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov.store import loader  # noqa: E402


def _register(*entries: str) -> str:
    return "# Register\n\n" + "\n".join(entries)


def _entry(number: int, *lines: str) -> str:
    return "\n".join([f"### DEC-{number} — Entry {number}", "- **Status:** ACCEPTED", *lines, ""])


def _changers(label_line: str, me: int = 500) -> set[tuple[str, str, str]]:
    text = _register(_entry(me, label_line))
    return {(s["source"], s["target"], s["cls"]) for s in loader.register_statements(text)
            if s["target"] == f"DEC-{me}" and s["where"] == "label"}


# (1) the value ends at " · " and at any line break that starts a list item, at any indentation

def test_a_sub_item_below_the_label_names_no_changer():
    found = _changers("- **Changed by:** DEC-601 (item 2)\n  - DEC-602 moves the work, but nothing lets it write.\n"
                      "    - DEC-603 deeper still.")
    assert found == {("DEC-601", "DEC-500", "amend")}


@pytest.mark.parametrize("item", ["- ", "* ", "+ ", "1. ", "2) "])
@pytest.mark.parametrize("indent", ["", " ", "   ", "\t"])
def test_a_list_item_at_any_indentation_ends_the_value(indent, item):
    found = _changers(f"- **Lifted by:** DEC-601 as a gate\n{indent}{item}DEC-602 ran the sweep.")
    assert found == {("DEC-601", "DEC-500", "amend")}


def test_the_value_ends_at_the_middle_dot():
    found = _changers("- **Changed by:** DEC-601 · the rest names DEC-602")
    assert found == {("DEC-601", "DEC-500", "amend")}


def test_a_plain_line_break_inside_the_value_does_not_end_it():
    found = _changers("- **Changed by:** DEC-601,\n  DEC-602 (its expiry)")
    assert found == {("DEC-601", "DEC-500", "amend"), ("DEC-602", "DEC-500", "amend")}


# (2) clauses split at each ";" outside parentheses

def test_each_clause_gives_its_head():
    found = _changers("- **Changed by:** DEC-601: its basis is kept; DEC-602 item 3: the entries go; DEC-603")
    assert {s for s, _, _ in found} == {"DEC-601", "DEC-602", "DEC-603"}


def test_a_semicolon_inside_parentheses_splits_nothing():
    found = _changers("- **Changed by:** DEC-601 (item 1; and DEC-602: kept): DEC-603 is replaced")
    assert found == {("DEC-601", "DEC-500", "amend")}


# (3) a clause's head is its text before its first ":" outside parentheses, or the whole clause

def test_an_id_in_the_prose_after_the_colon_is_no_changer():
    found = _changers("- **Changed by:** DEC-601: the default is kept, replacing its basis DEC-602 and DEC-603, "
                      "which DEC-604 changed.")
    assert found == {("DEC-601", "DEC-500", "amend")}


def test_a_colon_inside_parentheses_does_not_end_the_head():
    found = _changers("- **Changed by:** DEC-601 (lifted: no record per round, DEC-605), DEC-602 (its expiry)")
    assert found == {("DEC-601", "DEC-500", "amend"), ("DEC-602", "DEC-500", "amend")}


def test_a_clause_with_no_colon_is_its_own_head():
    found = _changers("- **Changed by:** DEC-601: part one; its item 3 stands while DEC-602 holds")
    assert found == {("DEC-601", "DEC-500", "amend"), ("DEC-602", "DEC-500", "amend")}


def test_only_the_first_colon_ends_the_head():
    found = _changers("- **Changed by:** DEC-601: see: DEC-602 and DEC-603")
    assert found == {("DEC-601", "DEC-500", "amend")}


# (4) the changers are the ids in a head that stand outside parentheses

def test_an_id_inside_parentheses_in_the_head_is_no_changer():
    found = _changers("- **Changed by:** DEC-601 and DEC-602 (P-IS-4 (a), after DEC-603): the gates refuse at once")
    assert found == {("DEC-601", "DEC-500", "amend"), ("DEC-602", "DEC-500", "amend")}


def test_several_ids_in_one_head_are_all_changers():
    found = _changers("- **Changed by:** DEC-601 item 3 and DEC-602 (for one part): a broken context is refused.")
    assert found == {("DEC-601", "DEC-500", "amend"), ("DEC-602", "DEC-500", "amend")}


# each label: the class it gave before

@pytest.mark.parametrize("label, cls", [("Changed by", "amend"), ("Amended by", "amend"), ("Lifted by", "amend"),
                                        ("Superseded by", "supersede"), ("Amended", "amend")])
def test_each_verbless_label_keeps_its_class_and_drops_its_prose(label, cls):
    found = _changers(f"- **{label}:** DEC-601: the prose names DEC-602 (and DEC-603)")
    assert found == {("DEC-601", "DEC-500", cls)}
    statement = next(s for s in loader.register_statements(_register(_entry(500, f"- **{label}:** DEC-601: x")))
                     if s["source"] == "DEC-601")
    assert statement["form"] == f"**{label}:**" and statement["whole"] is False


# labels with a verb, and the other forms, are unchanged

def test_a_label_with_a_verb_still_takes_its_by_ids():
    found = _changers("- **Changed by:** amended by DEC-601 and DEC-602; the rest: DEC-603\n  - DEC-604 below")
    assert found == {("DEC-601", "DEC-500", "amend"), ("DEC-602", "DEC-500", "amend")}


def test_the_out_labels_still_name_every_id_on_their_line():
    text = _register(_entry(500, "- **Changes:** DEC-601: its basis DEC-602 (and DEC-603)\n  - DEC-604 below"))
    targets = {s["target"] for s in loader.register_statements(text) if s["form"] == "**Changes:**"}
    assert targets == {"DEC-601", "DEC-602", "DEC-603", "DEC-604"}  # the cut is S11's alone


def test_the_clause_heads_helper_on_its_own():
    assert loader._clause_heads(" DEC-1057 (lifted: R-6), DEC-522 (its expiry)\n- ") == ["1057", "522"]
    assert loader._clause_heads(" DEC-900: retired; DEC-899 item 3: removed. · DEC-901") == ["900", "899"]
    assert loader._clause_heads(" (DEC-601") == []  # an open parenthesis to the end: nothing outside it
    assert loader._clause_heads(" DEC-601) DEC-602") == ["601", "602"]  # a stray closing one: ignored

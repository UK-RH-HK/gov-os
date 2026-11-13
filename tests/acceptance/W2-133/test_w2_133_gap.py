"""W2-133 S2 (DEC-1083, DEC-1082 (2)): a register item whose first line lies in the preface or a gap between entries
carries its chunk id, not the first entry it touches further down (W2-131 S1); an item whose first line lies inside
an entry carries that entry.

In the planted register (``w2_133_support.REGISTER_TEXT``, plain text, cut by size alone) the chunk at lines 49-64
starts in the section ``Interlude`` (lines 37-50, in no entry) and runs into DEC-476 (51-77); the whole-file parent
starts in the preface. Today ``retrieve``'s ``item()`` labels a register item by the first entry its lines touch.
"""

from __future__ import annotations

import pytest

import w2_133_support as support

WHOLE_FILE = (1, len(support.REGISTER_TEXT.split("\n")) - 1)


def _only_register_item(bundle):
    items = support.register_items(bundle)
    assert len(items) == 1, f"premise: the question names one register chunk; the bundle holds {items}"
    return items[0]


def _gap_item(raw):
    item = _only_register_item(raw("lanterns", bundle_budget=300))
    assert support.holder(item["start_line"]) is None, "premise: the chunk's first line lies in no entry"
    assert support.line_of("## Interlude") < item["start_line"] < support.line_of("### DEC-476 "), \
        "premise: the chunk starts in the gap before DEC-476"
    assert support.touched(item["start_line"], item["end_line"]) == ["DEC-476"], "premise: it runs into DEC-476"
    return item


def test_s2_an_item_starting_in_the_gap_before_dec_476_carries_its_chunk_id(raw):
    item = _gap_item(raw)
    assert item["id"] == item["chunk_id"], (
        f"the chunk at lines {item['start_line']}-{item['end_line']}, starting in the gap before DEC-476, is labelled"
        f" {item['id']!r}, not its chunk id {item['chunk_id']!r}")


def test_s2_an_item_starting_in_the_gap_names_no_entry_beside_its_chunk_id(raw):
    """W2-131 S1's rule beside S2's: where an item names its entry, the entry and the id agree, so an item that
    carries its chunk id names no entry it only touches further down."""
    item = _gap_item(raw)
    assert item.get("entry") in (None, item["id"]), (
        f"the chunk starting in the gap names the entry {item.get('entry')!r} beside its id {item['id']!r}")


def test_s2_the_whole_file_parent_starting_in_the_preface_carries_its_chunk_id(raw):
    item = _only_register_item(raw("persimmon"))
    assert (item["start_line"], item["end_line"]) == WHOLE_FILE, "premise: the hit expands to the whole-file parent"
    assert support.holder(item["start_line"]) is None, "premise: the parent's first line lies in the preface"
    assert item["id"] == item["chunk_id"], (
        f"the parent at lines {WHOLE_FILE[0]}-{WHOLE_FILE[1]}, starting in the preface, is labelled {item['id']!r},"
        f" not its chunk id {item['chunk_id']!r}")


def test_s2_a_narrowed_item_starting_in_the_gap_carries_its_chunk_id(ask):
    bundle = ask("lanterns")
    assert [(e["start_line"], e["end_line"]) for e in bundle["expansions"]] == [WHOLE_FILE], \
        "premise: the hit expands to the whole-file parent"
    item = _only_register_item(bundle)
    assert support.holder(item["start_line"]) is None and (item["start_line"], item["end_line"]) != WHOLE_FILE, \
        "premise: leave_out narrowed the parent to the chunk that starts in the gap"
    assert item["id"] == item["chunk_id"], (
        f"the item narrowed to lines {item['start_line']}-{item['end_line']}, starting in the gap, is labelled"
        f" {item['id']!r}, not its chunk id {item['chunk_id']!r}")


@pytest.mark.parametrize("query, own, others", [
    pytest.param("cardamom", "DEC-476", [], id="inside-DEC-476"),
    pytest.param("tamarind", "DEC-101", ["DEC-476"], id="inside-DEC-101-running-into-DEC-476"),
])
def test_s2_guard_an_item_starting_inside_an_entry_carries_that_entry(raw, query, own, others):
    item = _only_register_item(raw(query, bundle_budget=300))
    assert support.holder(item["start_line"]) == own, f"premise: the chunk's first line lies in {own}"
    assert support.touched(item["start_line"], item["end_line"])[1:] == others, "premise: the entries it runs into"
    assert (item["id"], item.get("entry")) == (own, own), (
        f"the chunk at lines {item['start_line']}-{item['end_line']}, starting inside {own}, carries id"
        f" {item['id']!r} and entry {item.get('entry')!r}")
    assert [mark.get("entry") for mark in item.get("also", [])] == others, f"its also is {item.get('also')}"

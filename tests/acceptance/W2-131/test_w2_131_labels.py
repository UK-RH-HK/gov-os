"""W2-131 S1 (DEC-1082 (2), DEC-1073): every evidence item that lies in the decision register carries as its id the
entry that holds its first line; a chunk in the preface or between entries its chunk id; a parent expansion the id of
its first entry; and where the item names its entry (W2-92 S9's ``entry``), the two agree.

The planted register holds DEC-476, DEC-999 and DEC-1082 (``w2_131_support.REGISTER_TEXT``). Today every register
item is labelled DEC-999: the path-to-record map keeps one id per path, and DEC-999 sorts last as text.
"""

from __future__ import annotations

import pytest

import w2_131_support as support


def _only_register_item(bundle):
    items = support.register_items(bundle)
    assert len(items) == 1, f"premise: the question names one register span; the bundle holds {items}"
    return items[0]


@pytest.mark.parametrize("query, kwargs, expected", [
    pytest.param("marigold", {}, "DEC-476", id="DEC-476"),
    pytest.param("juniper", {}, "DEC-999", id="DEC-999"),
    pytest.param("cardamom", {"bundle_budget": 300}, "DEC-1082", id="DEC-1082-a-later-chunk-alone"),
])
def test_s1_a_register_chunk_is_labelled_by_the_entry_that_holds_its_first_line(ask, query, kwargs, expected):
    item = _only_register_item(ask(query, **kwargs))
    first, last = support.entry_spans()[expected]
    assert first <= item["start_line"] <= last, f"premise: the chunk at {item['start_line']} lies in {expected}"
    assert item["id"] == expected, (
        f"the chunk at lines {item['start_line']}-{item['end_line']}, inside {expected}, is labelled {item['id']!r}")


@pytest.mark.parametrize("query, where", [
    pytest.param("almanac", "The register's preface", id="the-preface"),
    pytest.param("tamarind", "Between the entries", id="between-entries"),
])
def test_s1_a_chunk_in_the_preface_or_between_entries_carries_its_chunk_id(ask, query, where):
    item = _only_register_item(ask(query))
    assert item["start_line"] <= support.line_of(where) <= item["end_line"], "premise: the chunk holds the line"
    assert not any(a <= item["start_line"] <= b for a, b in support.entry_spans().values()), \
        "premise: the chunk's first line lies in no entry"
    assert item["id"] == item["chunk_id"], (
        f"the chunk at lines {item['start_line']}-{item['end_line']}, in no entry, is labelled {item['id']!r},"
        f" not its chunk id {item['chunk_id']!r}")


def test_s1_a_parent_expansion_carries_the_id_of_its_first_entry(ask):
    bundle = ask("cardamom")
    heading = support.line_of("### DEC-1082 ")
    assert [(e["start_line"], e["end_line"]) for e in bundle["expansions"]] == [
        support.entry_spans()["DEC-1082"]], "premise: the hit on DEC-1082's last chunk expands to the whole entry"
    item = _only_register_item(bundle)
    assert item["start_line"] == heading, "premise: the expanded item starts at DEC-1082's heading"
    assert item["id"] == "DEC-1082", f"the expansion of DEC-1082 is labelled {item['id']!r}"


@pytest.mark.parametrize("name, query, kwargs", [pytest.param(*case, id=case[0]) for case in support.SCENARIOS])
def test_s1_every_register_item_s_id_is_its_entry_and_agrees_with_the_entry_key(ask, name, query, kwargs):
    items = [item for page in support.pages(ask, query, kwargs) for item in support.register_items(page)]
    assert items, "premise: the bundle (its pages followed to the end) holds a register item"
    wrong = [(item["start_line"], item["id"], support.label(item)) for item in items
             if item["id"] != support.label(item)]
    assert not wrong, f"register items labelled with another entry's id (first line, id, its own): {wrong}"
    disagree = [(item["start_line"], item["id"], item["entry"]) for item in items
                if "entry" in item and item["id"] != item["entry"]]
    assert not disagree, f"id and entry disagree (first line, id, entry): {disagree}"

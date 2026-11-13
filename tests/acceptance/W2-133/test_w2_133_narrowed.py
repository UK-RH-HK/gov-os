"""W2-133 S1 (DEC-1083, DEC-1082 (2), DEC-1073): when the register's ``leave_out`` narrows an expanded register item to
its own chunk (the parent touched a superseded or done entry, the chunk does not), the kept item's ``id``, ``entry``,
``status``, ``in_force`` and ``also`` are those of the narrowed chunk, computed from its own lines, never the parent's.

The planted register (``w2_133_support.REGISTER_TEXT``) is plain text, so its one parent is the whole file (lines
1-77): it spans the preface, the superseded DEC-100 (5-7), DEC-101 (9-35), a section between entries and DEC-476
(51-77). A hit on a chunk expands to that parent within the default budget, and ``leave_out`` narrows it back to the
chunk, since the parent touches DEC-100. Today the kept item is ``{**parent item, lines, sha256, text}``: it keeps
the parent's DEC-100 id, entry and SUPERSEDED status.
"""

from __future__ import annotations

import pytest

import w2_133_support as support

WHOLE_FILE = (1, len(support.REGISTER_TEXT.split("\n")) - 1)  # the text ends in a newline

# (question, the entry whose lines hold the chunk's first line): each question names one chunk lying clear of DEC-100
NARROWED = [
    pytest.param("persimmon", "DEC-101", id="persimmon-inside-DEC-101"),
    pytest.param("tamarind", "DEC-101", id="tamarind-DEC-101-into-DEC-476"),
    pytest.param("cardamom", "DEC-476", id="cardamom-inside-DEC-476"),
]


def _only_register_item(bundle):
    items = support.register_items(bundle)
    assert len(items) == 1, f"premise: the question names one register chunk; the bundle holds {items}"
    return items[0]


def _narrowed(ask, query):
    bundle = ask(query)
    assert [(e["start_line"], e["end_line"]) for e in bundle["expansions"]] == [WHOLE_FILE], \
        "premise: the hit expands to the whole-file parent within the default budget"
    item = _only_register_item(bundle)
    assert (item["start_line"], item["end_line"]) != WHOLE_FILE, "premise: leave_out narrowed the parent to its chunk"
    assert support.SUPERSEDED not in support.touched(item["start_line"], item["end_line"]), \
        "premise: the narrowed chunk touches no line of the superseded DEC-100"
    return bundle, item


def test_s1_premise_the_expanded_parent_spans_the_superseded_dec_100_then_dec_101(raw):
    bundle = raw("persimmon")
    item = _only_register_item(bundle)
    assert (item["start_line"], item["end_line"]) == WHOLE_FILE, "premise: retrieve sends the whole-file parent"
    assert support.touched(*WHOLE_FILE)[:2] == ["DEC-100", "DEC-101"], "premise: the parent spans DEC-100 then DEC-101"
    assert support.status_of("DEC-100") == "SUPERSEDED", "premise: DEC-100 is superseded"


@pytest.mark.parametrize("query, own", NARROWED)
def test_s1_the_narrowed_item_carries_its_own_entry_s_id_entry_and_status(ask, query, own):
    _, item = _narrowed(ask, query)
    assert support.holder(item["start_line"]) == own, f"premise: the chunk's first line lies in {own}"
    wrong = {key: (item.get(key), want) for key, want in
             (("id", own), ("entry", own), ("status", support.status_of(own)), ("in_force", True))
             if item.get(key) != want}
    if "not_in_force" in item:
        wrong["not_in_force"] = (item["not_in_force"], "absent: the chunk's own entry is in force")
    assert not wrong, (f"the item narrowed to lines {item['start_line']}-{item['end_line']}, inside {own}, carries"
                       f" another entry's marks (field: (carried, its own)): {wrong}")


@pytest.mark.parametrize("query, own", NARROWED)
def test_s1_the_narrowed_item_s_also_names_the_other_entries_its_own_lines_touch(ask, query, own):
    _, item = _narrowed(ask, query)
    others = support.touched(item["start_line"], item["end_line"])[1:]
    carried = [mark.get("entry") for mark in item.get("also", [])]
    assert carried == others, (f"the item narrowed to lines {item['start_line']}-{item['end_line']} names as its other"
                               f" entries {carried}, where its own lines touch {others}")


@pytest.mark.parametrize("query, own", NARROWED)
def test_s1_the_narrowed_item_s_marks_are_those_its_chunk_carries_sent_alone(ask, query, own):
    _, item = _narrowed(ask, query)
    alone = _only_register_item(ask(query, bundle_budget=300))
    assert not ask(query, bundle_budget=300)["expansions"], "premise: at a budget of 300 the chunk is sent alone"
    assert (alone["start_line"], alone["end_line"], alone["chunk_id"]) == \
        (item["start_line"], item["end_line"], item["chunk_id"]), "premise: the same chunk, narrowed and alone"
    marks = {key: item[key] for key in support.LABEL_FIELDS if key in item}
    own_marks = {key: alone[key] for key in support.LABEL_FIELDS if key in alone}
    assert marks == own_marks, (f"the narrowed item's marks {marks} are not those its own lines give it sent alone"
                                f" {own_marks}")


@pytest.mark.parametrize("query, kwargs", [
    pytest.param("persimmon", {}, id="a-narrowed-parent"),
    pytest.param("quince", {}, id="a-hit-on-DEC-100-expanded"),
    pytest.param("quince", {"bundle_budget": 300}, id="a-hit-on-DEC-100-alone"),
])
def test_s1_guard_what_leave_out_leaves_out_and_counts_is_unchanged(ask, query, kwargs):
    bundle = ask(query, **kwargs)
    kept = [(item["start_line"], item["end_line"]) for item in support.register_items(bundle)]
    assert not [span for span in kept if support.SUPERSEDED in support.touched(*span)], \
        f"a register item that touches the superseded DEC-100 is kept: {kept}"
    assert bundle.get("left_out") == {"count": 1, "superseded": ["DEC-100"], "done": []}, \
        f"left_out is {bundle.get('left_out')}"

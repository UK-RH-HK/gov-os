"""W2-135 S1 (DEC-1086 B, BUNDLE-BUDGET-1 (a)): an evidence item whose text is over 4,000 characters is sent as its
first 4,000 characters and carries ``cut: {"chars": <its full length>, "sent": 4000}``; its path, start_line, end_line,
id, chunk_id and sha256 (of the full span, as today) are unchanged, so a citation still names the whole span.

The full span is read from the planted files (``w2_135_support.span_text``, ``span_bytes``); today's item is the one
``retrieve.py`` as ``w2/integrate`` held it gives on the same store (``w2_135_support.TODAY_BLOB``).
"""

from __future__ import annotations

import hashlib

import pytest

import w2_135_support as support

CAP = support.CAP
LONG = support.line_of(support.SURVEY, "The quillwort tally")
SECTION = support.section_of_survey("# Survey of the harbour")

# (case name, question, keyword arguments, path, (first line, last line))
SCENARIOS = [
    ("json-one-line-24575", "zephyrine", {}, support.JSON, (1, 1)),
    ("markdown-long-line-alone", "quillwort", {"bundle_budget": 1}, support.SURVEY, (LONG, LONG)),
    ("markdown-section-expanded", "quillwort", {}, support.SURVEY, SECTION),
    ("one-over-the-cap-4001", "beacon", {}, support.OVER_CAP, (1, 1)),
    ("accented-4500-characters", "brioche", {}, support.ACCENTED_OVER, (1, 1)),
]
CASES = [pytest.param(*case, id=case[0]) for case in SCENARIOS]


def _the_item(bundle, rel, lines):
    found = [item for item in bundle["evidence"]
             if item["path"] == rel and (item["start_line"], item["end_line"]) == lines]
    assert len(found) == 1, f"premise: one item {rel}:{lines[0]}-{lines[1]}; the bundle sends " \
                            f"{[(i['path'], i['start_line'], i['end_line']) for i in bundle['evidence']]}"
    return found[0]


@pytest.mark.parametrize("name, query, kwargs, rel, lines", CASES)
def test_s1_premise_today_sends_the_item_whole(ask, today, name, query, kwargs, rel, lines):
    full = support.span_text(rel, *lines)
    assert len(full) > CAP, f"premise: the span holds over {CAP} characters ({len(full)})"
    item = _the_item(ask(query, module=today, **kwargs), rel, lines)
    assert item["text"] == full and "cut" not in item, "premise: today's code sends the item whole, with no cut key"


@pytest.mark.parametrize("name, query, kwargs, rel, lines", CASES)
def test_s1_the_item_s_text_is_its_first_4000_characters(ask, name, query, kwargs, rel, lines):
    full = support.span_text(rel, *lines)
    item = _the_item(ask(query, **kwargs), rel, lines)
    assert len(item["text"]) == CAP and item["text"] == full[:CAP], \
        f"{rel}:{lines[0]}-{lines[1]} is sent as {len(item['text'])} characters, not its first {CAP} " \
        f"(of {len(full)})"


@pytest.mark.parametrize("name, query, kwargs, rel, lines", CASES)
def test_s1_the_cut_item_carries_its_cut_key(ask, name, query, kwargs, rel, lines):
    full = support.span_text(rel, *lines)
    item = _the_item(ask(query, **kwargs), rel, lines)
    assert item.get("cut") == {"chars": len(full), "sent": CAP}, \
        f"{rel}:{lines[0]}-{lines[1]} carries cut {item.get('cut')!r}, not {{'chars': {len(full)}, 'sent': {CAP}}}"


def test_s1_the_one_line_json_file_s_cut_names_24575_characters(ask):
    item = _the_item(ask("zephyrine"), support.JSON, (1, 1))
    assert item.get("cut") == {"chars": 24_575, "sent": CAP}, f"the JSON file's item carries {item.get('cut')!r}"


@pytest.mark.parametrize("name, query, kwargs, rel, lines", CASES)
def test_s1_guard_the_cited_fields_are_today_s_and_the_sha256_is_of_the_full_span(ask, today, name, query, kwargs,
                                                                                 rel, lines):
    item = _the_item(ask(query, **kwargs), rel, lines)
    was = _the_item(ask(query, module=today, **kwargs), rel, lines)
    for key in ("path", "start_line", "end_line", "id", "chunk_id", "sha256"):
        assert item[key] == was[key], f"the cut item's {key!r} is {item[key]!r}, where today's is {was[key]!r}"
    assert item["sha256"] == hashlib.sha256(support.span_bytes(rel, *lines)).hexdigest(), \
        "the sha256 is not of the full span"

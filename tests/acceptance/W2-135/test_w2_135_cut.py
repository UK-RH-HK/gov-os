"""W2-135 S1 (DEC-1086 B, BUNDLE-BUDGET-1 (a); round 2, the review's F1): in an evidence item, each line over 4,000
characters is sent as its first 4,000 characters; every other line of the item is sent whole, so an item of ordinary
lines is never cut however long it is. An item with a cut line carries
``cut: {"chars": <the item's full text length>, "sent": <the length of the text sent>, "lines": [<the lines cut>]}``;
its path, start_line, end_line, id, chunk_id and sha256 (of the full span, as today) are unchanged.

The full span and what is sent are read from the planted files (``w2_135_support.span_text``, ``sent_text``,
``cut_key``): a line's length is counted without its newline, and a cut line keeps its newline (README N-1). Today's
item is the one ``retrieve.py`` and ``register.py`` as ``w2/integrate`` held them give on the same store
(``w2_135_support.TODAY_BLOBS``).
"""

from __future__ import annotations

import hashlib

import pytest

import w2_135_support as support

CAP = support.CAP
LONG = support.line_of(support.SURVEY, "The quillwort tally")
SECTION = support.section_of_survey("# Survey of the harbour")
REG_LONG = support.line_of(support.REGISTER, "- **Clause 6:**")
REG_ALL = (1, support.line_count(support.REGISTER))
REGISTER = {"repo": "register"}

# (case name, question, keyword arguments of ``ask``, path, (first line, last line))
SCENARIOS = [
    ("json-one-line-24575", "zephyrine", {}, support.JSON, (1, 1)),
    ("markdown-long-line-alone", "quillwort", {"bundle_budget": 1}, support.SURVEY, (LONG, LONG)),
    ("markdown-section-expanded", "quillwort", {}, support.SURVEY, SECTION),
    ("one-over-the-cap-4001", "beacon", {}, support.OVER_CAP, (1, 1)),
    ("accented-4500-characters", "brioche", {}, support.ACCENTED_OVER, (1, 1)),
    ("register-parent-retrieve-alone", "samphire", REGISTER, support.REGISTER, REG_ALL),
    ("register-narrowed-to-the-long-clause", "samphire", {**REGISTER, "pipeline": True}, support.REGISTER,
     (REG_LONG, REG_LONG)),
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
    assert support.cut_key(rel, *lines), f"premise: the span holds a line over {CAP} characters"
    item = _the_item(ask(query, module=today, **kwargs), rel, lines)
    assert item["text"] == full and "cut" not in item, "premise: today's code sends the item whole, with no cut key"


@pytest.mark.parametrize("name, query, kwargs, rel, lines", CASES)
def test_s1_each_line_over_4000_is_its_first_4000_and_every_other_line_whole(ask, name, query, kwargs, rel, lines):
    want = support.sent_text(rel, *lines)
    item = _the_item(ask(query, **kwargs), rel, lines)
    sent = item["text"].splitlines(keepends=True)
    assert item["text"] == want, \
        f"{rel}:{lines[0]}-{lines[1]} is sent as {len(item['text'])} characters in {len(sent)} lines, the longest " \
        f"{max(map(len, sent), default=0)}; S1 sends {len(want)} (each line over {CAP} cut, every other line whole)"


@pytest.mark.parametrize("name, query, kwargs, rel, lines", CASES)
def test_s1_the_item_with_a_cut_line_carries_its_cut_key(ask, name, query, kwargs, rel, lines):
    want = support.cut_key(rel, *lines)
    item = _the_item(ask(query, **kwargs), rel, lines)
    assert item.get("cut") == want, f"{rel}:{lines[0]}-{lines[1]} carries cut {item.get('cut')!r}, not {want!r}"


def test_s1_the_one_line_json_file_s_cut_names_24575_characters(ask):
    item = _the_item(ask("zephyrine"), support.JSON, (1, 1))
    assert item.get("cut") == {"chars": 24_575, "sent": CAP, "lines": [1]}, \
        f"the JSON file's item carries {item.get('cut')!r}"


def test_s1_the_long_markdown_line_alone_keeps_its_newline(ask):
    """The item of line 9 alone: the line's first 4,000 characters and its newline (10,632 characters in all)."""
    item = _the_item(ask("quillwort", bundle_budget=1), support.SURVEY, (LONG, LONG))
    want = {"chars": support.LONG_LINE_CHARS + 1, "sent": CAP + 1, "lines": [LONG]}
    assert (item["text"], item.get("cut")) == (support.LONG_LINE[:CAP] + "\n", want), \
        f"line {LONG} alone is sent as {len(item['text'])} characters with cut {item.get('cut')!r}, not {want!r}"


@pytest.mark.parametrize("name, query, kwargs", [
    pytest.param("markdown-section-expanded", "quillwort", {}, id="markdown-section-expanded"),
    pytest.param("register-parent-retrieve-alone", "samphire", REGISTER, id="register-parent-retrieve-alone"),
])
def test_s1_guard_the_long_line_s_neighbours_are_sent_whole_in_their_own_lines(ask, name, query, kwargs):
    """Every line of the item but the long one is sent whole, as a line of its own, in order (the review's F1: an
    item is never cut at a character count)."""
    rel, (first, last), long = ((support.SURVEY, SECTION, LONG) if name.startswith("markdown")
                                else (support.REGISTER, REG_ALL, REG_LONG))
    item = _the_item(ask(query, **kwargs), rel, (first, last))
    sent = item["text"].splitlines(keepends=True)
    full = support.span_text(rel, first, last).splitlines(keepends=True)
    assert len(sent) == len(full), f"{rel}:{first}-{last} is sent in {len(sent)} lines, not {len(full)}"
    for number, (now, was) in enumerate(zip(sent, full), first):
        if number != long:
            assert now == was, f"{rel} line {number}, beside the long line {long}, is not sent whole"


@pytest.mark.parametrize("name, query, kwargs, rel, lines", CASES)
def test_s1_guard_the_cited_fields_are_today_s_and_the_sha256_is_of_the_full_span(ask, today, name, query, kwargs,
                                                                                 rel, lines):
    item = _the_item(ask(query, **kwargs), rel, lines)
    was = _the_item(ask(query, module=today, **kwargs), rel, lines)
    for key in ("path", "start_line", "end_line", "id", "chunk_id", "sha256"):
        assert item[key] == was[key], f"the cut item's {key!r} is {item[key]!r}, where today's is {was[key]!r}"
    assert item["sha256"] == hashlib.sha256(support.span_bytes(rel, *lines)).hexdigest(), \
        "the sha256 is not of the full span"


def test_s1_guard_the_word_asked_for_past_character_4000_of_an_ordinary_section_is_sent(ask):
    """The review's F1 probe: the logbook's section (about 11,000 characters of ordinary lines) is expanded around the
    chunk that holds the word asked for, past character 4,000; the word is in the text sent."""
    first, last = support.section_of(support.LOGBOOK, "# Logbook")
    item = _the_item(ask(support.LOGBOOK_WORD), support.LOGBOOK, (first, last))
    assert support.LOGBOOK_WORD in item["text"], \
        f"the word asked for (line {support.LOGBOOK_LINE}) is not in the {len(item['text'])} characters sent"

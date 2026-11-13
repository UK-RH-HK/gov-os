"""W2-135 S2 (DEC-1086 B; round 2, the review's F2): an item with no line over 4,000 characters is sent as today, with
no cut key, whatever its total length; a register item narrowed from a cut parent carries a cut key only if its own
lines hold a cut line.

"As today" is the item ``retrieve.py`` and ``register.py`` as ``w2/integrate`` held them give on the same store
(``w2_135_support.TODAY_BLOBS``): every field equal. A line's length is counted in characters, not bytes, and without
its newline (README N-1, N-2).
"""

from __future__ import annotations

import pytest

import w2_135_support as support

CAP = support.CAP
REG_LONG = support.line_of(support.REGISTER, "- **Clause 6:**")
MARJORAM = support.line_of(support.REGISTER, "- **Clause 24:**")
GOV_RETRIEVE = {"repo": "register", "pipeline": True}

# (case name, question, keyword arguments of ``ask``, the path its items lie in)
SCENARIOS = [
    ("exactly-the-cap-4000", "lantern", {}, support.AT_CAP),
    ("accented-3000-characters-over-4000-bytes", "meringue", {}, support.ACCENTED_UNDER),
    ("ordinary-note", "kestrel", {}, support.NOTE),
    ("ordinary-section-expanded-about-11000", support.LOGBOOK_WORD, {}, support.LOGBOOK),
    ("line-of-4000-and-its-newline-expanded", "candlewick", {}, support.CANDLE),
    ("line-of-4000-and-its-newline-alone", "candlewick", {"bundle_budget": 1}, support.CANDLE),
    ("register-narrowed-without-the-long-clause", "marjoram", GOV_RETRIEVE, support.REGISTER),
]
CASES = [pytest.param(*case, id=case[0]) for case in SCENARIOS]


@pytest.mark.parametrize("name, query, kwargs, rel", CASES)
def test_s2_an_item_with_no_line_over_4000_is_sent_as_today_with_no_cut_key(ask, today, name, query, kwargs, rel):
    new, old = ask(query, **kwargs), ask(query, module=today, **kwargs)
    items = support.items_of(new, rel)
    assert items and [item["path"] for item in new["evidence"]] == [rel] * len(items), \
        f"premise: the question reaches {rel} alone; it sends {[i['path'] for i in new['evidence']]}"
    for item in items:
        full = support.span_text(rel, item["start_line"], item["end_line"])
        where = f"{rel}:{item['start_line']}-{item['end_line']} ({len(full)} characters)"
        assert not support.has_long_line(full), f"premise: {where} holds no line over {CAP}"
        assert "cut" not in item, f"{where} carries cut {item['cut']!r}"
        assert item["text"] == full, f"{where} is sent as {len(item['text'])}"
    assert new["evidence"] == old["evidence"], "an item with no line over the cap differs from today's"


def test_s2_premise_the_long_cases_are_long(ask, today):
    """The logbook's section is sent as one item of about 11,000 characters, the candle's two lines as one item over
    4,000 characters, today: their total length is over the cap, no line of them is."""
    logbook = support.items_of(ask(support.LOGBOOK_WORD, module=today), support.LOGBOOK)
    candle = support.items_of(ask("candlewick", module=today), support.CANDLE)
    assert [(i["start_line"], i["end_line"]) for i in logbook] == [support.section_of(support.LOGBOOK, "# Logbook")]
    assert len(logbook[0]["text"]) > 10_500
    assert [(i["start_line"], i["end_line"]) for i in candle] == [(1, 2)] and len(candle[0]["text"]) > CAP + 1


def test_s2_premise_the_narrowed_item_s_parent_holds_the_long_clause(ask, today):
    """Through ``retrieve`` alone, the ``marjoram`` item is the register's one parent, whose lines hold the long clause
    (line 17), and ``gov retrieve``'s ``leave_out`` narrows it to its own chunk, clear of that line (today's code)."""
    parent = support.items_of(ask("marjoram", module=today, repo="register"), support.REGISTER)
    assert [(i["start_line"], i["end_line"]) for i in parent] == [(1, support.line_count(support.REGISTER))]
    narrowed = support.items_of(ask("marjoram", module=today, **GOV_RETRIEVE), support.REGISTER)
    assert len(narrowed) == 1 and narrowed[0]["start_line"] <= MARJORAM <= narrowed[0]["end_line"]
    assert not narrowed[0]["start_line"] <= REG_LONG <= narrowed[0]["end_line"], narrowed[0]["start_line"]


def test_s2_a_narrowed_register_item_carries_no_cut_key_unless_its_own_lines_hold_a_cut_line(ask):
    """The review's F2: the narrowed item holds no line over 4,000, so it carries no cut key, whatever its parent's,
    and its text is its own lines whole."""
    items = support.items_of(ask("marjoram", **GOV_RETRIEVE), support.REGISTER)
    assert len(items) == 1, f"premise: one narrowed item; {[(i['start_line'], i['end_line']) for i in items]}"
    item = items[0]
    full = support.span_text(support.REGISTER, item["start_line"], item["end_line"])
    assert "cut" not in item, f"the narrowed item {item['start_line']}-{item['end_line']} carries cut {item['cut']!r}"
    assert item["text"] == full


def test_s2_every_item_with_no_line_over_the_cap_in_every_scenario_is_today_s(ask, today):
    seen = 0
    for name, query, kwargs in support.SCENARIOS:
        olds = support.pages(lambda q, **more: ask(q, module=today, **more), query, kwargs)
        news = support.pages(ask, query, kwargs)
        assert len(news) == len(olds), name
        for old, new in zip(olds, news):
            assert len(new["evidence"]) == len(old["evidence"]), name
            for was, now in zip(old["evidence"], new["evidence"]):
                if not support.has_long_line(was["text"]):
                    seen += 1
                    assert now == was, f"{name}: {now['path']}:{now['start_line']}-{now['end_line']} " \
                                       f"({len(was['text'])} characters, no line over {CAP}) differs from today's"
    assert seen >= 30, f"premise: the scenarios send many items with no line over the cap ({seen})"

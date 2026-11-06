"""W2-135 S2 (DEC-1086 B): an item at or under 4,000 characters is sent as today, with no cut key.

"As today" is the item ``retrieve.py`` as ``w2/integrate`` held it gives on the same store
(``w2_135_support.TODAY_BLOB``): every field equal. The cap counts characters, not bytes: a 3,000-character accented
line of over 4,000 bytes is under it.
"""

from __future__ import annotations

import pytest

import w2_135_support as support

CAP = support.CAP

# (case name, question, the path its items lie in)
SCENARIOS = [
    ("exactly-the-cap-4000", "lantern", support.AT_CAP),
    ("accented-3000-characters-over-4000-bytes", "meringue", support.ACCENTED_UNDER),
    ("ordinary-note", "kestrel", support.NOTE),
]
CASES = [pytest.param(*case, id=case[0]) for case in SCENARIOS]


@pytest.mark.parametrize("name, query, rel", CASES)
def test_s2_an_item_at_or_under_4000_characters_is_sent_as_today_with_no_cut_key(ask, today, name, query, rel):
    new, old = ask(query), ask(query, module=today)
    items = support.items_of(new, rel)
    assert items and [item["path"] for item in new["evidence"]] == [rel] * len(items), \
        f"premise: the question reaches {rel} alone; it sends {[i['path'] for i in new['evidence']]}"
    for item in items:
        full = support.span_text(rel, item["start_line"], item["end_line"])
        assert len(full) <= CAP, f"premise: {rel}:{item['start_line']}-{item['end_line']} holds at most {CAP}"
        assert "cut" not in item, f"an item of {len(full)} characters carries cut {item['cut']!r}"
        assert item["text"] == full, f"an item of {len(full)} characters is sent as {len(item['text'])}"
    assert new["evidence"] == old["evidence"], "an item at or under the cap differs from today's"


def test_s2_every_item_at_or_under_the_cap_in_every_scenario_is_today_s(ask, today):
    seen = 0
    for name, query, kwargs in support.SCENARIOS:
        olds = support.pages(lambda q, **more: ask(q, module=today, **more), query, kwargs)
        news = support.pages(ask, query, kwargs)
        assert len(news) == len(olds), name
        for old, new in zip(olds, news):
            assert len(new["evidence"]) == len(old["evidence"]), name
            for was, now in zip(old["evidence"], new["evidence"]):
                if len(was["text"]) <= CAP:
                    seen += 1
                    assert now == was, f"{name}: {now['path']}:{now['start_line']}-{now['end_line']} " \
                                       f"({len(was['text'])} characters) differs from today's"
    assert seen >= 20, f"premise: the scenarios send many items at or under the cap ({seen})"

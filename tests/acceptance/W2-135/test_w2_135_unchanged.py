"""W2-135 S3 (DEC-1086 B): nothing else changes: the same items in the same order, the batches, the expansions and
their left-out spans, the repeats, the gaps, the continuation, and the budget's ``used`` (still counted on the full
text, as today). The reranker's input is unchanged.

"Before" is ``retrieve.py`` as ``w2/integrate`` held it (``w2_135_support.TODAY_BLOB``), loaded from git beside the
running tree's; both are asked on the same store, in the same process, with the same stand-ins, every batched question
followed through its continuations. The comparison sets apart each item's ``text`` and ``cut`` only, and even those
are held: an item with a ``cut`` key is today's text's first 4,000 characters, and one without is today's text.
"""

from __future__ import annotations

import pytest

import w2_135_support as support

CAP = support.CAP
CASES = [pytest.param(*case, id=case[0]) for case in support.SCENARIOS]
APART = ("text", "cut")


def _cited(bundle):
    return [(item["path"], item["start_line"], item["end_line"], item["chunk_id"], item["sha256"])
            for item in bundle["evidence"]]


def _same(old, new, where):
    assert set(new) == set(old), f"{where}: the bundle's keys changed: {sorted(set(new) ^ set(old))}"
    for key in ("budget", "batches", "expansions", "repeats", "gaps", "continuation", "merge", "facets",
                "stopping_reason", "rerank"):
        assert new.get(key) == old.get(key), f"{where}: the bundle's {key!r} changed"
    for key in sorted(set(new) - {"evidence"}):
        assert new[key] == old[key], f"{where}: the bundle's {key!r} changed"
    assert _cited(new) == _cited(old), f"{where}: the items, their order or their cited lines changed"
    for was, now in zip(old["evidence"], new["evidence"]):
        span = f"{where}: {now['path']}:{now['start_line']}-{now['end_line']}"
        assert {k: v for k, v in now.items() if k not in APART} == {k: v for k, v in was.items() if k not in APART}, \
            f"{span}: a field beside the text and the cut key changed"
        if "cut" in now:
            assert now["text"] == was["text"][:CAP], f"{span}: the cut text is not today's first {CAP} characters"
        else:
            assert now["text"] == was["text"], f"{span}: the text changed with no cut key"


def _both(ask, today, query, kwargs):
    """Today's pages and the running tree's, each with the texts its reranker was sent."""
    old_scorer, new_scorer = support.Scorer(), support.Scorer()
    olds = support.pages(lambda q, **more: ask(q, module=today, scorer=old_scorer, **more), query, kwargs)
    news = support.pages(lambda q, **more: ask(q, scorer=new_scorer, **more), query, kwargs)
    return olds, news, old_scorer.texts, new_scorer.texts


@pytest.mark.parametrize("name, query, kwargs", CASES)
def test_s3_the_bundles_are_today_s_but_for_the_cut_text_and_cut_key(ask, today, name, query, kwargs):
    olds, news, *_ = _both(ask, today, query, kwargs)
    assert len(news) == len(olds), f"{name}: {len(news)} pages, where today gives {len(olds)}"
    for number, (old, new) in enumerate(zip(olds, news), 1):
        _same(old, new, f"{name}, page {number}")


@pytest.mark.parametrize("name, query, kwargs", CASES)
def test_s3_the_reranker_s_input_is_today_s(ask, today, name, query, kwargs):
    _, _, old_texts, new_texts = _both(ask, today, query, kwargs)
    assert old_texts, f"premise: {name}: the reranker is sent texts"
    assert new_texts == old_texts, f"{name}: the texts the reranker is sent changed"


def test_s3_premise_the_scenarios_hold_what_s3_names(ask, today):
    """Today's bundles of the scenarios hold an expansion with a left-out span, repeats of both kinds, gaps, a
    continuation, items over the cap alone and inside an expansion, and a call whose budget, counted on the cut text,
    would let a parent expand that today's (on the full text) does not."""
    held = {}
    for name, query, kwargs in support.SCENARIOS:
        held[name] = support.pages(lambda q, **more: ask(q, module=today, **more), query, kwargs)
    every = [bundle for found in held.values() for bundle in found]
    assert any(e.get("left_out") for b in every for e in b["expansions"]), "no expansion leaves a span out"
    reasons = {r["reason"] for b in every for r in b["repeats"]}
    assert {"SENT_IN_AN_EARLIER_PARENT", "SENT_EARLIER_AS_A_CHILD"} <= reasons, f"repeats of {reasons} only"
    assert any(g["reason"] == "NOT_GATHERED" for b in every for g in b["gaps"]), "no gap"
    assert any(b["continuation"] for b in every), "no continuation"
    assert any(len(b["batches"]) > 1 for b in every), "no second batch"
    expanded = {(e["path"], e["start_line"], e["end_line"]) for b in every for e in b["expansions"]}
    over = [(i["path"], i["start_line"], i["end_line"]) for b in every for i in b["evidence"] if len(i["text"]) > CAP]
    assert any(span not in expanded for span in over), "no item over the cap sent alone"
    assert any(span in expanded for span in over), "no expansion over the cap"
    # the JSON file beside the long line: today used is over the limit, so the survey's section is not expanded;
    # counted on the cut text it would fit, so a count on the cut text changes the bundle
    bundle = held["json-beside-the-long-line"][0]
    limit, used = bundle["budget"]["bundle"]["limit"], bundle["budget"]["bundle"]["used"]
    assert used > limit and not bundle["expansions"], bundle["budget"]
    assert used == sum(support.tokens(item["text"]) for item in bundle["evidence"])
    first, last = support.section_of_survey("# Survey of the harbour")
    long = support.line_of(support.SURVEY, "The quillwort tally")
    cost = support.tokens(support.span_text(support.SURVEY, first, last)) \
        - support.tokens(support.span_text(support.SURVEY, long, long))
    on_cut = sum(support.tokens(item["text"][:CAP]) for item in bundle["evidence"])
    assert on_cut + cost <= limit < used + cost, (on_cut, cost, used, limit)

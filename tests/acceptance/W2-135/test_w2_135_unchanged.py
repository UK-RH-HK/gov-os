"""W2-135 S3 (DEC-1086 B): nothing else changes: the same items in the same order, the batches, the expansions and
their left-out spans, the repeats, the gaps, the continuation, and the budget's ``used`` (still counted on the full
text, as today). The reranker's input is unchanged.

"Before" is ``retrieve.py`` and ``register.py`` as ``w2/integrate`` held them (``w2_135_support.TODAY_BLOBS``), loaded
from git beside the running tree's; both are asked on the same store, in the same process, with the same stand-ins,
through ``retrieve`` alone and, on the register's repository, through ``gov retrieve``'s pipeline, every batched
question followed through its continuations. The comparison takes off only the cut lines' text and the cut key: an
item's text is today's line for line, each line either today's whole or, where today's line is over 4,000 characters,
its first 4,000 and its newline. Every other field and bundle key must be today's.
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


def _lines_today_s_but_cut(was: str, now: str, span: str) -> None:
    """``now`` is ``was`` line for line, each line whole or, where ``was``'s line is over CAP, cut to CAP."""
    old, new = was.splitlines(keepends=True), now.splitlines(keepends=True)
    assert len(new) == len(old), f"{span}: sent in {len(new)} lines, where today sends {len(old)}"
    for number, (line, sent) in enumerate(zip(old, new), 1):
        body = line.rstrip("\n")
        if sent != line:
            assert len(body) > CAP and sent == body[:CAP] + line[len(body):], \
                f"{span}: its line {number} ({len(body)} characters) is changed beside a cut of a line over {CAP}"


def _same(old, new, where):
    assert set(new) == set(old), f"{where}: the bundle's keys changed: {sorted(set(new) ^ set(old))}"
    for key in ("budget", "batches", "expansions", "repeats", "gaps", "continuation", "merge", "facets",
                "stopping_reason", "rerank", "left_out"):
        assert new.get(key) == old.get(key), f"{where}: the bundle's {key!r} changed"
    for key in sorted(set(new) - {"evidence"}):
        assert new[key] == old[key], f"{where}: the bundle's {key!r} changed"
    assert _cited(new) == _cited(old), f"{where}: the items, their order or their cited lines changed"
    for was, now in zip(old["evidence"], new["evidence"]):
        span = f"{where}: {now['path']}:{now['start_line']}-{now['end_line']}"
        assert {k: v for k, v in now.items() if k not in APART} == {k: v for k, v in was.items() if k not in APART}, \
            f"{span}: a field beside the text and the cut key changed"
        _lines_today_s_but_cut(was["text"], now["text"], span)


def _both(ask, today, query, kwargs):
    """Today's pages and the running tree's, each with the texts its reranker was sent."""
    old_scorer, new_scorer = support.Scorer(), support.Scorer()
    olds = support.pages(lambda q, **more: ask(q, module=today, scorer=old_scorer, **more), query, kwargs)
    news = support.pages(lambda q, **more: ask(q, scorer=new_scorer, **more), query, kwargs)
    return olds, news, old_scorer.texts, new_scorer.texts


@pytest.mark.parametrize("name, query, kwargs", CASES)
def test_s3_the_bundles_are_today_s_but_for_the_cut_lines_and_cut_key(ask, today, name, query, kwargs):
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
    continuation, a register entry left out, items with a line over the cap alone and inside an expansion, an
    expansion over the cap with no such line, and a call whose budget, counted on the cut text, would let a parent
    expand that today's (on the full text) does not."""
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
    assert any(b.get("left_out") for b in every), "no register entry left out"
    expanded = {(e["path"], e["start_line"], e["end_line"]) for b in every for e in b["expansions"]}
    spans = [((i["path"], i["start_line"], i["end_line"]), i["text"]) for b in every for i in b["evidence"]]
    long = [span for span, text in spans if support.has_long_line(text)]
    assert any(span not in expanded for span in long), "no item with a line over the cap sent alone"
    assert any(span in expanded for span in long), "no expansion with a line over the cap"
    assert any(span in expanded and len(text) > 10_000 and not support.has_long_line(text) for span, text in spans), \
        "no expansion of ordinary lines over 10,000 characters"
    # the JSON file beside the long line: today used is over the limit, so the survey's section is not expanded;
    # counted on the cut text it would fit, so a count on the cut text changes the bundle
    bundle = held["json-beside-the-long-line"][0]
    limit, used = bundle["budget"]["bundle"]["limit"], bundle["budget"]["bundle"]["used"]
    assert used > limit and not bundle["expansions"], bundle["budget"]
    assert used == sum(support.tokens(item["text"]) for item in bundle["evidence"])
    first, last = support.section_of_survey("# Survey of the harbour")
    long_line = support.line_of(support.SURVEY, "The quillwort tally")
    cost = support.tokens(support.span_text(support.SURVEY, first, last)) \
        - support.tokens(support.span_text(support.SURVEY, long_line, long_line))
    on_cut = sum(support.tokens(support.cut(item["text"])[0]) for item in bundle["evidence"])
    assert on_cut + cost <= limit < used + cost, (on_cut, cost, used, limit)

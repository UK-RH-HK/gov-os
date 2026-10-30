"""W2-61, KPI success 5 -- stacked, never giant.

"Stacked, never giant: each question is answered by retrieval in batches, ranked and stacked within the budget,
never one giant query or context; the script measures the stacked answer [DEC-860 items 1 to 3]".

The rule, as the ticket's brief states it: each question's first call passes ``--batch-size`` and
``--bundle-budget``; while the last call returned a ``continuation`` and the stacked context is within the stack
budget, the next call passes ``--continue <that token>`` with the same options. The stacked context is the calls'
items in order, an item already taken (same path and span) taken once; an item's size is its text's length in
characters divided by 4, rounded up; the stacking stops before the first item that would pass the stack budget, or
when a call returns no continuation. hit@5 is counted on the stacked context's first five items, in the bundle on
the first call's items, full evidence on the whole stacked context.

The planted gov logs each call's arguments; its continuation tokens are ``w2_61_support.token(query, n)``.

Red now: ``gov.retrieval.measure`` does not exist.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_61_support as s  # noqa: E402

GOLD_HEADING = "## DEC-4 The resume"
SOURCES = [{"path": s.DECISIONS, "heading": GOLD_HEADING}]
QUESTIONS = {
    # id: (question, (hit_at_5, in_bundle, full_evidence, first_gold_rank, calls))
    "s01": ("Found only in the second batch, at rank 3?", (True, False, True, 3, 2)),
    "s02": ("Found only in the second batch, at rank 6?", (False, False, True, 6, 2)),
    "s03": ("An item repeated in a later batch is taken once?", (True, False, True, 4, 2)),
    "s04": ("Three batches, the last without a continuation?", (True, False, True, 3, 3)),
}


def _plant(world):
    gold = world.section(s.DECISIONS, GOLD_HEADING)
    n = world.noise
    bundles = {
        "s01": [[n(1), n(2)], [gold]],
        "s02": [[n(1), n(2), n(3), n(4), n(5)], [gold]],
        "s03": [[n(1), n(2)], [n(1), n(2), n(3), gold]],
        "s04": [[n(1)], [n(2)], [gold]],
    }
    for qid, (question, _) in QUESTIONS.items():
        world.question(qid, {"question": question, "gold_answer": "from its last checkpoint", "sources": SOURCES},
                       bundles[qid])


@pytest.fixture
def world(tmp_path):
    w = s.make_world(tmp_path, commit=False)
    _plant(w)
    w.commit()
    return w


def _calls_of(world, question):
    return [s.options(call["argv"]) for call in world.calls() if s.options(call["argv"])["query"] == [question]]


def test_evidence_in_a_later_batch_counts_for_full_evidence_not_for_the_bundle(world):
    document = world.measure(s.SET, "--json").json()
    for qid, (_, (hit, bundle, full, rank, calls)) in QUESTIONS.items():
        got = s.question(document, qid)
        want = {"hit_at_5": hit, "in_bundle": bundle, "full_evidence": full, "first_gold_rank": rank, "calls": calls}
        have = {key: got.get(key, "<missing>") for key in want}
        assert have == want, f"{qid}: the measure gives {have}, not {want}"


def test_each_next_call_continues_the_last_with_the_same_options(world):
    world.measure(s.SET, "--batch-size", 3, "--bundle-budget", 500, "--json").json()
    for qid, (question, (*_, calls)) in QUESTIONS.items():
        made = _calls_of(world, question)
        assert len(made) == calls, f"{qid}: {len(made)} retrieve calls, not {calls}: {made}"
        for number, call in enumerate(made):
            assert call.get("--batch-size") == ["3"], f"{qid} call {number + 1}: --batch-size {call.get('--batch-size')}"
            assert call.get("--bundle-budget") == ["500"], (
                f"{qid} call {number + 1}: --bundle-budget {call.get('--bundle-budget')}")
            assert call.get("--json"), f"{qid} call {number + 1}: no --json"
            want = None if number == 0 else [s.token(question, number)]
            assert call.get("--continue") == want, (
                f"{qid} call {number + 1}: --continue {call.get('--continue')}, not {want}")


def test_the_defaults_are_10_6000_and_24000_and_are_named(world):
    document = world.measure(s.SET, "--json").json()
    assert document.get("budget") == {"batch_size": 10, "bundle_budget": 6000, "stack_budget": 24000}, (
        f"budget: {document.get('budget')!r}")
    calls = [s.options(call["argv"]) for call in world.calls()]
    assert calls, "no retrieve call was made"
    for call in calls:
        assert call.get("--batch-size") == ["10"] and call.get("--bundle-budget") == ["6000"], (
            f"a call without the default batch size and bundle budget: {call}")


def test_never_one_giant_call(world):
    """Whatever the stack budget, no call asks for a larger batch or bundle than stated."""
    document = world.measure(s.SET, "--batch-size", 2, "--bundle-budget", 300, "--stack-budget", 100000,
                             "--json").json()
    assert document.get("budget") == {"batch_size": 2, "bundle_budget": 300, "stack_budget": 100000}, (
        f"budget: {document.get('budget')!r}")
    for call in (s.options(c["argv"]) for c in world.calls()):
        assert call.get("--batch-size") == ["2"] and call.get("--bundle-budget") == ["300"], (
            f"a call asked for more than stated: {call}")


# --------------------------------------------------------------------------
# The stack budget
# --------------------------------------------------------------------------

BUDGET_QUESTION = "Within the stack budget?"


@pytest.fixture
def budget_world(tmp_path):
    """One question; every item 40 characters (10 tokens). Batches: [a, b], [c, gold], [d]."""
    w = s.make_world(tmp_path, commit=False)
    first, last = w.span(s.DECISIONS, GOLD_HEADING)

    def sized(rel, a=1, b=1):
        return w.item(rel, a, b, text="x" * 39 + "\n")

    gold = w.item(s.DECISIONS, first, last, text="y" * 39 + "\n")
    w.question("b01", {"question": BUDGET_QUESTION, "gold_answer": "from its last checkpoint", "sources": SOURCES},
               [[sized("docs/noise/n01.md"), sized("docs/noise/n02.md")], [sized("docs/noise/n03.md"), gold],
                [sized("docs/noise/n04.md")]])
    w.commit()
    return w


def test_the_stack_budget_admits_an_item_that_fits_exactly(budget_world):
    document = budget_world.measure(s.SET, "--stack-budget", 40, "--json").json()
    got = s.question(document, "b01")
    assert got.get("full_evidence") is True and got.get("first_gold_rank") == 4, (
        f"a 40-token stack holds a, b, c and the gold item: {got}")


def test_the_stack_budget_stops_before_the_first_item_that_would_pass_it(budget_world):
    document = budget_world.measure(s.SET, "--stack-budget", 39, "--json").json()
    got = s.question(document, "b01")
    assert got.get("full_evidence") is False and got.get("first_gold_rank") is None, (
        f"a 39-token stack holds a, b and c only: {got}")
    assert got.get("hit_at_5") is False, f"the gold item is past the stack: {got}"


def test_a_stack_budget_reached_in_the_first_call_asks_for_no_more_than_needed(budget_world):
    document = budget_world.measure(s.SET, "--stack-budget", 15, "--json").json()
    got = s.question(document, "b01")
    assert got.get("full_evidence") is False, f"a 15-token stack holds a only: {got}"
    calls = _calls_of(budget_world, BUDGET_QUESTION)
    assert 1 <= len(calls) <= 3, f"{len(calls)} calls"

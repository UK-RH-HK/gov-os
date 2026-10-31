"""W2-87 part 2: the authority order, read from the path map's ``retrieval_authority`` block (DEC-952 item 1).

The planted blocks are in ``w2_87_support.CONFIGS``: ``main`` (governing, middle, reports; a lift of 0.004 per step
on the fused score and 1.0 on the reranker's), ``flipped`` (reports first, decisions last), ``small`` (a fused lift
of 0.00054 per step), ``absent`` (no block) and four that must refuse with ``CONFIG_INVALID``.
"""

from __future__ import annotations

import json

import pytest

import w2_87_support as support
from w2_87_support import (ADR, CAPABILITY, CUT_PHRASE, CUT_REPORTS, CUT_SPEC, FAVOURED, NEW, NO_RERANKER, OLD,
                           PHRASE, REPORT, SPEC, STUB, TEST)

GOVERNING = [NEW, ADR, SPEC, CAPABILITY]   # an accepted register entry, an ADR, a specification, a capability
LOWER = [REPORT, TEST]                     # an assessment report and a test
EVERYTHING = 50                            # a batch size that gathers every chunk of the corpus in the first call


def _bundle(api, root, how, query=PHRASE, **kwargs):
    """The bundle asked through the Python interface without a reranker, with a stub that scores every text alike,
    or through ``gov retrieve --json`` (whose empty HOME holds no reranker)."""
    if how == "cli":
        done = api.command(root, "--batch-size", str(kwargs.get("batch_size", EVERYTHING)), query)
        envelope = json.loads(done.stdout)
        assert done.returncode == 0 and envelope["ok"], f"gov retrieve failed:\n{done.stdout}\n{done.stderr[-2000:]}"
        return envelope["result"]
    kwargs.setdefault("batch_size", EVERYTHING)
    if how == "stub-alike":
        return api.retrieve(root, query, favour=(), reranker=STUB, **kwargs)
    return api.retrieve(root, query, reranker=NO_RERANKER, **kwargs)


def _above(names, upper, lower):
    """Every name of ``upper`` ranks better than every name of ``lower``; the offending pairs otherwise."""
    return [(high, low) for high in upper for low in lower
            if support.rank_of(names, high) > support.rank_of(names, low)]


# ---- 1. For the same match, a governing source outranks a test or an assessment report (KPI success 1)

@pytest.mark.parametrize("how", ["no-reranker", "stub-alike", "cli"])
def test_1_every_governing_chunk_outranks_every_test_and_report(api, planted, how):
    root = planted("main")
    plain = [path for _, path in api.plain_order(root, PHRASE)]
    assert plain.index(REPORT) < plain.index(SPEC), f"the plant no longer puts a report first in the plain order: {plain}"
    names = support.labels(_bundle(api, root, how))
    wrong = _above(names, GOVERNING, LOWER)
    assert not wrong, f"a test or a report outranks a governing source of the same match: {wrong}; order: {names}"


# ---- 2. The order counts where it decides what is gathered, and the lift is bounded (KPI success 2)

def test_2a_a_governing_chunk_just_past_the_first_call_enters_it(api, planted):
    """``cinder gate tally``: six reports, then the specification, in the plain fused order. With a batch size of 2
    the first call gathers four; the specification enters them."""
    root = planted("main")
    plain = [path for _, path in api.plain_order(root, CUT_PHRASE)]
    assert plain == [*CUT_REPORTS, CUT_SPEC], f"the plant's plain order changed: {plain}"
    bundle = _bundle(api, root, "no-reranker", CUT_PHRASE, batch_size=2)
    names = support.labels(bundle)
    assert len(names) == 4, f"the first call should gather 2 x 2 chunks: {names}"
    assert CUT_SPEC in names, f"the governing chunk was left past the first call's cut: evidence {names}; " \
                              f"not gathered: {[gap['path'] for gap in bundle['gaps']]}"
    assert names[0] == CUT_SPEC, f"a lift of 0.004 per step puts the specification first: {names}"


def test_2b_a_lower_chunk_better_by_more_than_the_lift_keeps_its_place(api, planted):
    """A lift of 0.00054 per step: 0.00108 between the specification (plain rank 7, 1/67) and a report. The reports
    at plain ranks 1 and 2 are better by 0.00147 and 0.00120, more than the lift, and keep their places ahead; the
    report at rank 3 is better by 0.00095, less than the lift, and is overtaken, so the specification enters the
    first call's four and the reports of ranks 4 to 6 are left out."""
    root = planted("small")
    bundle = _bundle(api, root, "no-reranker", CUT_PHRASE, batch_size=2)
    names = support.labels(bundle)
    assert names == [CUT_REPORTS[0], CUT_REPORTS[1], CUT_SPEC, CUT_REPORTS[2]], \
        f"expected two reports, the specification, then the third report: {names}"
    left_out = [gap["path"] for gap in bundle["gaps"] if gap.get("reason") == support.NOT_GATHERED]
    assert left_out == CUT_REPORTS[3:], f"the not-gathered gaps should be the last three reports: {left_out}"


def test_2c_the_rerank_does_not_undo_the_order_and_its_lift_is_bounded(api, planted):
    """A stub reranker scores the report 3 (three favoured words), the test 1 and every other chunk 0; the rerank
    lift is 1.0 per step (2.0 between a governing chunk and a report). The report, better by 3, keeps its place
    above every governing chunk; the test, better by 1 only, falls below every one of them."""
    root = planted("main")
    names = support.labels(api.retrieve(root, PHRASE, favour=(FAVOURED,), reranker=STUB, batch_size=EVERYTHING))
    assert not _above(names, [REPORT], GOVERNING), f"the report, better by more than the lift, lost its place: {names}"
    assert not _above(names, GOVERNING, [TEST]), f"the test, better by less than the lift, outranks a governing " \
                                                 f"chunk after the rerank: {names}"


# ---- 3. The order is configuration, not code (KPI success 3)

def test_3a_a_path_map_that_puts_tests_above_decisions_flips_the_order(api, planted):
    root = planted("flipped")
    names = support.labels(_bundle(api, root, "no-reranker"))
    wrong = _above(names, LOWER, GOVERNING)
    assert not wrong, f"the planted order puts tests and reports first; a governing chunk still outranks them: " \
                      f"{wrong}; order: {names}"


def test_3b_without_the_block_the_order_is_the_plain_fused_one(api, planted):
    root = planted("absent")
    bundle = _bundle(api, root, "no-reranker")
    dropped = {entry["path"] for entry in bundle["merge"]["dropped"]}
    plain = [chunk for chunk, path in api.plain_order(root, PHRASE) if path not in dropped]
    assert [item["chunk_id"] for item in bundle["evidence"]] == plain, \
        f"without the block the bundle is not the plain fused order: {support.labels(bundle)}"


# ---- 4. Fail closed (KPI success 3, failure 3)

@pytest.mark.parametrize("config", ["not-a-mapping", "unknown-default", "unknown-key", "status-not-a-word"])
def test_4_an_unreadable_block_refuses_with_config_invalid(api, planted, config):
    root = planted(config)
    outcome = api.outcome(root, PHRASE, reranker=NO_RERANKER)
    assert outcome["error"] is not None, \
        f"the block {support.CONFIGS[config]!r} was read as an order; the call returned a bundle of " \
        f"{len(outcome['value']['evidence'])} items"
    assert outcome["error"]["code"] == support.CONFIG_INVALID, f"the refusal is not CONFIG_INVALID: {outcome['error']}"


def test_4_the_command_carries_config_invalid_in_its_json_error(api, planted):
    done = api.command(planted("unknown-default"), PHRASE)
    envelope = json.loads(done.stdout)
    assert envelope.get("ok") is False and done.returncode != 0, \
        f"gov retrieve accepted a block whose default names no tier:\n{done.stdout[:2000]}"
    assert envelope.get("error", {}).get("code") == support.CONFIG_INVALID, f"the error is not CONFIG_INVALID: {envelope}"


# ---- 5. A superseded decision never outranks its successor (KPI success 4, failure 2)

@pytest.mark.parametrize("how", ["no-reranker", "stub-alike"])
def test_5_the_superseded_entry_ranks_below_its_successor_and_gets_no_lift(api, planted, how):
    root = planted("main")
    names = support.labels(_bundle(api, root, how))
    assert support.rank_of(names, NEW) < support.rank_of(names, OLD), \
        f"{OLD}, superseded by {NEW}, outranks it: {names}"
    assert not _above(names, GOVERNING, [OLD]), f"{OLD} is superseded and got a lift above a governing chunk: {names}"


# ---- 6. Nothing else changes (KPI success 5, failure 4 and 5)

def test_6a_two_runs_on_one_store_give_one_bundle(api, planted):
    root = planted("main")
    for query, kwargs in ((PHRASE, {"batch_size": EVERYTHING}), (CUT_PHRASE, {"batch_size": 2})):
        first, second = (api.retrieve(root, query, favour=(FAVOURED,), reranker=STUB, **kwargs) for _ in range(2))
        assert first == second, f"two runs of {query!r} gave two bundles"


@pytest.mark.parametrize("query", [PHRASE, CUT_PHRASE])
def test_6b_the_block_changes_the_order_only(api, planted, query):
    """When everything is gathered, the same chunks are kept and the same left out, with and without the block."""
    with_block = api.retrieve(planted("main"), query, batch_size=EVERYTHING)
    without = api.retrieve(planted("absent"), query, batch_size=EVERYTHING)
    assert support.gathered_set(with_block) == support.gathered_set(without), \
        f"the block changed what is kept or left out:\nwith: {support.labels(with_block)} " \
        f"{with_block['merge']['dropped']}\nwithout: {support.labels(without)} {without['merge']['dropped']}"
    for key in ("stopping_reason", "continuation"):
        assert with_block[key] == without[key], f"the block changed `{key}`: {with_block[key]!r} != {without[key]!r}"

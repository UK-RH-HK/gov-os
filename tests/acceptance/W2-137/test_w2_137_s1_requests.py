"""W2-137 S1: a search's pool of 40 goes in one request when it fits the padded-character bound; the bound stays.

KPI S1 (DAEO-5emz): the cap on texts per request (``rerank.MAX_REQUEST_TEXTS``, 16 on integrate) is raised so that a
search at the pool's ``rerank_depth`` (40) sends its candidates in one request when they fit the padded-character
bound; ``MAX_REQUEST_CHARS`` stays and still splits a request whose texts are long. The expected shapes come from the
ticket's rule (a request's padded size is its count times its longest pair), computed in ``w2_137_support``.
"""
from __future__ import annotations

import random

import pytest

import w2_137_support as support
from gov.retrieval import rerank

Q = support.QUERY


def test_s1_premise_the_pool_reranks_forty_and_the_padded_bound_stays():
    assert support.depth() == 40, "premise: the pool's rerank_depth is the ticket's 40 (retrieval.yaml)"
    assert rerank.MAX_REQUEST_CHARS == support.TICKET_CHARS, "S1: the padded-character bound stays"


def test_s1_the_count_cap_carries_the_pool_s_depth():
    assert rerank.MAX_REQUEST_TEXTS >= support.depth(), (
        f"the count cap {rerank.MAX_REQUEST_TEXTS} splits a pool of {support.depth()} by count alone")


@pytest.mark.parametrize("length", [1, 100, "at-the-padded-bound"], ids=["one-char", "100-chars", "at-the-padded-bound"])
def test_s1_the_pool_s_short_texts_go_in_one_request(length):
    count = support.depth()
    if length == "at-the-padded-bound":  # 40 texts whose padded size is the bound's largest multiple of 40
        length = support.TICKET_CHARS // count - len(Q)
    texts = support.texts_of(count, length)
    assert support.padded(Q, texts) <= support.TICKET_CHARS, "premise: the pool fits the padded bound"
    out = rerank.requests(Q, texts)
    support.check_requests(Q, texts, out, rerank.MAX_REQUEST_TEXTS, rerank.MAX_REQUEST_CHARS)
    assert len(out) == 1, f"{count} texts of {length} characters fit one request; sent in {[len(s) for _, s in out]}"


def test_s1_rerank_asks_the_reranker_once_for_the_pool():
    calls: list = []
    texts = support.texts_of(support.depth(), 120)
    candidates = [{"n": number, "text": text} for number, text in enumerate(texts)]
    ranked = rerank.rerank(Q, candidates, reranker=support.recording(calls))
    assert [len(call) for call in calls] == [len(texts)], f"one request of {len(texts)}; asked {[len(c) for c in calls]}"
    expected = sorted(range(len(texts)), key=lambda n: -support.base_score(Q, texts[n]))
    assert [entry["n"] for entry in ranked] == expected and all("rerank_score" in entry for entry in ranked)


@pytest.mark.parametrize("length", [1000, 2000, 5000, 12000],
                         ids=["1000-chars-22-a-request", "2000-chars-11-a-request", "5000-chars-4-a-request",
                              "12000-chars-1-a-request"])
def test_s1_long_texts_split_by_the_padded_bound_never_by_count_alone(length):
    count = support.depth()
    texts = support.texts_of(count, length)
    per = support.per_request(Q, length)
    out = rerank.requests(Q, texts)
    support.check_requests(Q, texts, out, rerank.MAX_REQUEST_TEXTS, rerank.MAX_REQUEST_CHARS)
    sizes = [len(sent) for _, sent in out]
    assert len(out) == support.expected_requests(count, Q, length), (
        f"{count} texts of {length}: {per} fit a request by characters, so "
        f"{support.expected_requests(count, Q, length)} requests; sent as {sizes}")
    assert all(size == per for size in sizes[:-1]), f"each full request holds the {per} the bound allows: {sizes}"


def test_s1_a_long_text_goes_alone_and_the_short_ones_together():
    count = support.depth()
    texts = support.texts_of(count - 1, 200, "s")
    texts.insert(17, "L" * 23_000)  # the CTO's case of 2026-11-04: one 23,000-character chunk among short ones
    out = rerank.requests(Q, texts)
    support.check_requests(Q, texts, out, rerank.MAX_REQUEST_TEXTS, rerank.MAX_REQUEST_CHARS)
    groups = sorted((sorted(indices) for indices, _ in out), key=len)
    assert groups == [[17], [n for n in range(count) if n != 17]], (
        f"the long text alone, the {count - 1} short ones in one request: {[len(g) for g in groups]}")


def test_s1_one_text_over_the_bound_alone_is_read_up_to_it():
    text = "O" * 30_000
    out = rerank.requests(Q, [text])
    support.check_requests(Q, [text], out, rerank.MAX_REQUEST_TEXTS, rerank.MAX_REQUEST_CHARS)
    [(indices, [sent])] = out
    assert indices == [0] and sent == text[:support.TICKET_CHARS - len(Q)]
    assert support.padded(Q, [sent]) == support.TICKET_CHARS


def test_s1_one_text_over_the_bound_among_the_pool_is_read_up_to_it():
    count = support.depth()
    texts = support.texts_of(count - 1, 150, "s") + ["O" * 30_000]
    out = rerank.requests(Q, texts)
    support.check_requests(Q, texts, out, rerank.MAX_REQUEST_TEXTS, rerank.MAX_REQUEST_CHARS)
    [long] = [sent for indices, sent in out if count - 1 in indices]
    assert long == [texts[-1][:support.TICKET_CHARS - len(Q)]], "the over-long text alone, read up to the bound"
    assert len(out) == 2, f"the over-long text alone and the {count - 1} short ones together: {[len(s) for _, s in out]}"


@pytest.mark.parametrize("seed", [1, 2, 3, 4, 5])
def test_s1_guard_every_request_keeps_both_bounds_on_mixed_pools(seed):
    pick = random.Random(seed)
    for count in (1, 16, 17, support.depth(), 90, 200):
        texts = [chr(97 + n % 26) * pick.choice([1, 50, 400, 900, 3000, 8000, 23_500, 26_000]) for n in range(count)]
        out = rerank.requests(Q, texts)
        support.check_requests(Q, texts, out, rerank.MAX_REQUEST_TEXTS, rerank.MAX_REQUEST_CHARS)

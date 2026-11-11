"""W2-137 S3: the cap does not change the scores: the same order, every score within 1e-3.

KPI S3 (DAEO-5emz): for the same question and candidates, the order under the new cap equals the order under 16 per
request, and the largest score difference is within 1e-3. The stand-in encoder (``w2_137_support.Encoder``) is
deterministic and, like a padded model, moves a score by under 1e-5 with the batch it is padded into, so the two
batchings give scores that differ, within the ticket's 1e-3. Every request goes through the service's own request
handling (``rerank_service.answer``), JSON both ways.
"""
from __future__ import annotations

import pytest

import w2_137_support as support
from gov.retrieval import rerank, rerank_service

Q = support.QUERY


def _pool(kind: str) -> list[str]:
    count = support.depth()
    if kind == "short":
        return support.texts_of(count, 120)
    if kind == "at-the-padded-bound":
        return support.texts_of(count, support.TICKET_CHARS // count - len(Q))
    # mixed: a few long chunks among short ones, so the padded bound splits the pool under either cap
    texts = support.texts_of(count - 4, 300, "s")
    for at, length in ((3, 23_000), (11, 9_000), (25, 4_000), (30, 26_000)):
        texts.insert(at, support.texts_of(1, length, f"L{at}")[0])
    return texts


def _ranked(texts: list[str], monkeypatch, cap: int | None):
    """``rerank.rerank``'s order and scores, under the module's own cap (``cap`` None) or under ``cap``."""
    with monkeypatch.context() as patch:
        if cap is not None:
            patch.setattr(rerank, "MAX_REQUEST_TEXTS", cap)
        calls: list = []
        candidates = [{"n": number, "text": text} for number, text in enumerate(texts)]
        ranked = rerank.rerank(Q, candidates, reranker=support.via_service(support.Encoder(), calls))
    assert all("rerank_score" in entry for entry in ranked), "every candidate scored"
    return [entry["n"] for entry in ranked], {entry["n"]: entry["rerank_score"] for entry in ranked}, calls


def _premise_distinct(texts: list[str]) -> None:
    room = support.TICKET_CHARS - len(Q)
    values = sorted(support.base_score(Q, text[:room]) for text in texts)
    gap = min(b - a for a, b in zip(values, values[1:]))
    assert gap > 1e-3, f"premise: the stand-in's scores are apart by more than the tolerance ({gap})"


@pytest.mark.parametrize("kind", ["short", "at-the-padded-bound", "mixed"])
def test_s3_the_order_and_scores_under_the_cap_equal_those_under_16(kind, monkeypatch):
    texts = _pool(kind)
    _premise_distinct(texts)
    order, scores, calls = _ranked(texts, monkeypatch, None)
    order16, scores16, calls16 = _ranked(texts, monkeypatch, support.OLD_CAP)
    assert all(len(call) <= support.OLD_CAP for call in calls16), "premise: the reference is requests of 16 at most"
    assert order == order16, "the cap alone changed the order"
    worst = max(abs(scores[n] - scores16[n]) for n in scores)
    assert worst <= 1e-3, f"the cap alone moved a score by {worst}"


@pytest.mark.parametrize("kind", ["short", "at-the-padded-bound"])
def test_s3_the_service_scores_the_pool_in_one_request_as_in_requests_of_16(kind):
    """The service's own answer for the whole pool in one request against the same pool sent 16 at a time: the
    request the new cap sends, asked of the service directly."""
    import json

    texts = _pool(kind)
    _premise_distinct(texts)
    encoder = support.Encoder()

    def ask(batch):
        answer = rerank_service.answer(encoder, "cuda:0", (json.dumps([Q, batch]) + "\n").encode())
        assert "error" not in answer, answer
        return answer["scores"]

    whole = ask(texts)
    parts = [score for at in range(0, len(texts), support.OLD_CAP) for score in ask(texts[at:at + support.OLD_CAP])]
    sizes = [min(support.OLD_CAP, len(texts) - at) for at in range(0, len(texts), support.OLD_CAP)]
    assert encoder.batches == [len(texts)] + sizes, "premise: one request of the pool, then requests of 16"
    assert sorted(range(len(texts)), key=lambda n: -whole[n]) == sorted(range(len(texts)), key=lambda n: -parts[n])
    assert max(abs(a - b) for a, b in zip(whole, parts)) <= 1e-3

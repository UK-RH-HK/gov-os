"""W2-137 S2: the service accepts the larger requests and refuses one over its bound, named, never truncated.

KPI S2 (DAEO-5emz): the service's own bound (``rerank_service.MAX_TEXTS``) is at least the new cap, and a request
over its bound is refused with a named reason, never truncated silently. The bound assumed here is the ticket's
relation only: the service's bound is at least the client's cap (and so at least the pool's 40), whatever either
number is; no value of either is fixed by these tests. The service is driven in this process
(``rerank_service.answer``) with a stand-in encoder; the client's side (``rerank._ask``) with a stand-in connection.
"""
from __future__ import annotations

import io
import json

import pytest

import w2_137_support as support
from gov.retrieval import rerank, rerank_service

Q = support.QUERY


def _line(texts) -> bytes:
    return (json.dumps([Q, texts]) + "\n").encode()


def test_s2_the_service_bound_is_at_least_the_client_cap():
    assert rerank_service.MAX_TEXTS >= rerank.MAX_REQUEST_TEXTS, (
        f"the service refuses {rerank_service.MAX_TEXTS + 1}+ texts but the client sends up to {rerank.MAX_REQUEST_TEXTS}")
    assert rerank_service.MAX_TEXTS >= support.depth()


@pytest.mark.parametrize("size", ["the-client-cap", "the-pool-depth", "the-service-bound"])
def test_s2_the_service_answers_a_request_at_the_cap_whole(size):
    count = {"the-client-cap": rerank.MAX_REQUEST_TEXTS, "the-pool-depth": support.depth(),
             "the-service-bound": rerank_service.MAX_TEXTS}[size]
    texts = support.texts_of(count, 20)
    encoder = support.Encoder()
    answer = rerank_service.answer(encoder, "cuda:0", _line(texts))
    assert "error" not in answer, answer
    assert answer["device"] == "cuda:0" and len(answer["scores"]) == count
    assert encoder.batches == [count], "every text of the request scored, in the one request it came in"
    assert answer["scores"] == pytest.approx([support.base_score(Q, text) for text in texts], abs=1e-4)


def test_s2_a_request_over_the_service_bound_is_refused_with_a_named_reason():
    texts = support.texts_of(rerank_service.MAX_TEXTS + 1, 5)
    encoder = support.Encoder()
    answer = rerank_service.answer(encoder, "cuda:0", _line(texts))
    assert "scores" not in answer, "a request over the bound is never scored in part"
    assert encoder.batches == [], "nothing of an over-bound request reaches the model"
    assert str(rerank_service.MAX_TEXTS) in answer["error"] and "texts" in answer["error"], (
        f"the refusal names the bound: {answer['error']!r}")


def test_s2_every_request_a_search_makes_is_within_the_service_bound():
    for count, length in ((support.depth(), 30), (rerank_service.MAX_TEXTS + 1, 3), (3 * support.depth(), 100)):
        texts = support.texts_of(count, length)
        for indices, sent in rerank.requests(Q, texts):
            assert len(sent) <= rerank_service.MAX_TEXTS, f"a search's request of {len(sent)} texts would be refused"


class _Connection:
    def __init__(self, answer: dict):
        self.answer, self.sent = answer, []

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def settimeout(self, _):
        pass

    def sendall(self, data: bytes):
        self.sent.append(json.loads(data))

    def makefile(self, _):
        return io.BytesIO((json.dumps(self.answer) + "\n").encode())


def test_s2_the_client_names_the_service_s_refusal(monkeypatch):
    texts = support.texts_of(rerank.MAX_REQUEST_TEXTS, 10)
    refusal = rerank_service.answer(support.Encoder(), "cuda:0", _line(["x"] * (rerank_service.MAX_TEXTS + 1)))
    connection = _Connection(refusal)
    monkeypatch.setattr(rerank, "_connect", lambda _interpreter: connection)
    with pytest.raises(RuntimeError, match="refused the request") as raised:
        rerank._ask("python", Q, texts)
    assert refusal["error"] in str(raised.value), "the service's own reason is carried in the client's error"
    assert connection.sent == [[Q, texts]], "the client sent the request whole"


def test_s2_an_answer_short_of_scores_is_an_error_never_a_truncation(monkeypatch):
    texts = support.texts_of(rerank.MAX_REQUEST_TEXTS, 10)
    short = {"scores": [1.0] * (len(texts) - 1), "device": "cuda:0"}
    monkeypatch.setattr(rerank, "_connect", lambda _interpreter: _Connection(short))
    with pytest.raises(ValueError, match="does not match"):
        rerank._ask("python", Q, texts)


def test_s2_a_reranker_that_drops_texts_leaves_the_pool_unscored_and_named():
    texts = support.texts_of(support.depth(), 10)
    candidates = [{"n": number, "text": text} for number, text in enumerate(texts)]

    def dropping(query, batch):
        return [support.base_score(query, text) for text in batch[:-1]]

    ranked = rerank.rerank(Q, candidates, reranker=lambda: dropping)
    assert ranked == candidates, "the order given is kept and no candidate carries a score"
    outcome = rerank.last_outcome()
    assert outcome["by"] == "unavailable" and "scores for" in outcome["reason"]

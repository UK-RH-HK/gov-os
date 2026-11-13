"""Builder tests for W2-137: the shared reranker's request cap raised (DEC-1090 (2)).

Regression evidence only (DEC-136). Stand-ins only: a stub encoder and a stub torch in this process; no model, no
GPU, no socket, never the reranker environment.
"""
from __future__ import annotations

import hashlib
import io
import json
import re
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov.retrieval import rerank, rerank_service  # noqa: E402

QUERY = "who fires the bowls"
POOL_DEPTH, ROUTE_DEPTH = 40, 60  # the pool's rerank_depth and the routes' depth (pool.py)
OLD_CAP = 16  # DEC-1067 (f), before DEC-1090 (2)


def _padded(query, texts):
    """A request's size as the reranker pads it: its count times its longest pair."""
    return len(texts) * max(len(query) + len(text) for text in texts)


def _stub_score(query: str, text: str) -> float:
    """A stand-in cross-encoder's score: fixed for a pair, whatever else is in the request."""
    return int(hashlib.sha256(f"{query}\0{text}".encode()).hexdigest()[:8], 16) / 16 ** 8


class _Encoder:
    """A stand-in encoder for the service: records each call's pair count."""

    def __init__(self, events: list | None = None):
        self.calls: list[int] = []
        self.events = events if events is not None else []

    def predict(self, pairs):
        self.calls.append(len(pairs))
        self.events.append("predict")
        return [_stub_score(query, text) for query, text in pairs]


def _short(count: int, length: int = 100) -> list[str]:
    return [f"{n:03}" + "s" * (length - 3) for n in range(count)]


# --- S1: the cap holds a search's candidates in one request when they fit the padded bound ----------------------

def test_s1_the_cap_holds_the_pool_s_40_and_the_routes_60():
    assert rerank.MAX_REQUEST_TEXTS >= ROUTE_DEPTH > POOL_DEPTH
    assert rerank.MAX_REQUEST_TEXTS == 64
    assert rerank.MAX_REQUEST_CHARS == 24_000  # the padded bound stays


@pytest.mark.parametrize("count", [POOL_DEPTH, ROUTE_DEPTH])
def test_s1_short_texts_at_the_pool_s_depth_go_in_one_request(count):
    [(indices, texts)] = rerank.requests(QUERY, _short(count))
    assert indices == list(range(count)) and texts == _short(count)
    assert _padded(QUERY, texts) <= rerank.MAX_REQUEST_CHARS


def test_s1_40_long_texts_are_split_by_characters_never_by_count_alone():
    texts = ["l" * 2_000 for _ in range(POOL_DEPTH)]
    groups = rerank.requests(QUERY, texts)
    per_request = rerank.MAX_REQUEST_CHARS // (len(QUERY) + 2_000)  # 11: the padded bound binds, not the count
    assert per_request < POOL_DEPTH < rerank.MAX_REQUEST_TEXTS
    assert [len(indices) for indices, _ in groups] == [per_request] * (POOL_DEPTH // per_request) + \
        [POOL_DEPTH % per_request]
    assert all(_padded(QUERY, batch) <= rerank.MAX_REQUEST_CHARS for _, batch in groups)
    assert sorted(i for indices, _ in groups for i in indices) == list(range(POOL_DEPTH))  # each once


def test_s1_one_long_text_with_short_ones_goes_alone_and_the_short_ones_together():
    texts = ["l" * 23_000] + _short(POOL_DEPTH - 1)
    groups = rerank.requests(QUERY, texts)
    assert [indices for indices, _ in groups] == [[0], list(range(1, POOL_DEPTH))]
    assert all(_padded(QUERY, batch) <= rerank.MAX_REQUEST_CHARS for _, batch in groups)


def test_s1_one_text_over_the_bound_is_read_up_to_it():
    [(indices, texts)] = rerank.requests(QUERY, ["y" * 40_000])
    assert indices == [0] and len(QUERY) + len(texts[0]) == rerank.MAX_REQUEST_CHARS


def test_s1_a_pool_over_the_cap_still_goes_in_requests_of_at_most_the_cap():
    groups = rerank.requests(QUERY, _short(100, length=20))
    assert [len(indices) for indices, _ in groups] == [rerank.MAX_REQUEST_TEXTS, 100 - rerank.MAX_REQUEST_TEXTS]


def test_s1_a_rerank_of_40_short_candidates_asks_the_shared_service_once(tmp_path, monkeypatch):
    interpreter = tmp_path / rerank.PYTHON_REL
    interpreter.parent.mkdir(parents=True)
    interpreter.write_text("")
    monkeypatch.setenv("HOME", str(tmp_path))
    asked = []
    monkeypatch.setattr(rerank, "_ask", lambda interpreter, query, texts: asked.append(len(texts))
                        or ([1.0] * len(texts), "cuda:0"))
    ranked = rerank.rerank(QUERY, [{"chunk_id": str(n), "text": text} for n, text in enumerate(_short(POOL_DEPTH))])
    assert asked == [POOL_DEPTH] and rerank.last_outcome()["by"] == "service"
    assert all("rerank_score" in candidate for candidate in ranked)


# --- S2: the service accepts the larger requests and refuses one over its bound, named ------------------------

def test_s2_the_service_s_bound_is_at_least_the_client_s_cap():
    assert rerank_service.MAX_TEXTS >= rerank.MAX_REQUEST_TEXTS


@pytest.mark.parametrize("count", [rerank.MAX_REQUEST_TEXTS, rerank_service.MAX_TEXTS])
def test_s2_the_service_scores_a_request_at_the_cap_and_at_its_bound(count):
    encoder = _Encoder()
    texts = _short(count, length=10)
    answer = rerank_service.answer(encoder, "cuda:0", json.dumps([QUERY, texts]).encode())
    assert "error" not in answer and len(answer["scores"]) == count
    assert encoder.calls == [count]


def test_s2_a_request_over_the_service_s_bound_is_refused_with_its_count_named_never_truncated():
    encoder = _Encoder()
    over = rerank_service.MAX_TEXTS + 1
    answer = rerank_service.answer(encoder, "cuda:0", json.dumps([QUERY, ["x"] * over]).encode())
    assert "scores" not in answer and encoder.calls == []  # nothing scored: not a truncated answer
    assert answer["device"] == "cuda:0"
    assert answer["error"].startswith("ValueError: ")
    assert f"at most {rerank_service.MAX_TEXTS} texts" in answer["error"] and f"has {over}" in answer["error"]


def test_s2_a_malformed_request_keeps_its_own_reason():
    answer = rerank_service.answer(_Encoder(), "cuda:0", json.dumps([1, ["x"]]).encode())
    assert "error" in answer and "has " not in answer["error"]


def test_s2_the_client_names_the_service_s_refusal(monkeypatch):
    class Connection:
        def __enter__(self):
            return self

        def __exit__(self, *_):
            pass

        def settimeout(self, _):
            pass

        def sendall(self, data):
            self.sent = data

        def makefile(self, _):
            query, texts = json.loads(self.sent)
            line = rerank_service.answer(_Encoder(), "cuda:0", json.dumps([query, texts]).encode())
            return io.BytesIO((json.dumps(line) + "\n").encode())

    monkeypatch.setattr(rerank, "_connect", lambda interpreter: Connection())
    with pytest.raises(RuntimeError, match=r"refused the request: ValueError: .*at most 512 texts: this one has 513"):
        rerank._ask("unused", QUERY, ["x"] * (rerank_service.MAX_TEXTS + 1))


# --- S3: the scores and the order do not depend on how the texts are split --------------------------------------

def _ranked(texts, cap, monkeypatch):
    monkeypatch.setattr(rerank, "MAX_REQUEST_TEXTS", cap)
    sizes = []

    def loader():
        def score(query, batch):
            sizes.append(len(batch))
            return [_stub_score(query, text) for text in batch]
        return score
    ranked = rerank.rerank(QUERY, [{"chunk_id": str(n), "text": text} for n, text in enumerate(texts)], loader)
    return [(c["chunk_id"], c["rerank_score"]) for c in ranked], sizes


@pytest.mark.parametrize("texts", [_short(POOL_DEPTH), _short(ROUTE_DEPTH, length=40), _short(100, length=20),
                                   ["l" * 2_000] * 10 + _short(30), ["l" * 23_000] + _short(39)],
                         ids=["40-short", "60-short", "100-short", "10-long-30-short", "1-huge-39-short"])
def test_s3_the_order_and_scores_under_the_new_cap_equal_those_under_16(texts, monkeypatch):
    old, old_sizes = _ranked(texts, OLD_CAP, monkeypatch)
    new, new_sizes = _ranked(texts, 64, monkeypatch)
    assert [chunk for chunk, _ in new] == [chunk for chunk, _ in old]
    assert max(abs(a - b) for (_, a), (_, b) in zip(new, old)) <= 1e-3
    assert len(new_sizes) <= len(old_sizes) and sum(new_sizes) == sum(old_sizes) == len(texts)


def test_s3_the_service_scores_a_text_the_same_in_one_request_or_in_pieces_of_16():
    texts = _short(POOL_DEPTH)
    whole = rerank_service.answer(_Encoder(), "cuda:0", json.dumps([QUERY, texts]).encode())["scores"]
    pieces = []
    for start in range(0, len(texts), OLD_CAP):
        line = json.dumps([QUERY, texts[start:start + OLD_CAP]]).encode()
        pieces += rerank_service.answer(_Encoder(), "cuda:0", line)["scores"]
    assert whole == pieces


# --- S4: the memory release and its MEMORY line, whatever the request size --------------------------------------

MEMORY_LINE = "allocated 1200 MiB, reserved 1300 MiB"


class _Torch:
    def __init__(self, events: list):
        self.cuda, self.events = self, events

    def empty_cache(self):
        self.events.append("release")

    def memory_allocated(self):
        return 1200 * 2 ** 20

    def memory_reserved(self):
        return 1300 * 2 ** 20


class _Connection:
    def __init__(self, events: list, line: bytes):
        self.events, self.line = events, line

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.events.append("closed")

    def settimeout(self, _):
        pass

    def makefile(self, _):
        return io.BytesIO(self.line)

    def sendall(self, data: bytes):
        self.events.append(("sent", json.loads(data)))


class _Listener:
    def __init__(self, connection):
        self.connection = connection

    def accept(self):
        return self.connection, None


@pytest.mark.parametrize("count", [1, OLD_CAP, POOL_DEPTH, rerank.MAX_REQUEST_TEXTS, rerank_service.MAX_TEXTS,
                                   rerank_service.MAX_TEXTS + 1])
def test_s4_every_request_is_released_once_after_its_answer_with_its_memory_line(tmp_path, monkeypatch, count):
    events: list = []
    monkeypatch.setitem(sys.modules, "torch", _Torch(events))
    log = tmp_path / "rerank.log"
    line = json.dumps([QUERY, _short(count, length=10)]).encode() + b"\n"
    rerank_service.serve(_Listener(_Connection(events, line)), _Encoder(events), "cuda:0", str(log))
    assert events.count("release") == 1 and events[-1] == "release"
    [sent] = [event for event in events if isinstance(event, tuple)]
    assert events.index(sent) < events.index("release")
    if count <= rerank_service.MAX_TEXTS:
        assert len(sent[1]["scores"]) == count and events.index("predict") < events.index(sent)
    else:
        assert "error" in sent[1] and "predict" not in events
    [entry] = log.read_text().splitlines()
    assert re.fullmatch(r"\S+\tMEMORY\t" + MEMORY_LINE, entry)

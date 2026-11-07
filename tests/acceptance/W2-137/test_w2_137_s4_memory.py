"""W2-137 S4: the memory release stays at the new cap: after every request, the cache emptied and MEMORY logged.

KPI S4 (DAEO-5emz): after every request the service empties its GPU cache and logs MEMORY with allocated and reserved
MiB, whatever the request size (W2-112's release, DEC-1068). Driven through ``rerank_service.serve`` with W2-112's
in-process seam: a stand-in listener and connection, a stand-in encoder, and a stand-in ``torch`` in ``sys.modules``
whose allocator calls are events. The existing W2-112 tests are the other half of S4 and are not repeated here.
"""
from __future__ import annotations

import json
import re
import sys

import pytest

import w2_137_support as support
from gov.retrieval import rerank, rerank_service

Q = support.QUERY


def _texts(size: str) -> list[str]:
    if size == "the-client-cap":
        return support.texts_of(rerank.MAX_REQUEST_TEXTS, 40)
    if size == "the-pool-depth":
        return support.texts_of(support.depth(), 40)
    if size == "the-cap-at-the-padded-bound":  # the largest request the client sends: its cap of texts, padded full
        count = rerank.MAX_REQUEST_TEXTS
        return support.texts_of(count, max(1, rerank.MAX_REQUEST_CHARS // count - len(Q)))
    return support.texts_of(rerank_service.MAX_TEXTS + 1, 5)  # over the service's bound: refused, still released


@pytest.mark.parametrize("size", ["the-client-cap", "the-pool-depth", "the-cap-at-the-padded-bound",
                                  "over-the-service-bound"])
def test_s4_a_request_at_the_new_cap_still_releases_and_logs_memory(size, tmp_path, monkeypatch):
    texts = _texts(size)
    events: list = []
    monkeypatch.setitem(sys.modules, "torch", support.Torch(events))
    log = tmp_path / "rerank.log"
    line = (json.dumps([Q, texts]) + "\n").encode()
    rerank_service.serve(support.Listener(support.Connection(events, line)), support.Encoder(events), "cuda:0",
                         str(log))
    [sent] = [event[1] for event in events if isinstance(event, tuple)]
    if size == "over-the-service-bound":
        assert "error" in sent and events == [("sent", sent), "closed", "release"]
    else:
        assert "error" not in sent and len(sent["scores"]) == len(texts), "the whole request answered"
        assert events == ["predict", ("sent", sent), "closed", "release"], "one release, after the answer is sent"
    lines = log.read_text().splitlines()
    assert len(lines) == 1, lines
    assert re.fullmatch(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d[+-]\d{4}\tMEMORY\t" + support.MEMORY_DETAIL, lines[0]), lines[0]
    assert lines[0].endswith("allocated 1200 MiB, reserved 1300 MiB")


def test_s4_a_search_s_requests_each_release_once(tmp_path, monkeypatch):
    """A search's pool at the new cap, served request by request: one release and one MEMORY line per request."""
    events: list = []
    monkeypatch.setitem(sys.modules, "torch", support.Torch(events))
    log = tmp_path / "rerank.log"
    texts = support.texts_of(support.depth() - 1, 200, "s") + ["L" * 23_000]
    out = rerank.requests(Q, texts)
    for _, sent in out:
        line = (json.dumps([Q, sent]) + "\n").encode()
        rerank_service.serve(support.Listener(support.Connection(events, line)), support.Encoder(events), "cuda:0",
                             str(log))
    assert events.count("release") == len(out) and events.count("predict") == len(out)
    memory = [line for line in log.read_text().splitlines() if "\tMEMORY\t" in line]
    assert len(memory) == len(out) and all(re.search(support.MEMORY_DETAIL + "$", line) for line in memory)

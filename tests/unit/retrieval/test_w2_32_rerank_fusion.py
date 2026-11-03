"""W2-32 S4 (W2-M104): a reranker that dies after loading is reported, not raised; S5 (W2-M103): the fusion limit is
honoured. Regression evidence only (DEC-136): no store, no model; the routes, the records and the reranker are
stand-ins, and no reranker process is started.
"""
from __future__ import annotations

import functools
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov.retrieval import fusion, rerank  # noqa: E402

NAMES = [f"chunk-{number:02}" for number in range(45)]


def _dies(error):
    def score(query, texts):
        raise error
    return score


DEATHS = {"a broken pipe": _dies(BrokenPipeError(32, "Broken pipe")),
          "an empty answer": _dies(ValueError("Expecting value: line 1 column 1 (char 0)")),
          "an end of input": _dies(EOFError("the reranker closed its output")),
          "too few scores": lambda query, texts: [1.0] * (len(texts) - 1),
          "no numbers": lambda query, texts: ["high"] * len(texts)}


@pytest.fixture()
def routes(monkeypatch):
    """Two routes over 45 chunks (the lexical one names them all, the semantic one the last ten, in reverse)."""
    lexical = [{"chunk_id": n, "path": f"notes/{n}.md", "start_line": 1, "end_line": 2, "parent_id": "p"}
               for n in NAMES]
    semantic = list(reversed(lexical[-10:]))
    monkeypatch.setattr(fusion.lexical, "search", lambda root, query, refresh: {"available": True, "hits": lexical})
    monkeypatch.setattr(fusion.semantic, "search", lambda root, query, refresh: {"available": True, "hits": semantic})
    monkeypatch.setattr(fusion, "_records", lambda root, fused: [{**hit, "text": f"text of {hit['chunk_id']}"}
                                                                 for hit in fused])
    return fusion.rrf({"lexical": lexical, "semantic": semantic})


# --- S4 ------------------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("death", DEATHS, ids=list(DEATHS))
def test_a_reranker_that_dies_after_loading_keeps_the_order_and_says_why(death):
    given = [{"chunk_id": n, "text": n} for n in NAMES[:5]]
    ranked = rerank.rerank("q", given, lambda: DEATHS[death])
    assert ranked == given and not any("rerank_score" in c for c in ranked)
    outcome = rerank.last_outcome()
    assert outcome["by"] == "unavailable" and "after loading" in outcome["reason"]


def test_a_loader_that_raises_is_reported_too():
    given = [{"chunk_id": "a", "text": "a"}]

    def loader():
        raise OSError("no reranker environment")
    assert rerank.rerank("q", given, loader) == given
    assert rerank.last_outcome()["by"] == "unavailable" and "no reranker environment" in rerank.last_outcome()["reason"]


@pytest.mark.parametrize("death", DEATHS, ids=list(DEATHS))
def test_fusion_search_says_reranked_false_and_names_the_failure(routes, death):
    answer = fusion.search(Path("unused"), "q", limit=None, reranker=lambda: DEATHS[death])
    assert answer["reranked"] is False and answer["rerank"]["by"] == "unavailable"
    assert [hit["chunk_id"] for hit in answer["hits"]] == [hit["chunk_id"] for hit in routes[:fusion.RERANK_TOP]]
    assert not any("rerank_score" in hit for hit in answer["hits"])


def test_a_private_reranker_that_dies_is_reported_and_started_again_next_time(tmp_path, monkeypatch):
    """The default reranker: the shared service does not answer, the private one loads, then dies mid-search."""
    interpreter = tmp_path / rerank.PYTHON_REL
    interpreter.parent.mkdir(parents=True)
    interpreter.write_text("")
    monkeypatch.setenv("HOME", str(tmp_path))
    starts = []

    def no_service(interpreter, query, texts):
        raise ConnectionError("no service")

    @functools.lru_cache(maxsize=None)
    def started(interpreter):
        starts.append(interpreter)
        return DEATHS["a broken pipe"], "cpu", None

    monkeypatch.setattr(rerank, "_ask", no_service)
    monkeypatch.setattr(rerank, "_started", started)
    given = [{"chunk_id": "a", "text": "a"}, {"chunk_id": "b", "text": "b"}]
    assert rerank.rerank("q", given) == given
    assert rerank.last_outcome()["by"] == "unavailable" and "BrokenPipeError" in rerank.last_outcome()["reason"]
    rerank.rerank("q", given)
    assert len(starts) == 2  # the dead one was not kept: the next search started another


# --- S5 ------------------------------------------------------------------------------------------------------------

def _score(query, texts):
    return [float(text.splitlines()[0].split("chunk-")[1][:2]) for text in texts]


@pytest.mark.parametrize("limit", [0, 1, 5, 30, 31, 40, 45])
def test_a_limit_gives_exactly_that_many_distinct_hits(routes, limit):
    answer = fusion.search(Path("unused"), "q", limit=limit, reranker=lambda: _score)
    ids = [hit["chunk_id"] for hit in answer["hits"]]
    assert len(ids) == limit == len(set(ids))
    head = sorted((hit["chunk_id"] for hit in routes[:fusion.RERANK_TOP]), reverse=True)
    assert ids[:fusion.RERANK_TOP] == head[:limit]  # the reranked head first, best first
    assert ids[fusion.RERANK_TOP:] == [hit["chunk_id"] for hit in routes[fusion.RERANK_TOP:limit]]  # then fused order
    assert answer["reranked"] is True  # the head was reranked, whatever the limit cuts after it


def test_a_limit_above_what_there_is_gives_all_there_is(routes):
    answer = fusion.search(Path("unused"), "q", limit=1000, reranker=lambda: _score)
    assert sorted(hit["chunk_id"] for hit in answer["hits"]) == sorted(NAMES)


def test_no_limit_gives_the_reranked_head(routes):
    assert len(fusion.search(Path("unused"), "q", limit=None, reranker=lambda: _score)["hits"]) == fusion.RERANK_TOP


@pytest.mark.parametrize("limit", [-1, 2.5, "5", True])
def test_a_limit_that_is_no_whole_number_of_0_or_more_is_refused_by_name(routes, limit):
    with pytest.raises(ValueError, match="limit"):
        fusion.search(Path("unused"), "q", limit=limit, reranker=lambda: _score)

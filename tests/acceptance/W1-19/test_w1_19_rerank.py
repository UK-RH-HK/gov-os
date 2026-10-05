"""KPI success 1, the rerank: one lazily loaded reranker pass over the merged set [CAP-18.a].

``gov.retrieval.rerank.rerank(query, candidates, reranker=None)`` orders ``candidates`` by the reranker's scores.
``reranker`` is the loader: a function without arguments that returns ``score(query, texts) -> [float, ...]``,
higher is better. The default is the pinned Qwen3 reranker. Here the loader is a stand-in held by the driver
process, which counts each load and records each pass. So "lazily loaded" and "one pass" are read from outside:

- nothing is loaded when the modules are imported, nor by a call that does not rerank;
- one ``rerank`` is one call of the scorer, with every candidate's text.

No model, no index and no store is involved.
"""

from __future__ import annotations

import w1_19_support as support

QUERY = "where is the quartz seam"


def candidate(name, text, **extra):
    return {"chunk_id": name, "path": f"notes/{name}.md", "start_line": 1, "end_line": 3,
            "parent_id": f"parent-of-{name}", "text": text, **extra}


CANDIDATES = [
    candidate("plain", "Nothing of interest stands here.", score=0.03, routes=["lexical"]),
    candidate("twice", "The quartz seam runs under the quartz yard.", score=0.02, routes=["semantic"]),
    candidate("once", "A quartz pebble.", score=0.01, routes=["lexical", "semantic"]),
]


def rerank(api, candidates, calls_before=()):
    outcome = api.run([*calls_before, (support.RERANK, "rerank", (QUERY, candidates), {"reranker": support.RERANKER})],
                      favour=[support.FAVOURED])
    ordered = outcome.value(len(calls_before))
    assert isinstance(ordered, list), f"rerank did not return a list: {ordered!r}"
    return ordered, outcome


def test_the_candidates_come_back_in_the_order_of_the_rerankers_scores(api):
    ordered, _ = rerank(api, CANDIDATES)
    assert [entry["chunk_id"] for entry in ordered] == ["twice", "once", "plain"], \
        "the order is not the reranker's: the fused order (plain, twice, once) was kept or changed otherwise"
    scores = [entry.get("rerank_score") for entry in ordered]
    assert scores == [2.0, 1.0, 0.0], f"a candidate does not carry the reranker's score: {ordered!r}"
    for entry in ordered:
        support.check_hit(entry)
        given = next(item for item in CANDIDATES if item["chunk_id"] == entry["chunk_id"])
        assert {key: entry.get(key) for key in given} == given, f"a candidate lost what it came with: {entry!r}"


def test_one_rerank_is_one_load_and_one_pass_over_every_candidate(api):
    _, outcome = rerank(api, CANDIDATES)
    assert outcome.loads == 1, f"the reranker was loaded {outcome.loads} times for one rerank"
    assert len(outcome.passes) == 1, \
        f"the reranker was called {len(outcome.passes)} times: the merged set is scored in one pass"
    assert outcome.passes[0]["query"] == QUERY
    assert outcome.passes[0]["texts"] == [entry["text"] for entry in CANDIDATES], \
        "the one pass did not hold every candidate's text, in the order given"


def test_nothing_is_loaded_before_the_first_rerank(api):
    routes = {"lexical": CANDIDATES[:2], "semantic": CANDIDATES[1:]}
    _, outcome = rerank(api, CANDIDATES, calls_before=[(support.FUSION, "rrf", (routes,), {})])
    assert outcome.heavy_after_import == [], \
        f"importing the modules loaded {outcome.heavy_after_import}: the reranker's libraries load at the first rerank"
    fusing, reranking = outcome.calls
    assert fusing["error"] is None, f"rrf raised: {fusing['error']}"
    assert reranking["loads_before"] == 0, "the reranker was loaded by the fusion, before any rerank"
    assert reranking["heavy_before"] == [], f"{reranking['heavy_before']} were loaded before the first rerank"
    assert outcome.loads == 1 and len(outcome.passes) == 1


def test_no_candidate_means_no_load_and_no_pass(api):
    ordered, outcome = rerank(api, [])
    assert ordered == []
    assert outcome.loads == 0, "the reranker was loaded to rerank nothing"
    assert outcome.passes == []


def test_reranking_with_no_reranker_that_can_be_loaded_keeps_the_order_given_and_does_not_raise(api):
    # DEC-379: no function raises because the reranker is absent. DEC-374: nothing is reranked and the order is
    # kept. No `reranker` is given, and the default cannot be loaded: this machine has no reranker process today
    # (DEC-384), and the scratch environment has an empty HOME and no Hugging Face cache.
    outcome = api.run([(support.RERANK, "rerank", (QUERY, CANDIDATES), {})], favour=[support.FAVOURED])
    assert outcome.calls[0]["error"] is None, \
        f"rerank raised when the default reranker could not be loaded: {outcome.calls[0]['error']}"
    ordered = outcome.value()
    assert isinstance(ordered, list), f"rerank did not return a list: {ordered!r}"
    assert [entry.get("chunk_id") for entry in ordered] == [entry["chunk_id"] for entry in CANDIDATES], \
        "with no reranker the candidates are not returned in the order given (plain, twice, once)"
    for entry, given in zip(ordered, CANDIDATES):
        assert {key: entry.get(key) for key in given} == given, f"a candidate lost what it came with: {entry!r}"
        assert not isinstance(entry.get("rerank_score"), (int, float)), \
            f"a candidate carries a reranker's score although nothing was reranked: {entry!r}"
    assert outcome.loads == 0 and outcome.passes == [], "the tests' stand-in reranker was used: it was not given"


def test_candidates_the_reranker_scores_alike_keep_the_order_they_came_in(api):
    alike = [candidate(name, "No favoured word here.") for name in ("first", "second", "third")]
    ordered, _ = rerank(api, alike)
    assert [entry["chunk_id"] for entry in ordered] == ["first", "second", "third"]

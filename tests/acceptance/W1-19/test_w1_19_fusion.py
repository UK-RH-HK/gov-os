"""KPI success 1, the fusion: reciprocal rank fusion of the routes' ranked lists [CAP-18.a].

``gov.retrieval.fusion.rrf(routes, k=60)`` takes ``route name -> ranked hits`` and returns one list. A chunk's
score is the sum, over the routes that returned it, of ``1 / (k + rank)``, with ranks from 1. A chunk is in the
list once, whatever the number of routes or hits that named it (deduplication by chunk hash: the ``chunk_id`` of
W1-17). No model, no index and no store is involved.
"""

from __future__ import annotations

import pytest

import w1_19_support as support


def hit(name, **extra):
    return {"chunk_id": name, "path": f"notes/{name}.md", "start_line": 1, "end_line": 4,
            "parent_id": f"parent-of-{name}", **extra}


def rrf(api, routes, **kwargs):
    fused = api.call(support.FUSION, "rrf", routes, **kwargs)
    assert isinstance(fused, list), f"rrf did not return a list: {fused!r}"
    for entry in fused:
        assert isinstance(entry, dict) and isinstance(entry.get("chunk_id"), str), f"not a fused hit: {entry!r}"
    return fused


def ids(fused):
    return [entry["chunk_id"] for entry in fused]


def test_a_chunk_scores_the_sum_of_its_reciprocal_ranks(api):
    routes = {"lexical": [hit("a"), hit("b"), hit("c")], "semantic": [hit("c"), hit("d"), hit("a")]}
    fused = rrf(api, routes, k=support.RRF_K)
    k = support.RRF_K
    expected = {"a": 1 / (k + 1) + 1 / (k + 3), "c": 1 / (k + 3) + 1 / (k + 1), "b": 1 / (k + 2), "d": 1 / (k + 2)}
    assert {entry["chunk_id"]: entry.get("score") for entry in fused} == pytest.approx(expected)
    scores = [entry["score"] for entry in fused]
    assert scores == sorted(scores, reverse=True), f"the fused list is not ordered by score: {fused!r}"
    assert set(ids(fused)[:2]) == {"a", "c"}, "the chunks both routes returned do not lead the fused list"


def test_a_chunk_two_routes_agree_on_outranks_the_top_of_one_route(api):
    # 2 / (k + 2) > 1 / (k + 1) for every k > 0, so this holds whatever the constant is.
    routes = {"lexical": [hit("only-lexical"), hit("both")], "semantic": [hit("only-semantic"), hit("both")]}
    assert ids(rrf(api, routes))[0] == "both"


def test_a_chunk_is_in_the_fused_list_once_and_names_its_routes(api):
    routes = {"lexical": [hit("a"), hit("b")], "semantic": [hit("b"), hit("c")]}
    fused = rrf(api, routes)
    assert sorted(ids(fused)) == ["a", "b", "c"], f"the fused list is not the routes' chunks, each once: {fused!r}"
    named = {entry["chunk_id"]: sorted(entry.get("routes") or []) for entry in fused}
    assert named == {"a": ["lexical"], "b": ["lexical", "semantic"], "c": ["semantic"]}


def test_several_hits_in_one_chunk_count_once_at_their_best_rank(api):
    # The lexical route reports one hit per line (DEC-340): two lines of one chunk are one candidate.
    lexical = [hit("a", line=3), hit("a", line=4), hit("b", line=9)]
    fused = rrf(api, {"lexical": lexical}, k=support.RRF_K)
    assert ids(fused) == ["a", "b"], f"the chunk hit on two lines is not one entry: {fused!r}"
    assert fused[0]["score"] == pytest.approx(1 / (support.RRF_K + 1))
    assert fused[1]["score"] == pytest.approx(1 / (support.RRF_K + 2)), \
        "the second chunk is not ranked second: a repeated hit took a rank of its own"


def test_a_fused_hit_keeps_the_chunk_record_it_came_with(api):
    fused = rrf(api, {"semantic": [hit("a"), hit("b")]})
    for entry in fused:
        support.check_hit(entry)
        assert entry["path"] == f"notes/{entry['chunk_id']}.md"
        assert entry["parent_id"] == f"parent-of-{entry['chunk_id']}", "the parent of the chunk was lost (DEC-091)"


def test_one_route_alone_keeps_its_order_and_no_route_gives_an_empty_list(api):
    ranked = [hit("c"), hit("a"), hit("b")]
    assert ids(rrf(api, {"lexical": ranked, "semantic": []})) == ["c", "a", "b"]
    assert rrf(api, {"lexical": [], "semantic": []}) == []
    assert rrf(api, {}) == []


def test_the_same_lists_give_the_same_fused_list(api):
    # a and b tie exactly; the order between them must not change from one call to the next.
    routes = {"lexical": [hit("a"), hit("b")], "semantic": [hit("b"), hit("a")]}
    outcome = api.run([(support.FUSION, "rrf", (routes,), {})] * 3)
    first, second, third = outcome.values()
    assert first == second == third
    assert sorted(ids(first)) == ["a", "b"]

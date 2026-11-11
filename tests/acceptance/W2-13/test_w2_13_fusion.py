"""KPI success 2: the fusion receives a ranked lexical list beside the semantic one, so that lexical, semantic and
the reranker each contribute [DEC-725, W2-M102].

``gov.retrieval.fusion.search(root, question, limit, refresh=False, reranker=...)`` is asked a plain-word question
that no line holds verbatim. The semantic route is the stand-in endpoint's (vectors made of words, so no model
runs), the reranker a stand-in loader that scores a text by the favoured word. The lexical route's ranked list is
its search answer's ``ranked`` (DEC-1000), not its ``hits``. The dev query set's lexical-only hit@5 is the lead's
evidence, not a test.
"""

from __future__ import annotations

import pytest

import w2_13_support as support

pytestmark = pytest.mark.needs("git", "gitleaks", "sqlite_vec")


def fused(box, root, question, env, reranker, favour=()):
    outcome = box.run([(support.FUSION, "search", [support.path_arg(root), question, None],
                        {"refresh": False, "reranker": reranker})], env=env, favour=favour)
    answer = outcome.value()
    assert isinstance(answer, dict) and isinstance(answer.get("hits"), list), f"not a fused answer: {answer!r}"
    for hit in answer["hits"]:
        assert isinstance(hit.get("routes"), list) and hit["routes"], f"a fused hit names no route: {hit!r}"
    return answer, outcome


def test_lexical_semantic_and_the_reranker_each_contribute(box, built, ollama):
    answer, outcome = fused(box, built, support.PLAIN_QUESTION, box.scratch_env(ollama.host), support.RERANKER,
                            favour=("pilot",))
    facets = answer.get("facets", {})
    for route in (support.ROUTE_LEXICAL, support.ROUTE_SEMANTIC):
        assert facets.get(route, {}).get("available") is True, f"premise: the {route} route is not available: {facets!r}"
    routes = {route for hit in answer["hits"] for route in hit["routes"]}
    assert support.ROUTE_LEXICAL in routes, \
        f"no fused hit came from the lexical route for {support.PLAIN_QUESTION!r}: routes {sorted(routes)}"
    assert support.ROUTE_SEMANTIC in routes, f"no fused hit came from the semantic route: routes {sorted(routes)}"
    lexical = {hit["path"] for hit in answer["hits"] if support.ROUTE_LEXICAL in hit["routes"]}
    assert support.BEST in lexical, f"{support.BEST} is not among the lexical route's fused hits: {sorted(lexical)}"
    assert answer.get("reranked") is True and outcome.loads >= 1 and outcome.passes >= 1, \
        f"the reranker did not score the fused hits (reranked {answer.get('reranked')!r}, " \
        f"loads {outcome.loads}, passes {outcome.passes})"


def test_the_lexical_route_hands_the_fusion_its_ranking_best_first(box, built):
    """No endpoint and no reranker: the lexical route alone reaches the fusion, and the fused list keeps the order of
    the route's ``ranked`` list (DEC-1000; one route's list keeps its order through the fusion, W1-19), best first."""
    env = box.scratch_env()
    route = support.ranked_list_paths(box.search(built, support.PLAIN_QUESTION, env=env), support.PLAIN_QUESTION)
    answer, _ = fused(box, built, support.PLAIN_QUESTION, env, support.ABSENT_RERANKER)
    paths = list(dict.fromkeys(hit["path"] for hit in answer["hits"]))
    assert paths, f"the fusion holds no hit for {support.PLAIN_QUESTION!r} without the semantic route"
    assert not any(support.ROUTE_SEMANTIC in hit["routes"] for hit in answer["hits"]), \
        f"premise: a hit came from the semantic route, which has no endpoint: {answer['hits'][:3]!r}"
    assert paths[0] == support.BEST, f"the fused list does not start with the best lexical match: {paths}"
    assert paths == route[:len(paths)], f"the fused order is not the lexical route's ranking:\n  fused: {paths}\n" \
                                        f"  route: {route}"


def test_gov_retrieve_cites_what_the_lexical_route_ranks_for_a_plain_word_question(box, built, ollama):
    bundle = support.check_bundle(box.retrieve(built, support.PLAIN_QUESTION, host=ollama.host).result(), root=built)
    lexical = [item["path"] for item in bundle[support.K_EVIDENCE] if support.ROUTE_LEXICAL in item["routes"]]
    assert support.BEST in lexical, \
        f"gov retrieve does not cite {support.BEST} by the lexical route; cited by it: {lexical}; " \
        f"all cited: {support.cited_paths(bundle)}"

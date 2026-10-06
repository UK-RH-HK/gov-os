"""KPI success 1 (facets; dedup by chunk hash; one rerank over the merged set) [CAP-18.a].

The reranker here is a stand-in given as its loader, as ``gov.retrieval.fusion.search`` takes it (W1-19): it
counts its loads and passes, and scores a text by how often it holds the favoured word. No model runs.
"""

from __future__ import annotations

import pytest

import w1_21_support as support

pytestmark = pytest.mark.needs("gitleaks", "sqlite_vec")


def reranked(api, project, ollama, reranker=support.RERANKER, **kwargs):
    outcome = api.outcome(project, support.PHRASE, host=ollama.host, favour=[support.FAVOURED], reranker=reranker,
                          bundle_budget=0, **kwargs)
    return outcome, support.check_bundle(outcome.value(), root=project)


# ---- dedup by chunk hash

def test_a_chunk_both_routes_return_is_cited_once_and_names_both(api, project, ollama):
    """The phrase stands on two lines of one chunk, and the chunk reaches the vectors: three hits, one citation."""
    bundle = support.check_bundle(api.retrieve(project, support.DEDUP_PHRASE, host=ollama.host,
                                               batch_size=support.BATCH_LARGE, radius=support.RADIUS_FULL),
                                  root=project)
    items = [item for item in bundle[support.K_EVIDENCE] if item[support.E_PATH] == support.BAKERY]
    assert len(items) == 1, f"{support.BAKERY} is one chunk and is cited {len(items)} times"
    assert {support.ROUTE_LEXICAL, support.ROUTE_SEMANTIC} <= set(items[0][support.E_ROUTES]), \
        f"both routes returned the chunk and it names {items[0][support.E_ROUTES]}"
    merge = bundle[support.K_MERGE]
    assert type(merge.get(support.M_DUPLICATES)) is int and merge[support.M_DUPLICATES] >= 1, \
        f"the merge does not say how many duplicates it removed: {merge!r}"
    assert type(merge.get(support.M_CANDIDATES)) is int and merge[support.M_CANDIDATES] >= len(bundle[support.K_EVIDENCE])


def test_small_batches_cite_no_chunk_twice(api, project, ollama):
    """The same chunk arrives by two routes in different batches: still once (``check_bundle`` holds it)."""
    bundle = support.check_bundle(api.retrieve(project, support.DEDUP_PHRASE, host=ollama.host, batch_size=1,
                                               radius=support.RADIUS_FULL), root=project)
    assert len(bundle[support.K_BATCHES]) > 1


# ---- the routes, as facets

def test_the_bundle_names_the_routes_and_their_state(api, project, ollama):
    bundle = support.check_bundle(api.retrieve(project, support.PHRASE, host=ollama.host,
                                               batch_size=support.BATCH_LARGE, radius=support.RADIUS_FULL))
    for facet in (support.ROUTE_LEXICAL, support.ROUTE_SEMANTIC):
        assert bundle[support.K_FACETS][facet]["available"] is True, bundle[support.K_FACETS]
    by_path = {item[support.E_PATH]: item[support.E_ROUTES] for item in bundle[support.K_EVIDENCE]}
    assert all(support.ROUTE_LEXICAL in by_path[rel] for rel in support.PAGING), \
        "a file found by the exact string does not name the lexical route"
    assert support.ROUTE_SEMANTIC in by_path.get(support.TIDES, []), \
        f"{support.TIDES} is found by the vectors alone and does not name the semantic route: {by_path.get(support.TIDES)}"


# ---- one rerank over the merged set

def test_several_batches_are_reranked_in_one_pass_over_the_merged_set(api, project, ollama):
    """Batches of three. The favoured file is the fifth by path, so it is not in the first batch of a route; the
    one pass sees it and it comes first."""
    outcome, bundle = reranked(api, project, ollama, batch_size=3, radius=support.RADIUS_FULL)
    evidence = bundle[support.K_EVIDENCE]
    assert len(bundle[support.K_BATCHES]) > 1 and bundle[support.K_CONTINUATION] is None
    assert outcome.loads == 1, f"the reranker was loaded {outcome.loads} times"
    assert len(outcome.passes) == 1, f"{len(outcome.passes)} rerank passes for one bundle of several batches"
    texts = outcome.passes[0]["texts"]
    assert len(texts) >= len(evidence) > 3, \
        f"the one pass scored {len(texts)} texts and the bundle cites {len(evidence)} chunks"
    assert len(set(texts)) == len(texts), "a candidate was scored twice: the pass was not over the deduplicated set"
    assert evidence[0][support.E_PATH] == support.FAVOURED_PAGE, \
        f"the reranker scored {support.FAVOURED_PAGE} highest and the bundle starts with {evidence[0][support.E_PATH]}"
    assert bundle[support.K_MERGE].get(support.M_RERANKED) is True


def test_a_continued_bundle_is_reranked_once_too(api, project, ollama):
    _, first = reranked(api, project, ollama, batch_size=2, radius=support.RADIUS_LITE)
    outcome, _ = reranked(api, project, ollama, batch_size=2, radius=support.RADIUS_LITE,
                          continuation=first[support.K_CONTINUATION])
    assert len(outcome.passes) == 1, f"{len(outcome.passes)} rerank passes for one continued bundle"


def test_without_a_reranker_the_bundle_says_nothing_was_reranked(api, project, ollama):
    """DEC-374: an absent reranker keeps the fused order, says so and does not raise."""
    outcome, bundle = reranked(api, project, ollama, reranker=support.ABSENT_RERANKER,
                               batch_size=support.BATCH_LARGE, radius=support.RADIUS_FULL)
    assert bundle[support.K_MERGE].get(support.M_RERANKED) is False and not outcome.passes
    assert set(support.PAGING) <= set(support.paths(bundle))


def test_a_reranker_that_dies_after_loading_does_not_end_the_retrieval(api, project, ollama):
    """W1-19's known residual: the scorer raises when its process has ended. The bundle is still returned, in
    the merged order, and says nothing was reranked (package DP-6)."""
    outcome = api.outcome(project, support.PHRASE, host=ollama.host, reranker=support.BROKEN_RERANKER,
                          batch_size=support.BATCH_LARGE, radius=support.RADIUS_FULL)
    assert outcome.error() is None, f"the retrieval raised with the reranker: {outcome.error()!r}"
    bundle = support.check_bundle(outcome.value(), root=project)
    assert bundle[support.K_MERGE].get(support.M_RERANKED) is False
    assert set(support.PAGING) <= set(support.paths(bundle))


# ---- a merged set above 30 in one rerank (DEC-419 DP-9, DEC-422)

WIDE_PHRASE = "tungsten lighthouse protocol"


def test_a_rerank_over_more_than_thirty_candidates(api, ollama, tmp_path):
    """DEC-419 DP-9: one rerank call over all candidates. At radius 2, three rounds of batch_size=10 gather up to
    30 from one route, plus more from the other. The merged set exceeds the semantic route's TOP_K=30 and the
    reranker sees them all in one pass."""
    root = tmp_path / "wide"
    root.mkdir()
    support.git(root, "init", "-q", "-b", "main")
    support.adopt(root, {"all": (["**"], support.NOT_EMBEDDED)})
    for number in range(1, 45):
        support.write(root, f"pages/p{number:03d}.md",
                      f"# Page {number}\n\nThe {WIDE_PHRASE} is logged at station {number}.\n")
    support.commit(root, "44 pages", support.BASE_DATE)
    api.build(root, ollama.host)
    outcome = api.outcome(root, WIDE_PHRASE, host=ollama.host, favour=["tungsten"],
                          reranker=support.RERANKER, batch_size=10, radius=2, bundle_budget=0)
    bundle = support.check_bundle(outcome.value(), root=root)
    merge = bundle[support.K_MERGE]
    assert merge.get(support.M_RERANKED) is True, f"the bundle was not reranked: {merge!r}"
    assert type(merge.get(support.M_CANDIDATES)) is int and merge[support.M_CANDIDATES] > 30, \
        f"the merged candidate set is at most 30: {merge.get(support.M_CANDIDATES)!r}"
    assert len(outcome.passes) == 1, f"the reranker made {len(outcome.passes)} passes, not one"
    assert len(outcome.passes[0]["texts"]) > 30, \
        f"the one rerank pass scored {len(outcome.passes[0]['texts'])} texts, not more than 30"

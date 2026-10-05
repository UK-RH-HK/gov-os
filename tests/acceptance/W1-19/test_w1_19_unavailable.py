"""KPI success 1 without its daemon: Ollama absent, the semantic facet is reported unavailable, never raised
(DEC-260, DEC-257, DEC-342), and the fused list is the lexical route's, reranked once [CAP-18.a].

"Absent" is the state of this machine's sandbox and of CI: no ``ollama`` on ``PATH``, none under ``HOME``, and
nothing listening on the endpoint. No model and no ``sqlite_vec`` is needed: these cases can go green now.
"""

from __future__ import annotations

import importlib.util

import pytest

import w1_19_support as support

ROOT = support.path_arg


@pytest.mark.needs("gitleaks")
def test_the_semantic_route_says_unavailable_when_ollama_is_absent(api, repo):
    outcome = api.run([(support.SEMANTIC, "search", (ROOT(repo), support.BAKERY_QUESTION), {})])
    assert outcome.calls[0]["error"] is None, \
        f"semantic.search raised with Ollama absent (DEC-260: never raises): {outcome.calls[0]['error']}"
    answer = support.check_semantic(outcome.value())
    assert answer["available"] is False, f"the semantic facet is given as available without Ollama: {answer!r}"
    assert answer["hits"] == []


@pytest.mark.needs("gitleaks")
def test_building_the_vectors_says_unavailable_when_ollama_is_absent(api, repo):
    outcome = api.run([(support.SEMANTIC, "refresh", (ROOT(repo),), {})])
    assert outcome.calls[0]["error"] is None, \
        f"semantic.refresh raised with Ollama absent (DEC-260: never raises): {outcome.calls[0]['error']}"
    report = support.check_facet(outcome.value(), support.SEMANTIC_FACET)
    assert report["available"] is False, f"vectors are reported as built without Ollama: {report!r}"


def test_a_search_that_may_not_write_reports_a_missing_index_and_writes_nothing(api, repo, ollama):
    # The endpoint is healthy here: what is missing is the index (DEC-342), and refresh=False never writes (DEC-322).
    env = api.scratch_env(ollama_host=ollama.host)
    answer = support.check_semantic(
        api.call(support.SEMANTIC, "search", ROOT(repo), support.BAKERY_QUESTION, refresh=False, env=env))
    assert answer["available"] is False, f"a project with no index answered as available: {answer!r}"
    assert not (repo / support.RUNTIME_REL).exists(), \
        f"a search with refresh=False wrote {support.runtime_files(repo)} under {support.RUNTIME_REL}/"
    assert support.git(repo, "status", "--porcelain") == "", "a search with refresh=False changed the project"


def test_there_is_no_manifest_before_there_is_an_index(api, repo):
    assert api.call(support.SEMANTIC, "manifest", ROOT(repo)) is None
    assert not (repo / support.RUNTIME_REL).exists(), "reading the manifest wrote under .gov-runtime/"


@pytest.mark.needs("gitleaks")
def test_without_ollama_the_fused_list_is_the_lexical_routes_reranked_in_one_pass(api, repo):
    outcome = api.run([(support.FUSION, "search", (ROOT(repo), support.PHRASE),
                        {"limit": None, "reranker": support.RERANKER})], favour=[support.FAVOURED])
    assert outcome.calls[0]["error"] is None, \
        f"fusion.search raised with Ollama absent (DEC-260: never raises): {outcome.calls[0]['error']}"
    answer = support.check_fused(outcome.value())
    semantic, lexical = answer["facets"][support.SEMANTIC_FACET], answer["facets"][support.LEXICAL_FACET]
    assert semantic["available"] is False, f"the semantic facet is given as available without Ollama: {semantic!r}"
    assert lexical["available"] is True, f"the lexical route did not answer: {lexical!r}"
    found = support.paths(answer["hits"])
    assert set(support.PHRASE_FILES) <= set(found), \
        f"the results are not FTS-only results (DEC-257): the files holding the phrase are missing from {found}"
    assert found.count(support.MARKER) == 1, "the chunk that holds the phrase on two lines is in the list twice"
    for entry in answer["hits"]:
        assert support.SEMANTIC_FACET not in entry["routes"], f"a hit names the unavailable route: {entry!r}"
    # One rerank over the merged set: the stand-in favours the file the lexical route lists last.
    assert answer["reranked"] is True
    assert outcome.calls[0]["loads_before"] == 0
    assert outcome.loads == 1, f"the reranker was loaded {outcome.loads} times for one retrieval"
    assert len(outcome.passes) == 1, f"{len(outcome.passes)} reranker passes for one retrieval; the KPI says one"
    assert outcome.passes[0]["query"] == support.PHRASE
    assert len(outcome.passes[0]["texts"]) == len(answer["hits"]), \
        "the one pass was not over the merged set: its size is not the size of the full fused list"
    assert found[0] == support.ZETA, f"the first result is not the one the reranker scored highest: {found}"


@pytest.mark.needs("gitleaks")
def test_a_limit_cuts_the_list_after_the_rerank_not_before(api, repo):
    outcome = api.run([(support.FUSION, "search", (ROOT(repo), support.PHRASE),
                        {"limit": 1, "reranker": support.RERANKER})], favour=[support.FAVOURED])
    answer = support.check_fused(outcome.value())
    assert support.paths(answer["hits"]) == [support.ZETA], \
        "with limit=1 the result is not the reranker's best of the merged set"
    assert len(outcome.passes) == 1 and len(outcome.passes[0]["texts"]) >= len(support.PHRASE_FILES)


@pytest.mark.needs("gitleaks")
def test_a_reranker_that_cannot_be_loaded_leaves_the_fused_list_and_says_so(api, repo):
    # Package DP-4. The scratch environment has an empty HOME and names no reranker environment.
    if importlib.util.find_spec("sentence_transformers") is not None:
        pytest.skip("sentence_transformers can be imported by this interpreter: the reranker is not absent here")
    outcome = api.run([(support.FUSION, "search", (ROOT(repo), support.PHRASE), {"limit": None})])
    assert outcome.calls[0]["error"] is None, \
        f"fusion.search raised when the reranker could not be loaded: {outcome.calls[0]['error']}"
    answer = support.check_fused(outcome.value())
    assert answer["reranked"] is False, "the list is given as reranked although no reranker could be loaded"
    assert set(support.PHRASE_FILES) <= set(support.paths(answer["hits"])), "the fused list was dropped"

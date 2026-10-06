"""How the closure joins a retrieval, and what an absent part gives [CAP-16.b, CAP-55.a].

A ticket or an id given to the retrieval is closed over the record graph by ``gov.closure`` (W1-20) to the depth
of the radius (DEC-391: 1, 3, 8); what the closure reaches is evidence of the route ``closure``, and its gaps and
its stopping reason are the bundle's. An absent model, endpoint, index or code tool is a stated gap or a
stopping reason, never an exception and never a silent omission (package DP-6 for which reason wins).
"""

from __future__ import annotations

import pytest

import w1_21_support as support

pytestmark = pytest.mark.needs("gitleaks", "sqlite_vec")

ONE_BATCH = {"batch_size": support.BATCH_LARGE}


def ask(api, project, ollama, query=support.NO_SUCH_TEXT, **kwargs):
    return support.check_bundle(api.retrieve(project, query, host=ollama.host, **{**ONE_BATCH, **kwargs}),
                                root=project)


def routes_of(bundle, rel):
    return {route for item in bundle[support.K_EVIDENCE] if item[support.E_PATH] == rel
            for route in item[support.E_ROUTES]}


# ---- the closure

def test_a_tickets_closure_is_gathered_over_several_hops(api, project, ollama):
    """RT-0003 -> ADR-0030 -> ADR-0031 -> ADR-0032: three hops, within FULL's depth of eight."""
    bundle = ask(api, project, ollama, ticket=support.TICKET_CHAIN, radius=support.RADIUS_FULL)
    for rel in support.CHAIN:
        assert support.ROUTE_CLOSURE in routes_of(bundle, rel), \
            f"{rel} is in the ticket's closure and is not cited by the route {support.ROUTE_CLOSURE!r}"
    assert bundle[support.K_REASON] in support.NOTHING_LEFT, bundle[support.K_REASON]
    assert bundle[support.K_FACETS].get(support.ROUTE_CLOSURE, {}).get("available") is True, bundle[support.K_FACETS]


def test_a_closure_cut_by_the_depth_says_so_and_names_the_gap(api, project, ollama):
    """LITE's depth is one: ADR-0030 is reached, ADR-0031 is a gap, and the reason is the depth, not completeness."""
    bundle = ask(api, project, ollama, ticket=support.TICKET_CHAIN, radius=support.RADIUS_LITE)
    cited = set(support.paths(bundle))
    assert support.CHAIN[0] in cited and not cited & set(support.CHAIN[1:]), sorted(cited)
    assert "ADR-0031" in support.gap_names(bundle), f"the id beyond the depth is in no gap: {bundle[support.K_GAPS]!r}"
    assert bundle[support.K_REASON] == support.DEPTH_LIMIT, bundle[support.K_REASON]


def test_an_id_the_ticket_names_and_nothing_resolves_is_a_gap(api, project, ollama):
    bundle = ask(api, project, ollama, ticket=support.TICKET_DANGLING, radius=support.RADIUS_FULL)
    gaps = {gap.get("id"): gap["reason"] for gap in bundle[support.K_GAPS]}
    assert gaps.get(support.DANGLING_ID) == support.GAP_UNRESOLVED, f"{support.DANGLING_ID} is no gap: {gaps!r}"
    assert bundle[support.K_REASON] == support.UNRESOLVED_IDS, bundle[support.K_REASON]


def test_an_id_given_by_itself_is_cited(api, project, ollama):
    bundle = ask(api, project, ollama, ids=["ADR-0032"], radius=support.RADIUS_LITE)
    assert support.ROUTE_CLOSURE in routes_of(bundle, support.CHAIN[2])


def test_a_ticket_no_record_has_is_a_gap_and_no_exception(api, project, ollama):
    """A governance error with its code, or a bundle that names the ticket as a gap; never a bundle that says
    nothing is left."""
    outcome = api.outcome(project, support.NO_SUCH_TEXT, host=ollama.host, ticket="RT-9999",
                          radius=support.RADIUS_FULL, **ONE_BATCH)
    error = outcome.error()
    if error is not None:
        assert error["type"] == "GovError" and error["code"], f"not a governance error: {error!r}"
        return
    bundle = support.check_bundle(outcome.value(), root=project)
    assert "RT-9999" in support.gap_names(bundle)
    assert bundle[support.K_REASON] not in support.NOTHING_LEFT, bundle[support.K_REASON]


def test_an_id_that_exists_nowhere_is_named_as_a_gap_and_nothing_is_made_up(api, project, ollama):
    """RETR-X-02's first half, on the fixture. ``DEC-9999`` is no record; the code tool, which the closure asks
    for every id that is no record (DEC-391), is not installed here. Either way the id is a gap, the reason is
    not one that says nothing is left, and no evidence carries the id."""
    bundle = ask(api, project, ollama, support.RETR_X_02_MISSING_ID, ids=[support.RETR_X_02_MISSING_ID],
                 radius=support.RADIUS_FULL)
    assert support.RETR_X_02_MISSING_ID in support.gap_names(bundle), bundle[support.K_GAPS]
    assert bundle[support.K_REASON] in (support.UNRESOLVED_IDS, support.FACET_UNAVAILABLE), bundle[support.K_REASON]
    for item in bundle[support.K_EVIDENCE]:
        assert support.RETR_X_02_MISSING_ID not in (item[support.E_ID], item[support.E_PATH]) and \
            support.RETR_X_02_MISSING_ID not in item[support.E_TEXT], f"evidence was made up for the id: {item!r}"


# ---- an absent part

def test_without_the_embedding_endpoint_the_bundle_says_so_and_keeps_the_exact_hits(api, project):
    """No Ollama answers. No exception; the semantic route is reported unavailable with its reason; the bundle's
    stopping reason is FACET_UNAVAILABLE; what the exact string finds is still cited (G-22)."""
    outcome = api.outcome(project, support.PHRASE, batch_size=support.BATCH_LARGE, radius=support.RADIUS_FULL)
    assert outcome.error() is None, f"the retrieval raised without the endpoint: {outcome.error()!r}"
    bundle = support.check_bundle(outcome.value(), root=project)
    semantic = bundle[support.K_FACETS][support.ROUTE_SEMANTIC]
    assert semantic["available"] is False and isinstance(semantic.get("reason"), str) and semantic["reason"], semantic
    assert bundle[support.K_FACETS][support.ROUTE_LEXICAL]["available"] is True
    assert bundle[support.K_REASON] == support.FACET_UNAVAILABLE, \
        f"a route did not answer and the bundle says {bundle[support.K_REASON]}"
    assert set(support.PAGING) <= set(support.paths(bundle)), "the exact hits were dropped with the semantic route"


def test_vectors_that_were_never_built_are_an_unavailable_route(box, api, repo, ollama):
    """The endpoint answers and the project has no vectors: a retrieval reads, it builds nothing."""
    box.run([(support.LEXICAL, "refresh", [support.path_arg(repo)], {}),
             (support.STORE, "load", [support.path_arg(repo)], {})], env=box.scratch_env(ollama.host))
    before = support.tree(repo)
    bundle = support.check_bundle(api.retrieve(repo, support.PHRASE, host=ollama.host, **ONE_BATCH), root=repo)
    assert bundle[support.K_FACETS][support.ROUTE_SEMANTIC]["available"] is False
    assert bundle[support.K_REASON] == support.FACET_UNAVAILABLE, bundle[support.K_REASON]
    assert set(support.PAGING) <= set(support.paths(bundle))
    assert support.tree(repo) == before, "the retrieval built or changed a file of the project"


def test_a_project_without_any_index_is_answered_without_evidence_and_nothing_is_built(api, repo, ollama):
    """Never refreshed, no store. A governance error, or a bundle that says FACET_UNAVAILABLE and cites nothing:
    never a traceback, never an empty bundle that says nothing is left, and no runtime folder is made."""
    outcome = api.outcome(repo, support.PHRASE, host=ollama.host, **ONE_BATCH)
    error = outcome.error()
    if error is not None:
        assert error["type"] == "GovError" and error["code"], f"not a governance error: {error!r}"
    else:
        bundle = support.check_bundle(outcome.value(), root=repo)
        assert bundle[support.K_REASON] == support.FACET_UNAVAILABLE and not bundle[support.K_EVIDENCE], bundle
        assert bundle[support.K_FACETS][support.ROUTE_LEXICAL]["available"] is False
    assert not (repo / support.RUNTIME_REL).exists(), "a retrieval made the runtime folder"


@pytest.mark.parametrize("kwargs", [{}, {"ticket": support.TICKET_IN_SCOPE, "radius": support.RADIUS_FULL},
                                    {"batch_size": 1}], ids=["a question", "a ticket", "batches of one"])
def test_a_retrieval_writes_nothing(api, repo, ollama, kwargs):
    """A read command writes nowhere (DEC-317): not the index, not the store, not a cache."""
    api.build(repo, ollama.host)
    before = support.tree(repo)
    support.check_bundle(api.retrieve(repo, support.PHRASE, host=ollama.host, **kwargs), root=repo)
    assert support.tree(repo) == before, "the retrieval wrote or changed a file of the project"

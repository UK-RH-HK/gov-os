"""KPI success 2: every bundle cites by id and sha256 and carries one stopping reason from the fixed list
[CAP-55.a].

Also here: a citation whose sha256 does not match the cited bytes, two stopping reasons or none, and output that
differs between two runs on the same commit and store.
"""

from __future__ import annotations

import pytest

import w1_21_support as support

pytestmark = pytest.mark.needs("gitleaks", "sqlite_vec")

# What is asked, in words and as arguments: a spread over the paths a retrieval can take.
ASKS = {
    "an exact phrase": (support.PHRASE, {}),
    "a phrase in one batch": (support.PHRASE, {"batch_size": support.BATCH_LARGE, "radius": support.RADIUS_FULL}),
    "batches of one": (support.PHRASE, {"batch_size": 1, "radius": support.RADIUS_LITE}),
    "a text no file holds": (support.NO_SUCH_TEXT, {}),
    "a question": (support.SEMANTIC_QUESTION, {"radius": 2}),
    "a ticket": (support.CODE_PHRASE, {"ticket": support.TICKET_IN_SCOPE, "radius": support.RADIUS_FULL}),
    "a ticket that names nothing": (support.NO_SUCH_TEXT, {"ticket": support.TICKET_DANGLING,
                                                          "radius": support.RADIUS_FULL}),
    "an id beyond the depth": (support.NO_SUCH_TEXT, {"ticket": support.TICKET_CHAIN, "radius": support.RADIUS_LITE}),
    "a small bundle budget": (support.EXPANSION_PHRASE, {"bundle_budget": support.BUDGET_SMALL}),
}


@pytest.mark.parametrize("ask", ASKS, ids=list(ASKS))
def test_every_bundle_cites_by_id_and_sha256_and_carries_one_stopping_reason(api, project, ollama, ask):
    """One reason, a string of the fixed list; every evidence item with an id, a sha256 that is the hash of the
    bytes it cites, and the lines it quotes."""
    query, kwargs = ASKS[ask]
    support.check_bundle(api.retrieve(project, query, host=ollama.host, **kwargs), root=project)


@pytest.mark.parametrize("ask", ASKS, ids=list(ASKS))
def test_a_bundle_without_the_embedding_endpoint_has_the_same_form(api, project, ask):
    """No Ollama: the bundle still has one stopping reason and checked citations."""
    query, kwargs = ASKS[ask]
    support.check_bundle(api.retrieve(project, query, **kwargs), root=project)


def test_the_stopping_reason_is_one_value_and_no_second_one_is_carried(api, project, ollama):
    bundle = support.check_bundle(api.retrieve(project, support.PHRASE, host=ollama.host, batch_size=2,
                                               radius=support.RADIUS_LITE))
    assert not isinstance(bundle[support.K_REASON], (list, dict))
    others = [key for key, value in bundle.items()
              if key != support.K_REASON and isinstance(value, str) and value in support.REASONS]
    assert not others, f"the bundle carries a second stopping reason under {others}"


def test_a_cited_chunk_is_a_chunk_of_the_index_with_the_hash_of_its_file(api, project, ollama):
    bundle = support.check_bundle(api.retrieve(project, support.PHRASE, host=ollama.host,
                                               batch_size=support.BATCH_LARGE, radius=support.RADIUS_FULL),
                                  root=project)
    known = {chunk["chunk_id"]: chunk["path"] for chunk in api.call(support.LEXICAL, "chunks",
                                                                  support.path_arg(project))}
    for item in bundle[support.K_EVIDENCE]:
        assert known.get(item[support.E_CHUNK]) == item[support.E_PATH], \
            f"the cited chunk {item[support.E_CHUNK]} is not a chunk of {item[support.E_PATH]} in the index"
    assert set(support.PAGING) <= set(support.paths(bundle)), "a file that holds the phrase is not cited"


def test_a_file_changed_after_the_index_is_never_cited_at_its_old_bytes(api, repo, ollama):
    """A citation whose sha256 does not match the cited bytes. The index is stale, which makes the route
    unavailable (DEC-342): the bundle says so and cites nothing the working tree no longer holds."""
    api.build(repo, ollama.host)
    support.write(repo, support.PAGING[2], f"# Paging 3\n\nThe {support.PHRASE} was moved to the east pier.\n")
    support.commit(repo, "one file changes after the index was built")
    bundle = support.check_bundle(api.retrieve(repo, support.PHRASE, host=ollama.host,
                                               batch_size=support.BATCH_LARGE), root=repo)
    assert bundle[support.K_REASON] == support.FACET_UNAVAILABLE, \
        f"the index is stale and the bundle says {bundle[support.K_REASON]}"


def test_two_runs_on_the_same_commit_and_store_give_the_same_bundle(api, project, ollama):
    kwargs = {"host": ollama.host, "ticket": support.TICKET_IN_SCOPE, "batch_size": 3, "radius": 2}
    first = api.retrieve(project, support.PHRASE, **kwargs)
    second = api.retrieve(project, support.PHRASE, **kwargs)
    assert first == second, "the same question on the same commit and store gave two different bundles"

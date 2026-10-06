"""KPI success 4: a child hit is expanded to its parent span only within the bundle budget, and the bundle names
each expansion (DEC-091) [CAP-18.b].

A parent is the section of a document and the function of a Python file (DEC-343); the tests read both from
``gov.retrieval.lexical`` (DEC-340). The boundary cases ask without the embedding endpoint, so the exact string
is the only route and the one hit is known; the bundle budget is in tokens of four characters (package DP-3),
and the two limits used hold in characters too.
"""

from __future__ import annotations

import pytest

import w1_21_support as support

pytestmark = pytest.mark.needs("gitleaks", "sqlite_vec")

HITS = {"a section of a document": (support.EXPANSION_PHRASE, support.MANUAL, "section"),
        "a function of a Python file": (support.CODE_PHRASE, support.POOL, "function")}


def the_hit(api, project, phrase):
    """``(chunk record, parent record)`` of the one chunk that holds ``phrase``."""
    root = support.path_arg(project)
    hits = api.call(support.LEXICAL, "search", root, phrase, refresh=False)["hits"]
    assert len({hit["chunk_id"] for hit in hits}) == 1, f"the fixture holds {phrase!r} in more than one chunk"
    chunk = next(chunk for chunk in api.call(support.LEXICAL, "chunks", root, hits[0]["path"])
                 if chunk["chunk_id"] == hits[0]["chunk_id"])
    return chunk, api.call(support.LEXICAL, "parent", root, chunk["parent_id"])


def item_of(bundle, chunk):
    found = [item for item in bundle[support.K_EVIDENCE] if item[support.E_CHUNK] == chunk["chunk_id"]]
    assert len(found) == 1, f"the chunk that holds the phrase is cited {len(found)} times"
    return found[0]


def named(bundle, chunk):
    return [entry for entry in bundle[support.K_EXPANSIONS] if entry.get("chunk_id") == chunk["chunk_id"]]


@pytest.mark.parametrize("hit", HITS, ids=list(HITS))
def test_a_child_hit_is_expanded_to_its_parent_and_the_expansion_is_named(api, project, hit):
    phrase, rel, kind = HITS[hit]
    chunk, parent = the_hit(api, project, phrase)
    assert parent["kind"] == kind and (parent["start_line"], parent["end_line"]) != (chunk["start_line"], chunk["end_line"])
    bundle = support.check_bundle(api.retrieve(project, phrase, bundle_budget=support.BUDGET_LARGE), root=project)
    item = item_of(bundle, chunk)
    assert (item[support.E_PATH], item[support.E_START], item[support.E_END]) == \
        (rel, parent["start_line"], parent["end_line"]), \
        f"the hit is cited as lines {item[support.E_START]}-{item[support.E_END]}, not as its {kind} " \
        f"(lines {parent['start_line']}-{parent['end_line']})"
    entries = named(bundle, chunk)
    assert len(entries) == 1, f"the bundle names {len(entries)} expansions of the chunk: {bundle[support.K_EXPANSIONS]!r}"
    for key in ("parent_id", "path", "start_line", "end_line"):
        assert entries[0].get(key) == parent[key], f"the named expansion's {key} is {entries[0].get(key)!r}, not {parent[key]!r}"
    first, last = support.span_of(project, rel, parent["start_line"], parent["start_line"]), \
        support.span_of(project, rel, parent["end_line"], parent["end_line"])
    assert first.decode().strip() in item[support.E_TEXT] and last.decode().strip() in item[support.E_TEXT], \
        "the cited text is not the whole parent span"


def test_a_parent_that_does_not_fit_the_bundle_budget_is_not_expanded(api, project):
    """The section is some 8 600 characters, the chunk at most 1 200: under a budget of 1 500 the child stands as
    it was found, the bundle stays within its budget, and no expansion of it is named."""
    chunk, parent = the_hit(api, project, support.EXPANSION_PHRASE)
    bundle = support.check_bundle(api.retrieve(project, support.EXPANSION_PHRASE, bundle_budget=support.BUDGET_SMALL),
                                  root=project)
    item = item_of(bundle, chunk)
    assert (item[support.E_START], item[support.E_END]) == (chunk["start_line"], chunk["end_line"]), \
        f"the hit is cited as lines {item[support.E_START]}-{item[support.E_END]} under a budget its parent exceeds"
    assert not named(bundle, chunk), "an expansion is named that the budget does not allow"
    budget = bundle[support.K_BUDGET][support.B_BUNDLE]
    assert budget[support.B_LIMIT] == support.BUDGET_SMALL and 0 < budget[support.B_USED] <= support.BUDGET_SMALL, budget


def test_a_bundle_budget_of_nothing_expands_nothing(api, project, ollama):
    bundle = support.check_bundle(api.retrieve(project, support.EXPANSION_PHRASE, host=ollama.host, bundle_budget=0,
                                               batch_size=support.BATCH_LARGE), root=project)
    assert bundle[support.K_EVIDENCE] and bundle[support.K_EXPANSIONS] == []


@pytest.mark.parametrize("query", [support.EXPANSION_PHRASE, support.CODE_PHRASE, support.AUTHORITY_PHRASE,
                                   support.SEMANTIC_QUESTION])
def test_every_span_wider_than_its_chunk_is_a_named_expansion(api, project, ollama, query):
    """All routes, a large budget. A cited span is the chunk's own or its parent's, and each parent span is named
    with the chunk it was expanded from; nothing is named that is not cited."""
    root = support.path_arg(project)
    bundle = support.check_bundle(api.retrieve(project, query, host=ollama.host, batch_size=support.BATCH_LARGE,
                                               radius=support.RADIUS_FULL, bundle_budget=support.BUDGET_LARGE),
                                  root=project)
    chunks = {chunk["chunk_id"]: chunk for chunk in api.call(support.LEXICAL, "chunks", root)}
    expansions = {entry.get("chunk_id"): entry for entry in bundle[support.K_EXPANSIONS]}
    assert len(expansions) == len(bundle[support.K_EXPANSIONS]), "a chunk's expansion is named twice"
    assert set(expansions) <= set(support.chunk_ids(bundle)), "an expansion is named for a chunk that is not cited"
    for item in bundle[support.K_EVIDENCE]:
        chunk = chunks[item[support.E_CHUNK]]
        span = (item[support.E_START], item[support.E_END])
        if span == (chunk["start_line"], chunk["end_line"]) and item[support.E_CHUNK] not in expansions:
            continue
        parent = api.call(support.LEXICAL, "parent", root, chunk["parent_id"])
        assert span == (parent["start_line"], parent["end_line"]), \
            f"{item[support.E_PATH]} lines {span[0]}-{span[1]} is neither the chunk nor its parent"
        assert expansions.get(item[support.E_CHUNK], {}).get("parent_id") == chunk["parent_id"], \
            f"{item[support.E_PATH]} is cited at its parent's span and no expansion names it"

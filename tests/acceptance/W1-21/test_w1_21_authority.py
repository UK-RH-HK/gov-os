"""KPI success 1 (the authority/current filter drops superseded and must-not-cite records) [CAP-51.b] and KPI
failure 2 (a superseded record is cited as current), route by route: the exact string, the vectors, the closure,
the parent expansion, a failure or lesson record put ahead, a continuation, and a project without a record graph.

What marks a record superseded is read from the frontmatter the store loaded (DEC-329, G-19): its ``status``, a
``superseded_by`` of its own, or a ``supersedes`` of its successor. Prose is never read.
"""

from __future__ import annotations

import pytest

import w1_21_support as support

pytestmark = pytest.mark.needs("gitleaks", "sqlite_vec")

EVERYTHING = {"batch_size": support.BATCH_LARGE, "radius": support.RADIUS_FULL,
              "bundle_budget": support.BUDGET_LARGE}


def cited(api, project, ollama, query, **kwargs):
    bundle = support.check_bundle(api.retrieve(project, query, host=ollama.host, **{**EVERYTHING, **kwargs}),
                                  root=project)
    return bundle, set(support.paths(bundle))


def test_the_fixture_offers_every_superseded_record_to_the_filter(api, project):
    """The exact-string route returns all seven decisions: what the bundle leaves out, the filter dropped."""
    hits = api.call(support.LEXICAL, "search", support.path_arg(project), support.AUTHORITY_PHRASE, refresh=False)
    found = {hit["path"] for hit in hits["hits"]}
    assert set(support.SUPERSEDED) | set(support.CURRENT) | {support.MUST_NOT_CITE, support.UNTYPED_SUPERSEDED} <= found


def test_current_records_are_cited(api, project, ollama):
    _, paths = cited(api, project, ollama, support.AUTHORITY_PHRASE)
    assert set(support.CURRENT) <= paths, f"a current decision is not cited: {sorted(set(support.CURRENT) - paths)}"


@pytest.mark.parametrize("rel", sorted(support.SUPERSEDED), ids=lambda rel: rel.rsplit("/", 1)[-1])
def test_a_superseded_record_found_by_the_exact_string_is_not_cited(api, project, ollama, rel):
    """Also with every hit expanded to its parent: ``adr-0004.md`` is a long record of several chunks."""
    _, paths = cited(api, project, ollama, support.AUTHORITY_PHRASE)
    assert rel not in paths, f"{rel} is cited although {support.SUPERSEDED[rel]}"


def test_the_bundle_names_what_the_filter_dropped_and_why(api, project, ollama):
    """Dropped, never silently: the merge lists each dropped record with its reason."""
    bundle, _ = cited(api, project, ollama, support.AUTHORITY_PHRASE)
    dropped = support.dropped(bundle)
    for rel in support.SUPERSEDED:
        assert dropped.get(rel) == support.DROP_SUPERSEDED, \
            f"{rel} was dropped and the merge says {dropped.get(rel)!r}, not {support.DROP_SUPERSEDED}"
    assert not set(support.CURRENT) & set(dropped), "a current decision is listed as dropped"


def test_a_must_not_cite_record_is_not_cited(api, project, ollama):
    """Package DP-4: a record whose status is DEPRECATED is must-not-cite."""
    bundle, paths = cited(api, project, ollama, support.AUTHORITY_PHRASE)
    assert support.MUST_NOT_CITE not in paths, f"{support.MUST_NOT_CITE} ({support.MUST_NOT_CITE_STATUS}) is cited"
    assert support.MUST_NOT_CITE in support.dropped(bundle)


def test_a_superseded_file_the_store_could_not_load_is_not_cited(api, project, ollama):
    """Package DP-4: its frontmatter says SUPERSEDED and has no ``type``, so the store holds no record of it
    (DEC-274). The dev tiers' decisions are of this kind."""
    _, paths = cited(api, project, ollama, support.AUTHORITY_PHRASE)
    assert support.UNTYPED_SUPERSEDED not in paths, f"{support.UNTYPED_SUPERSEDED} says SUPERSEDED and is cited"


def test_a_superseded_record_found_by_the_vectors_is_not_cited(api, project, ollama):
    hits = api.call(support.SEMANTIC, "search", support.path_arg(project), support.SEMANTIC_QUESTION, refresh=False,
                    env=api.scratch_env(ollama.host))
    assert support.SEMANTIC_SUPERSEDED in {hit["path"] for hit in hits["hits"]}, \
        "the semantic route does not return the superseded decision: this case would hold nothing"
    _, paths = cited(api, project, ollama, support.SEMANTIC_QUESTION)
    assert support.SEMANTIC_CURRENT in paths, f"the current decision {support.SEMANTIC_CURRENT} is not cited"
    assert support.SEMANTIC_SUPERSEDED not in paths, f"{support.SEMANTIC_SUPERSEDED} is SUPERSEDED and is cited"


def test_a_superseded_record_reached_through_the_closure_is_not_cited(api, project, ollama):
    """The ticket implements ADR-0010, which supersedes ADR-0003: the closure reaches both (DEC-391 follows the
    edge both ways), and only the current one is evidence."""
    _, paths = cited(api, project, ollama, support.NO_SUCH_TEXT, ticket=support.TICKET_IN_SCOPE)
    assert support.CURRENT[0] in paths, "the decision the ticket implements is not cited"
    assert support.DECISIONS + "adr-0003.md" not in paths, "the decision it supersedes is cited"


def test_a_superseded_lesson_is_not_put_ahead(api, project, ollama):
    """Its scope matches the ticket as the current lesson's does; only the current one is returned."""
    _, paths = cited(api, project, ollama, support.CODE_PHRASE, ticket=support.TICKET_IN_SCOPE)
    assert support.LESSON in paths
    assert support.SUPERSEDED_LESSON not in paths, f"{support.SUPERSEDED_LESSON} is SUPERSEDED and is cited"


def test_no_bundle_of_a_continuation_cites_a_superseded_record(api, project, ollama):
    kwargs = {"host": ollama.host, "batch_size": 1, "radius": support.RADIUS_LITE, "bundle_budget": 0}
    first = support.check_bundle(api.retrieve(project, support.AUTHORITY_PHRASE, **kwargs))
    bundles = support.follow(api, project, support.AUTHORITY_PHRASE, first, **kwargs)
    paths = {rel for bundle in bundles for rel in support.paths(bundle)}
    assert set(support.CURRENT) <= paths
    assert not paths & set(support.SUPERSEDED), f"cited across the continuation: {sorted(paths & set(support.SUPERSEDED))}"


def test_a_supersession_committed_later_holds_once_the_store_is_loaded_again(api, repo, ollama):
    api.build(repo, ollama.host)
    kwargs = {"host": ollama.host, **EVERYTHING}
    assert support.CURRENT[1] in support.paths(api.retrieve(repo, support.AUTHORITY_PHRASE, **kwargs))
    rule = f"The {support.AUTHORITY_PHRASE} applies to every sealed crate and cask."
    support.write(repo, support.DECISIONS + "adr-0013.md",
                  support.record("ADR-0013", "decision", "ACCEPTED", rule, supersedes=["ADR-0012"]))
    support.commit(repo, "ADR-0013 supersedes ADR-0012")
    api.build(repo, ollama.host)
    paths = support.paths(support.check_bundle(api.retrieve(repo, support.AUTHORITY_PHRASE, **kwargs), root=repo))
    assert support.DECISIONS + "adr-0013.md" in paths and support.CURRENT[1] not in paths, paths


def test_without_a_record_graph_no_superseded_record_is_cited_as_current(box, api, repo):
    """The index exists and no store was loaded: what is superseded cannot be read. The retrieval says so, by an
    error or by an unavailable facet, and cites none of them."""
    box.run([(support.LEXICAL, "refresh", [support.path_arg(repo)], {})])
    outcome = api.outcome(repo, support.AUTHORITY_PHRASE, **EVERYTHING)
    if outcome.error() is not None:
        assert outcome.error()["type"] == "GovError" and outcome.error()["code"], outcome.error()
        return
    bundle = support.check_bundle(outcome.value(), root=repo)
    assert bundle[support.K_REASON] == support.FACET_UNAVAILABLE, bundle[support.K_REASON]
    assert not set(support.paths(bundle)) & set(support.SUPERSEDED), \
        "no record graph was loaded and a superseded decision is cited as current"

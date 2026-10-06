"""KPI success 1, the corpus of the vectors: a namespace that is not embedded never reaches them (DEC-381)
[CAP-10.a].

A namespace of the path map carries ``embedding_policy``. The schema of W1-08 allows any non-empty text there, so
the reading is closed here: the value ``embedded`` embeds, and everything else does not: ``not embedded``, an
unknown value, and a namespace without the field (fail closed). "Never reaches the vectors" is read from outside,
through the interface of DEC-379 and the stand-in Ollama endpoint, which records every request:

- none of the namespace's text is sent to be embedded;
- none of its chunks is a hit of the semantic route, alone or in the fused list.

The lexical index is W1-17's and is not changed: the same files are still found by the lexical route.

The policy fixture has four governance namespaces that differ only in ``embedding_policy``, one file in each. The
first case needs no ``sqlite_vec`` and holds on every machine; without ``sqlite_vec`` nothing can be embedded at
all, so what it shows today is the half of the rule that can be seen without an index. The second case needs
``sqlite_vec`` and shows the whole rule, with its premise: the namespace that says ``embedded`` is embedded.
"""

from __future__ import annotations

import pytest

import w1_19_support as support

ROOT = support.path_arg


def check_nothing_refused_reached_the_vectors(api, repo, endpoint):
    """Build what can be built, ask every route, and return the report of the build.

    Fails when a word of a file that is not embedded was sent to the endpoint, or when such a file is a semantic hit.
    """
    env = api.scratch_env(ollama_host=endpoint.host)
    built = api.run([(support.SEMANTIC, "refresh", (ROOT(repo),), {})], env=env)
    assert built.calls[0]["error"] is None, f"semantic.refresh raised: {built.calls[0]['error']}"
    report = support.check_facet(built.value(), support.SEMANTIC_FACET)

    for path, (why, word, question) in support.NEVER_EMBEDDED.items():
        answer = support.check_semantic(api.call(support.SEMANTIC, "search", ROOT(repo), question, env=env))
        assert path not in support.paths(answer["hits"]), \
            f"{path} is a hit of the semantic route although {why} (DEC-381)"

    outcome = api.run([(support.FUSION, "search", (ROOT(repo), support.POLICY_PHRASE),
                        {"limit": None, "reranker": support.RERANKER})], env=env)
    fused = support.check_fused(outcome.value())
    routes = {hit["path"]: set() for hit in fused["hits"]}
    for hit in fused["hits"]:
        routes[hit["path"]] |= set(hit["routes"])
    for path, (why, word, _) in support.NEVER_EMBEDDED.items():
        # W1-17's index does not read the policy: the file is still found by the lexical route.
        assert support.LEXICAL_FACET in routes.get(path, ()), \
            f"{path} is no longer found by the lexical route: DEC-381 keeps a file from the vectors only"
        assert support.SEMANTIC_FACET not in routes[path], \
            f"{path} is named by the semantic route in the fused list although {why} (DEC-381)"

    # Read last: by now the build, three semantic searches and one fused search have used the endpoint.
    sent = endpoint.embedded_text()
    for path, (why, word, _) in support.NEVER_EMBEDDED.items():
        assert word not in sent, f"text of {path} was sent to be embedded although {why} (DEC-381)"
    return report, routes


@pytest.mark.needs("gitleaks")
def test_no_text_of_a_namespace_that_is_not_embedded_is_sent_to_be_embedded_or_returned(api, policy_repo, ollama):
    check_nothing_refused_reached_the_vectors(api, policy_repo, ollama)


@pytest.mark.needs("gitleaks", "sqlite_vec")
def test_only_the_namespace_that_says_embedded_reaches_the_vectors(api, policy_repo, ollama):
    report, routes = check_nothing_refused_reached_the_vectors(api, policy_repo, ollama)
    assert report["available"] is True, f"the vectors were not built: {report!r}"
    assert support.ORCHARD_WORD in ollama.embedded_text(), \
        "the premise is wrong: the file of the namespace that says `embedded` was not sent to be embedded"
    assert support.SEMANTIC_FACET in routes.get(support.ORCHARD, ()), \
        f"{support.ORCHARD} is not named by the semantic route in the fused list: {routes}"
    env = api.scratch_env(ollama_host=ollama.host)
    # Files without a vector are not missing vectors: the index is complete, and a search that may not write answers.
    answer = support.check_semantic(
        api.call(support.SEMANTIC, "search", ROOT(policy_repo), support.ORCHARD_QUESTION, refresh=False, env=env))
    assert answer["available"] is True, \
        f"the index is reported unavailable because some files are not embedded: {answer!r}"
    assert set(support.paths(answer["hits"])) == {support.ORCHARD}, \
        f"the semantic route holds other files than the one that is embedded: {support.paths(answer['hits'])}"

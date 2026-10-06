"""KPI success 1 and 3 on the fixture: vectors in the shared store, the manifest, and the fused, reranked list
[CAP-10.a, CAP-18.a].

These cases need ``sqlite_vec`` (to store a vector) and ``gitleaks`` (the secret filter every index uses), and no
model: the embeddings come from a stand-in Ollama endpoint on a loopback port, which answers the daemon's HTTP
interface and computes a vector from the words of a text. So they show the mechanism, not the quality of the
real model (that is ``test_w1_19_real_models.py``).
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys

import pytest

import w1_19_support as support

ROOT = support.path_arg
INDEX = pytest.mark.needs("gitleaks", "sqlite_vec")


@pytest.mark.needs("gitleaks")
def test_the_secret_filter_lets_the_fixture_corpus_through_and_nothing_else(base, tmp_path_factory):
    """A premise, not a test of the ticket: the fixture is what the other tests take it to be (W1-15)."""
    caller = support.Api(tmp_path_factory.mktemp("w1-19-premise"))
    asked = [*support.CORPUS, support.PRODUCT_FILE, support.LEAK]
    source = ("import json, sys\nfrom pathlib import Path\nfrom gov.secrets import indexable\n"
              "print(json.dumps(indexable(Path(sys.argv[1]), json.loads(sys.argv[2]))))\n")
    done = subprocess.run([sys.executable, "-c", source, str(base), json.dumps(asked)], capture_output=True,
                          text=True, env=caller.scratch_env(), cwd=str(caller.workdir / "elsewhere"))
    assert done.returncode == 0, done.stderr
    assert sorted(json.loads(done.stdout)) == sorted(support.CORPUS)


@INDEX
def test_a_question_no_line_holds_reaches_its_chunk_by_its_vector(api, indexed):
    root, endpoint, report = indexed
    support.check_facet(report, support.SEMANTIC_FACET)
    assert report["available"] is True, f"the vectors were not built: {report!r}"
    env = api.scratch_env(ollama_host=endpoint.host)
    for question, path in ((support.BAKERY_QUESTION, support.BAKERY), (support.TIDES_QUESTION, support.TIDES)):
        exact = api.call(support.LEXICAL, "search", ROOT(root), question, refresh=False, env=env)
        assert exact["hits"] == [], "the premise is wrong: a line of the corpus holds the question"
        answer = support.check_semantic(
            api.call(support.SEMANTIC, "search", ROOT(root), question, refresh=False, env=env))
        assert answer["available"] is True, f"the semantic facet is unavailable on a fresh index: {answer!r}"
        assert support.paths(answer["hits"])[:1] == [path], \
            f"the nearest chunk to {question!r} is not in {path}: {support.paths(answer['hits'])[:5]}"


@INDEX
def test_a_semantic_hit_is_a_chunk_record_of_the_shared_store_with_its_parent(api, indexed):
    root, endpoint, _ = indexed
    env = api.scratch_env(ollama_host=endpoint.host)
    answer = support.check_semantic(
        api.call(support.SEMANTIC, "search", ROOT(root), support.BAKERY_QUESTION, refresh=False, env=env))
    records = {record["chunk_id"]: record for record in api.call(support.LEXICAL, "chunks", ROOT(root), env=env)}
    assert answer["hits"], "no hit"
    for hit in answer["hits"]:
        assert hit["chunk_id"] in records, f"a hit names a chunk the lexical index does not hold: {hit!r}"
        record = records[hit["chunk_id"]]
        assert {key: hit[key] for key in record} == record, \
            f"a hit and its chunk record disagree (path, lines or parent_id, DEC-091): {hit!r} / {record!r}"


@INDEX
def test_the_vectors_are_in_the_shared_store_beside_the_lexical_index(api, indexed, base, tmp_path):
    root, endpoint, report = indexed
    # The premise, which this case did not hold before: without it the lexical index alone satisfies what follows.
    assert report["available"] is True, f"the vectors were not built: {report!r}"
    files = support.runtime_files(root)
    assert "store.db" in files and all(name.startswith("store.db") for name in files), \
        f"the vectors are not in the one shared store (G-20): .gov-runtime/ holds {files}"
    env = api.scratch_env(ollama_host=endpoint.host)
    assert api.call(support.LEXICAL, "freshness", ROOT(root), env=env)["status"] == "fresh", \
        "building the vectors left the lexical index of the same store missing or stale"
    assert support.git(root, "status", "--porcelain") == "", "building the vectors changed a tracked file"
    # The vectors are in that store and nowhere else: a second clone of the same commit, given the store's files and
    # nothing more, answers from them without writing.
    other = support.clone(base, tmp_path / "other")
    (other / support.RUNTIME_REL).mkdir()
    for name in files:
        shutil.copy2(root / support.RUNTIME_REL / name, other / support.RUNTIME_REL / name)
    answer = support.check_semantic(
        api.call(support.SEMANTIC, "search", ROOT(other), support.BAKERY_QUESTION, refresh=False, env=env))
    assert answer["available"] is True, \
        f"a clone given only {files} has no vectors to answer from: they are not in {support.STORE_REL}: {answer!r}"
    assert support.paths(answer["hits"])[:1] == [support.BAKERY]


@INDEX
def test_the_manifest_records_the_model_ids_and_their_revisions(api, indexed):
    root, endpoint, _ = indexed
    manifest = api.call(support.SEMANTIC, "manifest", ROOT(root), env=api.scratch_env(ollama_host=endpoint.host))
    assert isinstance(manifest, dict), f"the index has no manifest: {manifest!r}"
    embedder, reranker = manifest.get("embedder"), manifest.get("reranker")
    assert isinstance(embedder, dict) and isinstance(reranker, dict), \
        f"the manifest does not record the embedder and the reranker: {manifest!r}"
    assert embedder.get("model") == support.EMBED_MODEL, f"the embedding model's id is not recorded: {embedder!r}"
    assert support.is_revision(embedder.get("revision"), support.EMBED_REVISION), \
        f"the embedding model's revision {support.EMBED_REVISION} is not recorded: {embedder!r}"
    assert support.records_digest(embedder.get("revision"), endpoint.digest), \
        f"the embedder's revision is not the digest the endpoint's model list reports (DEC-374): {embedder!r}"
    assert reranker.get("model") == support.RERANK_MODEL, f"the reranker's id is not recorded: {reranker!r}"
    assert reranker.get("revision") == support.RERANK_REVISION, \
        f"the reranker's revision is not recorded: {reranker!r}"


@INDEX
def test_the_embedders_revision_is_the_one_the_model_list_reports_not_a_constant(api, repo):
    # DEC-374. This endpoint's model list reports a digest that is not the pin; no other answer carries a digest.
    endpoint = support.OllamaStandIn(digest=support.OTHER_DIGEST)
    try:
        env = api.scratch_env(ollama_host=endpoint.host)
        report = api.call(support.SEMANTIC, "refresh", ROOT(repo), env=env)
        assert report["available"] is True, f"the vectors were not built: {report!r}"
        manifest = api.call(support.SEMANTIC, "manifest", ROOT(repo), env=env)
    finally:
        endpoint.close()
    assert isinstance(manifest, dict) and isinstance(manifest.get("embedder"), dict), \
        f"the index has no manifest that names the embedder: {manifest!r}"
    embedder = manifest["embedder"]
    assert embedder.get("model") == support.EMBED_MODEL
    assert not support.is_revision(embedder.get("revision"), support.EMBED_REVISION), \
        f"the manifest records the pin {support.EMBED_REVISION} although the model list reports another digest: " \
        f"the revision is a constant, not the one observed (DEC-374): {embedder!r}"
    assert support.records_digest(embedder.get("revision"), support.OTHER_DIGEST), \
        f"the manifest does not record the digest the model list reports ({support.OTHER_DIGEST[:12]}…): {embedder!r}"


@INDEX
def test_the_manifest_is_held_in_the_shared_store_and_read_without_ollama(api, indexed, base, tmp_path):
    # DEC-374. A second clone of the same commit is given the store's files and nothing else; its manifest is then
    # read with no endpoint at all, so the manifest is in the store and reading it asks Ollama nothing.
    root, endpoint, _ = indexed
    manifest = api.call(support.SEMANTIC, "manifest", ROOT(root), env=api.scratch_env(ollama_host=endpoint.host))
    assert isinstance(manifest, dict), f"the index has no manifest: {manifest!r}"
    other = support.clone(base, tmp_path / "other")
    (other / support.RUNTIME_REL).mkdir()
    stores = [name for name in support.runtime_files(root) if name.startswith("store.db")]
    for name in stores:
        shutil.copy2(root / support.RUNTIME_REL / name, other / support.RUNTIME_REL / name)
    assert api.call(support.SEMANTIC, "manifest", ROOT(other)) == manifest, \
        f"the manifest is not read from {support.STORE_REL} alone: a clone given only {stores} has another, or none"
    assert support.git(other, "status", "--porcelain") == "", "reading the manifest changed a tracked file"


@INDEX
def test_no_text_the_secret_filter_refuses_is_embedded_or_returned(api, repo, ollama):
    env = api.scratch_env(ollama_host=ollama.host)
    report = api.call(support.SEMANTIC, "refresh", ROOT(repo), env=env)
    assert report["available"] is True, f"the vectors were not built: {report!r}"
    sent = ollama.embedded_text()
    assert "Sourdough" in sent, "the premise is wrong: the corpus was not sent to the endpoint to be embedded"
    for needle, what in ((support.CANARY, "the planted secret"), ("vermilion", "the file that holds a secret"),
                         ("heliotrope", "the product-data file")):
        assert needle not in sent, f"{what} was sent to be embedded: the index did not use the secret filter"
    for question, refused in ((support.LEAK_QUESTION, support.LEAK),
                              (support.PRODUCT_QUESTION, support.PRODUCT_FILE)):
        answer = support.check_semantic(api.call(support.SEMANTIC, "search", ROOT(repo), question, env=env))
        assert refused not in support.paths(answer["hits"]), f"{refused} is returned by the semantic route"


@INDEX
def test_both_routes_are_fused_into_one_list_and_reranked_in_one_pass(api, indexed):
    root, endpoint, _ = indexed
    outcome = api.run([(support.FUSION, "search", (ROOT(root), support.PHRASE),
                        {"limit": None, "refresh": False, "reranker": support.RERANKER})],
                      env=api.scratch_env(ollama_host=endpoint.host), favour=[support.FAVOURED])
    answer = support.check_fused(outcome.value())
    for facet in (support.LEXICAL_FACET, support.SEMANTIC_FACET):
        assert answer["facets"][facet]["available"] is True, f"the {facet} route did not answer: {answer['facets']}"
    found = support.paths(answer["hits"])
    assert set(support.PHRASE_FILES) <= set(found)
    both = [entry for entry in answer["hits"]
            if {support.LEXICAL_FACET, support.SEMANTIC_FACET} <= set(entry["routes"])]
    assert both, "no chunk is named by both routes: the lists were joined, not fused by chunk"
    assert answer["reranked"] is True
    assert outcome.loads == 1 and len(outcome.passes) == 1, \
        f"{outcome.loads} loads and {len(outcome.passes)} passes of the reranker for one retrieval; the KPI says one"
    assert len(outcome.passes[0]["texts"]) == len(answer["hits"]), "the one pass was not over the merged set"
    assert found[0] == support.ZETA, f"the first result is not the one the reranker scored highest: {found}"


@INDEX
def test_a_changed_file_is_embedded_before_the_next_retrieval_and_stale_vectors_are_reported(api, repo, ollama):
    env = api.scratch_env(ollama_host=ollama.host)
    api.call(support.SEMANTIC, "refresh", ROOT(repo), env=env)
    support.write(repo, "notes/kiln.md", "# Kiln\n\nThe potter fires the glazed bowls in the kiln on Thursdays.\n")
    support.commit(repo, "one file is added")
    question = "when does the potter fire the glazed bowls"
    stale = support.check_semantic(
        api.call(support.SEMANTIC, "search", ROOT(repo), question, refresh=False, env=env))
    assert stale["available"] is False, \
        "vectors older than the tracked files were answered from as if current (DEC-342)"
    fresh = support.check_semantic(api.call(support.SEMANTIC, "search", ROOT(repo), question, env=env))
    assert fresh["available"] is True
    assert support.paths(fresh["hits"])[:1] == ["notes/kiln.md"], \
        f"the added file was not embedded before the retrieval: {support.paths(fresh['hits'])[:5]}"

"""S2: an unpinned or mismatched model fails closed with a named error [CAP-19.a, W2-M073, W2-M191, W2-L065].

"Fails closed": nothing is embedded or answered with a model other than the pinned one; the semantic store is not
reported recreated and the semantic route answers unavailable with no hit. "A named error": an upper-case code in
the answer, ``..._UNPINNED`` / ``..._MISMATCH`` (README, "Named errors").

- W2-M073 (no version pin in the store; configuration changes not re-judged): the pin is checked against the store
  and against the endpoint at every search and rebuild.
- W2-M191 (``gov rebuild --no-embeddings`` leaves stale vectors): vectors the rebuild did not renew are never answered
  from when they no longer match.
- W2-L065 (vectors built before the 512-character cut not detected as stale): the manifest records the cut, and a
  store that records none, or another, is stale.
"""

from __future__ import annotations

import pytest

import w2_32_support as s

QUESTION, GOLD = s.QUESTIONS[0]


def _refused_search(box, project):
    """A search that must fail closed: unavailable, no hit; its answer."""
    answer = s.result(box.call("semantic_search", root=str(project), query=QUESTION))
    assert answer["available"] is False and answer.get("state") == "FACET_UNAVAILABLE", \
        f"the semantic route answered although its vectors do not match the pin: {answer}"
    assert answer["hits"] == [], answer
    return answer


# ---- the default pin ----

def test_without_configuration_adr_0002s_pin_builds_and_the_planted_questions_are_answered(project, box, standin):
    standin.offer({s.PIN_MODEL: s.PIN_DIGEST})
    box.built(project)
    built_by = s.result(box.call("manifest", root=str(project)))
    assert built_by["embedder"]["model"] == s.PIN_MODEL and built_by["embedder"]["revision"].startswith(s.PIN_ID), \
        built_by
    for question, gold in s.QUESTIONS:
        answer = s.result(box.call("semantic_search", root=str(project), query=question))
        assert answer["available"] is True and gold in s.first_paths(answer["hits"]), (question, answer)


def test_an_endpoint_reporting_another_revision_of_the_pinned_model_fails_closed_at_rebuild(project, box, standin):
    standin.offer({s.PIN_MODEL: s.OTHER_DIGEST})
    envelope = box.rebuild(project)
    store = s.semantic_store(envelope)
    assert store.get("status") != "recreated", f"vectors were built with an unpinned revision: {store}"
    assert s.code_named(store, "MISMATCH"), f"no named error (…_MISMATCH) for the revision mismatch: {store}"
    assert standin.texts_embedded() == [], "nothing is embedded with a model that does not match the pin"
    assert s.vector_paths(project) == set(), "no vector of the mismatched model is in the store"


@pytest.mark.parametrize("revision", [..., "", None], ids=["no-revision", "empty-revision", "null-revision"])
def test_a_configured_model_without_a_revision_fails_closed_at_rebuild(project, box, standin, revision):
    s.pin(project, s.SWAP_MODEL, revision)
    envelope = box.rebuild(project)
    store = s.semantic_store(envelope)
    assert store.get("status") != "recreated", f"vectors were built with an unpinned model: {store}"
    assert s.code_named(store, "UNPINNED"), f"no named error (…_UNPINNED) for the unpinned model: {store}"
    assert standin.texts_embedded() == [], "nothing is embedded with an unpinned model"


def test_a_pinned_model_the_endpoint_does_not_list_fails_closed_at_rebuild(project, box, standin):
    standin.offer({s.PIN_MODEL: s.PIN_DIGEST})
    s.pin(project, s.SWAP_MODEL, s.SWAP_DIGEST)
    envelope = box.rebuild(project)
    store = s.semantic_store(envelope)
    assert store.get("status") != "recreated", f"vectors were built with a model other than the pinned one: {store}"
    assert s.any_code(store) and s.SWAP_MODEL in str(store), \
        f"the refusal names an error code and the pinned model: {store}"
    assert set(standin.models_asked()) <= {s.SWAP_MODEL}, \
        f"no other model is used in the pinned one's place: {standin.models_asked()}"


# ---- a store that no longer matches ----

def test_a_search_after_the_endpoints_revision_changed_fails_closed(project, box, standin):
    box.built(project)
    standin.offer({s.PIN_MODEL: s.OTHER_DIGEST, s.SWAP_MODEL: s.SWAP_DIGEST})
    answer = _refused_search(box, project)
    assert s.code_named(answer, "MISMATCH"), f"no named error (…_MISMATCH): {answer}"


def test_a_search_after_the_configured_pin_changed_without_a_rebuild_fails_closed(project, box, standin):
    box.built(project)
    s.pin(project, s.SWAP_MODEL, s.SWAP_DIGEST)
    answer = _refused_search(box, project)
    assert s.code_named(answer, "MISMATCH"), f"no named error (…_MISMATCH): {answer}"


def test_retrieve_reports_the_mismatch_as_an_unavailable_semantic_route(project, box, standin):
    box.built(project)
    s.pin(project, s.SWAP_MODEL, s.SWAP_DIGEST)
    bundle = s.result(box.call("retrieve", root=str(project), query=QUESTION))
    facet = bundle["facets"]["semantic"]
    assert facet["available"] is False, f"the bundle used vectors of another model than the pin: {facet}"
    assert s.code_named(facet, "MISMATCH"), f"the semantic facet's reason names the error (…_MISMATCH): {facet}"
    assert bundle["stopping_reason"] == "FACET_UNAVAILABLE", bundle["stopping_reason"]


# ---- W2-M191: --no-embeddings ----

def test_rebuild_without_embeddings_after_a_pin_change_leaves_no_vector_answering(project, box, standin):
    box.built(project)
    s.pin(project, s.SWAP_MODEL, s.SWAP_DIGEST)
    envelope = box.rebuild(project, "--no-embeddings")
    assert envelope.get("ok") is True, envelope
    _refused_search(box, project)


def test_rebuild_without_embeddings_after_a_file_changed_leaves_no_stale_vector_answering(project, box, standin):
    box.built(project)
    s.write(project, "docs/harbour.md", "# Harbour\n\nThe harbour is closed; the ferries moved to the river.\n")
    s.commit(project, "the harbour note changed")
    envelope = box.rebuild(project, "--no-embeddings")
    assert envelope.get("ok") is True, envelope
    _refused_search(box, project)


# ---- W2-L065: the embedding cut ----

def test_the_manifest_records_the_embedding_cut(project, box, standin):
    """Rewrite-Reason: W2-32's S7 (DEC-1066): the cut changes from 512 to the whole chunk, so the case asks that the
    manifest record a cut (a key besides the two models), not that it be 512."""
    box.built(project)
    built_by = s.result(box.call("manifest", root=str(project)))
    assert built_by is not None and s.cut_entries(built_by), \
        f"the manifest does not record the cut the chunks were embedded at: {built_by}"


def test_a_store_that_records_no_cut_is_stale_and_the_next_rebuild_renews_it(project, box, standin):
    box.built(project)
    s.without_cut_record(project)
    answer = _refused_search(box, project)
    assert answer.get("reason"), f"the stale store is reported with its reason: {answer}"
    box.built(project)
    renewed = s.result(box.call("semantic_search", root=str(project), query=QUESTION))
    assert renewed["available"] is True and GOLD in s.first_paths(renewed["hits"]), renewed
    # Rewrite-Reason: W2-32's S7 (DEC-1066): the renewed manifest records its cut, whatever S7 makes it.
    assert s.cut_entries(s.result(box.call("manifest", root=str(project))))

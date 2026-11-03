"""S1: changing the embedder pin in configuration triggers a full re-embed, and the dev-tier retrieval regression
passes [CAP-10.b] (with W2-M073: untracked configuration changes are re-judged).

The pin is the project's ``governance/project/models.yaml`` (``embedder: {model, revision}``); without it, ADR-0002
§2's pin holds (README, "The interface these cases assume"). The regression on a real second model is judged by the
record (README); here the planted questions are asked with the stand-in second embedder.
"""

from __future__ import annotations

import w2_32_support as s


def _swap(project, box, standin):
    """Build under the default pin, then pin the second embedder (untracked, W2-M073) and rebuild."""
    box.built(project)
    before = s.vectors(project)
    assert before and all(len(vector) == 4 * s.DIMENSIONS[s.PIN_MODEL] for _, vector in before.values()), \
        "premise: the first rebuild embeds every planted note with the pinned model"
    s.pin(project, s.SWAP_MODEL, s.SWAP_DIGEST)
    standin.clear()
    envelope = box.rebuild(project)
    return before, envelope


def test_a_changed_embedder_pin_re_embeds_every_chunk_at_the_next_rebuild(project, box, standin):
    before, envelope = _swap(project, box, standin)
    assert envelope.get("ok") is True and s.semantic_store(envelope).get("status") == "recreated", \
        f"the rebuild after the pin change did not recreate the vectors: {s.semantic_store(envelope)}"
    after = s.vectors(project)
    assert set(after) == set(before), "the same chunks have vectors after the swap"
    swapped = standin.returned.get(s.SWAP_MODEL, set())
    stale = sorted(path for path, vector in after.values() if vector not in swapped)
    assert not stale, f"vectors not made by the configured embedder {s.SWAP_MODEL} after the swap: {stale}"
    assert len(standin.texts_embedded(s.SWAP_MODEL)) >= len(after), \
        "every chunk is sent to the configured embedder: a full re-embed"
    built_by = s.result(box.call("manifest", root=str(project)))
    assert built_by and built_by["embedder"]["model"] == s.SWAP_MODEL, built_by
    assert s.SWAP_DIGEST.startswith(built_by["embedder"]["revision"][:12]) and \
        len(built_by["embedder"]["revision"]) >= 12, f"the manifest records the configured revision: {built_by}"


def test_removing_the_pin_change_re_embeds_every_chunk_with_the_default_pin_again(project, box, standin):
    _swap(project, box, standin)
    s.unpin(project)
    standin.clear()
    box.built(project)
    after = s.vectors(project)
    pinned = standin.returned.get(s.PIN_MODEL, set())
    assert after and all(vector in pinned for _, vector in after.values()), \
        "back on ADR-0002's pin, every vector is the pinned model's again"
    assert s.result(box.call("manifest", root=str(project)))["embedder"]["model"] == s.PIN_MODEL


def test_a_search_that_may_refresh_re_embeds_after_a_pin_change(project, box, standin):
    box.built(project)
    s.pin(project, s.SWAP_MODEL, s.SWAP_DIGEST)
    standin.clear()
    answer = s.result(box.call("semantic_search", root=str(project), query=s.QUESTIONS[0][0], refresh=True))
    assert answer["available"] is True, f"a refreshing search after the pin change answers: {answer}"
    swapped = standin.returned.get(s.SWAP_MODEL, set())
    assert all(vector in swapped for _, vector in s.vectors(project).values()), \
        "the refresh re-embedded every chunk with the configured embedder"


def test_after_the_swap_questions_are_embedded_by_the_new_model_and_the_planted_regression_passes(
        project, box, standin):
    _, envelope = _swap(project, box, standin)
    assert s.semantic_store(envelope).get("status") == "recreated", s.semantic_store(envelope)
    for question, gold in s.QUESTIONS:
        standin.clear()
        answer = s.result(box.call("semantic_search", root=str(project), query=question))
        assert answer["available"] is True, f"the semantic route answers after the swap: {answer}"
        assert standin.models_asked() and set(standin.models_asked()) == {s.SWAP_MODEL}, \
            f"the question is embedded by the configured model, and only by it: {standin.models_asked()}"
        assert gold in s.first_paths(answer["hits"]), f"{question!r}: {gold} not in the semantic route's first five"
        bundle = s.result(box.call("retrieve", root=str(project), query=question))
        assert bundle["facets"]["semantic"]["available"] is True, bundle["facets"]
        assert gold in s.first_paths(bundle["evidence"]), \
            f"{question!r}: {gold} not cited in the first five after the swap ({s.first_paths(bundle['evidence'])})"

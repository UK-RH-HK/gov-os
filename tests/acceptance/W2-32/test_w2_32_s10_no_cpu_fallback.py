"""S10: no CPU fallback for embeddings [DEC-1065, DEC-1031, ACT-RERANK-WAIT-1].

The line: when the shared GPU embedders cannot be reached (the launch sandbox included), a search reports its
semantic part unavailable with a named code and answers by keywords; gov never starts a private embedder
(``ensure_available`` and ``ensure_query_available`` check health only); a vector computed on the CPU is refused,
never cached or stored; a rebuild refuses to embed on the CPU.

- **Unreachable:** both embedder addresses (``OLLAMA_HOST``, ``GOV_QUERY_OLLAMA_HOST``) point at a loopback port
  nothing listens on.
- **No private embedder:** each child's ``GOV_OLLAMA_BIN`` is the trap (``w2_32_support.Box``), which only leaves a
  marker; every case here asserts the marker is absent (the box's teardown asserts it too).
- **On the CPU:** the stand-in reports the model loaded with ``size_vram`` 0 at ``/api/ps`` (DEC-1033's reading of
  the device). Elsewhere in this suite it reports the GPU.
- **A named code:** an upper-case code of two parts or more in the answer's text (README, "Named errors").
"""

from __future__ import annotations

import json

import w2_32_support as s

QUESTION, GOLD = s.QUESTIONS[0]


def _nothing_started(box):
    assert not box.marker.exists(), \
        f"gov tried to start a private embedder: {box.marker.read_text()!r} (S10, DEC-1065)"


def _unavailable_with_a_code(answer, what):
    assert answer["available"] is False and answer["hits"] == [], f"{what}: the semantic part answered: {answer}"
    assert s.any_code(answer), f"{what}: no named code for the unavailable semantic part: {answer}"


# ---- the embedders cannot be reached ----

def test_ensure_available_with_the_embedders_unreachable_checks_health_only(box):
    box.host = s.dead_host()
    answers = s.result(box.call("ensure"))
    for name, answer in answers.items():
        assert answer["available"] is False, f"the {name} embedder is reported available: {answer}"
        assert not answer.get("started"), f"the {name} embedder was started: {answer}"
    _nothing_started(box)


def test_a_search_with_the_embedders_unreachable_reports_the_semantic_part_unavailable_with_a_named_code(
        project, box, standin):
    box.built(project)
    box.host = s.dead_host()
    answer = s.result(box.call("semantic_search", root=str(project), query=QUESTION))
    _unavailable_with_a_code(answer, "the embedders unreachable")
    _nothing_started(box)


def test_retrieve_with_the_embedders_unreachable_answers_by_keywords(project, box, standin):
    box.built(project)
    box.host = s.dead_host()
    data = box.call("retrieve", root=str(project), query=QUESTION)
    bundle = s.result(data)
    facet = bundle["facets"]["semantic"]
    assert facet["available"] is False and s.any_code(facet), f"the semantic part is named unavailable: {facet}"
    assert GOLD in s.first_paths(bundle["evidence"]), \
        f"the keyword route still answers: {GOLD} not in {s.first_paths(bundle['evidence'])}"
    assert all("semantic" not in item["routes"] for item in bundle["evidence"]), "no item comes from the vectors"
    s.no_traceback(data)
    _nothing_started(box)


def test_a_rebuild_with_the_embedder_unreachable_refuses_the_vectors_and_starts_nothing(project, box, standin):
    box.host = s.dead_host()
    envelope = box.rebuild(project)
    store = s.semantic_store(envelope)
    assert store.get("status") != "recreated" and s.any_code(store), \
        f"the semantic store is refused with a named code: {store}"
    lexical = ((envelope.get("result") or {}).get("stores") or {}).get("lexical") or {}
    assert lexical.get("status") == "recreated", f"the keyword index is still built: {json.dumps(envelope)[:1500]}"
    assert s.vector_paths(project) == set()
    _nothing_started(box)


# ---- a vector computed on the CPU ----

def test_a_question_vector_computed_on_the_cpu_is_refused_and_nothing_cached(project, box, standin):
    box.built(project)
    rows = s.cache_rows(project)
    standin.device = "cpu"
    answer = s.result(box.call("semantic_search", root=str(project), query=QUESTION))
    _unavailable_with_a_code(answer, "the query embedder on the CPU")
    assert s.cache_rows(project) == rows, "a vector computed on the CPU was cached"
    _nothing_started(box)


def test_retrieve_with_the_query_embedder_on_the_cpu_answers_by_keywords(project, box, standin):
    box.built(project)
    standin.device = "cpu"
    bundle = s.result(box.call("retrieve", root=str(project), query=QUESTION))
    facet = bundle["facets"]["semantic"]
    assert facet["available"] is False and s.any_code(facet), f"the CPU vector is refused, named: {facet}"
    assert GOLD in s.first_paths(bundle["evidence"]), s.first_paths(bundle["evidence"])
    _nothing_started(box)


def test_a_rebuild_with_the_embedder_on_the_cpu_refuses_to_embed(project, box, standin):
    standin.device = "cpu"
    envelope = box.rebuild(project)
    store = s.semantic_store(envelope)
    assert store.get("status") != "recreated" and s.any_code(store), \
        f"a rebuild on the CPU is refused with a named code: {store}"
    assert s.vector_paths(project) == set(), "no vector computed on the CPU is stored"
    assert s.cache_rows(project) == 0, "no vector computed on the CPU is cached"
    _nothing_started(box)

"""S8 (G3, round 2; DEC-1067 (a), replacing DEC-1066 (2)'s wording): routing by question type.

The line: a question that names a symbol puts the code route's first 2 hits ahead after the rerank; a question that
names a record puts that record's 2 best chunks ahead; each half kept only if it holds at its measure. The CTO's
ruling for the build: each half behind its own setting, both off by default; off gives today's order exactly; an
invalid value is ``CONFIG_INVALID`` naming the key (``w2_32_routing``: the file and the keys the cases assume).

Every case asks ``gov.retrieval.retrieve.retrieve`` of the planted project (``w2_32_routing.plant``) with the stand-in
reranker that scores each text by its ``rankNN`` and keeps each request, and the stand-in code route. "The
reranker's order" is the order the same scores give the pool as the reranker received it (stable for ties); "ahead"
is the first places of the evidence; the rest keeps the reranker's order. Whether a half holds at its measure is
D-4b's record, not a case here.

Rewrite-Reason: the engineer's stated setting names: ``routing.code_first`` and ``routing.named_first`` in
``governance/project/retrieval.yaml``, counts (on: 2, the measured form; off: absent or 0), where the cases had
``route_by_symbol`` and ``route_by_record``, true or false. Every guard is kept; the "on" cases also ask for the
bundle's ``routing`` record of what it moved, which the engineer states.
"""

from __future__ import annotations

import json
import struct
from pathlib import Path

import pytest

import w2_32_routing as r
import w2_32_support as s

CAP = 16
ROUTE_ORDER_AHEAD = {(path, r.rank_of(r.CODE_TEXT[path])) for path in r.CODE[:2]}  # the fallback: no vectors
RECORD_AHEAD = {(r.RECORD_REL, rank) for rank in sorted(r.RECORD_RANKS, reverse=True)[:2]}


@pytest.fixture
def routed(tmp_path, needs_vectors, box):
    project = r.plant(tmp_path / "routed")
    box.built(project)
    return project


@pytest.fixture
def unvectored(tmp_path, needs_vectors, box):
    project = r.plant(tmp_path / "unvectored", code_vectors=False)
    box.built(project)
    return project


def _code_ahead(project, standin, question):
    """S8's measured form: the code route's first 2 hits by their stored vectors' cosine to the question (the
    question's vector the one the stand-in made from the text it was sent; ties in the route's order).

    Rewrite-Reason: S8's measured form (cosine order of the code route): the cases read "the code route's first 2
    hits" as the route's own order."""
    sent = [text for text in standin.texts_embedded(s.PIN_MODEL) if text.endswith(question)]
    assert sent, "premise: the question was sent to the stand-in embedder"
    asked = s.stand_in_vector(s.PIN_MODEL, sent[-1])
    stored = {path: vector for path, vector in s.vectors(project).values() if path in r.CODE}
    assert set(stored) == set(r.CODE), f"premise: every code hit has a stored vector: {sorted(stored)}"

    def cosine(vector):
        values = struct.unpack(f"{len(vector) // 4}f", vector)
        return sum(a * b for a, b in zip(asked, values))

    ranked = sorted(r.CODE, key=lambda path: (-cosine(stored[path]), r.CODE.index(path)))
    ahead = {(path, r.rank_of(r.CODE_TEXT[path])) for path in ranked[:2]}
    assert ahead != ROUTE_ORDER_AHEAD, "premise: the cosine order's first 2 are not the route's own first 2"
    return ahead


def _ask(box, project, question):
    """The bundle, the reranker's requests (each a list of texts) and the reranker's order of the pool's chunks."""
    log = Path(box.workdir) / "rerank-ranks.jsonl"
    if log.exists():
        log.unlink()
    data = box.call("retrieve", root=str(project), query=question, reranker=f"ranks:{log}", code_route=r.CODE_ROUTE)
    raised = data.get("raised")
    if raised is not None:
        return None, raised, []
    requests = [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines()] if log.exists() else []
    pool = [text for request in requests for text in request]
    # Each chunk once, at its first place (a chunk the code scores again in a later request is the same chunk).
    unique, seen = [], set()
    for text in pool:
        head, _, body = text.partition("\n")
        if (head, body) not in seen:
            seen.add((head, body))
            unique.append((head[len("[path: "):-1], r.rank_of(text)))
    order = [key for _, key in sorted(enumerate(unique), key=lambda pair: (-pair[1][1], pair[0]))]
    return data["result"], requests, order


def _evidence(bundle):
    return [r.key_of(item["path"], item["text"]) for item in bundle["evidence"]]


def _reranker_order(evidence, order):
    """The evidence's chunks in the reranker's order (as many of a key as the evidence holds)."""
    left = {}
    for key in evidence:
        left[key] = left.get(key, 0) + 1
    picked = []
    for key in order:
        if left.get(key):
            left[key] -= 1
            picked.append(key)
    return picked


def _moved_named(bundle, routed):
    """With a half on, the bundle carries a ``routing`` record of what it moved (the engineer's statement)."""
    record = bundle.get("routing")
    assert record, f"the bundle carries no routing record of what it moved: {sorted(bundle)}"
    text = json.dumps(record)
    moved = [item for item in bundle["evidence"] if r.key_of(item["path"], item["text"]) in routed]
    missing = sorted(r.key_of(item["path"], item["text"]) for item in moved
                     if item["chunk_id"] not in text and item["path"] not in text)
    assert moved and not missing, f"the routing record does not name what it moved ({missing}, by chunk id or " \
                                  f"path): {record}"


def _ahead(evidence, order, routed):
    """Fails unless the evidence starts with exactly ``routed`` and the rest keeps the reranker's order."""
    assert routed <= set(evidence), f"premise: the routed chunks are gathered: {sorted(routed - set(evidence))}"
    assert set(_reranker_order(evidence, order)[:len(routed)]) != routed, \
        "premise: the reranker alone does not put the routed chunks first (routing must be what does)"
    head, rest = evidence[:len(routed)], evidence[len(routed):]
    assert set(head) == routed, f"the routed chunks are not put ahead after the rerank: the first {len(routed)} are " \
                                f"{head}, not {sorted(routed)}"
    expected = list(_reranker_order(evidence, order))
    for key in head:
        expected.remove(key)
    assert rest == expected, \
        "after the routed chunks, the rest is not in the reranker's order"


QUESTIONS = {"symbol": r.SYMBOL_QUESTION, "record": r.RECORD_QUESTION, "both": r.BOTH_QUESTION,
             "plain": r.PLAIN_QUESTION}


# ---- off (the default): today's order exactly ---------------------------------------------------------------------

@pytest.mark.parametrize("asked", sorted(QUESTIONS))
@pytest.mark.parametrize("settings", ["absent", "both-zero", "empty-block"])
def test_with_both_halves_off_the_order_is_the_rerankers(routed, box, standin, settings, asked):
    if settings == "both-zero":
        r.set_routing(routed, symbol=r.OFF, record=r.OFF)
    elif settings == "empty-block":
        r.set_routing(routed)
    bundle, _, order = _ask(box, routed, QUESTIONS[asked])
    assert bundle is not None, f"the retrieval raised with routing off: {_}"
    evidence = _evidence(bundle)
    assert evidence == _reranker_order(evidence, order), \
        f"routing off ({settings}) changed the reranker's order: {evidence[:6]}"


def test_off_by_setting_gives_the_same_bundle_as_no_setting(routed, box, standin):
    absent, _, _ = _ask(box, routed, r.BOTH_QUESTION)
    r.set_routing(routed, symbol=r.OFF, record=r.OFF)
    off, _, _ = _ask(box, routed, r.BOTH_QUESTION)
    assert [(e["path"], e["start_line"], e["end_line"]) for e in off["evidence"]] == \
        [(e["path"], e["start_line"], e["end_line"]) for e in absent["evidence"]], "off differs from the default"


# ---- route by symbol ----------------------------------------------------------------------------------------------

def test_route_by_symbol_puts_the_code_routes_first_two_hits_ahead_after_the_rerank(routed, box, standin):
    r.set_routing(routed, symbol=r.ON)
    bundle, _, order = _ask(box, routed, r.SYMBOL_QUESTION)
    assert bundle["facets"].get("code", {}).get("available") is True, f"premise: the code route answers: {bundle['facets']}"
    ahead = _code_ahead(routed, standin, r.SYMBOL_QUESTION)
    _ahead(_evidence(bundle), order, ahead)
    _moved_named(bundle, ahead)


def test_route_by_symbol_without_stored_vectors_falls_back_to_the_routes_own_order(unvectored, box, standin):
    """S8's measured form: a code hit with no stored vector is ranked in the code route's own order (here no code
    file is embedded), so its first 2 hits are the route's first 2.

    Rewrite-Reason: S8's measured form (cosine order of the code route): the fallback, a case of its own."""
    r.set_routing(unvectored, symbol=r.ON)
    stored = {path for path, _ in s.vectors(unvectored).values()}
    assert not stored & set(r.CODE), f"premise: no code hit has a stored vector: {sorted(stored & set(r.CODE))}"
    bundle, _, order = _ask(box, unvectored, r.SYMBOL_QUESTION)
    assert bundle["facets"].get("code", {}).get("available") is True, f"premise: the code route answers: {bundle['facets']}"
    _ahead(_evidence(bundle), order, ROUTE_ORDER_AHEAD)
    _moved_named(bundle, ROUTE_ORDER_AHEAD)


@pytest.mark.parametrize("asked", ["plain", "record"])
def test_route_by_symbol_leaves_a_question_naming_no_symbol_in_the_rerankers_order(routed, box, standin, asked):
    r.set_routing(routed, symbol=r.ON)
    bundle, _, order = _ask(box, routed, QUESTIONS[asked])
    evidence = _evidence(bundle)
    assert evidence == _reranker_order(evidence, order), f"a question naming no symbol was routed: {evidence[:6]}"


# ---- route by record ----------------------------------------------------------------------------------------------

def test_route_by_record_puts_the_records_two_best_chunks_ahead_after_the_rerank(routed, box, standin):
    r.set_routing(routed, record=r.ON)
    bundle, _, order = _ask(box, routed, r.RECORD_QUESTION)
    assert bundle["facets"].get("closure", {}).get("available") is True, \
        f"premise: the record route answers: {bundle['facets']}"
    _ahead(_evidence(bundle), order, RECORD_AHEAD)
    _moved_named(bundle, RECORD_AHEAD)


@pytest.mark.parametrize("asked", ["plain", "symbol"])
def test_route_by_record_leaves_a_question_naming_no_record_in_the_rerankers_order(routed, box, standin, asked):
    r.set_routing(routed, record=r.ON)
    bundle, _, order = _ask(box, routed, QUESTIONS[asked])
    evidence = _evidence(bundle)
    assert evidence == _reranker_order(evidence, order), f"a question naming no record was routed: {evidence[:6]}"


# ---- both halves ----------------------------------------------------------------------------------------------------

def test_both_halves_on_a_question_naming_a_symbol_and_a_record_puts_both_ahead(routed, box, standin):
    r.set_routing(routed, symbol=r.ON, record=r.ON)
    bundle, _, order = _ask(box, routed, r.BOTH_QUESTION)
    ahead = _code_ahead(routed, standin, r.BOTH_QUESTION) | RECORD_AHEAD
    _ahead(_evidence(bundle), order, ahead)
    _moved_named(bundle, ahead)


def test_the_16_text_cap_holds_with_routing_on(routed, box, standin):
    r.set_routing(routed, symbol=r.ON, record=r.ON)
    _, requests, _ = _ask(box, routed, r.BOTH_QUESTION)
    sizes = [len(request) for request in requests]
    assert sum(sizes) > CAP, f"premise: the rerank pool holds more than {CAP} texts ({sum(sizes)})"
    assert all(size == CAP for size in sizes[:-1]) and sizes[-1] <= CAP, \
        f"with routing on, the rerank requests are not the pool cut into requests of {CAP} (DEC-1067 (f)): {sizes}"


# ---- an invalid setting --------------------------------------------------------------------------------------------

@pytest.mark.parametrize("value", [-1, "maybe", [2]], ids=["negative", "word", "list"])
@pytest.mark.parametrize("half", ["symbol", "record"])
def test_an_invalid_setting_is_config_invalid_naming_the_key(routed, box, standin, half, value):
    if half == "symbol":
        r.set_routing(routed, symbol=value)
    else:
        r.set_routing(routed, record=value)
    bundle, raised, _ = _ask(box, routed, r.BOTH_QUESTION)
    assert bundle is None and raised, f"an invalid {r.KEYS[half]} was taken: the retrieval answered"
    assert "CONFIG_INVALID" in (str(raised.get("code")) + raised["message"]), \
        f"the refusal is not CONFIG_INVALID: {raised['type']}: {raised['message']}"
    assert r.KEYS[half] in raised["message"], f"the refusal does not name the key {r.KEYS[half]}: {raised['message']}"

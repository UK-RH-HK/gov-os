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
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import w2_32_routing as r
import w2_32_support as s

CAP = 16
CODE_AHEAD = {(path, r.rank_of(r.CODE_TEXT[path])) for path in r.CODE[:2]}
RECORD_AHEAD = {(r.RECORD_REL, rank) for rank in sorted(r.RECORD_RANKS, reverse=True)[:2]}


@pytest.fixture
def routed(tmp_path, needs_vectors, box):
    project = r.plant(tmp_path / "routed")
    box.built(project)
    return project


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
    first_lines = [text.split("\n", 1) for text in pool]
    keyed = [(head[len("[path: "):-1], r.rank_of(text)) for (head, *_), text in zip(first_lines, pool)]
    order = [key for _, key in sorted(enumerate(keyed), key=lambda pair: (-pair[1][1], pair[0]))]
    return data["result"], requests, order


def _evidence(bundle):
    return [r.key_of(item["path"], item["text"]) for item in bundle["evidence"]]


def _reranker_order(evidence, order):
    """The evidence's chunks in the reranker's order."""
    present = set(evidence)
    return [key for key in order if key in present]


def _ahead(evidence, order, routed):
    """Fails unless the evidence starts with exactly ``routed`` and the rest keeps the reranker's order."""
    assert routed <= set(evidence), f"premise: the routed chunks are gathered: {sorted(routed - set(evidence))}"
    assert set(_reranker_order(evidence, order)[:len(routed)]) != routed, \
        "premise: the reranker alone does not put the routed chunks first (routing must be what does)"
    head, rest = evidence[:len(routed)], evidence[len(routed):]
    assert set(head) == routed, f"the routed chunks are not put ahead after the rerank: the first {len(routed)} are " \
                                f"{head}, not {sorted(routed)}"
    assert rest == [key for key in _reranker_order(evidence, order) if key not in routed], \
        "after the routed chunks, the rest is not in the reranker's order"


QUESTIONS = {"symbol": r.SYMBOL_QUESTION, "record": r.RECORD_QUESTION, "both": r.BOTH_QUESTION,
             "plain": r.PLAIN_QUESTION}


# ---- off (the default): today's order exactly ---------------------------------------------------------------------

@pytest.mark.parametrize("asked", sorted(QUESTIONS))
@pytest.mark.parametrize("settings", ["absent", "both-false"])
def test_with_both_halves_off_the_order_is_the_rerankers(routed, box, standin, settings, asked):
    if settings == "both-false":
        r.set_routing(routed, symbol=False, record=False)
    bundle, _, order = _ask(box, routed, QUESTIONS[asked])
    assert bundle is not None, f"the retrieval raised with routing off: {_}"
    evidence = _evidence(bundle)
    assert evidence == _reranker_order(evidence, order), \
        f"routing off ({settings}) changed the reranker's order: {evidence[:6]}"


def test_off_by_setting_gives_the_same_bundle_as_no_setting(routed, box, standin):
    absent, _, _ = _ask(box, routed, r.BOTH_QUESTION)
    r.set_routing(routed, symbol=False, record=False)
    off, _, _ = _ask(box, routed, r.BOTH_QUESTION)
    assert [(e["path"], e["start_line"], e["end_line"]) for e in off["evidence"]] == \
        [(e["path"], e["start_line"], e["end_line"]) for e in absent["evidence"]], "off differs from the default"


# ---- route by symbol ----------------------------------------------------------------------------------------------

def test_route_by_symbol_puts_the_code_routes_first_two_hits_ahead_after_the_rerank(routed, box, standin):
    r.set_routing(routed, symbol=True)
    bundle, _, order = _ask(box, routed, r.SYMBOL_QUESTION)
    assert bundle["facets"].get("code", {}).get("available") is True, f"premise: the code route answers: {bundle['facets']}"
    _ahead(_evidence(bundle), order, CODE_AHEAD)


@pytest.mark.parametrize("asked", ["plain", "record"])
def test_route_by_symbol_leaves_a_question_naming_no_symbol_in_the_rerankers_order(routed, box, standin, asked):
    r.set_routing(routed, symbol=True)
    bundle, _, order = _ask(box, routed, QUESTIONS[asked])
    evidence = _evidence(bundle)
    assert evidence == _reranker_order(evidence, order), f"a question naming no symbol was routed: {evidence[:6]}"


# ---- route by record ----------------------------------------------------------------------------------------------

def test_route_by_record_puts_the_records_two_best_chunks_ahead_after_the_rerank(routed, box, standin):
    r.set_routing(routed, record=True)
    bundle, _, order = _ask(box, routed, r.RECORD_QUESTION)
    assert bundle["facets"].get("closure", {}).get("available") is True, \
        f"premise: the record route answers: {bundle['facets']}"
    _ahead(_evidence(bundle), order, RECORD_AHEAD)


@pytest.mark.parametrize("asked", ["plain", "symbol"])
def test_route_by_record_leaves_a_question_naming_no_record_in_the_rerankers_order(routed, box, standin, asked):
    r.set_routing(routed, record=True)
    bundle, _, order = _ask(box, routed, QUESTIONS[asked])
    evidence = _evidence(bundle)
    assert evidence == _reranker_order(evidence, order), f"a question naming no record was routed: {evidence[:6]}"


# ---- both halves ----------------------------------------------------------------------------------------------------

def test_both_halves_on_a_question_naming_a_symbol_and_a_record_puts_both_ahead(routed, box, standin):
    r.set_routing(routed, symbol=True, record=True)
    bundle, _, order = _ask(box, routed, r.BOTH_QUESTION)
    _ahead(_evidence(bundle), order, CODE_AHEAD | RECORD_AHEAD)


def test_the_16_text_cap_holds_with_routing_on(routed, box, standin):
    r.set_routing(routed, symbol=True, record=True)
    _, requests, _ = _ask(box, routed, r.BOTH_QUESTION)
    sizes = [len(request) for request in requests]
    assert sum(sizes) > CAP, f"premise: the rerank pool holds more than {CAP} texts ({sum(sizes)})"
    assert all(size == CAP for size in sizes[:-1]) and sizes[-1] <= CAP, \
        f"with routing on, the rerank requests are not the pool cut into requests of {CAP} (DEC-1067 (f)): {sizes}"


# ---- an invalid setting --------------------------------------------------------------------------------------------

@pytest.mark.parametrize("half", ["symbol", "record"])
def test_an_invalid_setting_is_config_invalid_naming_the_key(routed, box, standin, half):
    r.set_routing(routed, raw=f"{r.KEYS[half]}: maybe\n")
    bundle, raised, _ = _ask(box, routed, r.BOTH_QUESTION)
    assert bundle is None and raised, f"an invalid {r.KEYS[half]} was taken: the retrieval answered"
    assert "CONFIG_INVALID" in (str(raised.get("code")) + raised["message"]), \
        f"the refusal is not CONFIG_INVALID: {raised['type']}: {raised['message']}"
    assert r.KEYS[half] in raised["message"], f"the refusal does not name the key {r.KEYS[half]}: {raised['message']}"

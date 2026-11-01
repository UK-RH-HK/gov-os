"""KPI success 3 and failure 3: a route that cannot answer is named in the bundle with why, never silently ok, and
never a failure of the whole answer: the other routes' evidence is still returned."""

from __future__ import annotations

import json

import pytest

import w2_92_support as support

# A question whose symbol is answered by today's lexical route as well, so a missing code index leaves evidence
# from another route. Today's lexical evidence for it is the planted files whose text holds the word (DEC-1006,
# P-W2-92-2): app/leaf.py and app/middle.py, not app/top.py, which only calls w92_mid. The base 7ca16b19df3f (no new
# routes) answered exactly these on the planted store: app/leaf.py 1-2 and app/middle.py 1-9, 4-5, 8-9.
SYMBOL_ONLY = support.LEAF
LEXICAL_PATHS = {rel for rel, text in support.corpus().items() if SYMBOL_ONLY in text}

CODE_CASES = [
    ("never indexed", "nocode", support.RECORDING),
    ("tool cannot read it", "full", support.BROKEN),
    ("tool not on PATH", "full", support.ABSENT),
]


def _states(bundle, words):
    return support.route_entries(bundle, words)


def _check_named_unavailable(bundle, words, what):
    entries = _states(bundle, words)
    assert entries, (
        f"{what}: the bundle names no state of that route; outside its evidence it holds "
        f"{json.dumps(support.outside_evidence(bundle))[:1500]}")
    said = [entry for entry in entries if support.unavailable(entry[1])]
    assert said, f"{what}: the route is not said to be unavailable, with a reason: {entries}"
    fine = [entry for entry in entries if support.reported_ok(entry[1])]
    assert not fine, f"{what}: the route is reported ok: {fine}"
    assert bundle.get("stopping_reason") not in ("SATURATED", "CLOSURE_COMPLETE"), \
        f"{what}: the bundle's stopping reason {bundle.get('stopping_reason')!r} says nothing was missing"


@pytest.mark.parametrize("label, kind, tool", CODE_CASES, ids=[case[0] for case in CODE_CASES])
def test_f1_a_code_index_that_cannot_answer_is_named_and_the_rest_is_returned(asked, label, kind, tool):
    bundle, _ = asked(kind, SYMBOL_ONLY, tool=tool)
    _check_named_unavailable(bundle, support.CODE_ROUTE_WORDS, f"code index: {label}")
    returned = set(support.paths(bundle)) & LEXICAL_PATHS
    assert returned == LEXICAL_PATHS, (
        f"code index: {label}: the lexical route's evidence for {SYMBOL_ONLY!r} ({sorted(LEXICAL_PATHS)}) is not "
        f"all returned: {support.paths(bundle)}")


def test_f2_the_command_answers_ok_when_the_code_index_is_missing(api, planted):
    done, _ = api.command(planted("nocode"), SYMBOL_ONLY)
    assert done.returncode == 0, f"gov retrieve failed (exit code {done.returncode}):\n{done.stdout}\n{done.stderr}"
    envelope = json.loads(done.stdout)
    assert envelope.get("ok") is True, f"the whole answer failed: {envelope.get('error')}"
    _check_named_unavailable(envelope["result"], support.CODE_ROUTE_WORDS, "code index missing, through the command")


def test_f3_a_missing_record_store_is_named_and_the_code_routes_evidence_is_returned(api, planted):
    """The lexical index and the code index are built, the record graph is not (``gov.store.load`` never ran). A
    question naming a decision and a symbol: the record route is named unavailable, the callers still come."""
    question = f"who calls {support.LEAF} under {support.NAMED_DEC}"
    record, _ = api.outcome(planted("nostore"), question)
    assert record["error"] is None, f"the whole answer failed for a missing record store: {record['error']}"
    bundle = record["value"]
    _check_named_unavailable(bundle, support.RECORD_ROUTE_WORDS, "record store missing")
    missing = [name for name in support.CALLERS[support.LEAF] if not support.covers(bundle, *support.SPANS[name])]
    assert not missing, f"record store missing: the code route's callers {missing} are not returned: " \
                        f"{support.items(bundle)}"


def test_f4_a_question_naming_no_symbol_does_not_report_the_code_route_ok_or_fail(asked):
    """With no code index, a question that names no symbol still gets an answer, and nothing calls the code route
    fine."""
    bundle, _ = asked("nocode", support.PLAIN_PHRASE)
    fine = [entry for entry in support.route_entries(bundle, support.CODE_ROUTE_WORDS)
            if support.reported_ok(entry[1])]
    assert not fine, f"the code route is reported ok in a project with no code index: {fine}"
    assert len(bundle["evidence"]) == len(support.PLAIN_PAGES), support.items(bundle)

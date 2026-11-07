"""S5: the findings. A ticket without needs: is planned as needing only its own writes and flagged NEEDS_UNDECLARED;
a deps that disagrees with depends_on is DEPS_DISAGREE; a waits_on id that names nothing is UNKNOWN_WAIT
(DEC-1088 (3)). A plan with findings exits 1 (S1)."""

from __future__ import annotations

import pytest

import w2_136_support as support
from w2_136_support import T

DONE = T("PLN-e009", "W2-509", status="closed", writes=("src/done/**",))


def _flagged(store, code):
    """The tickets the text and the JSON name under ``code``; both runs exit 1."""
    run = support.run(store.root, "--open")
    assert run.code == 1, run
    plan = support.text_plan(run.out, store, run)
    in_text = {tid for tid in store.tickets for line in support.lines_with(plan, code) if store.mentions(line, tid)}
    jrun = support.run(store.root, "--open", "--json")
    assert jrun.code == 1, jrun
    result = support.envelope(jrun)["result"]
    in_json = {tid for tid in store.tickets for e in support.entries(result, code)
               if support.json_mentions(store, e.get("ticket", e), tid)}
    return plan, in_text, in_json, run


def test_s5_a_ticket_without_needs_is_planned_on_its_own_writes_and_flagged_needs_undeclared(planted):
    undeclared = T("PLN-e001", "W2-501", writes=("src/a/**",), needs=None)
    declared = T("PLN-e002", "W2-502", writes=("src/b/**",), needs=())  # an empty list is a declared none
    writer = T("PLN-e003", "W2-503", status="in_progress", writes=("src/c/**",))
    store = planted((undeclared, declared, writer))
    plan, in_text, in_json, run = _flagged(store, "NEEDS_UNDECLARED")
    assert in_text == {"PLN-e001"} and in_json == {"PLN-e001"}, run
    assert plan.batches == [{"PLN-e001", "PLN-e002", "PLN-e003"}] and plan.waits == [], run


def test_s5_a_deps_that_disagrees_with_depends_on_is_deps_disagree(planted):
    a = T("PLN-e001", "W2-501", writes=("src/a/**",))
    disagree = T("PLN-e002", "W2-502", writes=("src/b/**",), depends_on=(), deps=("PLN-e001",))
    agree = T("PLN-e003", "W2-503", writes=("src/c/**",), depends_on=("PLN-e009",), deps=("PLN-e009",))
    store = planted((a, disagree, agree, DONE))
    plan, in_text, in_json, run = _flagged(store, "DEPS_DISAGREE")
    assert "PLN-e002" in in_text and "PLN-e002" in in_json, run
    assert "PLN-e003" not in in_text | in_json, run


def test_s5_a_waits_on_id_that_names_nothing_is_unknown_wait(planted):
    unknown = T("PLN-e001", "W2-501", writes=("src/a/**",), waits_on=("PLN-zz99",))
    known = T("PLN-e002", "W2-502", writes=("src/b/**",), waits_on=("PLN-e009",))
    store = planted((unknown, known, DONE))
    plan, in_text, in_json, run = _flagged(store, "UNKNOWN_WAIT")
    assert "PLN-e001" in in_text and "PLN-e001" in in_json, run
    assert "PLN-e002" not in in_text | in_json, run
    assert any("PLN-zz99" in line for line in support.lines_with(plan, "UNKNOWN_WAIT")), run


@pytest.mark.parametrize("form", ["text", "json"])
def test_s5_a_store_with_none_of_the_findings_names_none(planted, form):
    store = planted((T("PLN-e001", "W2-501", writes=("src/a/**",), waits_on=("PLN-e009",)),
                     T("PLN-e002", "W2-502", writes=("src/b/**",), depends_on=("PLN-e009",)), DONE))
    run = support.run(store.root, "--open", *(["--json"] if form == "json" else []))
    assert run.code == 0, run
    assert run.out.startswith(("gov plan:", "{")), run
    for code in ("NEEDS_UNDECLARED", "DEPS_DISAGREE", "UNKNOWN_WAIT"):
        assert code not in run.out, run

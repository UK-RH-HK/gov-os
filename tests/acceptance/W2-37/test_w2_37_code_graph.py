"""KPI 1, the code graph, and the S0b2 glue G-16 (id mapping): ``gov impact`` joins the record and code graphs by id.

Reading R5 (G-16): a record's typed edge whose target is no record but a symbol of the code index joins the two
graphs (DEC-391: ``gov closure`` follows no record-to-symbol edge, and leaves it ``UNRESOLVED``). From the symbol,
its callers and callees are followed as ``gov closure`` follows them. Back the other way, a symbol's change reaches
the records that name it. A mention in a record's prose is no edge (DEC-391: no text scan).

Reading R2 (kinds): a symbol defined in a test file (``tests/``) is listed under ``tests``; any other symbol under
``code``. Each carries ``graph: code``.

All cases run the real code tool on a temporary repository (``local_only``); they cannot run in a worker's
sandbox (P-W2-38).
"""

from __future__ import annotations

import pytest

import w2_37_support as support

pytestmark = pytest.mark.local_only


def test_a_decision_change_lists_the_symbol_it_names_from_the_code_graph(asked_code):
    found = asked_code(support.CHANGED)
    assert support.where(found, support.SYMBOL, symbol=True) == [("code", "code")], \
        f"{support.SYMBOL}, which DEC-001 constrains, is not listed once under `code` from the code graph: " \
        f"{support.where(found, support.SYMBOL, symbol=True)}"


def test_the_record_side_is_listed_beside_the_code_side(asked_code):
    found = asked_code(support.CHANGED)
    for record_id, kind in ((support.SPEC, "specifications"), (support.OTHER_DECISION, "decisions"),
                            (support.TICKET, "tickets"), (support.TEST_RECORD, "tests")):
        assert support.where(found, record_id) == [(kind, "record")], f"{record_id}: {support.where(found, record_id)}"


def test_the_callers_and_callees_of_the_named_symbol_are_listed_within_the_depth(asked_code):
    """w37_apply calls w37_helper; w37_entry and the test test_w37_apply call w37_apply (two hops from DEC-001)."""
    found = asked_code(support.CHANGED)
    expected = ((support.HELPER, "code"), (support.ENTRY, "code"), (support.TEST_FUNCTION, "tests"))
    for name, kind in expected:
        if found["depth"] >= 2:
            assert support.where(found, name, symbol=True) == [(kind, "code")], \
                f"{name} is not listed once under `{kind}` from the code graph: " \
                f"{support.where(found, name, symbol=True)}"
        else:
            assert support.in_gaps(found, name, symbol=True) or support.in_gaps(found, support.SYMBOL, symbol=True), \
                f"depth {found['depth']} does not reach {name}, and no gap says so"


def test_with_both_graphs_read_the_report_says_so(asked_code):
    found = asked_code(support.CHANGED)
    assert all(found["graphs"][g] == support.GRAPH_OK for g in support.GRAPHS), f"`graphs`: {found['graphs']}"
    if not found["gaps"]:
        assert found["complete"] is True, "both graphs read, no gap, and the report does not read as complete"


def test_a_symbol_change_reaches_the_records_that_name_its_callers(asked_code):
    """w37_helper is called by w37_apply and w37_orphan; DEC-001 names w37_apply, two hops from w37_helper."""
    found = asked_code(support.HELPER)
    for name in (support.SYMBOL, support.ORPHAN):
        assert support.where(found, name, symbol=True) == [("code", "code")], \
            f"{name}, a caller of {support.HELPER}: {support.where(found, name, symbol=True)}"
    if found["depth"] >= 2:
        assert support.where(found, support.CHANGED) == [("decisions", "record")], \
            f"{support.CHANGED} names {support.SYMBOL}, a caller of {support.HELPER}, and is not listed: " \
            f"{support.where(found, support.CHANGED)}"
        assert support.where(found, support.TEST_FUNCTION, symbol=True) == [("tests", "code")]


def test_a_mention_in_prose_is_no_link(asked_code):
    """DEC-060's body mentions w37_orphan; no edge names it."""
    found = asked_code(support.ORPHAN)
    assert not support.where(found, support.PROSE), f"{support.PROSE} is listed for a mention in its prose"


def test_every_item_is_traced_to_the_graph_it_came_from(asked_code):
    found = asked_code(support.CHANGED)
    records = {support.SPEC, support.CAP, support.OTHER_DECISION, support.TICKET, support.TEST_RECORD,
               support.FAR_SPEC}
    symbols = (support.SYMBOL, support.HELPER, support.ENTRY, support.TEST_FUNCTION)
    for kind in support.KINDS:
        for item in found["affected"][kind]:
            if item["id"] in records:
                assert item["graph"] == "record", f"{item} came from the record graph"
            if any(support.names_symbol(item["id"], name) for name in symbols):
                assert item["graph"] == "code", f"{item} came from the code graph"

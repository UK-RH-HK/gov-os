"""W2-124 S4: the close's gate on a rebuild result: the rule of the merge queue's ``rebuild_semantic_check.py``."""
from __future__ import annotations

import pytest

from gov.cli.errors import GovError
from gov.close import rebuild_gate
from gov.close.rebuild_gate import check, semantic_failure


def _stores(**semantic):
    return {"stores": {"lexical": {"status": "recreated"}, "semantic": semantic}}


CASES = {
    "recreated": (_stores(status="recreated"), None),
    "asked and unavailable": (_stores(status="not_recreated", reason="endpoint down"),
                              "semantic store not_recreated: endpoint down"),
    "asked, no reason": (_stores(status="not_recreated"), "semantic store not_recreated: no reason given"),
    "not asked": (_stores(status="not_recreated", requested=False, reason="--no-embeddings was given"), None),
    "requested true": (_stores(status="not_recreated", requested=True, reason="down"),
                       "semantic store not_recreated: down"),
    "no semantic entry": ({"stores": {"lexical": {"status": "recreated"}}}, "semantic store absent: no reason given"),
    "no stores": ({}, "semantic store absent: no reason given"),
}


@pytest.mark.parametrize("name", CASES)
def test_the_rule_on_a_result_and_on_its_envelope(name):
    result, expected = CASES[name]
    assert semantic_failure(result) == expected
    assert semantic_failure({"ok": True, "command": "rebuild", "result": result}) == expected


def test_a_result_that_is_no_dict_of_stores_is_a_failure_not_a_pass():
    assert semantic_failure({"result": None}) == "semantic store absent: no reason given"
    assert semantic_failure({"stores": {"semantic": "recreated"}}) == "semantic store absent: no reason given"


def test_check_passes_where_the_rule_finds_nothing():
    assert check(CASES["recreated"][0]) is None
    assert check(CASES["not asked"][0]) is None


def test_check_raises_rebuild_failed_naming_the_store_and_the_reason():
    result = _stores(status="not_recreated", reason="endpoint down")
    with pytest.raises(GovError) as raised:
        check(result)
    error = raised.value
    assert (error.code, error.exit_code) == ("REBUILD_FAILED", 1)
    assert "store: semantic" in error.message and "endpoint down" in error.message
    assert error.details == {"store": "semantic", "reason": "endpoint down", "stores": result["stores"]}


def test_check_on_an_envelope_raises_with_the_envelopes_stores():
    stores = _stores(status="not_recreated", reason="down")["stores"]
    with pytest.raises(GovError) as raised:
        check({"ok": True, "result": {"stores": stores}})
    assert raised.value.details["stores"] == stores and raised.value.details["store"] == "semantic"


def test_the_gate_is_the_one_rebuild_calls():
    from gov.rebuild import command

    assert command.check is rebuild_gate.check

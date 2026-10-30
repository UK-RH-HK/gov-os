"""W2-51 KPI success line 2: the two-way check of exit criterion 7.

"Every Contract item in Wave 2, and every lite item of Contract v4.2, is delivered by a Wave 2 ticket and cited by an
acceptance test; every Contract id a Wave 2 ticket cites exists in the Contract [DEC-744, DEC-723]."
"""

from __future__ import annotations

import pytest

from w2_51_support import (CITED, DELIVERED, IDS_EXIST, assert_fails_naming, assert_passes, build_and_run, plan_v41,
                           plan_v42)

PLANS = {"contract-4.1": plan_v41, "contract-4.2": plan_v42}


def _drop_closes(plan, w2, cid):
    """Take ``cid`` out of ticket ``w2``'s closes list and out of its WBS row's Closes column."""
    fm = plan.ticket(w2)
    fm["closes"] = [c for c in fm["closes"] if cid not in c] or ["DEC-900"]
    plan.wbs_rows = [(i, b, t, ("DEC-900" if i == w2 and cid in c else c)) for i, b, t, c in plan.wbs_rows]


@pytest.mark.parametrize("version", sorted(PLANS))
def test_the_two_way_check_passes_on_a_consistent_tree(tmp_path, version):
    res = build_and_run(tmp_path, PLANS[version]())
    assert_passes(res, DELIVERED, CITED, IDS_EXIST)


def test_a_wave_2_item_no_wave_2_ticket_delivers_fails_naming_it(tmp_path):
    plan = plan_v41()
    _drop_closes(plan, "W2-02", "CAP-91.b")
    res = build_and_run(tmp_path, plan)
    assert_fails_naming(res, DELIVERED, "CAP-91.b")


def test_a_wave_2_item_delivered_only_by_a_wave_1_ticket_fails_naming_it(tmp_path):
    plan = plan_v41()
    _drop_closes(plan, "W2-02", "CAP-91.b")
    plan.tickets["DAEO-w107.md"]["closes"].append("CAP-91.b")
    res = build_and_run(tmp_path, plan)
    assert_fails_naming(res, DELIVERED, "CAP-91.b")


def test_a_lite_item_of_contract_4_2_no_wave_2_ticket_delivers_fails_naming_it(tmp_path):
    plan = plan_v42()
    _drop_closes(plan, "W2-04", "CAP-93.b")
    res = build_and_run(tmp_path, plan)
    assert_fails_naming(res, DELIVERED, "CAP-93.b")


def test_a_wave_2_item_no_acceptance_test_cites_fails_naming_it(tmp_path):
    """Its only citations left are outside tests/acceptance/ (a unit test, a plan file): it is not cited."""
    plan = plan_v41()
    plan.tests["tests/acceptance/W2-02/README.md"] = "# W2-02\n\nNo Contract id here.\n"
    plan.tests["tests/unit/plan/test_nothing.py"] = "# [CAP-91.b] cited by a unit test only\n"
    res = build_and_run(tmp_path, plan)
    assert_fails_naming(res, CITED, "CAP-91.b")


def test_a_lite_item_of_contract_4_2_no_acceptance_test_cites_fails_naming_it(tmp_path):
    plan = plan_v42()
    plan.tests["tests/acceptance/W2-04/test_w2_04_release.py"] = "def test_manifest():\n    assert True\n"
    res = build_and_run(tmp_path, plan)
    assert_fails_naming(res, CITED, "CAP-93.b")


@pytest.mark.parametrize("unknown", ["CAP-99.z", "CAP-98"])
def test_a_contract_id_a_wave_2_ticket_cites_that_the_contract_lacks_fails_naming_it(tmp_path, unknown):
    """A covers id or a capability id, cited in a Wave 2 ticket's KPI and sources, absent from the Contract."""
    plan = plan_v41()
    fm = plan.ticket("W2-01")
    fm["sources"].append(unknown)
    fm["kpis"]["success"].append(f"It also does this [{unknown}].")
    res = build_and_run(tmp_path, plan)
    assert_fails_naming(res, IDS_EXIST, unknown)


def test_an_id_only_contract_4_2_holds_is_unknown_on_a_4_1_tree(tmp_path):
    """The validator reads the tree's own Contract: the split item of 4.2, cited on a 4.1 tree, does not exist."""
    plan = plan_v41()
    plan.ticket("W2-05")["sources"].append("CAP-93.d")
    res = build_and_run(tmp_path, plan)
    assert_fails_naming(res, IDS_EXIST, "CAP-93.d")

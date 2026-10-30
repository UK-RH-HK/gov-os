"""W2-51 KPI success line 3: W2-49's failure KPI.

"A Contract item moved to Wave 2 with no CIT-P line, or a CIT-P line with no change, fails it (W2-49's failure KPI)
[DEC-741]."
"""

from __future__ import annotations

import pytest

from w2_51_support import (CITP_APPLIED, CITP_MOVED, CIT_P_NAME, LITE_ITEM, REST_ITEM, assert_fails_naming,
                           assert_passes, build_and_run, cit_p_text, plan_v41, plan_v42)


def test_a_4_1_tree_with_no_cit_p_passes_both_checks(tmp_path):
    """Nothing moved beyond the plan's Wave 2 items, and no CIT-P line: the validator does not need v4.2 merged."""
    res = build_and_run(tmp_path, plan_v41())
    assert_passes(res, CITP_MOVED, CITP_APPLIED)
    assert res.returncode == 0, res


def test_a_4_2_tree_whose_moved_item_has_its_cit_p_line_passes_both_checks(tmp_path):
    res = build_and_run(tmp_path, plan_v42())
    assert_passes(res, CITP_MOVED, CITP_APPLIED)
    assert res.returncode == 0, res


def test_an_item_moved_to_wave_2_with_no_cit_p_line_fails_naming_it(tmp_path):
    """A second Wave 3 item set to W2, lite, delivered and cited, but named by no CIT-P line."""
    plan = plan_v42()
    plan.cover("CAP-94.a").update({"item": "Adoption verdict, lite: three verdicts", "source": "Contract v3 Z1; DEC-900",
                                   "wave": "W2"})
    plan.ticket("W2-04")["closes"].append("CAP-94.a")
    plan.tests["tests/acceptance/W2-04/README.md"] = "# W2-04\n\n| test_verdict | CAP-94.a |\n"
    res = build_and_run(tmp_path, plan)
    assert_fails_naming(res, CITP_MOVED, "CAP-94.a")


def test_an_item_moved_to_wave_2_with_no_cit_p_file_at_all_fails_naming_it(tmp_path):
    plan = plan_v42()
    plan.cit_p.clear()
    res = build_and_run(tmp_path, plan)
    assert_fails_naming(res, CITP_MOVED, "CAP-93.b")


def _line_wave_not_applied():
    """The CIT-P proposes an item into Wave 2; the Contract keeps it in Wave 3."""
    plan = plan_v42()
    plan.cit_p[CIT_P_NAME] = cit_p_text([("CAP-93.b", "W2", LITE_ITEM), ("CAP-93.c", None, ""),
                                         ("CAP-93.d", "W3", REST_ITEM), ("CAP-95.a", "W2", "Audit gate, lite")])
    return plan, "CAP-95.a"


def _line_new_item_not_added():
    """The CIT-P proposes a new split item; the Contract does not hold it."""
    plan = plan_v42()
    covers = plan.cap("CAP-93")["covers"]
    covers[:] = [cv for cv in covers if cv["id"] != "CAP-93.d"]
    plan.ticket("W2-05")["sources"].remove("CAP-93.d")
    return plan, "CAP-93.d"


def _proposal_on_a_4_1_tree():
    """W2-49's state before its apply round: the CIT-P is in the tree, the Contract is still 4.1."""
    plan = plan_v41()
    plan.cit_p[CIT_P_NAME] = plan_v42().cit_p[CIT_P_NAME]
    return plan, "CAP-93.b"


@pytest.mark.parametrize("make", [_line_wave_not_applied, _line_new_item_not_added, _proposal_on_a_4_1_tree],
                         ids=["wave-not-applied", "new-item-not-added", "proposal-on-a-4.1-tree"])
def test_a_cit_p_line_with_no_change_in_the_contract_fails_naming_it(tmp_path, make):
    plan, cid = make()
    res = build_and_run(tmp_path, plan)
    assert_fails_naming(res, CITP_APPLIED, cid)

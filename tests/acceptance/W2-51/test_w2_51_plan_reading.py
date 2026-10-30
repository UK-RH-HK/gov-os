"""W2-51 KPI success line 1: it reads the Wave 2 plan; each check prints pass or fail with a named reason.

"It reads the Wave 2 plan: the WBS ticket table, the Wave 2 tickets in .tickets/ (by wbs_id, or external-ref when it
has none; a letter suffix such as W2-15a is a W2 id), the list and the triage. Each check prints pass or fail with a
named reason [DEC-744, DEC-730]."
"""

from __future__ import annotations

import pytest

from w2_51_support import (CHECKS, DELIVERED, IDS_EXIST, STATUS_LINE, WAVE2_TICKETS, _ticket, assert_fails_naming,
                           assert_passes, build_and_run, plan_v41, plan_v42)

PLANS = {"contract-4.1": plan_v41, "contract-4.2": plan_v42}


@pytest.mark.parametrize("version", sorted(PLANS))
def test_every_check_prints_one_line_with_pass_and_a_named_reason(tmp_path, version):
    """A consistent tree: each of the eight named checks prints exactly one PASS line with a reason; exit 0."""
    res = build_and_run(tmp_path, PLANS[version]())
    assert_passes(res, *CHECKS)
    bad = [l for l in res.status_lines if not STATUS_LINE.match(l)]
    assert not bad, f"status lines not in the form '<STATUS> <name> — <reason>': {bad}\n{res!r}"
    assert not res.fail_lines(), res
    assert res.returncode == 0, f"a run with no failing check exits 0\n{res!r}"


def test_a_ticket_with_only_external_ref_is_read_as_a_wave_2_ticket(tmp_path):
    """W2-15a's form (DEC-730): the W2 id with a letter suffix, in external-ref only, is a Wave 2 ticket."""
    plan = plan_v41()
    fm = plan.ticket("W2-03a")
    assert "wbs_id" not in fm and fm["external-ref"] == "W2-03a"  # the fixture's own form
    res = build_and_run(tmp_path, plan)
    # It matches the WBS row **W2-03a**, and it delivers its Contract item.
    assert_passes(res, WAVE2_TICKETS, DELIVERED)


def test_a_wbs_row_whose_ticket_is_missing_fails_naming_it(tmp_path):
    """The external-ref-only ticket removed: its WBS row has no ticket, and its item is no longer delivered."""
    plan = plan_v41()
    del plan.tickets[plan.ticket_file("W2-03a")]
    res = build_and_run(tmp_path, plan)
    assert_fails_naming(res, WAVE2_TICKETS, "W2-03a")
    assert_fails_naming(res, DELIVERED, "CAP-92.b")


def test_a_wbs_row_with_no_ticket_file_fails_naming_it(tmp_path):
    plan = plan_v41()
    plan.wbs_rows.append(("W2-06", False, "A ticket nobody created", "AR-2"))
    res = build_and_run(tmp_path, plan)
    assert_fails_naming(res, WAVE2_TICKETS, "W2-06")


@pytest.mark.parametrize("field, w2", [("wbs_id", "W2-06"), ("external-ref", "W2-06b")])
def test_a_wave_2_ticket_missing_from_the_wbs_table_fails_naming_it(tmp_path, field, w2):
    """A Wave 2 ticket file, found by wbs_id or (with none) by external-ref, that the WBS table does not list."""
    plan = plan_v41()
    plan.tickets["DAEO-t006.md"] = _ticket("DAEO-t006", w2, "A ticket the plan forgot", wbs=(field == "wbs_id"))
    res = build_and_run(tmp_path, plan)
    assert_fails_naming(res, WAVE2_TICKETS, w2)


@pytest.mark.parametrize("bad_id", ["W2-06ab", "W2-06A", "W2-6"])
def test_a_malformed_id_is_not_taken_as_a_wave_2_ticket(tmp_path, bad_id):
    """DEC-730: one lower-case letter suffix is a W2 id; W2-15ab, W2-15A, W2-1 are not.

    A ticket carrying a malformed id cites a Contract id that does not exist: since it is not a Wave 2 ticket, the
    check of the ids Wave 2 tickets cite still passes.
    """
    plan = plan_v41()
    plan.tickets["DAEO-t006.md"] = _ticket("DAEO-t006", bad_id, "A ticket with a malformed id",
                                           kpi_ids=["CAP-99.y"], sources=["CAP-99.y"])
    res = build_and_run(tmp_path, plan)
    assert_passes(res, IDS_EXIST)


@pytest.mark.parametrize("bad_id", ["W2-03ab", "W2-03A", "W2-3"])
def test_an_item_delivered_only_by_a_ticket_with_a_malformed_id_is_not_delivered(tmp_path, bad_id):
    """The only ticket closing a Wave 2 item carries a malformed id: no Wave 2 ticket delivers the item."""
    plan = plan_v41()
    fm = plan.ticket("W2-03a")
    fm["external-ref"] = bad_id
    res = build_and_run(tmp_path, plan)
    assert_fails_naming(res, DELIVERED, "CAP-92.b")

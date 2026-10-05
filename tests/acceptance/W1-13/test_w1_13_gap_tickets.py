"""W1-13 -- KPI success 4 [CAP-30.b].

"Lists every required open row with its linked gap ticket id, or UNLINKED (DEC-089)."

Settled by the sources: the row's ``gap_ticket`` field (DEC-305) and the KPI's own word ``UNLINKED``. Whether the id
names a ticket that exists is not tested here: ``gov check`` fails an unlinked row (W1-26's KPI line).
"""

from __future__ import annotations

import pytest

import w1_13_support as support

GAP_A, GAP_B = "TST-g001", "TST-g002"


def test_a_required_open_row_is_listed_with_its_gap_ticket(project, gov, interface):
    rows = support.edit(support.complete_rows(), 7, state="MISSING", evidence=[], gap_ticket=GAP_A)
    project.specification(rows)
    report = support.held(gov(*support.select()), interface)
    assert support.gap_tickets(report) == {7: GAP_A}


@pytest.mark.parametrize("value", [None, "", "   "], ids=["null", "empty", "blank"])
def test_a_required_open_row_with_no_gap_ticket_is_unlinked(project, gov, interface, value):
    rows = support.edit(support.complete_rows(), 7, state="MISSING", evidence=[], gap_ticket=value)
    project.specification(rows)
    report = support.held(gov(*support.select()), interface)
    assert support.gap_tickets(report) == {7: support.UNLINKED}


def test_a_row_whose_gap_ticket_key_is_absent_is_unlinked(project, gov, interface):
    rows = support.edit(support.complete_rows(), 7, state="MISSING", evidence=[])
    for row in rows:
        if row["n"] == 7:
            del row["gap_ticket"]
    project.specification(rows)
    report = support.held(gov(*support.select()), interface)
    assert support.gap_tickets(report) == {7: support.UNLINKED}


def test_every_required_open_row_is_listed_linked_or_not(project, gov, interface):
    """A mixed record: three states, two gap tickets, two rows without one. None is left out."""
    rows = support.complete_rows()
    support.edit(rows, 4, state="MISSING", evidence=[], gap_ticket=GAP_A)
    support.edit(rows, 7, state="PROVISIONAL", evidence=[], reason="rests on DP-9", gap_ticket=GAP_B)
    support.edit(rows, 20, state="BLOCKED", evidence=[], reason="waits on TST-g001", gap_ticket=None)
    support.edit(rows, 26, state="MISSING", evidence=[], gap_ticket=None)
    project.specification(rows)
    report = support.held(gov(*support.select()), interface)
    assert support.gap_tickets(report) == {4: GAP_A, 7: GAP_B, 20: support.UNLINKED, 26: support.UNLINKED}


def test_a_fresh_full_record_lists_all_26_rows_unlinked(project, gov, interface):
    project.specification(support.fresh_rows())
    report = support.held(gov(*support.select()), interface)
    assert support.gap_tickets(report) == {number: support.UNLINKED for number in support.row_keys()}


def test_rows_that_are_satisfied_or_not_required_are_not_listed(project, gov, interface):
    """LITE: row 3 is open and linked but not required, row 1 is satisfied and still carries an old gap ticket."""
    rows = support.complete_rows("LITE")
    support.edit(rows, 3, gap_ticket=GAP_A)
    support.edit(rows, 1, gap_ticket=GAP_B)
    support.edit(rows, 5, state="MISSING", evidence=[], gap_ticket=None)
    project.specification(rows, profile="LITE")
    report = support.held(gov(*support.select()), interface)
    assert support.gap_tickets(report) == {5: support.UNLINKED}

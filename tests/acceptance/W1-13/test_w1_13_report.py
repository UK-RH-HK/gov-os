"""W1-13 -- KPI success 1, first half [CAP-30.a, CAP-53.a], and failure 1.

"Reports every row open for the profile (FULL for spines)", and "a spec with a required MISSING row is reported
closed" must never happen.

Settled by the sources: DEC-085 and ``docs/contract/readiness-dimensions.yaml`` give what each profile requires
(LITE the ten mandatory rows, STANDARD those plus the rows of each declared capability type, FULL all 26, a spine
always FULL), which states satisfy a row (PRESENT, N/A_WITH_REASON) and that a row a profile does not require may
stay MISSING. Where the profile, the spine mark and the capability types are declared is package DP-3; the report's
keys and the exit code are DP-4.
"""

from __future__ import annotations

import pytest

import w1_13_support as support

A = "TST-a001"

PROFILES = [
    pytest.param("LITE", False, (), id="LITE"),
    pytest.param("STANDARD", False, ("backend",), id="STANDARD-backend"),
    pytest.param("STANDARD", False, ("ux", "frontend"), id="STANDARD-ux-frontend"),
    pytest.param("FULL", False, (), id="FULL"),
    pytest.param("LITE", True, (), id="spine-opened-at-LITE"),
]


# ---- every row open for the profile

@pytest.mark.parametrize("profile, spine, types", PROFILES)
def test_a_fresh_record_has_every_row_its_profile_requires_open(project, gov, interface, profile, spine, types):
    """W1-12's template, unchanged: the open rows are exactly the rows the profile requires."""
    project.specification(support.fresh_rows(), profile=profile, spine=spine, capability_types=types)
    report = support.held(gov(*support.select()), interface)
    assert support.open_numbers(report) == support.required(profile, spine, types)


@pytest.mark.parametrize("profile, spine, types", PROFILES)
def test_a_record_with_every_required_row_satisfied_passes(project, gov, interface, profile, spine, types):
    """The rows the profile does not require stay MISSING and hold nothing (DEC-085)."""
    project.specification(support.complete_rows(profile, spine, types), profile=profile, spine=spine,
                          capability_types=types)
    support.passed(gov(*support.select()), interface)


def test_the_report_names_the_specification_and_its_profile(project, gov, interface):
    project.specification(support.complete_rows("STANDARD", capability_types=("backend",)), profile="STANDARD",
                          capability_types=("backend",))
    report = support.passed(gov(*support.select()), interface)
    assert report[support.KEY_SPECIFICATION] == support.SPEC
    assert report[support.KEY_REPORT_PROFILE] == "STANDARD"


def test_a_spine_is_judged_and_reported_at_full(project, gov, interface):
    """DEC-085: a spine closes at FULL, whatever the profile of the change that opens it."""
    project.specification(support.complete_rows("LITE"), profile="LITE", spine=True)
    report = support.held(gov(*support.select()), interface)
    assert report[support.KEY_REPORT_PROFILE] == "FULL"
    assert support.open_numbers(report) == support.not_required("LITE")


def test_each_open_row_carries_its_number_key_and_state(project, gov, interface):
    project.specification(support.fresh_rows(), profile="FULL")
    report = support.held(gov(*support.select()), interface)
    keys = support.row_keys()
    for row in report[support.KEY_OPEN]:
        assert row[support.ROW_KEY] == keys[row[support.ROW_N]], f"row {row[support.ROW_N]} has another key: {row}"
        assert row[support.ROW_STATE] == "MISSING", row


@pytest.mark.parametrize("state", ["MISSING", "PROVISIONAL", "BLOCKED"])
def test_a_required_row_in_a_state_that_does_not_satisfy_is_open(project, gov, interface, state):
    """Only PRESENT and N/A_WITH_REASON satisfy; the row is reported with the state it has."""
    rows = support.complete_rows()
    reason = None if state == "MISSING" else "waits on DP-9"
    project.specification(support.edit(rows, 7, state=state, evidence=[], reason=reason))
    report = support.held(gov(*support.select()), interface)
    assert [(row[support.ROW_N], row[support.ROW_STATE]) for row in report[support.KEY_OPEN]] == [(7, state)]


def test_a_row_that_is_not_applicable_with_its_reason_is_satisfied(project, gov, interface):
    rows = support.edit(support.complete_rows(), [12, 17], state="N/A_WITH_REASON", evidence=[],
                        reason="the feature has no user interface and calls no other system")
    project.specification(rows)
    support.passed(gov(*support.select()), interface)


def test_a_standard_specification_holds_only_the_rows_of_its_declared_types(project, gov, interface):
    """Row 19 belongs to observability-sre, row 13 to backend: only the declared type's row is required."""
    rows = support.edit(support.complete_rows("STANDARD", capability_types=("backend",)), 13, state="MISSING",
                        evidence=[])
    project.specification(rows, profile="STANDARD", capability_types=("backend",))
    report = support.held(gov(*support.select()), interface)
    assert support.open_numbers(report) == [13]


# ---- failure 1: a specification with a required MISSING row is never reported closed

@pytest.mark.parametrize("number", [1, 7, 26], ids=["first-row", "test-data-at-FULL", "last-row"])
def test_one_required_missing_row_is_enough(project, gov, interface, number):
    """CAP-30's acceptance line: test data MISSING at FULL."""
    project.specification(support.edit(support.complete_rows(), number, state="MISSING", evidence=[]))
    report = support.held(gov(*support.select()), interface)
    assert support.open_numbers(report) == [number]


def test_a_record_marked_closed_by_hand_with_a_required_row_missing_is_not_reported_closed(project, gov, interface):
    """The answer comes from the rows, not from the status somebody wrote."""
    rows = support.edit(support.complete_rows(), 7, state="MISSING", evidence=[])
    project.specification(rows, status=support.STATUS_CLOSED)
    report = support.held(gov(*support.select()), interface)
    assert support.open_numbers(report) == [7]


# ---- a ticket's specification (MR-1's acceptance line)

def test_the_open_cells_of_a_tickets_specification_are_named(project, gov, interface):
    """MR-1: for a production ticket whose specification is open, ``gov readiness`` names the open cells."""
    project.specification(support.edit(support.complete_rows(), [7, 20], state="MISSING", evidence=[]))
    project.ticket(A, "W9-01", specification=support.SPEC)
    report = support.held(gov(support.COMMAND, support.ARG_TICKET, A, "--json"), interface)
    assert report[support.KEY_SPECIFICATION] == support.SPEC
    assert support.open_numbers(report) == [7, 20]


def test_a_ticket_whose_specification_is_complete_passes(project, gov, interface):
    project.specification(support.complete_rows())
    project.ticket(A, "W9-01", specification=support.SPEC)
    support.passed(gov(support.COMMAND, support.ARG_TICKET, A, "--json"), interface)


# ---- nothing passes by default

def test_a_specification_with_no_profile_does_not_pass(project, gov, interface):
    """No profile is assumed: with the mandatory rows satisfied and no profile declared, nothing says "closed"."""
    project.specification(support.complete_rows("LITE"), profile=None)
    support.not_passed(gov(*support.select()), interface)


def test_a_capability_type_outside_the_taxonomy_does_not_pass(project, gov, interface):
    """The taxonomy is fixed (CAP-30.e): an unknown type cannot stand for "no extra rows"."""
    project.specification(support.complete_rows("LITE"), profile="STANDARD", capability_types=("blockchain",))
    support.not_passed(gov(*support.select()), interface)

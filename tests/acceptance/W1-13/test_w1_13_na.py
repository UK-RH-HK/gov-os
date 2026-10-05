"""W1-13 -- KPI success 1, second half [CAP-30.a], and failure 2.

"Rejects N/A_WITH_REASON with an empty reason", and "a defaulted N/A passes" must never happen.

Settled by the sources: DEC-085 ("there is no defaulted N/A: every N/A is written by an agent as N/A_WITH_REASON,
and the checker rejects an empty reason"), MR-1 ("an N/A without a reason is rejected") and the rules of
``readiness-dimensions.yaml`` (``silent_na``: a cell may not be empty, and N/A is only N/A_WITH_REASON with a
non-empty reason; five states; ``evidence``). The error code and where the rejected rows are named are DP-4.
"""

from __future__ import annotations

import pytest

import w1_13_support as support

# What a silent or defaulted N/A looks like in a record: the fields set on one row.
SILENT = [
    pytest.param({"state": "N/A_WITH_REASON", "reason": None}, id="reason-null"),
    pytest.param({"state": "N/A_WITH_REASON", "reason": ""}, id="reason-empty"),
    pytest.param({"state": "N/A_WITH_REASON", "reason": "   "}, id="reason-blank"),
    pytest.param({"state": "N/A", "reason": "not applicable"}, id="state-N/A"),
    pytest.param({"state": None}, id="state-null"),
    pytest.param({"state": ""}, id="state-empty"),
    pytest.param({"state": "DONE"}, id="state-outside-the-five"),
]


@pytest.mark.parametrize("fields", SILENT)
def test_a_silent_na_on_a_required_row_is_rejected(project, gov, interface, fields):
    """Every other row is satisfied: the one cell alone makes the record invalid, and it is named."""
    project.specification(support.edit(support.complete_rows(), 12, evidence=[], **fields))
    assert support.rejected(gov(*support.select()), interface) == [12]


@pytest.mark.parametrize("fields", SILENT[:2])
def test_a_silent_na_on_a_row_the_profile_does_not_require_is_rejected(project, gov, interface, fields):
    """``silent_na`` is a rule of the cell, not of the profile: row 12 is not required at LITE."""
    project.specification(support.edit(support.complete_rows("LITE"), 12, evidence=[], **fields), profile="LITE")
    assert support.rejected(gov(*support.select()), interface) == [12]


def test_every_rejected_row_is_named(project, gov, interface):
    rows = support.edit(support.complete_rows(), [3, 12, 22], state="N/A_WITH_REASON", evidence=[], reason="")
    project.specification(rows)
    assert support.rejected(gov(*support.select()), interface) == [3, 12, 22]


def test_a_record_that_defaults_every_optional_row_to_na_does_not_pass(project, gov, interface):
    """Failure 2 as a tool would cause it: the 16 rows outside the mandatory set filled with N/A and no reason."""
    optional = support.not_required("LITE")
    rows = support.edit(support.complete_rows("LITE"), optional, state="N/A_WITH_REASON", evidence=[], reason=None)
    project.specification(rows, profile="FULL")
    assert support.rejected(gov(*support.select()), interface) == optional


def test_a_record_that_drops_a_row_does_not_pass(project, gov, interface):
    """A row left out is an empty cell: it is neither satisfied nor "not applicable"."""
    rows = [row for row in support.complete_rows() if row["n"] != 12]
    project.specification(rows)
    support.not_passed(gov(*support.select()), interface)


def test_a_present_row_that_cites_nothing_does_not_pass(project, gov, interface):
    """The ``evidence`` rule: every PRESENT cell cites at least one decision id or document section."""
    project.specification(support.edit(support.complete_rows(), 9, state="PRESENT", evidence=[]))
    support.not_passed(gov(*support.select()), interface)


def test_a_reason_written_by_an_agent_is_accepted_on_every_optional_row(project, gov, interface):
    """The same record as the defaulted one, with reasons: it passes. The reason is what was missing."""
    optional = support.not_required("LITE")
    rows = support.edit(support.complete_rows("LITE"), optional, state="N/A_WITH_REASON", evidence=[],
                        reason="a command-line tool with no service, no store and no interface of its own")
    project.specification(rows, profile="FULL")
    support.passed(gov(*support.select()), interface)

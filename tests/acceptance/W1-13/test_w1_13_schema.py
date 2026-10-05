"""W1-13, second batch (DEC-136) -- B2: a weakened project schema does not weaken the gate.

KPI failure 1: "a spec with a required MISSING row is reported closed" must never happen [CAP-30.a, CAP-53.a].
What a profile requires is DEC-085's and the Contract's (``docs/contract/readiness-dimensions.yaml``): FULL and
every spine all 26 rows, STANDARD the ten mandatory rows plus the rows the capability-type table marks for the
declared types; the taxonomy is fixed (CAP-30.e) and an unknown capability type does not pass (DEC-350).

An adopted project holds its own copy of the ``feature-readiness`` schema (``openspec/schemas/feature-readiness/
schema.yaml``), a file the project can edit. Each case edits that copy and leaves a row open (MISSING) that the
profile requires by the Contract. Expected: the command does not pass (``SPEC_NOT_CLOSED`` or ``READINESS_INVALID``:
which of the two is not fixed) and ``gov.readiness.close`` refuses and writes nothing.

The control, the schema as the template ships it and a complete specification passing, is
``test_w1_13_report.py::test_a_record_with_every_required_row_satisfied_passes``.
"""

from __future__ import annotations

import pytest

import w1_13_support as support

REMOVED = 7          # representative test data: outside the mandatory ten (CAP-30's acceptance line)
BACKEND_ROW = 13     # backend/service behaviour: the Contract marks it for the capability type ``backend``
UNKNOWN_TYPE = "blockchain"


def _drop_row(schema):
    schema["dimensions"] = [row for row in schema["dimensions"] if row["n"] != REMOVED]


def _keep_mandatory_rows(schema):
    mandatory = set(support.required("LITE"))
    schema["dimensions"] = [row for row in schema["dimensions"] if row["n"] in mandatory]


def _empty_backend(schema):
    schema["capability_types"]["extra_rows_for_standard"]["backend"] = []


def _add_type(schema):
    schema["capability_types"]["extra_rows_for_standard"][UNKNOWN_TYPE] = []


def _one_missing(number, profile="FULL", spine=False, types=()):
    return support.edit(support.complete_rows(profile, spine, types), number, state="MISSING", evidence=[])


# The schema edit, then the specification: its rows, profile, spine mark and capability types.
CASES = [
    pytest.param(_drop_row, lambda: _one_missing(REMOVED), "FULL", False, (), id="row-removed-FULL"),
    pytest.param(_drop_row, lambda: _one_missing(REMOVED), "LITE", True, (), id="row-removed-spine-opened-at-LITE"),
    pytest.param(_keep_mandatory_rows, lambda: support.complete_rows("LITE"), "FULL", False, (),
                 id="only-the-mandatory-rows-FULL"),
    pytest.param(_empty_backend, lambda: _one_missing(BACKEND_ROW, "STANDARD", types=("backend",)), "STANDARD",
                 False, ("backend",), id="type-emptied-STANDARD"),
    pytest.param(_add_type, lambda: support.complete_rows("LITE"), "STANDARD", False, (UNKNOWN_TYPE,),
                 id="type-added-STANDARD"),
]


def _build(project, weaken, rows, profile, spine, types):
    assert REMOVED not in support.required("LITE") and BACKEND_ROW in support.required("STANDARD", False, ("backend",))
    assert UNKNOWN_TYPE not in support.source()["capability_types"]["extra_rows_for_standard"]
    support.edit_schema(project, weaken)
    project.specification(rows(), profile=profile, spine=spine, capability_types=types)


@pytest.mark.parametrize("weaken, rows, profile, spine, types", CASES)
def test_a_weakened_schema_does_not_let_a_specification_pass(project, gov, interface, weaken, rows, profile, spine,
                                                             types):
    _build(project, weaken, rows, profile, spine, types)
    support.not_passed(gov(*support.select()), interface)


@pytest.mark.parametrize("weaken, rows, profile, spine, types", CASES)
def test_a_weakened_schema_does_not_let_a_specification_be_closed(project, weaken, rows, profile, spine, types):
    _build(project, weaken, rows, profile, spine, types)
    project.settle()
    before, tickets = project.state(), project.tickets()
    outcome = project.close()
    assert not outcome.ok, f"closed with a row open that its profile requires ({outcome.describe()})"
    assert project.status() == support.STATUS_OPEN
    assert project.tickets() == tickets, "a refused closure created a ticket"
    assert project.state() == before, "a refused closure changed the project"

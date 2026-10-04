"""W1-13 -- KPI success 2: "Blocks OpenSpec apply/archive and ticket READY while required rows are open."

What this ticket can hold, from ``src/gov/readiness/**`` alone (README, point 1, and package DP-1):

- **apply/archive.** OpenSpec is not this ticket's tool, and the hook, check or skill that runs before
  ``openspec apply`` or ``archive`` belongs to W1-26, W1-35 and W1-40. What they consume is the exit code of
  ``gov readiness``: 0 only when no required row is open and the record is valid (API-0002; the command module
  convention of ``gov.cli.main``). The gate reads the rows, never the status.
- **READY.** The READY rule is W1-09's (``gov.tasks``): a ticket whose ``specification`` record is not ``CLOSED``
  is held (DEC-307). This ticket's part is that a specification with a required row open cannot become
  ``CLOSED`` through ``gov.readiness.close`` (DP-2), and that one without can.

The command is a read command (CAP-27): no form of it writes, whatever it finds.
"""

from __future__ import annotations

import pytest

import w1_13_support as support

tasks_support = support.tasks_support
A, B = "TST-a001", "TST-a002"


# ---- the exit code a gate before apply or archive reads

def test_the_gate_is_shut_while_a_required_row_is_open(project, gov):
    project.specification(support.edit(support.complete_rows(), 7, state="MISSING", evidence=[]))
    for flags in (("--json",), ()):
        run = gov(support.COMMAND, support.ARG_SPECIFICATION, support.SPEC, *flags)
        assert run.returncode == support.EXIT_OPEN, f"a required row is open\n{run.describe()}"


def test_the_gate_is_open_when_no_required_row_is_open(project, gov):
    project.specification(support.complete_rows())
    for flags in (("--json",), ()):
        run = gov(support.COMMAND, support.ARG_SPECIFICATION, support.SPEC, *flags)
        assert run.returncode == 0, f"every required row is satisfied\n{run.describe()}"


def test_the_gate_is_shut_on_an_invalid_record(project, gov):
    """A silent N/A is not a satisfied row: apply and archive are held too."""
    project.specification(support.edit(support.complete_rows(), 12, state="N/A_WITH_REASON", evidence=[], reason=""))
    for flags in (("--json",), ()):
        run = gov(support.COMMAND, support.ARG_SPECIFICATION, support.SPEC, *flags)
        assert run.returncode == support.EXIT_INVALID, run.describe()


def test_the_gate_reads_the_rows_and_not_the_status(project, gov):
    """Archive comes after a specification was closed: a row reopened since then shuts the gate again."""
    project.specification(support.edit(support.complete_rows(), 7, state="MISSING", evidence=[]),
                          status=support.STATUS_CLOSED)
    assert gov(*support.select()).returncode == support.EXIT_OPEN


def test_the_gate_opens_when_the_last_open_row_is_settled(project, gov):
    project.specification(support.edit(support.complete_rows(), 7, state="MISSING", evidence=[]))
    assert gov(*support.select()).returncode == support.EXIT_OPEN
    project.rows(support.complete_rows())
    assert gov(*support.select()).returncode == 0


def test_the_gate_judges_each_specification_on_its_own(project, gov):
    project.specification(support.fresh_rows())
    project.specification(support.complete_rows(), spec_id=support.OTHER_SPEC, change=support.OTHER_CHANGE)
    assert gov(*support.select(support.SPEC)).returncode == support.EXIT_OPEN
    assert gov(*support.select(support.OTHER_SPEC)).returncode == 0


# ---- ticket READY

def test_a_ticket_stays_out_of_ready_while_its_specification_has_a_required_row_open(project):
    """MR-1, CAP-30's acceptance line: test data MISSING at FULL keeps the production ticket out of READY."""
    project.specification(support.edit(support.complete_rows(), 7, state="MISSING", evidence=[]))
    project.ticket(A, "W9-01", specification=support.SPEC)
    project.ticket(B, "W9-02")
    outcome = project.close()
    assert not outcome.ok, f"a specification with a required row open was closed ({outcome.describe()})"
    assert project.status() != support.STATUS_CLOSED
    ready, blocked = project.queue()
    assert ready == [B]
    assert blocked == {A: [tasks_support.SPEC_NOT_CLOSED]}


def test_a_ticket_is_ready_once_its_specification_is_complete_and_closed(project):
    project.specification(support.complete_rows("LITE"), profile="LITE")
    project.ticket(A, "W9-01", specification=support.SPEC)
    ready, blocked = project.queue()
    assert ready == [] and blocked[A] == [tasks_support.SPEC_NOT_CLOSED], \
        "a specification nobody closed already lets its ticket through"
    outcome = project.close()
    assert outcome.ok, f"a complete LITE specification was not closed ({outcome.describe()})"
    ready, blocked = project.queue()
    assert ready == [A]
    assert A not in blocked


# ---- the command only reads (CAP-27)

def _held(project):
    project.specification(support.fresh_rows())
    return (support.ARG_SPECIFICATION, support.SPEC)


def _complete_spine(project):
    project.specification(support.complete_rows(), profile="LITE", spine=True)
    return (support.ARG_SPECIFICATION, support.SPEC)


def _invalid(project):
    project.specification(support.edit(support.complete_rows(), 12, state="N/A", evidence=[]))
    return (support.ARG_SPECIFICATION, support.SPEC)


def _by_ticket(project):
    project.specification(support.complete_rows())
    project.ticket(A, "W9-01", specification=support.SPEC)
    return (support.ARG_TICKET, A)


@pytest.mark.parametrize("build", [_held, _complete_spine, _invalid, _by_ticket],
                         ids=["held", "complete-spine", "invalid", "by-ticket"])
def test_the_command_writes_nothing(project, gov, build):
    """No file, no ref, no ticket: a complete spine is reported, and neither closed nor given an audit ticket."""
    selector = build(project)
    project.settle()
    before = project.state()
    tickets = project.tickets()
    for flags in (("--json",), ()):
        run = gov(support.COMMAND, *selector, *flags)
        assert project.state() == before, f"gov readiness changed the project\n{run.describe()}"
    assert project.tickets() == tickets
    assert project.status() == support.STATUS_OPEN

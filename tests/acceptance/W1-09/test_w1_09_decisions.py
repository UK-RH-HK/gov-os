"""KPI success 5 [CAP-34.e]: non-global blocking.

"A ticket waiting on an open decision package is blocked, and tickets that do
not depend on it stay READY."

A decision package is a record of type ``decision-package`` (the kernel template
of W1-08). It names the tickets that wait on it in its ``constrains`` key, which
is a CONSTRAINS edge of the record graph (DEC-277). It is open while its status
is ``PROPOSED``.
"""

from __future__ import annotations

import w1_09_support as support

A, B, C = "TST-a001", "TST-a002", "TST-a003"


def package(project, record_id, status, tickets):
    return project.record(f"spec/gates/{record_id}.md", record_id, "decision-package", status, constrains=tickets)


def test_a_ticket_waiting_on_an_open_decision_package_is_blocked(project):
    project.ticket(A, "W9-01")
    package(project, "DP-0001", "PROPOSED", [A])
    ready, blocked = project.queue()
    assert ready == []
    assert blocked == {A: [support.DECISION_OPEN]}


def test_tickets_that_do_not_depend_on_the_package_stay_ready(project):
    project.ticket(A, "W9-01")
    project.ticket(B, "W9-02")
    project.ticket(C, "W9-03")
    package(project, "DP-0001", "PROPOSED", [A])
    ready, blocked = project.queue()
    assert ready == [B, C], "an open decision package blocked tickets that do not wait on it"
    assert blocked == {A: [support.DECISION_OPEN]}


def test_the_ticket_is_ready_again_when_the_package_is_answered(project):
    project.ticket(A, "W9-01")
    package(project, "DP-0001", "PROPOSED", [A])
    assert project.ready() == []
    package(project, "DP-0001", "ACCEPTED", [A])
    ready, blocked = project.queue()
    assert ready == [A]
    assert blocked == {}


def test_a_ticket_waiting_on_two_packages_is_blocked_while_one_is_open(project):
    project.ticket(A, "W9-01")
    package(project, "DP-0001", "ACCEPTED", [A])
    package(project, "DP-0002", "PROPOSED", [A])
    assert project.ready() == []
    assert project.blocked(settle=False) == {A: [support.DECISION_OPEN]}


def test_a_ticket_that_depends_on_the_blocked_ticket_waits_for_it_as_for_any_dependency(project):
    project.ticket(A, "W9-01")
    project.ticket(B, "W9-02", deps=[A])
    project.ticket(C, "W9-03")
    package(project, "DP-0001", "PROPOSED", [A])
    ready, blocked = project.queue()
    assert ready == [C]
    assert blocked == {A: [support.DECISION_OPEN], B: [support.DEPENDENCY_OPEN]}


def test_an_open_package_that_names_no_ticket_of_the_project_blocks_nothing(project):
    project.ticket(A, "W9-01")
    project.ticket(B, "W9-02")
    package(project, "DP-0001", "PROPOSED", ["TST-zzzz"])
    package(project, "DP-0002", "PROPOSED", [])
    assert project.ready() == [A, B]


def test_a_record_of_another_type_that_constrains_a_ticket_does_not_block_it(project):
    """Only an open decision package blocks: a decision that constrains a ticket is not a question waiting."""
    project.ticket(A, "W9-01")
    project.record("spec/decisions/ADR-0101.md", "ADR-0101", "decision", "PROPOSED", constrains=[A])
    assert project.ready() == [A]

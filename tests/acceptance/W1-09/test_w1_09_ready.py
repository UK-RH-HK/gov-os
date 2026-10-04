"""KPI success 3 [CAP-31.c] and failure 2: the ready queue.

"The ready queue excludes tickets that are claimed, whose acceptance tests
directory is missing, or whose specification is not closed", in a queue ordered
by dependency (CAP-31.c: parallel and serial execution by dependency), and "a
ticket without tests/acceptance/<id>/ appears as READY" must never happen.
"""

from __future__ import annotations

import w1_09_support as support

A, B, C, D = "TST-a001", "TST-a002", "TST-a003", "TST-a004"
HOLDER = "engineer:session-1"


# ---- by dependency [CAP-31.c]

def test_tickets_with_nothing_in_their_way_are_all_ready(project):
    """Independent tickets are READY together: they can run in parallel."""
    for ticket, wbs in ((A, "W9-01"), (B, "W9-02"), (C, "W9-03")):
        project.ticket(ticket, wbs)
    ready, blocked = project.queue()
    assert ready == [A, B, C]
    assert blocked == {}


def test_a_ticket_is_not_ready_before_its_dependencies_are_closed(project):
    """A chain runs in series: only the head of the chain is READY."""
    project.ticket(A, "W9-01")
    project.ticket(B, "W9-02", deps=[A])
    project.ticket(C, "W9-03", deps=[B])
    project.ticket(D, "W9-04")
    ready, blocked = project.queue()
    assert ready == [A, D]
    assert blocked == {B: [support.DEPENDENCY_OPEN], C: [support.DEPENDENCY_OPEN]}


def test_closing_a_dependency_makes_the_next_ticket_ready(project):
    project.ticket(A, "W9-01")
    project.ticket(B, "W9-02", deps=[A])
    project.ticket(C, "W9-03", deps=[B])
    assert project.ready() == [A]
    project.set_status(A, "closed")
    ready, blocked = project.queue()
    assert ready == [B]
    assert blocked == {C: [support.DEPENDENCY_OPEN]}


def test_a_ticket_with_one_of_two_dependencies_open_is_not_ready(project):
    project.ticket(A, "W9-01", status="closed")
    project.ticket(B, "W9-02")
    project.ticket(C, "W9-03", deps=[A, B])
    assert project.ready() == [B]


def test_a_closed_ticket_is_neither_ready_nor_blocked(project):
    project.ticket(A, "W9-01", status="closed")
    project.ticket(B, "W9-02")
    ready, blocked = project.queue()
    assert ready == [B]
    assert A not in blocked


# ---- claimed

def test_a_claimed_ticket_is_not_in_the_ready_queue(project):
    """CAP-23's acceptance line: the held ticket is absent from the ready queue; the others stay."""
    project.ticket(A, "W9-01")
    project.ticket(B, "W9-02")
    assert project.ready() == [A, B]
    assert project.claim(A, HOLDER).ok
    ready, blocked = project.queue()
    assert ready == [B]
    assert blocked == {A: [support.CLAIMED]}


def test_a_ticket_in_progress_is_not_in_the_ready_queue(project):
    """DEC-116: claimed means ``status: in_progress``, with or without a lock file."""
    project.ticket(A, "W9-01", status="in_progress")
    project.ticket(B, "W9-02")
    ready, blocked = project.queue()
    assert ready == [B]
    assert blocked == {A: [support.CLAIMED]}


def test_a_ticket_whose_dependency_is_only_claimed_is_not_ready(project):
    project.ticket(A, "W9-01", status="in_progress")
    project.ticket(B, "W9-02", deps=[A])
    assert project.ready() == []
    assert project.blocked(settle=False)[B] == [support.DEPENDENCY_OPEN]


# ---- acceptance tests folder (failure 2)

def test_a_ticket_without_its_acceptance_tests_folder_is_not_ready(project):
    project.ticket(A, "W9-01", tests=False)
    project.ticket(B, "W9-02")
    ready, blocked = project.queue()
    assert A not in ready, "a ticket without tests/acceptance/<id>/ appears as READY"
    assert ready == [B]
    assert blocked == {A: [support.NO_ACCEPTANCE_TESTS]}


def test_the_ticket_becomes_ready_when_its_acceptance_tests_folder_exists(project):
    project.ticket(A, "W9-01", tests=False)
    assert project.ready() == []
    project.tests_folder("W9-01")
    assert project.ready() == [A]


def test_the_acceptance_tests_of_another_ticket_do_not_count(project):
    project.ticket(A, "W9-01", tests=False)
    project.tests_folder("W9-010")
    project.tests_folder("W9-02")
    assert project.ready() == []


def test_a_file_in_place_of_the_acceptance_tests_folder_does_not_count(project):
    project.ticket(A, "W9-01", tests=False)
    support.write(project.root, "tests/acceptance/W9-01", "not a folder\n")
    assert project.ready() == []
    assert project.blocked(settle=False) == {A: [support.NO_ACCEPTANCE_TESTS]}


def test_the_folder_is_the_one_the_ticket_names(project):
    """``acceptance_tests.path`` of the ticket is the folder looked for."""
    project.ticket(A, "W9-01", tests=False, acceptance="tests/acceptance/feature-one/")
    project.tests_folder("W9-01")
    assert project.ready() == [], "the folder the ticket names is missing and the ticket is READY"
    project.tests_folder("feature-one")
    assert project.ready() == [A]


def test_a_ticket_that_names_no_folder_needs_the_folder_of_its_own_id(project):
    """Without ``acceptance_tests.path`` and without a WBS id, the folder is ``tests/acceptance/<ticket id>/``."""
    project.ticket(A, None, tests=False, acceptance=False)
    assert project.ready() == []
    assert project.blocked(settle=False) == {A: [support.NO_ACCEPTANCE_TESTS]}
    project.tests_folder(A)
    assert project.ready() == [A]


# ---- specification not closed

def test_a_ticket_whose_specification_is_closed_is_ready(project):
    project.record("openspec/specs/SPEC-0001.md", "SPEC-0001", "specification", "CLOSED")
    project.ticket(A, "W9-01", specification="SPEC-0001")
    assert project.ready() == [A]


def test_a_ticket_whose_specification_is_not_closed_is_not_ready(project):
    project.record("openspec/specs/SPEC-0001.md", "SPEC-0001", "specification", "OPEN")
    project.record("openspec/specs/SPEC-0002.md", "SPEC-0002", "specification", "CLOSED")
    project.ticket(A, "W9-01", specification="SPEC-0001")
    project.ticket(B, "W9-02", specification="SPEC-0002")
    ready, blocked = project.queue()
    assert ready == [B]
    assert blocked == {A: [support.SPEC_NOT_CLOSED]}


def test_the_ticket_becomes_ready_when_its_specification_closes(project):
    project.record("openspec/specs/SPEC-0001.md", "SPEC-0001", "specification", "OPEN")
    project.ticket(A, "W9-01", specification="SPEC-0001")
    assert project.ready() == []
    project.record("openspec/specs/SPEC-0001.md", "SPEC-0001", "specification", "CLOSED")
    assert project.ready() == [A]


def test_a_specification_that_is_no_record_is_not_closed(project):
    project.ticket(A, "W9-01", specification="SPEC-0404")
    assert project.ready() == []
    assert project.blocked(settle=False) == {A: [support.SPEC_NOT_CLOSED]}


# ---- the queue as a whole

def test_every_reason_that_holds_a_ticket_is_reported(project):
    project.ticket(A, "W9-01")
    project.ticket(B, "W9-02", deps=[A], tests=False)
    assert project.claim(B, HOLDER).ok
    assert project.blocked()[B] == sorted([support.CLAIMED, support.DEPENDENCY_OPEN, support.NO_ACCEPTANCE_TESTS])


def test_every_open_ticket_is_either_ready_or_blocked(project):
    project.ticket(A, "W9-01", status="closed")
    project.ticket(B, "W9-02", deps=[A])
    project.ticket(C, "W9-03", deps=[B])
    project.ticket(D, "W9-04", tests=False)
    project.ticket("TST-a005", "W9-05", status="in_progress")
    ready, blocked = project.queue()
    assert ready == [B]
    assert sorted(blocked) == [C, D, "TST-a005"]
    assert not set(ready) & set(blocked)


def test_reading_the_queue_changes_nothing_in_the_project(project):
    project.ticket(A, "W9-01")
    project.ticket(B, "W9-02", deps=[A], tests=False)
    assert project.claim(A, HOLDER).ok
    project.settle()
    before = support.tree(project.root)
    project.ready(settle=False)
    project.blocked(settle=False)
    assert support.tree(project.root) == before, "reading the ready queue wrote in the project"

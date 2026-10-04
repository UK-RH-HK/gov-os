"""KPI success 4 [CAP-31.d]: a ticket whose mandatory input is absent or superseded is not READY.

A ticket names its mandatory inputs in the frontmatter key ``inputs``, a list of
record ids. An input is absent when no record has that id, and superseded when
a SUPERSEDES edge of the record graph points at it (DEC-277).
"""

from __future__ import annotations

import w1_09_support as support

A, B = "TST-a001", "TST-a002"


def decision(project, record_id, status="ACTIVE", **keys):
    return project.record(f"spec/decisions/{record_id}.md", record_id, "decision", status, **keys)


def test_a_ticket_whose_mandatory_inputs_are_all_present_is_ready(project):
    decision(project, "ADR-0101")
    decision(project, "ADR-0102")
    project.ticket(A, "W9-01", inputs=["ADR-0101", "ADR-0102"])
    ready, blocked = project.queue()
    assert ready == [A]
    assert blocked == {}


def test_a_ticket_whose_mandatory_input_is_absent_is_not_ready(project):
    project.ticket(A, "W9-01", inputs=["ADR-0404"])
    ready, blocked = project.queue()
    assert ready == []
    assert blocked == {A: [support.INPUT_ABSENT]}


def test_one_absent_input_among_several_is_enough(project):
    decision(project, "ADR-0101")
    project.ticket(A, "W9-01", inputs=["ADR-0101", "ADR-0404"])
    assert project.ready() == []
    assert project.blocked(settle=False) == {A: [support.INPUT_ABSENT]}


def test_the_ticket_becomes_ready_when_the_absent_input_arrives(project):
    project.ticket(A, "W9-01", inputs=["ADR-0101"])
    assert project.ready() == []
    decision(project, "ADR-0101")
    assert project.ready() == [A]


def test_a_ticket_whose_mandatory_input_is_superseded_is_not_ready(project):
    """Another record names the input in its ``supersedes``."""
    decision(project, "ADR-0101")
    decision(project, "ADR-0102", supersedes=["ADR-0101"])
    project.ticket(A, "W9-01", inputs=["ADR-0101"])
    ready, blocked = project.queue()
    assert ready == []
    assert blocked == {A: [support.INPUT_SUPERSEDED]}


def test_an_input_that_names_its_own_successor_is_superseded(project):
    """``superseded_by`` on the input gives the same SUPERSEDES edge."""
    decision(project, "ADR-0101", status="SUPERSEDED", superseded_by="ADR-0102")
    decision(project, "ADR-0102")
    project.ticket(A, "W9-01", inputs=["ADR-0101"])
    assert project.ready() == []
    assert project.blocked(settle=False) == {A: [support.INPUT_SUPERSEDED]}


def test_the_successor_of_a_superseded_input_is_a_good_input(project):
    decision(project, "ADR-0101")
    decision(project, "ADR-0102", supersedes=["ADR-0101"])
    project.ticket(A, "W9-01", inputs=["ADR-0102"])
    assert project.ready() == [A]


def test_a_ticket_becomes_not_ready_when_its_input_is_superseded_later(project):
    decision(project, "ADR-0101")
    project.ticket(A, "W9-01", inputs=["ADR-0101"])
    assert project.ready() == [A]
    decision(project, "ADR-0102", supersedes=["ADR-0101"])
    assert project.ready() == []


def test_a_bad_input_holds_only_the_ticket_that_names_it(project):
    decision(project, "ADR-0101")
    decision(project, "ADR-0102", supersedes=["ADR-0101"])
    project.ticket(A, "W9-01", inputs=["ADR-0101", "ADR-0404"])
    project.ticket(B, "W9-02", inputs=["ADR-0102"])
    ready, blocked = project.queue()
    assert ready == [B]
    assert blocked == {A: sorted([support.INPUT_ABSENT, support.INPUT_SUPERSEDED])}

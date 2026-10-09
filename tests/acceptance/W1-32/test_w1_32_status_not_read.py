"""A result is measured or it is refused (DEC-449, DEC-454), part by part; and failure 2.

"An open gate is missing from the output."

No part of the answer may turn "could not read" into a clean answer. A ticket
list, a decision package, a specification's readiness, a share, a pause state
or a doctor part whose source is absent or cannot be read is reported as not
read, with the reason: never as empty, zero, "ok", closed or "not paused".

A gate is what holds work until somebody answers or supplies something
(README, "Gates"): an open decision package (the gate record of CAP-34,
DEC-308) and a specification whose required readiness rows are open (the
READY gate of CAP-30, with DEC-089's gap ticket or ``UNLINKED``). One whose
state cannot be read is shown as such, never left out.

One case a part. The governance share and the doctor's unmeasured parts are
in ``test_w1_32_status_parts.py``: on every project of this suite they are
what could not be measured.
"""

from __future__ import annotations

import os

import pytest

import w1_32_support as support

spec_support = support.spec_support
tasks_support = support.tasks_support
pause_support = support.pause_support

BROKEN_TICKET = "TST-s099"
LATE_PACKAGE = "DP-9199"
BROKEN_SPEC, BROKEN_CHANGE = "SPEC-zs03", "zs03-unreadable-feature"
NO_RECORD_CHANGE = "zs04-no-record"


# --------------------------------------------------------------------------
# Tickets
# --------------------------------------------------------------------------

def test_a_ticket_file_that_cannot_be_read_is_reported_and_not_left_out(project, sandbox, interface):
    """Its frontmatter is no YAML: the ticket is in no queue by a status of its own, and it is still a ticket."""
    tasks_support.write(project.root, f".tickets/{BROKEN_TICKET}.md", "---\nid: [unclosed\nstatus: open\n---\n# x\n")
    support.settle(project)
    tickets = support.parts(support.status(project, sandbox), interface)[support.TICKETS]
    said = support.text_of(tickets)
    assert BROKEN_TICKET in said, f"a ticket whose file cannot be read is left out of the answer: {said[:600]}"
    named = [item for item in support.unread_entries(tickets) if BROKEN_TICKET in support.text_of(item)]
    assert named, (f"{BROKEN_TICKET} is shown as a ticket like any other: nothing that names it says read: false "
                   f"with a reason: {said[:600]}")
    if support.unread_reason(tickets) is None and support.unread_reason(tickets[support.READY]) is None:
        assert BROKEN_TICKET not in support.ids(tickets[support.READY]), "an unreadable ticket is listed as ready"


def test_without_the_store_the_ready_tickets_are_not_read(project, sandbox, interface):
    """The READY rule reads the store and answers "none" without it (W1-09): the status may not pass that on as
    "no ticket is ready"."""
    (project.root / support.STORE_REL).unlink()
    tickets = support.parts(support.status(project, sandbox), interface)[support.TICKETS]
    support.assert_not_read(tickets, "the store is absent and the ready tickets", within=(support.READY,))


# --------------------------------------------------------------------------
# Open decision packages: a gate is never left out
# --------------------------------------------------------------------------

def test_without_the_store_the_decision_packages_are_not_read(project, sandbox, interface):
    """Two packages are open and their only recorded source is gone: "no open package" would hide two gates."""
    (project.root / support.STORE_REL).unlink()
    packages = support.parts(support.status(project, sandbox), interface)[support.PACKAGES]
    reasons = support.assert_not_read(packages, "the store is absent and the open decision packages")
    assert any("store" in reason.lower() for reason in reasons), f"the reason does not name the store: {reasons}"


def test_a_store_that_is_no_database_is_not_read_either(project, sandbox, interface):
    (project.root / support.STORE_REL).write_bytes(b"not a database\n")
    answer = support.parts(support.status(project, sandbox), interface)
    support.assert_not_read(answer[support.PACKAGES], "the store cannot be read and the open decision packages")
    support.assert_not_read(answer[support.TICKETS], "the store cannot be read and the ready tickets",
                            within=(support.READY,))


def test_a_package_opened_after_the_store_was_loaded_is_not_hidden(project, sandbox, interface):
    """The package is committed and the store is older than the commit: it is listed, or the packages are
    reported as not read. A clean list without it is the failure line."""
    support.package(project, LATE_PACKAGE, support.OPEN_STATUS, [support.T_READY])
    support.commit(project)
    packages = support.parts(support.status(project, sandbox), interface)[support.PACKAGES]
    if support.unread_reason(packages) is None:
        assert LATE_PACKAGE in support.ids(packages), \
            f"an open decision package recorded after the last load is missing: {support.ids(packages)}"


def test_every_open_package_is_listed_however_many(empty_project, sandbox, interface):
    """Twelve open packages, more than one batch of five (CAP-34.c): none is cut off."""
    wanted = [f"DP-92{number:02d}" for number in range(12)]
    for record_id in wanted:
        support.package(empty_project, record_id, support.OPEN_STATUS)
    support.settle(empty_project)
    packages = support.answered(support.status(empty_project, sandbox), interface)[support.PACKAGES]
    assert support.ids(packages) == wanted


# --------------------------------------------------------------------------
# Readiness: the READY gate of each specification
# --------------------------------------------------------------------------

def test_an_open_specification_shows_every_open_row_linked_or_not(status, interface):
    """DEC-089: each required open row with its gap ticket, or ``UNLINKED``."""
    said = support.entry(support.answered(status(), interface)[support.READINESS], support.SPEC_OPEN)
    rows = {row[spec_support.ROW_N]: row for row in said[spec_support.KEY_OPEN]}
    assert sorted(rows) == [support.ROW_LINKED, support.ROW_UNLINKED], f"the open rows shown are {sorted(rows)}"
    assert rows[support.ROW_LINKED][spec_support.ROW_GAP] == support.GAP_TICKET
    assert rows[support.ROW_UNLINKED][spec_support.ROW_GAP] == spec_support.UNLINKED


def test_a_specification_whose_readiness_cannot_be_read_is_shown_as_such(project, sandbox, interface):
    """Its ``readiness.yaml`` is no YAML: the specification is listed, not closed, with why it could not be judged."""
    project.specification(spec_support.complete_rows(), spec_id=BROKEN_SPEC, change=BROKEN_CHANGE)
    tasks_support.write(project.root, f"{spec_support.CHANGES_REL}/{BROKEN_CHANGE}/{spec_support.READINESS_NAME}",
                        "rows: [unclosed\n")
    support.settle(project)
    readiness = support.parts(support.status(project, sandbox), interface)[support.READINESS]
    assert BROKEN_SPEC in support.ids(readiness), \
        f"a specification whose readiness cannot be read is left out: {support.ids(readiness)}"
    said = support.entry(readiness, BROKEN_SPEC)
    assert said.get(spec_support.KEY_CLOSED) is not True, f"it is shown as closed: {support.text_of(said)}"
    reason = said.get(support.KEY_REASON)
    assert isinstance(reason, str) and reason.strip(), \
        f"{BROKEN_SPEC} is shown without the reason it could not be judged: {support.text_of(said)}"
    assert support.entry(readiness, support.SPEC_CLOSED)[spec_support.KEY_CLOSED] is True, \
        "one unreadable specification changed the verdict of another"


def test_a_change_that_holds_no_specification_record_is_shown(project, sandbox, interface):
    """The checker cannot judge it and says so by the change's folder (W1-13): the status does not drop it."""
    spec_support.write_change(project, NO_RECORD_CHANGE, None, spec_support.complete_rows())
    support.settle(project)
    readiness = support.parts(support.status(project, sandbox), interface)[support.READINESS]
    assert NO_RECORD_CHANGE in support.text_of(readiness), \
        f"a change with no specification record is left out: {support.text_of(readiness)[:600]}"


# --------------------------------------------------------------------------
# Pause state
# --------------------------------------------------------------------------

def _directory(flag):
    flag.mkdir(parents=True)


def _unreadable(flag):
    if os.geteuid() == 0:
        pytest.skip("no file is unreadable for the superuser")
    flag.parent.mkdir(parents=True, exist_ok=True)
    flag.write_text("a note, without the marker word\n", encoding="utf-8")
    flag.chmod(0o000)


@pytest.mark.parametrize("make", (_directory, _unreadable), ids=("a-directory", "no-read-permission"))
def test_a_flag_that_cannot_be_read_is_never_reported_as_not_paused(project, sandbox, interface, make):
    """The guard cannot tell and holds the tree frozen (DEC-402): the status says paused, or says it could not
    read the flag and why."""
    flag = project.root / support.FREEZE_FLAG_REL
    make(flag)
    try:
        answer = support.parts(support.status(project, sandbox), interface)
    finally:
        if flag.is_file():
            flag.chmod(0o600)
    assert support.paused(answer) is not False, \
        f"the flag cannot be read and the status says not paused: {support.text_of(answer[support.PAUSE])}"


# --------------------------------------------------------------------------
# One part that cannot be read does not empty the others
# --------------------------------------------------------------------------

def test_the_parts_that_can_be_read_are_still_given_without_the_store(project, sandbox, interface):
    (project.root / support.STORE_REL).unlink()
    answer = support.parts(support.status(project, sandbox), interface)
    assert support.ids(answer[support.READINESS]) == [support.SPEC_CLOSED, support.SPEC_OPEN]
    assert support.paused(answer) is False
    assert isinstance(answer[support.DOCTOR], dict) and "healthy" in answer[support.DOCTOR]

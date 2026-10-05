"""W1-13 -- KPI success 5 [CAP-47.d] and failure 3.

"Closing a spine, STANDARD or FULL feature specification creates an audit ticket for a fresh Independent Auditor
naming the milestone (DEC-088)", and "a spine, STANDARD or FULL specification closes without an audit ticket" must
never happen.

Settled by the sources: closing is the specification record's status becoming ``CLOSED`` (DEC-307); the trigger and
its exception, a LITE feature specification, which is audited at the wave exit (DEC-088); a ticket is created with
``gov.tasks.create``, which runs the project's own vendored ticket script (W1-09); the role name and the class of an
audit ticket are those of this repository's one audit ticket (W1-43); the keys a ticket must carry are
``ticket.schema.json``'s (W1-08). The milestone is the closure of that specification, so the ticket names the
specification's id.

**Every test of this file depends on package DP-2**: the command is a read command (CAP-27), so closing is the
public function ``gov.readiness.close(root, specification_id)``. It works in the working tree and commits nothing.
"""

from __future__ import annotations

import pytest

import w1_13_support as support

tasks_support = support.tasks_support

# profile, spine, capability types: the three kinds of specification DEC-088 names.
AUDITED = [
    pytest.param("FULL", False, (), id="FULL-feature"),
    pytest.param("STANDARD", False, ("backend",), id="STANDARD-feature"),
    pytest.param("LITE", True, (), id="spine-opened-at-LITE"),
]


def _complete(project, profile="FULL", spine=False, types=(), **keys):
    return project.specification(support.complete_rows(profile, spine, types), profile=profile, spine=spine,
                                 capability_types=types, **keys)


def _close(project, spec_id=support.SPEC):
    """Close, and return ``(value, ids of the tickets created)``."""
    before = project.tickets()
    outcome = project.close(spec_id)
    assert outcome.ok, f"the specification was not closed ({outcome.describe()})"
    assert isinstance(outcome.value, dict), f"close did not return a map: {outcome.value!r}"
    return outcome.value, sorted(set(project.tickets()) - set(before))


# ---- closing creates the audit ticket

@pytest.mark.parametrize("profile, spine, types", AUDITED)
def test_closing_marks_the_record_closed_and_creates_one_audit_ticket(project, profile, spine, types):
    _complete(project, profile, spine, types)
    value, created = _close(project)
    assert project.status() == support.STATUS_CLOSED
    assert len(created) == 1, f"closing created {len(created)} tickets: {created}"
    assert value.get(support.KEY_AUDIT_TICKET) == created[0], f"close does not name the ticket it created: {value}"


@pytest.mark.parametrize("profile, spine, types", AUDITED)
def test_the_audit_ticket_is_for_an_independent_auditor_and_names_the_milestone(project, profile, spine, types):
    _complete(project, profile, spine, types)
    _, created = _close(project)
    front = project.ticket_front(created[0])
    assert front.get("role") == support.AUDIT_ROLE, f"the audit ticket's role: {front.get('role')!r}"
    assert front.get("class") == support.AUDIT_CLASS, f"the audit ticket's class: {front.get('class')!r}"
    title = project.ticket_title(created[0])
    assert support.SPEC in title, f"the audit ticket's title does not name the specification that closed: {title!r}"


def test_the_audit_ticket_is_an_open_ticket_nobody_holds(project):
    """A fresh auditor takes it from the queue: it is open and unclaimed."""
    _complete(project)
    _, created = _close(project)
    front = project.ticket_front(created[0])
    assert front.get("status") == "open"
    assert front.get("state_class") == "AUTHORITATIVE"
    assert not project.root.joinpath(tasks_support.CLAIMS_REL, created[0]).exists()


def test_the_audit_ticket_carries_what_the_ticket_schema_requires(project):
    """``ticket.schema.json``: role, a non-empty ``allowed_paths``, and ``kpis`` with at least one success line."""
    _complete(project)
    _, created = _close(project)
    front = project.ticket_front(created[0])
    paths, kpis = front.get("allowed_paths"), front.get("kpis")
    assert isinstance(paths, list) and paths and all(isinstance(path, str) and path for path in paths), paths
    assert isinstance(kpis, dict) and isinstance(kpis.get("success"), list) and kpis["success"], kpis
    assert isinstance(kpis.get("failure"), list), kpis


def test_closing_changes_the_record_and_adds_the_ticket_and_nothing_else(project):
    """In the working tree, uncommitted: the record's status and one new ticket file."""
    _complete(project)
    project.ticket("TST-a001", "W9-01", specification=support.SPEC)
    project.settle()
    before, state = project.tree(), project.state()
    _, created = _close(project)
    changed = support.cli_support.snapshot_difference(before, project.tree())
    record = f"{support.CHANGES_REL}/{support.CHANGE}/{support.SPEC_RECORD_NAME}"
    assert sorted(changed) == sorted([f"changed: {record}", f"created: .tickets/{created[0]}.md"]), changed
    assert project.state()[2] == state[2], "closing moved HEAD or a ref"


def test_a_closed_specification_with_its_audit_ticket_passes_the_command(project, gov, interface):
    _complete(project)
    _close(project)
    support.passed(gov(*support.select()), interface)


# ---- the exception: a LITE feature specification

def test_closing_a_lite_feature_specification_creates_no_audit_ticket(project):
    """DEC-088: LITE feature specifications are audited at the wave exit."""
    _complete(project, "LITE")
    value, created = _close(project)
    assert project.status() == support.STATUS_CLOSED
    assert created == [], f"a LITE feature closure created the tickets {created}"
    assert value.get(support.KEY_AUDIT_TICKET) is None, value


# ---- failure 3: never closed without its audit ticket

def test_a_specification_is_not_closed_when_its_audit_ticket_cannot_be_created(driver, built, tmp_path):
    """A project without the ticket script: the closure fails, and the record is not left ``CLOSED``."""
    project = support.Project(tmp_path / "no-tk", driver, tk=False)
    _complete(project)
    outcome = project.close()
    assert not outcome.ok, f"closed with no way to create the audit ticket ({outcome.describe()})"
    assert project.status() != support.STATUS_CLOSED, "the specification is CLOSED and has no audit ticket"
    assert project.tickets() == []


def test_closing_twice_creates_one_audit_ticket(project):
    """One closure, one audit: a second call on a closed specification adds no ticket."""
    _complete(project)
    _, created = _close(project)
    project.close()
    assert project.status() == support.STATUS_CLOSED
    assert project.tickets() == created


# ---- what cannot be closed

@pytest.mark.parametrize("profile, spine, types", AUDITED)
def test_a_specification_with_a_required_row_open_is_not_closed(project, profile, spine, types):
    rows = support.edit(support.complete_rows(profile, spine, types), 5, state="MISSING", evidence=[])
    project.specification(rows, profile=profile, spine=spine, capability_types=types)
    project.settle()
    before = project.state()
    outcome = project.close()
    assert outcome.error is not None and outcome.error["code"] == support.SPEC_NOT_CLOSED, outcome.describe()
    assert project.state() == before, "a refused closure changed the project"


def test_a_spine_complete_only_for_the_profile_that_opened_it_is_not_closed(project):
    """DEC-085: opened at LITE, its mandatory rows satisfied: it still closes at FULL."""
    project.specification(support.complete_rows("LITE"), profile="LITE", spine=True)
    project.settle()
    before = project.state()
    outcome = project.close()
    assert outcome.error is not None and outcome.error["code"] == support.SPEC_NOT_CLOSED, outcome.describe()
    assert project.state() == before


def test_a_specification_with_a_silent_na_is_not_closed(project):
    project.specification(support.edit(support.complete_rows(), 12, state="N/A_WITH_REASON", evidence=[],
                                       reason=None))
    project.settle()
    before = project.state()
    outcome = project.close()
    assert outcome.error is not None and outcome.error["code"] == support.READINESS_INVALID, outcome.describe()
    assert project.state() == before

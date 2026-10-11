"""Round 16, piece 2 (DEC-628, DEC-633): the context-reproducibility check measures the project's own tickets.

DEC-628, the owner's words: "The context-reproducibility check measures the project's own tickets only, not the
kernel's template ticket."

DEC-633: "the context check measures the tickets of the project's ticket folder (``.tickets/``), whatever their
type name, and no other record of the store."

Measured before the round: the kernel's template ticket (``governance/kernel/templates/ticket.md`` of an adopted
project, id ``PROJ-0000``, type ``task``) is a record of the store. The check takes every store record of type
``ticket`` or ``task`` for a ticket, tries to build a context for the template ticket and fails ("ticket
'PROJ-0000' not found"). It is red in every project that holds the kernel's templates.

Every project of this module holds the template ticket as the single named file it is, at the kernel's path, and
its store is loaded through the public load path (``gov.store.load``). Each case first holds that the store does
hold the template ticket as a ticket record (``gov.records.records``), so that no case passes for want of the
record. The check is run as the kernel template declares it, by ``sh -c`` in the project root (DEC-285), and
through ``gov check``.

The cases of round 15 (``test_w1_30_r15_context_tickets.py``) and of W1-24 (``test_w1_24_family_check.py``) hold
the check in projects without the template ticket and stand as they are.
"""

from __future__ import annotations

import pytest

import w1_30_r15_support as r15
import w1_30_r16_support as r16

CHECK = r16.CONTEXT_CHECK
TEMPLATE = r16.TEMPLATE_TICKET_ID
SOUND = ("PROJ-aaaa", "PROJ-bbbb")
BROKEN = "PROJ-cccc"
UNREAD = "PROJ-dddd"
ELSEWHERE = "PROJ-eeee"


def _project(scratch, template=True, sound=SOUND):
    """A project that holds the base source, the kernel's declaration of the check, the kernel's template
    ticket and the sound tickets given."""
    project = scratch()
    project.write(r15.PATH_MAP_REL, "namespaces: {}\n")
    project.base_source()
    if template:
        r16.place_template_ticket(project)
    for number, ticket in enumerate(sound, start=1):
        project.write(f".tickets/{ticket}.md", r16.sound_ticket(ticket, f"W9-0{number}"))
    project.declare_as_the_kernel_does(CHECK)
    return project


def _loaded(project, sandbox, template=True):
    project.load_store(sandbox)
    if template:
        r16.assert_the_store_holds_the_template_ticket(project, sandbox)
    return project


def _run(project, sandbox):
    done = r15.run_declared_command(CHECK, project, sandbox)
    return done, r16.output_of(done)


# --------------------------------------------------------------------------
# The template ticket is not measured
# --------------------------------------------------------------------------

def test_a_project_that_holds_the_template_ticket_and_sound_tickets_is_green(scratch, sandbox):
    """Red before the round: "ERROR: PROJ-0000: ... ticket 'PROJ-0000' not found", exit code 1."""
    project = _loaded(_project(scratch), sandbox)
    done, output = _run(project, sandbox)
    assert TEMPLATE not in output, \
        f"the check names the kernel's template ticket ({TEMPLATE}), which is no ticket of the project\n{output}"
    assert done.returncode == 0, \
        f"every ticket of the project reproduces and the check is not green\n{output}"


def test_gov_check_reports_the_check_green_in_a_project_that_holds_the_template_ticket(scratch, sandbox):
    """The same through the runner. Red before the round: the entry is RED, its finding names PROJ-0000."""
    project = _loaded(_project(scratch), sandbox)
    status, entry, run = r15.status_of(project, sandbox, CHECK, commit=False)
    assert TEMPLATE not in str(entry["findings"]), \
        f"gov check reports the kernel's template ticket as a ticket of the project: {entry['findings']}"
    assert status == r15.GREEN and entry["findings"] == [], \
        f"the check is {status} in a project whose own tickets all reproduce: {entry['findings']}\n{run.describe()}"


def test_a_project_ticket_with_a_missing_input_is_red_and_only_that_ticket_is_named(scratch, sandbox):
    """Red before the round: the check is not green, but it names PROJ-0000 as failing beside the ticket."""
    project = _project(scratch)
    project.write(f".tickets/{BROKEN}.md", r16.broken_ticket(BROKEN, "W9-09"))
    _loaded(project, sandbox)
    done, output = _run(project, sandbox)
    assert done.returncode != 0, f"a project ticket's context cannot be built and the check is green\n{output}"
    assert BROKEN in output, f"the check does not name the ticket whose input is missing ({BROKEN})\n{output}"
    for ticket in SOUND:
        assert ticket not in output, f"the check names {ticket}, whose context reproduces\n{output}"
    assert TEMPLATE not in output, f"the check names the kernel's template ticket ({TEMPLATE}) as failing\n{output}"
    status, entry, run = r15.status_of(project, sandbox, CHECK, commit=False)
    found = str(entry["findings"])
    assert status == r15.RED and BROKEN in found and TEMPLATE not in found, \
        f"gov check does not report the check RED naming {BROKEN} alone: {status}, {entry['findings']}\n{run.describe()}"


# --------------------------------------------------------------------------
# A project with no ticket of its own
# --------------------------------------------------------------------------

def test_a_project_whose_only_ticket_record_is_the_template_reads_unmeasured(scratch, sandbox):
    """No file in the project's ticket folder; the store's one ticket record is the template.
    Red before the round: not green and "unmeasured", but because the template's context "failed": the output
    names PROJ-0000 as an error."""
    project = _loaded(_project(scratch, sound=()), sandbox)
    assert r16.ticket_records(project, sandbox) == {TEMPLATE: r16.TEMPLATE_TICKET_REL}, \
        "the fixture's store holds another ticket record than the template"
    done, output = _run(project, sandbox)
    assert done.returncode != 0, f"a project with no ticket of its own is green\n{output}"
    assert "unmeasured" in output.lower(), f"nothing was measured and the output does not say 'unmeasured'\n{output}"
    assert TEMPLATE not in output, \
        f"the check measured the kernel's template ticket ({TEMPLATE}) in a project with no ticket\n{output}"
    status, entry, run = r15.status_of(project, sandbox, CHECK, commit=False)
    assert status != r15.GREEN and TEMPLATE not in str(entry["findings"]), \
        f"gov check: {status}, {entry['findings']}\n{run.describe()}"


def test_a_project_with_no_ticket_record_at_all_reads_unmeasured(scratch, sandbox):
    """Passes before the round and holds what must stay (W1-24 holds the same in its own project)."""
    project = _loaded(_project(scratch, template=False, sound=()), sandbox, template=False)
    assert r16.ticket_records(project, sandbox) == {}, "the fixture's store holds a ticket record"
    done, output = _run(project, sandbox)
    assert done.returncode != 0, f"a project with no ticket is green\n{output}"
    assert "unmeasured" in output.lower(), f"nothing was measured and the output does not say 'unmeasured'\n{output}"


# --------------------------------------------------------------------------
# Whatever name a project ticket's type has
# --------------------------------------------------------------------------

@pytest.mark.parametrize("type_name", [*r16.TICKET_TYPES, "story"])
def test_a_broken_project_ticket_is_red_and_named_whatever_its_type_is_called(type_name, scratch, sandbox):
    """``task`` and ``ticket`` pass before the round and hold what must stay (the check is red there today,
    and names the ticket). ``story`` is red before the round: the check does not select a record of that type,
    so the broken ticket is not measured (and the output names PROJ-0000 instead)."""
    project = _project(scratch)
    project.write(f".tickets/{BROKEN}.md", r16.broken_ticket(BROKEN, "W9-09", type_name))
    _loaded(project, sandbox)
    held = {row["id"]: row["type"] for row in r16.store_records(project, sandbox)}
    assert held.get(BROKEN) == type_name, f"the fixture's store holds {BROKEN} as {held.get(BROKEN)!r}"
    done, output = _run(project, sandbox)
    assert done.returncode != 0, \
        f"a project ticket of type {type_name!r} cannot have its context built and the check is green\n{output}"
    assert BROKEN in output, \
        f"the check does not name the broken project ticket of type {type_name!r} ({BROKEN})\n{output}"


# --------------------------------------------------------------------------
# No real ticket leaves the measurement
# --------------------------------------------------------------------------

def _broken_frontmatter(project, sandbox):
    """A ticket file whose frontmatter is no YAML: nothing can read it as a ticket."""
    project.write(f".tickets/{UNREAD}.md", "---\nid: " + UNREAD + "\ntype: task\nstatus: [open\nsources: {\n---\n\n# A ticket\n")
    project.load_store(sandbox)


def _no_type(project, sandbox):
    """A ticket file that states no type, so the store does not load it, and whose input is missing."""
    text = r16.broken_ticket(UNREAD, "W9-08")
    project.write(f".tickets/{UNREAD}.md", text.replace("type: task\n", ""))
    project.load_store(sandbox)


def _after_the_load(project, sandbox):
    """A ticket file written after the store was loaded, whose input is missing."""
    project.load_store(sandbox)
    project.write(f".tickets/{UNREAD}.md", r16.broken_ticket(UNREAD, "W9-08"))


OUTSIDE_THE_STORE = {"broken-frontmatter": _broken_frontmatter, "no-type": _no_type,
                     "written-after-the-load": _after_the_load}


@pytest.mark.parametrize("how", sorted(OUTSIDE_THE_STORE))
def test_a_ticket_file_the_store_does_not_hold_is_named_and_the_check_is_not_green(how, scratch, sandbox):
    """A file of the project's ticket folder that is no record of the store: either the check measures it (its
    input is missing: red, named) or it cannot read it as a ticket (named, not green). It never leaves the
    measurement silently. Red before the round: the file is no record of the store, so it is not looked at."""
    project = _project(scratch)
    OUTSIDE_THE_STORE[how](project, sandbox)
    r16.assert_the_store_holds_the_template_ticket(project, sandbox)
    assert UNREAD not in {row["id"] for row in r16.store_records(project, sandbox)}, \
        f"the fixture's store holds {UNREAD}: the case shows nothing"
    done, output = _run(project, sandbox)
    assert done.returncode != 0, \
        f".tickets/{UNREAD}.md is a ticket file the store does not hold ({how}) and the check is green\n{output}"
    assert UNREAD in output, f"the check does not name the ticket file it could not measure ({UNREAD}, {how})\n{output}"
    status, entry, run = r15.status_of(project, sandbox, CHECK, commit=False)
    assert status != r15.GREEN and UNREAD in str(entry["findings"]), \
        f"gov check: {status}, {entry['findings']}\n{run.describe()}"


# --------------------------------------------------------------------------
# A ticket-typed record outside the ticket folder
# --------------------------------------------------------------------------

@pytest.mark.parametrize("type_name", r16.TICKET_TYPES)
def test_a_record_of_a_ticket_s_type_outside_the_ticket_folder_is_not_measured(type_name, scratch, sandbox):
    """A record under ``docs/`` whose type is ``task`` or ``ticket``. Red before the round: the check takes it
    (and the template) for a ticket and fails on "ticket ... not found"."""
    project = _project(scratch)
    rel = f"docs/notes/{ELSEWHERE}.md"
    project.write(rel, r16.sound_ticket(ELSEWHERE, "W9-07", type_name))
    _loaded(project, sandbox)
    assert r16.ticket_records(project, sandbox).get(ELSEWHERE) == rel, \
        f"the fixture's store does not hold {ELSEWHERE} as a record of type {type_name!r} at {rel}"
    done, output = _run(project, sandbox)
    assert ELSEWHERE not in output and TEMPLATE not in output, \
        f"the check names a record that is no file of the project's ticket folder\n{output}"
    assert done.returncode == 0, f"the project's own tickets all reproduce and the check is not green\n{output}"

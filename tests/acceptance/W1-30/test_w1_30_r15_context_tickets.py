"""Round 15, piece 1 (DEC-612, DEC-620): the context-reproducibility check measures the tickets the store holds.

Measured before the round: the store holds a project's tickets as records of type ``task`` (the type the ticket
tool writes), and the check asks the store for a type name no record has. In every project that has tickets it
says "unmeasured: no tickets in the store": it can never be green.

The store of each case is loaded from ticket files as the ticket tool and the orchestrator write them (W1-09's
``ticket_text``: tk's own fields, ``type: task``, then the task contract), through the public load path
(``gov.store.load``). The check is run as the kernel template declares it, by ``sh -c`` in the project root
(DEC-285), and once through ``gov check``.

A store with no ticket at all stays unmeasured and not green: ``tests/acceptance/W1-24/test_w1_24_family_check.py``
holds that (``test_no_tickets_reports_unmeasured_and_is_not_green``) and is not repeated here.
"""

from __future__ import annotations

import w1_30_r15_support as r15

CHECK = "context-reproducibility"
REPRODUCES = ("PROJ-aaaa", "PROJ-bbbb")
DOES_NOT = "PROJ-cccc"
NO_SUCH_SOURCE = "DEC-999"      # no record of the project has this id: the ticket's context cannot be built


def _project(scratch, sandbox, broken=False):
    """A project whose store holds two tickets whose context reproduces and, with ``broken``, one whose context
    cannot be built (it names a mandatory input the store does not hold)."""
    project = scratch()
    project.write(r15.PATH_MAP_REL, "namespaces: {}\n")
    project.base_source()
    for number, ticket in enumerate(REPRODUCES, start=1):
        project.write(f".tickets/{ticket}.md", r15.ticket_text(ticket, f"W9-0{number}"))
    if broken:
        text = r15.ticket_text(DOES_NOT, "W9-09").replace(f"- {r15.support.BASE_SOURCE}", f"- {NO_SUCH_SOURCE}")
        assert NO_SUCH_SOURCE in text, "the fixture ticket does not name the missing source"
        project.write(f".tickets/{DOES_NOT}.md", text)
    project.declare_as_the_kernel_does(CHECK)
    project.load_store(sandbox)
    return project


def _says_no_tickets(output):
    return "no tickets" in output.lower()


def test_the_check_is_green_where_every_ticket_s_context_reproduces(scratch, sandbox):
    """Red before the round: "unmeasured: no tickets in the store", exit code 1."""
    project = _project(scratch, sandbox)
    done = r15.run_declared_command(CHECK, project, sandbox)
    output = done.stdout + done.stderr
    assert not _says_no_tickets(output), \
        f"the store holds {len(REPRODUCES)} tickets of type task and the check says it holds none\n{output}"
    assert done.returncode == 0, f"every ticket's context reproduces and the check is not green\n{output}"


def test_gov_check_reports_the_check_green_in_a_project_with_tickets(scratch, sandbox):
    """The same through the runner: the check's entry is GREEN and holds no finding.
    Red before the round: RED, finding "unmeasured: no tickets in the store"."""
    project = _project(scratch, sandbox)
    status, entry, run = r15.status_of(project, sandbox, CHECK, commit=False)
    assert status == r15.GREEN and entry["findings"] == [], \
        f"the check is {status} in a project whose tickets all reproduce: {entry['findings']}\n{run.describe()}"


def test_the_check_is_red_and_names_the_ticket_whose_context_does_not_reproduce(scratch, sandbox):
    """Red before the round: the check is not green, but for the wrong reason: it says there is no ticket and
    names none."""
    project = _project(scratch, sandbox, broken=True)
    done = r15.run_declared_command(CHECK, project, sandbox)
    output = done.stdout + done.stderr
    assert done.returncode != 0, f"a ticket's context cannot be built and the check is green\n{output}"
    assert not _says_no_tickets(output), f"the store holds tickets and the check says it holds none\n{output}"
    assert DOES_NOT in output, f"the check does not name the ticket whose context does not reproduce ({DOES_NOT})\n{output}"
    for ticket in REPRODUCES:
        assert ticket not in output, f"the check names {ticket}, whose context reproduces\n{output}"
    status, entry, run = r15.status_of(project, sandbox, CHECK, commit=False)
    assert status == r15.RED and DOES_NOT in str(entry["findings"]), \
        f"gov check does not report the check RED with the ticket named: {status}, {entry['findings']}\n{run.describe()}"

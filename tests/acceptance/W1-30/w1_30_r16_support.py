"""Support code for the round 16 cases of the W1-30 suite (the round on P-42 and P-43: DEC-627, DEC-628,
DEC-633).

A round 16 project is round 15's (``w1_30_r15_support.Scratch``): a temporary git repository that holds only
what its case writes. What this module adds: the kernel's template ticket, placed as the single file it is where
an adopted project holds it, and what the loaded store says of a project's records.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys

import w1_30_r15_support as r15

support = r15.support

CONTEXT_CHECK = "context-reproducibility"
AUTHORITY_CHECK = "core-authority"

TEMPLATE_TICKET_SOURCE = f"{r15.TEMPLATE_KERNEL}/templates/ticket.md"     # in this repository
TEMPLATE_TICKET_REL = f"{r15.INSTALLED_KERNEL}/templates/ticket.md"       # in an adopted project
TEMPLATE_TICKET_ID = "PROJ-0000"
TICKET_TYPES = ("task", "ticket")       # the two type names a ticket record has had (DEC-612)
NO_SUCH_SOURCE = "DEC-999"              # no record of any project of this round has this id

_RECORDS = (
    "import json, sys\n"
    "from gov.records import records\n"
    "print(json.dumps([{key: row[key] for key in ('id', 'type', 'status', 'path')} for row in records(sys.argv[1])]))\n"
)


def place_template_ticket(project):
    """The kernel's template ticket in the project, a copy of the one named file, at the path an adopted
    project holds it."""
    source = r15.REPO_ROOT / TEMPLATE_TICKET_SOURCE
    assert source.is_file(), f"the kernel template holds no {TEMPLATE_TICKET_SOURCE}"
    target = project.root / TEMPLATE_TICKET_REL
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    return TEMPLATE_TICKET_REL


def store_records(project, sandbox):
    """``[{id, type, status, path}]`` of every record the loaded store holds (``gov.records.records(root)``,
    W1-10's public query)."""
    done = subprocess.run([sys.executable, "-c", _RECORDS, str(project.root)], cwd=str(project.root),
                          env=support.sandbox_env(sandbox), capture_output=True, text=True,
                          stdin=subprocess.DEVNULL)
    assert done.returncode == 0, f"the store could not be read in the fixture:\n{done.stdout}\n{done.stderr}"
    return json.loads(done.stdout)


def assert_the_store_holds_the_template_ticket(project, sandbox):
    """The premise of every case with the template ticket: it is a record of the store, of a type the check
    took for a ticket's, at the kernel's path. Without it a case would pass for want of the record."""
    held = [row for row in store_records(project, sandbox) if row["id"] == TEMPLATE_TICKET_ID]
    assert [(row["path"], row["type"] in TICKET_TYPES) for row in held] == [(TEMPLATE_TICKET_REL, True)], \
        f"the fixture's store does not hold the kernel's template ticket as one ticket record: {held}"


def ticket_records(project, sandbox):
    """The store's records of a ticket's type names: ``{id: path}``."""
    return {row["id"]: row["path"] for row in store_records(project, sandbox) if row["type"] in TICKET_TYPES}


def sound_ticket(ticket_id, wbs, type_name="task"):
    """A ticket whose context can be built in a project that holds the base source."""
    text = r15.ticket_text(ticket_id, wbs)
    assert text.count("type: task\n") == 1, "the fixture ticket states no single type line"
    return text.replace("type: task\n", f"type: {type_name}\n")


def broken_ticket(ticket_id, wbs, type_name="task"):
    """A ticket that names a mandatory input no record of the project is: its context cannot be built."""
    text = sound_ticket(ticket_id, wbs, type_name)
    assert f"- {support.BASE_SOURCE}" in text, "the fixture ticket does not name the base source"
    return text.replace(f"- {support.BASE_SOURCE}", f"- {NO_SUCH_SOURCE}")


def output_of(done):
    return done.stdout + done.stderr

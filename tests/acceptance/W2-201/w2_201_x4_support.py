"""Support code for W2-201's fix line X4 (DEC-1219 (5)): a new ticket that is not a feature is flagged at the
landing, never refused.

It stands on W2-202's support (``tests/acceptance/W2-202/w2_202_support.py``, imported as ``base``), which stands on
W2-115b's (``kit``): the planted project (a package ``app``, tickets with acceptance suites, the test map that places
``.tickets/**`` as record-only, the kernel's ticket tool), its git helpers, ``gov queue`` through
``python3 -m gov.cli.main``, the answer and queue-record readers and the close record reader. Nothing of those modules
is changed. Added here: the new ticket files a branch adds (a feature's and the ways one is not), and the planted runs,
each built once per test session under a lock (W2-206's way), with a fixture check before ``gov queue`` runs.
"""

from __future__ import annotations

import fcntl
import json
import os
import shutil
import sys
import traceback
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "W2-202"))

import w2_202_support as base  # noqa: E402
from w2_202_support import CHANGED, kit, module_rel  # noqa: E402

A, B, C, D, E = kit.A, kit.B, kit.C, kit.D, kit.E
CODE = "NEW_TICKET_NOT_FEATURE"
NO_KPI = "no kpis.success line with a verify"
NO_SPEC = "no spec (the ticket's body is empty)"
UNREADABLE = "front matter unreadable"


def notice(tid, *missing):
    return f"{CODE} {tid}: " + "; ".join(missing)


def new_ticket(tid, success, body):
    """A new ticket file in the kernel schema's form, ``kpis.success`` as given (strings or ``{line, verify}``) and
    ``body`` after the front matter as given."""
    front = {"id": tid, "status": "open", "deps": [], "links": [], "created": "2026-11-19T12:00:00Z", "type": "task",
             "priority": 2, "assignee": "engineer", "external-ref": f"N-{tid[-4:]}", "wbs_id": f"N-{tid[-4:]}",
             "title": f"A new ticket {tid}", "class": "implementation", "state_class": "AUTHORITATIVE",
             "role": "engineer", "profile": "STANDARD", "allowed_paths": [f"src/app/new_{tid[-4:]}.py"],
             "kpis": {"success": success, "failure": ["It does not work"]}, "sources": [],
             "acceptance_tests": {"path": f"tests/acceptance/N-{tid[-4:]}/", "author": "independent-test-designer"}}
    return "---\n" + yaml.safe_dump(front, sort_keys=False) + "---\n" + body


SPEC_BODY = "# A new ticket\n\n## Problem\n\nThe count is wrong.\n\n## Approach\n\nCount again.\n"
VERIFIED = [{"line": "It counts right", "verify": "a planted test counts three items and sees 3"}]
VERIFIED_TEXT = ["It counts right. Verify: a planted test counts three items and sees 3"]
UNVERIFIED = ["It counts right"]

# id -> (the file's text, the notice it gives or None)
BAD = {"PROJ-nnew": (new_ticket("PROJ-nnew", UNVERIFIED, "\n  \n"), notice("PROJ-nnew", NO_KPI, NO_SPEC))}
GOOD = {"PROJ-good": (new_ticket("PROJ-good", VERIFIED, SPEC_BODY), None),
        "PROJ-strv": (new_ticket("PROJ-strv", VERIFIED_TEXT, SPEC_BODY), None)}
PARTIAL = {
    "PROJ-nobd": (new_ticket("PROJ-nobd", VERIFIED, ""), notice("PROJ-nobd", NO_SPEC)),
    "PROJ-novf": (new_ticket("PROJ-novf", UNVERIFIED, SPEC_BODY), notice("PROJ-novf", NO_KPI)),
    "PROJ-blnk": (new_ticket("PROJ-blnk", [{"line": "It counts right", "verify": "   "}], SPEC_BODY),
                  notice("PROJ-blnk", NO_KPI)),
    "PROJ-unrd": ("---\nid: PROJ-unrd\nstatus: [open\nkpis: {success: [\n---\n" + SPEC_BODY, None),  # see UNREAD
}
UNREAD = "PROJ-unrd"
# An existing ticket's file, edited by C's branch into what a new ticket would be flagged for.
D_EDITED = new_ticket(D.id, UNVERIFIED, "")


def files_of(table):
    return {f".tickets/{tid}.md": text for tid, (text, _) in table.items()}


# --------------------------------------------------------------------------
# The planted runs
# --------------------------------------------------------------------------

def shared(factory, name, build):
    """A planted run built once per test session (by the first process that asks, under a lock) and read by every
    other case; a build that fails is kept as failed."""
    root = factory.getbasetemp()
    if os.environ.get("PYTEST_XDIST_WORKER"):
        root = root.parent
    folder = root / f"w2-201-x4-{name}"
    with open(root / f"w2-201-x4-{name}.lock", "w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        done, broken = folder / "landing.json", folder / "broken.txt"
        if broken.is_file():
            raise AssertionError(f"the planted run {name} could not be built:\n{broken.read_text()}")
        if done.is_file():
            return kit.Landing(json.loads(done.read_text(encoding="utf-8")))
        if folder.exists():
            shutil.rmtree(folder)
        folder.mkdir(parents=True)
        try:
            data = build(folder)
        except BaseException:
            broken.write_text(traceback.format_exc(), encoding="utf-8")
            raise
        done.write_text(json.dumps(data), encoding="utf-8")
        return kit.Landing(data)


def _arg(project, ticket):
    return f"{ticket.id}={project.branches[ticket.id]}"


def build_notices(folder):
    """Tickets A, B, C, D and E at the base; four work branches, each changing its ticket's module and:

    - A (``topic/aa``) adds ``PROJ-nnew``: no KPI line with a verify and a blank body;
    - B (``topic/bb``) adds ``PROJ-good`` (a mapping line with a verify) and ``PROJ-strv`` (a string line with
      ``Verify:``), each with a body;
    - C (``topic/cc``) edits D's existing ticket file into one with no verify and no body;
    - E (``topic/ee``) adds one ticket per single missing part, and one whose front matter does not parse.

    ``gov queue A B C E --dry-run``, then ``gov queue A B C E``."""
    p = kit.Planted(folder / "project", folder / "told", tickets=(A, B, C, D, E))
    p.plant_branch(A, "topic/aa", [({module_rel("widget"): CHANGED, **files_of(BAD)}, "engineer", True)])
    p.plant_branch(B, "topic/bb", [({module_rel("gadget"): CHANGED, **files_of(GOOD)}, "engineer", True)])
    p.plant_branch(C, "topic/cc", [({module_rel("mod_cc"): CHANGED, D.ticket_rel: D_EDITED}, "engineer", True)])
    p.plant_branch(E, "topic/ee", [({module_rel("mod_ee"): CHANGED, **files_of(PARTIAL)}, "engineer", True)])
    assert kit.show(p.root, p.base, D.ticket_rel), "fixture: D's ticket file is not at the base"
    for tid in (*BAD, *GOOD, *PARTIAL):
        assert kit.show(p.root, p.base, f".tickets/{tid}.md") is None, f"fixture: {tid} is at the base"
    kit.self_check(p, {p.tips[t.id]: {t.node: "passed"} for t in (A, B, C, E)})
    args = [_arg(p, t) for t in (A, B, C, E)]
    before_dry = p.state()
    dry = kit.run_queue(p, *args, "--dry-run")
    dry_moved = p.state() != before_dry
    before = p.state()
    old_head = kit.rev(p.root, "main")
    run = kit.run_queue(p, *args)
    return kit.landing_data(p, run, "main", old_head, before, dry=dry, dry_moved=dry_moved)


def build_plain(folder):
    """A changes the widget and adds no ticket file. ``gov queue A``."""
    p = kit.Planted(folder / "project", folder / "told")
    p.plant_branch(A, "topic/aa", [({module_rel("widget"): CHANGED}, "engineer", True)])
    before = p.state()
    old_head = kit.rev(p.root, "main")
    run = kit.run_queue(p, _arg(p, A))
    return kit.landing_data(p, run, "main", old_head, before)


# --------------------------------------------------------------------------
# Reading the notices
# --------------------------------------------------------------------------

KEYS = ("ticket", "id", "code", "notice")


def by_id(entries, where):
    """``{id: entry}`` of a ``ticket_notices`` list, each entry cut to the four keys X4 names."""
    assert isinstance(entries, list), f"{where}: ticket_notices is {entries!r}, not a list"
    found = {}
    for entry in entries:
        assert isinstance(entry, dict), f"{where}: a ticket_notices entry is not a map: {entry!r}"
        found[entry.get("id")] = {key: entry.get(key) for key in KEYS}
    assert len(found) == len(entries), f"{where}: a new ticket is named twice: {entries!r}"
    return found


def expected():
    """``{id: entry}`` of the notices the notices run must give (the unreadable one apart: ``UNREAD``)."""
    want = {}
    for ticket, table in ((A, BAD), (B, GOOD), (E, PARTIAL)):
        for tid, (_, text) in table.items():
            if text is not None:
                want[tid] = {"ticket": ticket.id, "id": tid, "code": CODE, "notice": text}
    return want

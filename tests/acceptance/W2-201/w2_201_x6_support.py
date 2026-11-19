"""Support code for W2-201's fix line X6 (DEC-1219 (5)): a fix branch under a closed ticket lands through
``gov queue``; a plain branch on a closed ticket is still refused.

It stands on W2-202's support (``tests/acceptance/W2-202/w2_202_support.py``, imported as ``base``), which stands on
W2-115b's (``kit``): the planted project (a package ``app``, tickets with acceptance suites, the test map that places
``.tickets/**`` and ``docs/close/**`` as record-only, the kernel's ticket tool), its git helpers, ``gov queue`` through
``python3 -m gov.cli.main``, the answer, refusal and queue-record readers. Nothing of those modules is changed.

Added here: a closed ticket's file and close record at the base, branches whose commits carry ``Task:`` and ``Fix:``
trailers (from any start), and the planted runs, each built once per test session under a lock (W2-206's way), with
the fixture's own plain-pytest check before ``gov queue`` runs.
"""

from __future__ import annotations

import fcntl
import json
import os
import shutil
import sys
import traceback
from datetime import datetime, timedelta, timezone
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "W2-202"))

import w2_202_support as base  # noqa: E402
from w2_202_support import BROKEN, CHANGED, kit, module_rel  # noqa: E402

A, B, C = kit.A, kit.B, kit.C
CHANGED_AGAIN = "# CHANGED again by a second fix\nVALUE = 3\n"
PASSES = "    _tell(True)\n"   # a suite that passes whatever the modules hold

FIX_A1 = "the widget counts one too many when the list is empty"
FIX_A2 = "the widget's count is off again after the first fix"
FIX_C = "the module cc returns None for a blank name"
FIX_B = "the gadget's fix on a ticket still in progress"
FIX_OTHER = "a fix line written under another ticket's Task"
FIX_RED_A = "a fix that breaks the widget's unit test"
FIX_RED_C = "a fix that breaks the ticket's own acceptance suite"

ENTRY_KEYS = {"line", "branch", "tip", "tested", "landed"}
OWN_PLACES = kit.own_places


def close_rel(tid):
    return f"docs/close/{tid}/CL-{tid}.md"


def closed_record_text(ticket):
    """A close record of the first close, in the form the landing writes one (``gov.close.command``'s front matter,
    the queue's keys, the heading), with one line of prose under the heading."""
    front = {"id": f"CL-{ticket.id}", "type": "close", "status": "ACTIVE", "state_class": "AUTHORITATIVE",
             "task": ticket.id, "created": "2026-11-01T12:00:00Z",
             "outputs": [module_rel(ticket.modules[0]), close_rel(ticket.id)], "close": "queue",
             "commit": "0123456789abcdef0123456789abcdef01234567", "base_reds": [], "culprits": [],
             "queue": ".gov-runtime/queue/20261101T120000000000Z/queue.json"}
    return ("---\n" + yaml.safe_dump(front, sort_keys=False, allow_unicode=True) + "---\n\n"
            f"# CL-{ticket.id} — Close record for {ticket.id}\n\nThe first close, landed by gov queue.\n")


def fix_body_line(line, branch, tip):
    return f"- fix landed: {line} ({branch} @ {tip[:12]})"


def split_record(text):
    """``(front matter, body)`` of a close record's text."""
    assert text and text.startswith("---"), f"the close record has no front matter: {text!r:.300}"
    parts = text.split("---", 2)
    assert len(parts) == 3, f"the close record's front matter is not closed: {text!r:.300}"
    return (yaml.safe_load(parts[1]) or {}), parts[2]


def body_lines(body):
    return [line.rstrip() for line in body.splitlines() if line.strip()]


def is_utc_time(value):
    """A UTC time: a datetime with offset 0 (as YAML reads ``...Z``) or an ISO 8601 string ending ``Z`` or ``+00:00``;
    within a day of now (the landing's own time, not a planted commit's)."""
    if isinstance(value, datetime):
        when = value
    elif isinstance(value, str):
        try:
            when = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
        except ValueError:
            return False
    else:
        return False
    if when.tzinfo is None or when.utcoffset() != timedelta(0):
        return False
    return abs(datetime.now(timezone.utc) - when) < timedelta(days=1)


# --------------------------------------------------------------------------
# Planting
# --------------------------------------------------------------------------

def project(folder, statuses, records=(), suites=None, tickets=(A, B, C)):
    """A planted project: ``statuses`` ``{ticket: status}`` written into the ticket files, a first close's record for
    each ticket of ``records``, and ``suites`` ``{ticket: body}`` replacing a ticket's acceptance test body."""
    told = folder / "told"
    extra = {t.ticket_rel: kit.ticket_text(t, status) for t, status in statuses.items()}
    extra.update({close_rel(t.id): closed_record_text(t) for t in records})
    for t, body in (suites or {}).items():
        extra[t.suite_file] = kit.telling(t.suite_file, told, t.modules, body=body)
    return kit.Planted(folder / "project", told, tickets=tickets, extra=extra)


def branch(p, name, steps, start=None, record_as=None):
    """A work branch ``name`` from ``start`` (the base when None): each step ``(files, trailer lines)`` is one
    engineer's commit, ``Role: engineer`` added. The home branch is checked out again; returns the tip."""
    p.branch_from(name, start)
    for files, trailers in steps:
        p.commit("work on the fix", kit.ENGINEER, [*trailers, "Role: engineer"], files)
    tip = kit.rev(p.root, "HEAD")
    p.home()
    if record_as is not None:
        p.tips[record_as.id], p.branches[record_as.id] = tip, name
    return tip


def check(p, expect):
    """The fixture's own check: ``expect`` ``{revision: {node: outcome}}`` by a plain pytest run at each revision."""
    for revision, nodes in expect.items():
        got = kit.plain_pytest(p, revision, sorted({n.split("::")[0] for n in nodes}))
        for n, want in nodes.items():
            assert got.get(n) == want, f"fixture: {n} at {revision[:12]} is {got.get(n)}, not {want}: {got}"


def status_check(p, revision, want):
    for t, status in want.items():
        got = kit.status_at(p.root, revision, t.id)
        assert got == status, f"fixture: {t.id} is {got!r} at {revision[:12]}, not {status}"


def run(p, *args):
    """The project's state and the integration head, then ``gov queue <args>``."""
    before, head = p.state(), kit.rev(p.root, "main")
    done = kit.run_queue(p, *args)
    return {"run": done, "before": before, "old_head": head, "after": p.state()}


# --------------------------------------------------------------------------
# The planted runs
# --------------------------------------------------------------------------

def shared(factory, name, build):
    """A planted run built once per test session (by the first process that asks, under a lock) and read by every
    other case; a build that fails is kept as failed."""
    root = factory.getbasetemp()
    if os.environ.get("PYTEST_XDIST_WORKER"):
        root = root.parent
    folder = root / f"w2-201-x6-{name}"
    with open(root / f"w2-201-x6-{name}.lock", "w") as lock:
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
        done.write_text(json.dumps(data, default=str), encoding="utf-8")
        return kit.Landing(data)


def build_fix(folder):
    """A closed with a first close's record, C closed with none, B open. Three branches:

    - ``topic/aa-fix1`` (A): a commit with ``Task: A`` and no ``Fix:`` (the widget), then one with ``Task: A`` and
      ``Fix: FIX_A1`` (the helper);
    - ``topic/cc-fix`` (C): one commit with ``Task: C`` and ``Fix: FIX_C`` (mod_cc);
    - ``topic/bb`` (B): an ordinary feature commit, ``Task: B`` (the gadget).

    ``gov queue A B C --dry-run``, then ``gov queue A B C``; then ``topic/aa-fix2`` from the integration head as it then
    is (``Task: A``, ``Fix: FIX_A2``, the widget again) and ``gov queue A=topic/aa-fix2``."""
    p = project(folder, {A: "closed", B: "open", C: "closed"}, records=(A,))
    a1 = branch(p, "topic/aa-fix1", [({module_rel("widget"): CHANGED}, [f"Task: {A.id}"]),
                                     ({module_rel("helper"): CHANGED}, [f"Task: {A.id}", f"Fix: {FIX_A1}"])],
                record_as=A)
    cc = branch(p, "topic/cc-fix", [({module_rel("mod_cc"): CHANGED}, [f"Task: {C.id}", f"Fix: {FIX_C}"])],
                record_as=C)
    bb = branch(p, "topic/bb", [({module_rel("gadget"): CHANGED}, [f"Task: {B.id}"])], record_as=B)
    status_check(p, p.base, {A: "closed", B: "open", C: "closed"})
    assert kit.show(p.root, p.base, close_rel(A.id)) == closed_record_text(A), "fixture: A's close record"
    assert kit.show(p.root, p.base, close_rel(C.id)) is None, "fixture: C has a close record at the base"
    check(p, {a1: {A.node: "passed", kit.USES_WIDGET_NODE: "passed"}, cc: {C.node: "passed"}, bb: {B.node: "passed"}})
    args = [f"{A.id}=topic/aa-fix1", f"{B.id}=topic/bb", f"{C.id}=topic/cc-fix"]
    dry = run(p, *args, "--dry-run")
    first = run(p, *args)
    head = kit.rev(p.root, "main")
    a2 = branch(p, "topic/aa-fix2", [({module_rel("widget"): CHANGED_AGAIN}, [f"Task: {A.id}", f"Fix: {FIX_A2}"])],
                start=head)
    check(p, {a2: {A.node: "passed"}})
    second = run(p, f"{A.id}=topic/aa-fix2")
    data = kit.landing_data(p, first["run"], "main", first["old_head"], first["before"])
    data["extra"] = {"dry": dry, "first": first, "second": second, "tips": {"a1": a1, "a2": a2, "cc": cc, "bb": bb},
                     "record_at_base": closed_record_text(A)}
    return data


def build_refuse(folder):
    """A closed (with a first close's record), B in_progress. ``gov queue A=topic/aa-plain`` (``Task: A``, no
    ``Fix:``), ``gov queue A=topic/aa-other`` (``Task: B`` and ``Fix:``), then ``gov queue B=topic/bb-fix`` (``Task:
    B`` and ``Fix:`` on the in_progress ticket)."""
    p = project(folder, {A: "closed", B: "in_progress"}, records=(A,), tickets=(A, B))
    plain = branch(p, "topic/aa-plain", [({module_rel("widget"): CHANGED}, [f"Task: {A.id}"])])
    other = branch(p, "topic/aa-other", [({module_rel("widget"): CHANGED}, [f"Task: {B.id}", f"Fix: {FIX_OTHER}"])])
    bb = branch(p, "topic/bb-fix", [({module_rel("gadget"): CHANGED}, [f"Task: {B.id}", f"Fix: {FIX_B}"])],
                record_as=B)
    status_check(p, p.base, {A: "closed", B: "in_progress"})
    check(p, {bb: {B.node: "passed"}})
    refused_plain = run(p, f"{A.id}=topic/aa-plain")
    refused_other = run(p, f"{A.id}=topic/aa-other")
    progress = run(p, f"{B.id}=topic/bb-fix")
    data = kit.landing_data(p, progress["run"], "main", progress["old_head"], progress["before"])
    data["extra"] = {"plain": refused_plain, "other": refused_other, "progress": progress,
                     "tips": {"plain": plain, "other": other, "bb": bb}}
    return data


def build_red(folder):
    """A and C closed, A with a first close's record. A's acceptance suite passes whatever the widget holds, so A's
    red is a selected unit test's only; C's module is guarded by its acceptance suite alone. ``gov queue
    C=topic/cc-broken`` (``Fix:``, mod_cc broken), then ``gov queue A=topic/aa-broken`` (``Fix:``, the widget
    broken)."""
    p = project(folder, {A: "closed", C: "closed"}, records=(A,), suites={A: PASSES}, tickets=(A, B, C))
    cc = branch(p, "topic/cc-broken", [({module_rel("mod_cc"): BROKEN}, [f"Task: {C.id}", f"Fix: {FIX_RED_C}"])])
    aa = branch(p, "topic/aa-broken", [({module_rel("widget"): BROKEN}, [f"Task: {A.id}", f"Fix: {FIX_RED_A}"])])
    status_check(p, p.base, {A: "closed", C: "closed"})
    check(p, {p.base: {C.node: "passed", kit.USES_WIDGET_NODE: "passed"}, cc: {C.node: "failed"},
              aa: {A.node: "passed", kit.USES_WIDGET_NODE: "failed"}})
    red_c = run(p, f"{C.id}=topic/cc-broken")
    red_a = run(p, f"{A.id}=topic/aa-broken")
    data = kit.landing_data(p, red_c["run"], "main", red_c["old_head"], red_c["before"])
    data["extra"] = {"red_c": red_c, "red_a": red_a, "tips": {"cc": cc, "aa": aa},
                     "record_at_base": closed_record_text(A)}
    return data


# --------------------------------------------------------------------------
# Reading what a landing left
# --------------------------------------------------------------------------

def not_refused_closed(done):
    """The candidate went through the landing: the answer is not a refusal ``TICKET_CLOSED`` (on the base a closed
    ticket's branch is refused so, before anything runs)."""
    run_ = done["run"]
    try:
        env = kit.envelope(run_)
    except AssertionError:
        return
    code = (env.get("error") or {}).get("code") if env.get("ok") is False else None
    assert code != "TICKET_CLOSED", (f"gov queue refused the fix branch TICKET_CLOSED: a branch with Task: and Fix: "
                                     f"trailers on a closed ticket is not a fix landing\n{kit.describe(run_)}")


def chain(root, tested, head):
    """The commits from the tested merge up to the head, oldest first: ``{ticket: (commit, subject, paths)}``, one per
    commit, each with exactly one ``Task:`` trailer."""
    found = {}
    for commit in kit.git(root, "rev-list", "--reverse", f"{tested}..{head}").split():
        tasks = [t.split(":", 1)[1].strip() for t in kit.trailers(root, commit) if t.startswith("Task:")]
        assert len(tasks) == 1, f"the close commit {commit[:12]} names {tasks}, not one ticket"
        assert tasks[0] not in found, f"two close commits for {tasks[0]}"
        subject = kit.git(root, "log", "-1", "--format=%s", commit).strip()
        found[tasks[0]] = (commit, subject, kit.changed_paths(root, commit))
    return found


def record_text(root, revision, tid):
    return kit.show(root, revision, close_rel(tid))


def closes_by_ticket(result, where):
    closes = result.get("closes")
    assert isinstance(closes, list), f"{where}: closes is {closes!r}"
    return {c.get("ticket"): c for c in closes if isinstance(c, dict)}


def fix_marks(value, found=None):
    """``{ticket: fix_line}`` of every map anywhere in ``value`` that names a ``ticket`` with ``fix: true``."""
    found = {} if found is None else found
    if isinstance(value, dict):
        if value.get("fix") is True and isinstance(value.get("ticket"), str):
            found.setdefault(value["ticket"], value.get("fix_line"))
        for item in value.values():
            fix_marks(item, found)
    elif isinstance(value, list):
        for item in value:
            fix_marks(item, found)
    return found

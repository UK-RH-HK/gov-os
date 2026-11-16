"""Support code for the W2-156 acceptance tests (standard library and PyYAML only).

W2-156 (DAEO-ylsh) puts the runaway brake in the product: ``gov spend check | clear | sum`` reads W2-60b's session records
(the cost) and W2-60a's launch records (the projection, a new ``projection_usd`` key), keeps one marker per braked ticket,
and ``gov launch`` refuses a braked ticket (``SPEND_BRAKED``). The cases drive the public interfaces only: ``gov spend``
through ``gov``'s console-script entry point (a child process), ``gov launch`` the same way, and the files they read and
write under the project's ``.gov-runtime``.

The launch machinery (sandbox HOME, open resource gate, fixture project, stand-in CLI at ``~/.local/bin/claude`` that
starts no model, run of ``gov``) is W2-60a's own support module, imported as ``b``; nothing of it is changed here. This
module adds the planted records (session records, launch records, markers), the reader of what a ``gov spend`` run wrote,
and the snapshot of a tree.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
import uuid
from dataclasses import dataclass
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "W2-60a"))
import w2_60a_support as b  # noqa: E402

TK = b.T.tk                      # the fixture's engineer ticket: ``gov launch engineer <TK>`` starts on the base
OTHER_TK = b.SPEC.tk             # a second fixture ticket
TICKETS = {name: f"DAEO-sp0{n}" for n, name in enumerate(("a", "b", "c", "d"), 1)}
A, B, C, D = (TICKETS[k] for k in "abcd")

PAST = "2026-01-01T00:00:00Z"    # before any clear a case makes
PAST_LATER = "2026-01-02T00:00:00Z"
FUTURE = "2099-01-01T00:00:00Z"  # after any clear a case makes
STAMP = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z")

RUNTIME = ".gov-runtime"
SPEND_REL = f"{RUNTIME}/spend"
BRAKED_REL = f"{SPEND_REL}/braked"
BRAKES_REL = f"{SPEND_REL}/brakes.jsonl"
INBOX_REL = f"{RUNTIME}/dispatch/inbox"
SESSIONS_REL = f"{RUNTIME}/sessions"
LAUNCHES_REL = f"{RUNTIME}/launches"
DISPATCH_REL = "governance/project/dispatch.yaml"

# W2-60b's session record: the measured keys, each an object with a value and a source, or a null value and the reason.
MEASURED = ("role", "ticket", "task_class", "model", "effort", "window", "tokens_input", "tokens_output",
            "tokens_cache_creation", "tokens_cache_read", "cost_usd", "minutes", "turns", "subagents",
            "rate_limit_events", "compactions", "claude_code_version", "tier", "criticality", "promotion")


# --------------------------------------------------------------------------
# The fixture project
# --------------------------------------------------------------------------

def make_project(box):
    """W2-60a's fixture project (its own git repository, its own main checkout) with four more in_progress tickets
    (``A`` to ``D``), so that every ticket a case names exists."""
    extra = {f".tickets/{tk}.md": b.ticket_text(b.Ticket(tk, b.ENGINEER, f"W2-156-{tk}", ("src/app/**",)))
             for tk in TICKETS.values()}
    return b.make_project(box, extra=extra)


def dead_pid():
    done = subprocess.Popen([sys.executable, "-c", "pass"])
    done.wait()
    return done.pid


# --------------------------------------------------------------------------
# Planted records
# --------------------------------------------------------------------------

def plant_session(project, ticket, cost, *, started=PAST, role="engineer", pid=None, ended=True, worktree=None,
                  sid=None):
    """A session record ``<project>/.gov-runtime/sessions/<sid>.json`` in W2-60b's form. ``cost``: a number (measured),
    or None (the record gives the cost as not measured: ``value`` null and a reason). ``ended``: False plants a live
    session (``ended_at`` and ``exit_code`` null). Returns the record's path."""
    sid = sid or str(uuid.uuid4())
    not_measured = {"value": None, "not_measured": "planted: the session's log gives no value"}
    record = {"record": "gov-session", "format": 1, "session_id": sid,
              "worktree": worktree or str(Path(project).parent / "planted-tree"),
              "pid": pid if pid is not None else dead_pid(), "started_at": started,
              "ended_at": started if ended else None, "exit_code": 0 if ended else None}
    for key in MEASURED:
        record[key] = dict(not_measured)
    record["role"] = {"value": role, "source": "launch record"}
    record["ticket"] = {"value": ticket, "source": "launch record"}
    record["task_class"] = {"value": "implementation", "source": "launch record"}
    if cost is not None:
        record["cost_usd"] = {"value": cost, "source": "session log"}
    return b.write(Path(project) / SESSIONS_REL / f"{sid}.json", json.dumps(record, indent=2) + "\n")


def plant_launch(project, ticket, projection, *, started=PAST, role="engineer"):
    """A launch record ``<project>/.gov-runtime/launches/<sid>.json`` of W2-60a's form with the new ``projection_usd``
    key (a number above 0, or None: null). Returns the record's path."""
    sid = str(uuid.uuid4())
    record = {"record": "gov-launch", "format": 1, "session_id": sid, "started_at": started, "role": role,
              "ticket": ticket, "projection_usd": projection}
    return b.write(Path(project) / LAUNCHES_REL / f"{sid}.json", json.dumps(record, indent=2) + "\n")


def plant_launch_without_projection(project, ticket, *, started=PAST, role="engineer"):
    """A launch record with no ``projection_usd`` key at all (a launch from before the key)."""
    sid = str(uuid.uuid4())
    record = {"record": "gov-launch", "format": 1, "session_id": sid, "started_at": started, "role": role,
              "ticket": ticket}
    return b.write(Path(project) / LAUNCHES_REL / f"{sid}.json", json.dumps(record, indent=2) + "\n")


def plant_marker(project, ticket, cost=10.05, projection=5.0):
    """A brake marker as the brake writes it: ``<project>/.gov-runtime/spend/braked/<ticket>.json``."""
    data = {"ticket": ticket, "cost_usd": cost, "projection_usd": projection, "at": PAST}
    return b.write(Path(project) / BRAKED_REL / f"{ticket}.json", json.dumps(data, indent=2) + "\n")


def plant_over(project, ticket, projection=5.0, cost_parts=(4.05, 3.0, 3.0), *, started=PAST):
    """A ticket whose measured cost (the sum of ``cost_parts``, 10.05 by default) is 2.01 times its projection."""
    plant_launch(project, ticket, projection, started=started)
    for part in cost_parts:
        plant_session(project, ticket, part, started=started)


# --------------------------------------------------------------------------
# Running gov spend, reading what it wrote
# --------------------------------------------------------------------------

def spend(box, *args, cwd=None):
    """``gov spend <args>`` as a child process, from ``cwd`` (default: the project, the command's default root)."""
    return b.run_gov(box, cwd or box.project, "spend", *args)


def assert_ok(run):
    assert run.returncode == 0, f"{run.describe()}\n(expected exit code 0)"
    return run


def said(run):
    return run.stdout + "\n" + run.stderr


def has_amount(text, amount):
    """``amount`` (a text such as ``4.50``) stands in ``text`` as a whole number, not inside a longer one."""
    return re.search(rf"(?<![\d.]){re.escape(amount)}(?!\d)", text) is not None


def brake_state(line):
    """``braked``, ``not braked`` or None: the brake state a ``sum`` line gives."""
    if re.search(r"\bnot braked\b", line):
        return "not braked"
    if re.search(r"\bbraked\b", line):
        return "braked"
    return None


def lines_of(run, ticket):
    return [line for line in run.stdout.splitlines() if ticket in line]


def one_line(run, ticket):
    lines = lines_of(run, ticket)
    assert len(lines) == 1, f"`gov spend sum` has {len(lines)} lines holding {ticket}, not one\n{run.describe()}"
    return lines[0]


@dataclass(frozen=True)
class Written:
    """What a project holds of the brake: the markers (name to parsed JSON), the lines of ``brakes.jsonl`` and the files
    of the inbox folder (name to text)."""
    markers: dict
    lines: list
    inbox: dict

    def of_kind(self, kind):
        return [line for line in self.lines if line.get("kind") == kind]


def _json(path, what):
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except ValueError:
        raise AssertionError(f"{what} {path} is not JSON: {Path(path).read_text(encoding='utf-8')[:300]!r}") from None
    assert isinstance(data, dict), f"{what} {path} is not a JSON object"
    return data


def written(project):
    project = Path(project)
    braked = project / BRAKED_REL
    markers = {p.name: _json(p, "the marker") for p in sorted(braked.glob("*.json"))} if braked.is_dir() else {}
    log = project / BRAKES_REL
    lines = []
    if log.is_file():
        for number, text in enumerate(log.read_text(encoding="utf-8").splitlines(), 1):
            if text.strip():
                try:
                    lines.append(json.loads(text))
                except ValueError:
                    raise AssertionError(f"{log} line {number} is not JSON: {text[:300]!r}") from None
    inbox_dir = project / INBOX_REL
    inbox = {p.name: p.read_text(encoding="utf-8", errors="replace")
             for p in sorted(inbox_dir.iterdir()) if p.is_file()} if inbox_dir.is_dir() else {}
    return Written(markers, lines, inbox)


def assert_nothing_written(project, what=""):
    w = written(project)
    assert not w.markers and not w.lines and not w.inbox, (
        f"the brake wrote something {what}: markers {sorted(w.markers)}, brakes.jsonl lines {w.lines}, "
        f"inbox items {sorted(w.inbox)}")


def assert_one_brake(project, ticket, cost, projection):
    """Exactly one brake record, one marker and one inbox item for ``ticket``; returns the three."""
    w = written(project)
    brakes = [line for line in w.of_kind("brake") if line.get("ticket") == ticket]
    assert len(brakes) == 1, f"{len(brakes)} brake records for {ticket}, not one: {w.lines}"
    assert sorted(k for k in brakes[0] if k in ("kind", "ticket", "cost_usd", "projection_usd", "at")) == sorted(
        ("kind", "ticket", "cost_usd", "projection_usd", "at")), f"the brake record lacks keys: {brakes[0]}"
    assert abs(float(brakes[0]["cost_usd"]) - cost) < 0.005 and abs(float(brakes[0]["projection_usd"]) - projection) < 0.005, (
        f"the brake record's cost and projection are not {cost} and {projection}: {brakes[0]}")
    assert isinstance(brakes[0]["at"], str) and STAMP.fullmatch(brakes[0]["at"]), f"the brake record's at: {brakes[0]}"
    marker_name = f"{ticket}.json"
    assert marker_name in w.markers, f"no marker {marker_name}; the markers: {sorted(w.markers)}"
    marker = w.markers[marker_name]
    assert marker.get("ticket") == ticket and abs(float(marker["cost_usd"]) - cost) < 0.005 \
        and abs(float(marker["projection_usd"]) - projection) < 0.005 and "at" in marker, (
        f"the marker does not hold the ticket, cost, projection and time: {marker}")
    items = {name: text for name, text in w.inbox.items() if ticket in text}
    assert len(items) == 1, (f"{len(items)} inbox items name {ticket}, not one; the inbox holds {sorted(w.inbox)}")
    text = next(iter(items.values()))
    assert has_amount(text, f"{cost:.2f}") and has_amount(text, f"{projection:.2f}"), (
        f"the inbox item does not give the cost {cost:.2f} and the projection {projection:.2f}:\n{text}")
    return brakes[0], marker, text


# --------------------------------------------------------------------------
# Snapshots of a tree
# --------------------------------------------------------------------------

def snapshot(root, skip=()):
    """``{relative path: sha256}`` of every file under ``root`` (links not followed), except ``.git`` and the relative
    prefixes in ``skip``."""
    root = Path(root)
    found = {}
    for here, folders, names in os.walk(root):
        rel = os.path.relpath(here, root)
        folders[:] = [f for f in folders if f != ".git" and os.path.normpath(os.path.join(rel, f)) not in skip]
        for name in names:
            path = Path(here) / name
            key = os.path.normpath(os.path.join(rel, name))
            try:
                found[key] = hashlib.sha256(path.read_bytes()).hexdigest() if not path.is_symlink() else "link"
            except OSError as error:
                found[key] = f"unreadable: {error}"
    return found


def difference(before, after):
    added = sorted(set(after) - set(before))
    removed = sorted(set(before) - set(after))
    changed = sorted(k for k in set(before) & set(after) if before[k] != after[k])
    return added, removed, changed


# --------------------------------------------------------------------------
# Launching (W2-60a's launcher over its stand-in CLI)
# --------------------------------------------------------------------------

def session_files(project):
    folder = Path(project) / SESSIONS_REL
    return sorted(p.name for p in folder.iterdir() if not p.name.startswith(".")) if folder.is_dir() else []


def launch_files(project):
    folder = Path(project) / LAUNCHES_REL
    return sorted(p.name for p in folder.iterdir() if not p.name.startswith(".")) if folder.is_dir() else []


def dispatch_yaml(notifier_argv):
    """``governance/project/dispatch.yaml``'s text with the required keys and ``notifier_command`` the given argv."""
    return yaml.safe_dump({"dispatch": {"max_leads": 2, "stagger_s": 1, "cpu_band": 0.8, "integration_branch": "main",
                                        "worktrees_root": "work", "notifier_command": list(notifier_argv)}},
                          sort_keys=False)

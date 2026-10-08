"""Support code for the ``gov status`` half of the W1-32 acceptance tests.

The command is used only through its public interface: ``gov status --json``,
its API-0002 envelope and its exit code. What the cases compare it with is
also public: ``gov.tasks`` (W1-09), ``gov readiness``, ``gov doctor``,
``gov telemetry`` and ``gov pause``, each run on the same temporary project.

**No case reads this repository's state.** Every project is W1-13's temporary
project (a git repository made from scratch, with the kernel's OpenSpec schema,
tickets, records and a loaded store). The code under test is this worktree's
``src/``. HOME is a temporary folder, so the freeze mirror (DEC-429) and the
session logs the counter would read are never this machine's.

What the cases hold ``gov status --json`` to (README, "The answer"):

- the answer has the six parts of the ticket's KPI line under these names:
  ``tickets`` (with ``ready``, ``blocked`` and ``claimed``),
  ``decision_packages``, ``readiness``, ``governance_share``, ``pause`` and
  ``doctor``. They stand in ``result``; when the command ends with an error of
  its own they stand in ``error.details`` (``parts`` reads both);
- a list of tickets, packages or specifications is a list of ids, a list of
  objects that carry the id, or a map from the id (``ids``, ``entry``);
- a part that was not read says so: ``read: false`` and a non-empty
  ``reason`` (``unread_reason``). The governance share uses the counter's own
  word, ``"not measured"``.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

for _suite in ("W1-13", "W1-28", "W1-09", "W1-07"):
    _path = str(Path(__file__).resolve().parents[1] / _suite)
    if _path not in sys.path:
        sys.path.insert(0, _path)

import w1_13_support as spec_support  # noqa: E402  the temporary project: changes, tickets, the store
import w1_28_support as pause_support  # noqa: E402  ``gov pause`` on a temporary project

cli_support = spec_support.cli_support
tasks_support = spec_support.tasks_support

REPO_ROOT = Path(__file__).resolve().parents[3]
COMMAND = "status"
NOT_IMPLEMENTED = cli_support.NOT_IMPLEMENTED

TICKETS, PACKAGES, READINESS, SHARE, PAUSE, DOCTOR = ("tickets", "decision_packages", "readiness",
                                                      "governance_share", "pause", "doctor")
PARTS = (TICKETS, PACKAGES, READINESS, SHARE, PAUSE, DOCTOR)
READY, BLOCKED, CLAIMED = "ready", "blocked", "claimed"
TICKET_LISTS = (READY, BLOCKED, CLAIMED)
PAUSED = "paused"
NOT_MEASURED = "not measured"            # the counter's word (W1-31), and ``gov close``'s
KEY_READ, KEY_REASON = "read", "reason"
ID_KEYS = ("id", "ticket", "specification", "package", "change", "name")

STORE_REL = ".gov-runtime/store.db"      # the store ``gov.store.load`` writes (W1-10)
FREEZE_FLAG_REL = pause_support.FREEZE_FLAG_REL
GATES_REL = "spec/gates"                 # where a product repository holds its gate records (ADR-0002 section 5)
PACKAGE_TYPE, OPEN_STATUS = "decision-package", "PROPOSED"   # DEC-308: open while PROPOSED

# The fixture's tickets and records.
T_READY, T_OTHER_READY, T_WAITS, T_DEPENDS, T_IN_PROGRESS, T_CLAIMED, T_CLOSED = (
    "TST-s001", "TST-s002", "TST-s003", "TST-s004", "TST-s005", "TST-s006", "TST-s007")
HOLDER = "engineer:w1-32-session-a"      # DEC-292: by convention ``<role>:<session>``
DP_OPEN, DP_OTHER_OPEN, DP_ANSWERED = "DP-9101", "DP-9102", "DP-9103"
SPEC_CLOSED, CHANGE_CLOSED = "SPEC-zs01", "zs01-ready-feature"
SPEC_OPEN, CHANGE_OPEN = "SPEC-zs02", "zs02-open-feature"
GAP_TICKET = "TST-g101"
ROW_LINKED, ROW_UNLINKED = 7, 20         # two rows a FULL specification requires


# --------------------------------------------------------------------------
# The temporary project
# --------------------------------------------------------------------------

def make_project(directory, driver):
    """W1-13's temporary project, empty: no ticket, no change, no record."""
    project = spec_support.Project(directory, driver)
    assert REPO_ROOT not in (project.root, *project.root.parents), f"{project.root} is inside this repository"
    tasks_support.write(project.root, ".gitignore", ".gov-runtime/\n.tickets/.claims/\n")   # DEC-297
    return project


def package(project, record_id, status, tickets=()):
    """A decision package as W1-09's suite records one: a record of type ``decision-package`` (DEC-308)."""
    return tasks_support.write(project.root, f"{GATES_REL}/{record_id}.md",
                               tasks_support.record_text(record_id, PACKAGE_TYPE, status, constrains=list(tickets)))


def open_rows():
    """The rows of a FULL specification with two required rows open: one linked to a gap ticket, one not."""
    rows = spec_support.complete_rows()
    spec_support.edit(rows, ROW_LINKED, state="MISSING", evidence=[], gap_ticket=GAP_TICKET)
    spec_support.edit(rows, ROW_UNLINKED, state="BLOCKED", evidence=[], reason="waits on an answer", gap_ticket=None)
    return rows


def populate(project):
    """Tickets in every queue, two open decision packages and an answered one, a closed and an open specification."""
    project.ticket(T_READY, "W9-01")
    project.ticket(T_OTHER_READY, "W9-02")
    project.ticket(T_WAITS, "W9-03")
    project.ticket(T_CLOSED, "W9-07", status="closed")
    project.ticket(T_DEPENDS, "W9-04", deps=[T_WAITS])
    project.ticket(T_IN_PROGRESS, "W9-05", status="in_progress")
    project.ticket(T_CLAIMED, "W9-06")
    package(project, DP_OPEN, OPEN_STATUS, [T_WAITS])
    package(project, DP_OTHER_OPEN, OPEN_STATUS, [])
    package(project, DP_ANSWERED, "ACCEPTED", [T_READY])
    project.specification(spec_support.complete_rows(), spec_id=SPEC_CLOSED, change=CHANGE_CLOSED)
    project.specification(open_rows(), spec_id=SPEC_OPEN, change=CHANGE_OPEN)
    settle(project)
    project.driver.call("gov.tasks", "claim", project.root, T_CLAIMED, HOLDER)
    return project


def commit(project, message="fixture, not loaded into the store"):
    """Commit the working tree without loading the store: the store is then older than the commit.

    The claims folder is ignored (DEC-297), so a plain ``git add -A`` leaves it out.
    """
    tasks_support.git(project.root, "add", "-A")
    tasks_support.git(project.root, "commit", "-q", "--allow-empty", "-m", message)


def settle(project):
    """Commit everything and load the store, as W1-13's ``Project.settle`` does for a project without claims."""
    commit(project, "fixture")
    project.driver.call("gov.store", "load", project.root)
    project._settled = tasks_support.git(project.root, "rev-parse", "HEAD").strip()


# --------------------------------------------------------------------------
# Running the command line
# --------------------------------------------------------------------------

def gov(project, sandbox, *args):
    """``gov <args>`` in the project as it is: nothing is committed and the store is not loaded first."""
    return cli_support.run_gov_with_code(REPO_ROOT, project.root, sandbox, *args)


def status(project, sandbox, *args):
    """``gov status --json`` in the project as it is."""
    return gov(project, sandbox, COMMAND, "--json", *args)


def parts(run, interface):
    """The six parts of the answer; a missing part fails the case by its name.

    The parts stand in ``result``; when the command ends with an error of its
    own (it reports what it could not read as a refusal), in ``error.details``.
    """
    envelope = cli_support.assert_envelope(run, interface, command=COMMAND)
    if not envelope["ok"]:
        code = envelope["error"]["code"]
        assert code != NOT_IMPLEMENTED, f"gov status is not built: {code}\n{run.describe()}"
        assert run.returncode != 2, f"gov status ended as a usage error\n{run.describe()}"
    answer = envelope["result"] if envelope["ok"] else envelope["error"]["details"]
    missing = [name for name in PARTS if name not in answer]
    assert not missing, f"gov status --json reports no part named {missing}\n{run.describe()}"
    tickets = answer[TICKETS]
    if unread_reason(tickets) is None:
        absent = [name for name in TICKET_LISTS if not isinstance(tickets, dict) or name not in tickets]
        assert not absent, f"the tickets part has no {absent}\n{run.describe()}"
    return answer


def answered(run, interface):
    """The parts of a run that succeeded: ``ok`` true, exit code 0."""
    answer = parts(run, interface)
    assert run.returncode == 0 and run.envelope()["ok"] is True, \
        f"gov status did not succeed on a project whose every source can be read\n{run.describe()}"
    return answer


# --------------------------------------------------------------------------
# Reading a part
# --------------------------------------------------------------------------

def text_of(value):
    """Everything a part says, as one string."""
    return json.dumps(value, sort_keys=True)


def _id_of(item):
    if isinstance(item, str):
        return item
    if isinstance(item, dict):
        for key in ID_KEYS:
            if isinstance(item.get(key), str):
                return item[key]
    return None


def _items(value):
    """``id -> detail`` of a list of ids, a list of objects that carry the id, or a map from the id."""
    if isinstance(value, dict) and unread_reason(value) is None:
        for key in ("items", "tickets", "packages", "specifications", "open"):
            if isinstance(value.get(key), (list, dict)) and not any(k in value for k in ID_KEYS):
                return _items(value[key])
        return {key: detail for key, detail in value.items() if key not in (KEY_READ, KEY_REASON)}
    if isinstance(value, list):
        found = {}
        for item in value:
            name = _id_of(item)
            assert name is not None, f"an entry carries no id (one of {ID_KEYS}): {text_of(item)}"
            found[name] = item
        return found
    raise AssertionError(f"not a list of ids, a list of objects with an id, or a map from the id: {text_of(value)}")


def ids(value):
    """The ids a list of the answer names, sorted."""
    return sorted(_items(value))


def entry(value, name):
    """What the list says of ``name``."""
    items = _items(value)
    assert name in items, f"{name} is not in {sorted(items)}"
    return items[name]


def unread_reason(part):
    """The reason a part gives for not having been read; None when it does not say it was not read.

    A part that was not read is an object with ``read: false`` and a non-empty
    string under ``reason``.
    """
    if not isinstance(part, dict) or part.get(KEY_READ, True) is not False:
        return None
    reason = part.get(KEY_REASON)
    assert isinstance(reason, str) and reason.strip(), \
        f"a part says it was not read and gives no reason: {text_of(part)}"
    return reason


def unread_entries(value):
    """Every object, at any depth of ``value``, that says it was not read (``read: false``, with its reason)."""
    found = []
    if isinstance(value, dict):
        if unread_reason(value) is not None:
            found.append(value)
        for item in value.values():
            found.extend(unread_entries(item))
    elif isinstance(value, list):
        for item in value:
            found.extend(unread_entries(item))
    return found


def assert_not_read(part, what, within=()):
    """``part``, or one of its lists named in ``within``, says it was not read, with a reason. Returns the reasons."""
    reasons = [unread_reason(part)]
    if isinstance(part, dict):
        reasons += [unread_reason(part.get(name)) for name in within]
    reasons = [reason for reason in reasons if reason is not None]
    assert reasons, (f"{what}: the answer does not say it was not read (read: false, with a reason); "
                     f"it says {text_of(part)[:600]}")
    return reasons


def numbers_in(value):
    """Every number in a part, at any depth (a bool is not a number)."""
    if isinstance(value, bool):
        return []
    if isinstance(value, (int, float)):
        return [value]
    if isinstance(value, dict):
        return [number for item in value.values() for number in numbers_in(item)]
    if isinstance(value, list):
        return [number for item in value for number in numbers_in(item)]
    return []


def paused(answer):
    """``pause.paused`` of the answer: true, false, or None when the part says it was not read."""
    part = answer[PAUSE]
    assert isinstance(part, dict), f"the pause part is not an object: {text_of(part)}"
    if unread_reason(part) is not None:
        assert part.get(PAUSED) is not False, f"a pause state that was not read says not paused: {text_of(part)}"
        return None
    assert isinstance(part.get(PAUSED), bool), f"the pause part has no true or false under {PAUSED!r}: {text_of(part)}"
    return part[PAUSED]


# --------------------------------------------------------------------------
# What a command that only reads leaves alone
# --------------------------------------------------------------------------

def state(project, sandbox):
    """The files (derived state included), ``git status``, the refs, and what lies outside the project."""
    return {
        "porcelain": cli_support.porcelain(project.root),
        "ignored": tasks_support.git(project.root, "status", "--porcelain", "--ignored"),
        "git": cli_support.git_state(project.root),
        "tree": cli_support.snapshot(project.root, skip=(".git",)),
        "home": cli_support.snapshot(sandbox.home, skip=()),
        "tmp": cli_support.snapshot(sandbox.tmpdir, skip=()),
        "elsewhere": cli_support.snapshot(sandbox.elsewhere, skip=()),
    }


def assert_unchanged(before, after, run):
    assert after["porcelain"] == before["porcelain"], \
        f"git status --porcelain changed:\n{after['porcelain']}\n{run.describe()}"
    assert after["ignored"] == before["ignored"], \
        f"an ignored file appeared or went:\n{after['ignored']}\n{run.describe()}"
    assert after["git"] == before["git"], f"HEAD or a ref moved\n{run.describe()}"
    for place in ("tree", "home", "tmp", "elsewhere"):
        changed = cli_support.snapshot_difference(before[place], after[place])
        assert not changed, f"gov status changed files ({place}): {changed}\n{run.describe()}"


def flag_state(path):
    """None when nothing is at ``path``; "sandbox placeholder" for a character device (W1-28's reading, DEC-402)."""
    import stat

    try:
        found = os.lstat(path)
    except FileNotFoundError:
        return None
    if stat.S_ISCHR(found.st_mode):
        return "sandbox placeholder"
    if stat.S_ISREG(found.st_mode) and found.st_size == 0:
        return None
    return (found.st_mode, found.st_ino, found.st_size, found.st_mtime_ns)

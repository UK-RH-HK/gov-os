"""The landing step of a pass (part b: S1 the claim and the batch, S2 the closes, S3 the nightly hold).

``step`` finalises a landing that has ended, then claims ``land.txt`` and launches the project's ``landing_command``
as one batch, when nothing holds it. A landing held is never a failed pass: the reason is the status's ``land`` text.

The claim is an atomic rename ``land.txt`` -> ``land-claimed-<land id>.txt`` made before the launch, so an approval is
never sent twice: a crash after the claim leaves the claimed file, never a second batch. The approvals are read from
the claimed file (a line appended between the first reading and the rename is part of it, and so of the batch).

``commit_records`` is the record commit a close makes: it retries while another process holds ``index.lock``.
"""

from __future__ import annotations

import datetime
import os
import re
import time
from pathlib import Path

from gov.dispatch import procs
from gov.dispatch import state as states
from gov.dispatch.shell import CommandFailed
from gov.resources import machine
from gov.util.gitenv import git_env

APPROVAL = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._+-]*=[0-9a-f]{12}$")
CLAIMED = "land-claimed-"
DONE = "land-done.txt"
TOKEN = "{approvals}"
ITEM_SUFFIX = ".land.txt"
TICKETS = ".tickets"
NO_INPUT = "/dev/null"


class CommitFailed(RuntimeError):
    """A record commit that did not land (after its attempts)."""


# --- the approvals ------------------------------------------------------------------------------------------------

def split_lines(lines: list[str]) -> tuple[list[str], list[str]]:
    """``(approvals, not sent)``: the lines of the form ``<W2>=<12-hex>`` (once each, in order) and the others."""
    good = list(dict.fromkeys(line for line in lines if APPROVAL.match(line)))
    return good, [line for line in lines if not APPROVAL.match(line)]


def done_set(state: states.State, besides: str | None = None) -> set[str]:
    """The approvals already in ``land-done.txt`` (the ones of land id ``besides`` left out)."""
    out = set()
    for line in state.lines(DONE):
        parts = line.split()
        if besides is None or parts[-1] != besides:
            out.add(parts[0])
    return out


def w2_of(approval: str) -> str:
    return approval.partition("=")[0]


def _claimed(state: states.State) -> list[Path]:
    try:
        return sorted(p for p in state.dir.iterdir() if p.name.startswith(CLAIMED) and p.name.endswith(".txt"))
    except OSError:
        return []


def _land_id_of(path: Path) -> str:
    return path.name[len(CLAIMED):-len(".txt")]


def new_id(state: states.State, moment: datetime.datetime) -> str:
    """``land-<UTC stamp>``; a second already used (by a landing finalised in the same second) moves on."""
    moment = moment.astimezone(datetime.timezone.utc)
    while True:
        land_id = "land-" + moment.strftime("%Y%m%dT%H%M%SZ")
        if not state.written(land_id + ITEM_SUFFIX) and not (state.logs / land_id).exists():
            return land_id
        moment += datetime.timedelta(seconds=1)


# --- the end of a landing -----------------------------------------------------------------------------------------

def finalise(state: states.State, now: datetime.datetime) -> list[dict]:
    """Finalise each claimed landing whose exit file is there: its done lines, its inbox item, the claimed file
    removed (in that order, so a pass that dies half way is finished by the next). What was finalised, for the status."""
    out = []
    for path in _claimed(state):
        land_id = _land_id_of(path)
        exit_file = state.exit_file(land_id)
        if not exit_file.exists():
            continue
        try:
            code = int(exit_file.read_text(encoding="utf-8").strip())
        except (OSError, ValueError):
            code = 1
        try:
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        lines = [line.strip() for line in lines if line.strip() and not line.lstrip().startswith("#")]
        good, bad = split_lines(lines)
        sent = [a for a in good if a not in done_set(state, land_id)]
        recorded = {line.split()[0] for line in state.lines(DONE) if line.split()[-1] == land_id}
        text = states.stamp(now)
        for approval in sent:
            if approval not in recorded:
                state.append(DONE, f"{approval} {text} {code} {land_id}")
        status = "landed" if code == 0 else f"failed (exit {code})"
        item = [f"log: {land_id}", f"W2: {' '.join(w2_of(a) for a in sent)}", f"status: {status}", "kind: land"]
        state.write_item(land_id + ITEM_SUFFIX, item)
        try:
            path.unlink()
        except OSError:
            pass
        out.append({"land_id": land_id, "status": status, "W2": [w2_of(a) for a in sent]})
    return out


# --- the nightly hold (S3) ------------------------------------------------------------------------------------------

def _clock(text: str) -> datetime.time:
    return datetime.time(int(text[:2]), int(text[3:]))


def nightly(hold: dict | None, root: Path, now: datetime.datetime) -> str | None:
    """The status text when the nightly hold is on now, else None. The window starts at ``from`` (local time) and ends
    at the next ``until``; with a ``marker`` it ends sooner, when the marker's mtime is later than that ``from``."""
    if not hold:
        return None
    local = now.astimezone().replace(tzinfo=None)
    begin_t, end_t = _clock(hold["from"]), _clock(hold["until"])
    if begin_t == end_t:
        return None
    begin = datetime.datetime.combine(local.date(), begin_t)
    if begin > local:
        begin -= datetime.timedelta(days=1)
    end = datetime.datetime.combine(begin.date() + datetime.timedelta(days=0 if end_t > begin_t else 1), end_t)
    if not begin <= local < end:
        return None
    marker = hold.get("marker")
    if marker:
        try:
            started = datetime.datetime.fromtimestamp((Path(root) / marker).stat().st_mtime)
        except OSError:
            started = None
        if started is not None and started > begin:
            return None
    return f"held for the nightly until it starts (from {hold['from']}, at the latest {hold['until']})"


# --- the closes (S2) ------------------------------------------------------------------------------------------------

def _frontmatter(text: str) -> dict:
    lines = text.splitlines()
    out: dict[str, str] = {}
    if not lines or lines[0].strip() != "---":
        return out
    for line in lines[1:]:
        if line.strip() == "---":
            break
        key, sep, value = line.partition(":")
        if sep and not line.startswith((" ", "\t", "-")):
            out.setdefault(key.strip(), value.split(" #")[0].strip().strip("'\""))
    return out


def ticket_ids(root: Path, w2s: set[str]) -> set[str]:
    """The ticket ids (``id:``) of the tickets whose ``external-ref:`` or ``wbs_id:`` is one of ``w2s``."""
    out = set()
    try:
        files = sorted((Path(root) / TICKETS).glob("*.md"))
    except OSError:
        return out
    for path in files:
        try:
            fields = _frontmatter(path.read_text(encoding="utf-8", errors="replace"))
        except OSError:
            continue
        if fields.get("external-ref") in w2s or fields.get("wbs_id") in w2s:
            out.add(fields.get("id") or path.stem)
    return out


def _tracked_changes(ctx) -> list[str]:
    done = ctx.runner.git(ctx.root, "status", "--porcelain=v1", "-z", "--untracked-files=no")
    if done.code != 0:
        raise CommandFailed(f"`git status` ended with {done.code}: {done.err.strip()}")
    paths, parts = [], done.out.split("\0")
    index = 0
    while index < len(parts):
        entry = parts[index]
        index += 1
        if len(entry) > 3:
            paths.append(entry[3:])
            if entry[0] in "RC" and index < len(parts):  # a rename or a copy names its origin in the next field
                paths.append(parts[index])
                index += 1
    return paths


def _index_locked(ctx) -> bool:
    done = ctx.runner.git(ctx.root, "rev-parse", "--absolute-git-dir")
    folder = Path(done.out.strip()) if done.code == 0 and done.out.strip() else Path(ctx.root) / ".git"
    return (folder / "index.lock").exists()


def close_arguments(table: dict, marker: str) -> dict[int, set[str]]:
    """The arguments of every process matching the close marker, by pid. A close run under a shell wrapper
    (``sh -c "cd x && <close command> <id>"``) is the wrapper in the jobs (its child is part of it), but the ids are
    the child's own arguments: so the children are read too (not a lead, not this process)."""
    own, found = os.getpid(), {}
    for pid, info in table.items():
        if pid == own or marker not in info["cmdline"]:
            continue
        arguments = procs.arguments(pid)
        if procs.lead_marker(arguments) is None:
            found[pid] = set(arguments)
    return found


def conflicting_close(ctx, running, w2s: set[str], changes: list[str], table: dict | None = None) -> str | None:
    """Why a running close holds the landing back, or None: a ticket it closes is in the set, or it is committing its
    records (``index.lock`` there, or every tracked change under ``close_record_paths``)."""
    closes = [job for job in running.jobs if job["kind"] == "close"]
    if not closes:
        return None
    wanted = w2s | ticket_ids(ctx.root, w2s)
    marker = ctx.conf.job_markers.get("close")
    table = machine.processes() if table is None else table
    for pid, arguments in sorted(close_arguments(table, marker).items() if marker else []):
        shared = sorted(arguments & wanted)
        if shared:
            return f"a close (pid {pid}) is closing {', '.join(shared)}, in the landing"
    prefixes = ctx.conf.close_record_paths
    if _index_locked(ctx):
        return f"a close (pid {closes[0]['pid']}) is committing its records (index.lock)"
    if changes and prefixes and all(any(path.startswith(p) for p in prefixes) for path in changes):
        return f"a close (pid {closes[0]['pid']}) is committing its records ({len(changes)} changed under " \
               f"close_record_paths)"
    return None


def commit_records(root, paths, message, trailers=(), attempts=3, wait_s=2) -> str:
    """Commit only ``paths`` in ``root`` (``git add`` then ``git commit -- <paths>``), retrying while another process holds
    ``index.lock``. The new commit's id; ``CommitFailed`` after ``attempts`` or on any other failure."""
    import subprocess

    root = Path(root)
    paths = [str(p) for p in paths]
    if isinstance(trailers, dict):
        trailers = [f"{key}: {value}" for key, value in trailers.items()]
    trailing = [part for line in trailers for part in ("--trailer", line)]
    env = git_env(root)
    why = ""
    for attempt in range(max(1, attempts)):
        for argv in (["add", "--", *paths], ["commit", "-m", message, *trailing, "--", *paths]):
            done = subprocess.run(["git", "-C", str(root), *argv], env=env, capture_output=True, text=True,
                                  errors="replace", stdin=subprocess.DEVNULL)
            if done.returncode != 0:
                why = (done.stderr or done.stdout).strip()
                break
        else:
            head = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"], env=env, capture_output=True,
                                  text=True, stdin=subprocess.DEVNULL)
            return head.stdout.strip()
        if "index.lock" not in why:
            raise CommitFailed(f"`git {argv[0]}` failed: {why}")
        if attempt + 1 < attempts:
            time.sleep(wait_s)
    raise CommitFailed(f"another git process held index.lock through {attempts} attempts: {why}")


# --- the step ---------------------------------------------------------------------------------------------------------

def command_for(template: list[str], approvals: list[str]) -> list[str]:
    """``landing_command`` with the argument ``{approvals}`` replaced by the approvals (appended when it is absent)."""
    if TOKEN not in template:
        return [*template, *approvals]
    out: list[str] = []
    for argument in template:
        out += approvals if argument == TOKEN else [argument]
    return out


def step(ctx, running, now: datetime.datetime, spawn) -> dict:
    """The pass's landing step; the fields it adds to the status. ``spawn(argv, cwd, brief, log, exit_file)`` starts the
    batch detached."""
    state, conf = ctx.state, ctx.conf
    out = {"land": None, "land_notes": [], "land_hold": None, "land_claimed": None, "land_finalised": []}
    out["land_finalised"] = finalise(state, now)
    for done in out["land_finalised"]:
        out["land_notes"].append(f"{done['land_id']} finalised ({done['status']}): {' '.join(done['W2'])}")
    lines = state.lines("land.txt")
    good, bad = split_lines(lines)
    out["land_notes"] += [f"not sent: {line} (not of the form <W2>=<12-hex>)" for line in bad]
    fresh = [a for a in good if a not in done_set(state)]
    out["land_hold"] = nightly(conf.nightly_hold, ctx.root, now)
    unfinished = [_land_id_of(p) for p in _claimed(state)]
    if unfinished:
        out["land"] = f"{', '.join(unfinished)} is still running (one landing at a time)"
        return out
    if not fresh:
        out["land"] = "nothing to land" if not out["land_hold"] else out["land_hold"]
        return out
    why = out["land_hold"] or _held(ctx, running, {w2_of(a) for a in fresh})
    if why:
        out["land"] = why
        return out
    land_id = new_id(state, now)
    claimed = state.file(f"{CLAIMED}{land_id}.txt")
    try:
        os.rename(state.file("land.txt"), claimed)  # atomic; before the launch
    except FileNotFoundError:
        out["land"] = "land.txt was taken before the claim"
        return out
    good, _ = split_lines([line.strip() for line in claimed.read_text(encoding="utf-8", errors="replace").splitlines()
                           if line.strip() and not line.lstrip().startswith("#")])
    batch = [a for a in good if a not in done_set(state)]
    log, exit_file = state.logs / land_id, state.exit_file(land_id)
    argv = command_for(conf.landing_command, batch)
    try:
        spawn(argv, Path(ctx.root), Path(NO_INPUT), log, exit_file)
    except OSError as error:
        log.write_text(f"the landing command could not be started: {error}\n", encoding="utf-8")
        exit_file.write_text("127\n", encoding="utf-8")
    out["land_claimed"] = {"land_id": land_id, "approvals": batch}
    out["land"] = f"claimed {land_id}: {' '.join(batch)}"
    return out


def _held(ctx, running, w2s: set[str]) -> str | None:
    """Why this pass may not claim (none of the nightly: that is read first), or None."""
    conf = ctx.conf
    if not conf.landing_command:
        return "no landing_command is configured"
    try:
        changes = _tracked_changes(ctx)
        why = conflicting_close(ctx, running, w2s, changes)
        if why:
            return why
        if _index_locked(ctx):
            return "the root's index is locked (index.lock)"
        if changes:
            return f"the root has tracked changes ({len(changes)}): {', '.join(changes[:5])}"
        branch = ctx.runner.git(ctx.root, "rev-parse", "--abbrev-ref", "HEAD")
    except CommandFailed as failure:
        return f"git could not be read: {failure}"
    if branch.code != 0 or branch.out.strip() != conf.integration_branch:
        return f"the root is on {branch.out.strip() or 'no branch'}, not on {conf.integration_branch}"
    return None

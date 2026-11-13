"""The machine-wide registry of live Gov OS sessions (W2-20 S1, S3; W2-M188, W2-M244, W2-M262).

One file per session, ``~/.gov-os/machine/sessions/<pid>.json``, whichever repository started it::

    {"pid": 4242, "repository": "/path/to/repo", "ticket": "DAEO-xxxx", "role": "engineer", "started": "..."}

An entry whose process is gone is removed by the read that finds it (``cleared``), and so is one whose pid now
belongs to another process: the entry records its process's boot and start (``boot``, ``start_ticks``), and a pid
alive with another start, or started after the entry's ``started``, is a reused pid (review F6, a WSL restart). An
entry that cannot be read is
named, and the gate shuts on it: a session the gate cannot see is never treated as absent.

Each live session's memory is its process tree's resident memory, less every subtree that is another registered
session's own: a worker started from its lead's tree is charged once, as its own session (failure line 6).
"""

from __future__ import annotations

import datetime
import json
import os
import tempfile
from pathlib import Path

from gov.resources import machine
from gov.resources.config import machine_dir

SESSIONS = "sessions"


def folder() -> Path:
    return machine_dir() / SESSIONS


def register(pid: int, repository, ticket: str, role: str, **extra) -> dict:
    """Enter one session, whole or not at all (a reader never sees half an entry)."""
    from gov.cli.errors import GovError

    if isinstance(pid, bool) or not isinstance(pid, int) or pid <= 0:
        raise GovError("RESOURCE_REGISTER_INVALID", f"{pid!r} is not a process id", {"pid": pid})
    entry = {"pid": pid, "repository": str(Path(repository).resolve()), "ticket": ticket, "role": role,
             "started": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"), **extra}
    found = machine.identity(pid)  # the process's own boot and start, so a reused pid is never taken for it (F6)
    if found is not None:
        entry.update({"boot": found["boot"], "start_ticks": found["start_ticks"]})
    place = folder()
    place.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", dir=place, prefix=".entry-", suffix=".tmp", delete=False) as handle:
        json.dump(entry, handle)
    os.replace(handle.name, place / f"{pid}.json")
    return entry


def unregister(pid: int) -> None:
    try:
        (folder() / f"{pid}.json").unlink()
    except OSError:
        pass


def sessions() -> tuple[list[dict], list[dict], str | None]:
    """``(live, cleared, why)``: the live entries, the stale ones removed now, and why any entry is unreadable."""
    live, cleared, unreadable = [], [], []
    place = folder()
    try:
        paths = sorted(place.glob("*.json")) if place.exists() else []
    except OSError as error:
        return [], [], f"{place}: {error}"
    for path in paths:
        try:
            entry = json.loads(path.read_text(encoding="utf-8"))
            pid = entry["pid"] if isinstance(entry, dict) else None
            if isinstance(pid, bool) or not isinstance(pid, int) or pid <= 0:
                raise ValueError("pid must be a positive integer")
        except FileNotFoundError:  # cleared by another reader meanwhile
            continue
        except (OSError, ValueError, KeyError, TypeError) as error:
            unreadable.append(f"{path}: {error}")
            continue
        if machine.alive(pid) and machine.same_process(pid, entry):
            live.append(entry)
        else:
            try:
                path.unlink()
            except FileNotFoundError:
                pass
            except OSError as error:
                unreadable.append(f"{path}: a stale entry that cannot be removed: {error}")
                continue
            cleared.append(entry)
    return live, cleared, "; ".join(unreadable) or None


def live_memory(entries: list[dict], table: dict[int, dict] | None = None) -> dict[int, int]:
    """``{pid: bytes}``: each session's process-tree memory, other sessions' subtrees left out (no double charge)."""
    table = machine.processes() if table is None else table
    pids = {entry["pid"] for entry in entries}
    return {pid: sum(table[p]["rss"] for p in machine.tree(table, pid, pids - {pid})) for pid in pids}

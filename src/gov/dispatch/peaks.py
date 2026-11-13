"""Peaks, not the moment (S3; DEC-1008): each kind of job's measured peak, and the room for a new lead's peak.

The history is a file of JSON lines ``{"kind", "at", "cpu", "mem_bytes"}`` (``history`` in the configuration). A kind's
peak is the maximum of its lines; ``peaks.json`` keeps ``{"computed", "kinds": {kind: {"cpu", "mem_bytes", "date",
"measured", "source"}}, "ignored_history_lines"}`` and is refreshed from the history when it is missing, unreadable,
older than a day, or older than the history file. A kind with no history counts the gate's working size as its memory
peak (and no CPU). A line that cannot be read is ignored and counted, never a default.

A new lead is admitted only when, with the peaks ahead of the work already running (each running job's kind peak less
what it holds now, never below 0; a start not yet seen in the processes holds nothing):

- ``available memory - memory floor - memory ahead >= the lead kind's memory peak``, and
- ``nproc - busy cores - cpu band - the cpu peaks ahead >= the lead kind's cpu peak``.
"""

from __future__ import annotations

import datetime
import json
import math
from pathlib import Path

from gov.dispatch import state as states

LEAD = "lead"
REFRESH_AFTER_S = 24 * 3600
SOURCE_HISTORY, SOURCE_GATE = "history", "gate working_size_bytes"


def _row(text: str):
    try:
        row = json.loads(text)
        kind, cpu, mem = row["kind"], row["cpu"], row["mem_bytes"]
        at = states.parse_time(row["at"])
    except (ValueError, KeyError, TypeError):
        return None
    ok = isinstance(kind, str) and kind and at is not None \
        and not isinstance(cpu, bool) and isinstance(cpu, (int, float)) and math.isfinite(cpu) and cpu >= 0 \
        and not isinstance(mem, bool) and isinstance(mem, int) and mem >= 0
    return (kind, float(cpu) if isinstance(cpu, float) else cpu, mem, at) if ok else None


def compute(history: Path, now: datetime.datetime) -> dict:
    """The peaks from the history file (none: no kinds)."""
    kinds, ignored = {}, 0
    try:
        lines = [line for line in history.read_text(encoding="utf-8", errors="replace").splitlines() if line.strip()]
    except OSError:
        lines = []
    for line in lines:
        row = _row(line)
        if row is None:
            ignored += 1
            continue
        kind, cpu, mem, at = row
        peak = kinds.setdefault(kind, {"cpu": 0, "mem_bytes": -1, "measured": ""})
        if mem > peak["mem_bytes"]:
            peak["mem_bytes"], peak["measured"] = mem, states.stamp(at)  # the date of the memory peak's own line
        peak["cpu"] = max(peak["cpu"], cpu)
    for peak in kinds.values():
        peak.update({"date": now.date().isoformat(), "source": SOURCE_HISTORY})
    return {"computed": now.isoformat(), "kinds": kinds, "ignored_history_lines": ignored}


def refresh(state: states.State, history: Path, now: datetime.datetime) -> dict:
    """``peaks.json``'s content, recomputed from the history and written whole when it is due."""
    path = state.file("peaks.json")
    try:
        current = json.loads(path.read_text(encoding="utf-8"))
        computed = states.parse_time(current["computed"])
        if computed is None or not isinstance(current["kinds"], dict):
            raise ValueError("computed")
        stale = (now - computed).total_seconds() > REFRESH_AFTER_S
        try:
            stale = stale or history.stat().st_mtime > computed.timestamp()
        except OSError:
            pass
    except (OSError, ValueError, KeyError, TypeError):
        current, stale = None, True
    if not stale:
        return current
    fresh = compute(history, now)
    state.write_whole(path, json.dumps(fresh, indent=2) + "\n")
    return fresh


def kind_peak(peaks: dict, kind: str, working_size: int | None) -> dict:
    """The kind's peak, or (no history) the gate's working size as its memory peak and no CPU."""
    found = peaks["kinds"].get(kind)
    if found is not None:
        return {"cpu": found["cpu"], "mem_bytes": found["mem_bytes"]}
    return {"cpu": 0, "mem_bytes": working_size}


def shown(peaks: dict, working_size: int | None) -> dict:
    """The peaks as the status shows them: every kind in the history, and the lead kind always."""
    kinds = {k: dict(v) for k, v in peaks["kinds"].items()}
    if LEAD not in kinds:
        kinds[LEAD] = {"cpu": 0, "mem_bytes": working_size, "date": peaks["computed"][:10], "source": SOURCE_GATE}
    return {"computed": peaks["computed"], "kinds": kinds, "ignored_history_lines": peaks.get("ignored_history_lines", 0)}


def ahead(peaks: dict, working_size: int | None, running, pending: int) -> dict:
    """The peaks still to come from the work already running: ``{"memory_bytes", "cpu", "jobs": [...]}``."""
    jobs = []
    for job in [{"kind": LEAD, **lead} for lead in running.leads] + running.jobs \
            + [{"kind": LEAD, "pid": None, "held_bytes": 0}] * pending:
        peak = kind_peak(peaks, job["kind"], working_size)
        memory = None if peak["mem_bytes"] is None else max(0, peak["mem_bytes"] - job["held_bytes"])
        jobs.append({"kind": job["kind"], "pid": job["pid"], "memory_bytes": memory or 0, "cpu": peak["cpu"]})
    return {"memory_bytes": sum(j["memory_bytes"] for j in jobs), "cpu": sum(j["cpu"] for j in jobs), "jobs": jobs}


def room(peaks: dict, working_size: int | None, floor: int | None, available: int | None, nproc: int | None,
         busy: float | None, band: float, coming: dict) -> str | None:
    """None when the machine has room for a new lead's peak, else the refusal with its figures."""
    need = kind_peak(peaks, LEAD, working_size)
    if None in (available, floor, nproc, busy) or need["mem_bytes"] is None:
        return "no room for its peak: a figure cannot be read (memory available, memory floor, working size, " \
               "processors or busy cores)"
    left_memory = available - floor - coming["memory_bytes"]
    left_cpu = nproc - busy - band - coming["cpu"]
    why = []
    if left_memory < need["mem_bytes"]:
        why.append(f"memory: available {available} - floor {floor} - ahead {coming['memory_bytes']} = {left_memory}"
                   f" < the lead's peak {need['mem_bytes']}")
    if left_cpu < need["cpu"]:
        why.append(f"cpu: processors {nproc} - busy {busy:g} - band {band:g} - ahead {coming['cpu']:g} = "
                   f"{left_cpu:g} < the lead's peak {need['cpu']:g}")
    return "no room for its peak: " + "; ".join(why) if why else None

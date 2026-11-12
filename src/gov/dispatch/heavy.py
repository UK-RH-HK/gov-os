"""The heavy steps running (S4): which hold a heavy-job slot, which run outside one.

A heavy step is a job of one of the ``job_markers`` kinds ``test``, ``rebuild``, ``check`` or ``measure``. It is in a slot
when it, or an ancestor of it, is the runner of a slot held (``gov.resources.slots.runners``). The parents are read from
the process table (``gov.resources.machine.processes``: ``/proc/<pid>/stat``, ``GOV_RESOURCES_PROC`` for a planted
folder). One outside a slot is a finding of the status, shown and never a failed pass.
"""

from __future__ import annotations

KINDS = ("test", "rebuild", "check", "measure")


def slot_of(pid: int, table: dict[int, dict], runners: dict[int, int]) -> int | None:
    """The slot whose runner is ``pid`` or its nearest ancestor, or None."""
    seen = set()
    while pid and pid > 1 and pid not in seen:
        if pid in runners:
            return runners[pid]
        seen.add(pid)
        entry = table.get(pid)
        if entry is None:
            return None
        pid = entry["ppid"]
    return None


def steps(jobs: list[dict], table: dict[int, dict], runners: dict[int, int]) -> tuple[list[dict], list[str]]:
    """``(heavy_steps, findings)``: each heavy job as ``{kind, pid, slot}`` (slot None outside one) and, for each of those,
    the finding ``heavy step outside a slot: <kind> pid <pid>``."""
    found = [{"kind": job["kind"], "pid": job["pid"], "slot": slot_of(job["pid"], table, runners)}
             for job in jobs if job["kind"] in KINDS]
    return found, [f"heavy step outside a slot: {s['kind']} pid {s['pid']}" for s in found if s["slot"] is None]

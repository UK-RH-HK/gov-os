"""The sessions and jobs running, counted from the processes only (S5; never from ``started.txt`` or the logs).

A running lead is a process whose command line carries ``--settings`` JSON with ``env.GOV_ROLE`` ``orchestrator`` and
the lead's ``env.GOV_TICKET``: the launcher's identity marker (``gov.launch.launcher.build_lead_settings``). The
processes are read from ``/proc`` (``GOV_RESOURCES_PROC`` for a planted folder), through ``gov.resources.machine``.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field

from gov.resources import machine

LEAD_ROLE = "orchestrator"


@dataclass
class Running:
    leads: list = field(default_factory=list)   # [{"ticket", "pid", "held_bytes"}]
    jobs: list = field(default_factory=list)    # [{"kind", "pid", "held_bytes"}], the kinds other than a lead

    def tickets(self) -> dict[str, int]:
        return {lead["ticket"]: lead["pid"] for lead in self.leads}


def lead_marker(arguments: list[str]) -> str | None:
    """The ticket of the lead whose command line this is, or None."""
    for index, argument in enumerate(arguments):
        value = None
        if argument == "--settings" and index + 1 < len(arguments):
            value = arguments[index + 1]
        elif argument.startswith("--settings="):
            value = argument.partition("=")[2]
        if value is None:
            continue
        try:
            env = json.loads(value).get("env")
        except (ValueError, AttributeError):
            continue
        if isinstance(env, dict) and env.get("GOV_ROLE") == LEAD_ROLE and isinstance(env.get("GOV_TICKET"), str) \
                and env["GOV_TICKET"]:
            return env["GOV_TICKET"]
    return None


def arguments(pid: int) -> list[str]:
    try:
        raw = (machine.proc_root() / str(pid) / "cmdline").read_bytes()
    except OSError:
        return []
    return [part.decode("utf-8", "replace") for part in raw.rstrip(b"\0").split(b"\0")]


def find(table: dict[int, dict], job_markers: dict[str, str]) -> Running:
    """The leads and the other jobs in the process table (``machine.processes()``)."""
    found = Running()
    own = os.getpid()
    leads = set()
    for pid, info in sorted(table.items()):
        if pid == own or "--settings" not in info["cmdline"]:
            continue
        ticket = lead_marker(arguments(pid))
        if ticket is not None:
            leads.add(pid)
            found.leads.append({"ticket": ticket, "pid": pid, "held_bytes": machine.tree_memory(table, pid)})
    for kind, marker in sorted(job_markers.items()):
        matches = {pid for pid, info in table.items() if marker in info["cmdline"] and pid not in leads and pid != own}
        for pid in sorted(matches):
            if table[pid]["ppid"] not in matches:  # a job's own children are the job
                found.jobs.append({"kind": kind, "pid": pid, "held_bytes": machine.tree_memory(table, pid)})
    return found

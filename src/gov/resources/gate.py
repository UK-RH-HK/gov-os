"""The machine-wide resource gate (W2-20; DEC-942, DEC-947, DEC-950, DEC-961, DEC-983, DEC-1010 item 7, DEC-1030).

``read(kind)`` is the reading of the machine, every live session and the gate with its named reasons. ``kind`` is
what would start: ``None`` (the reading itself, room for one more session), ``"session"`` (a session start, lead or
worker), ``"test"`` or ``"rebuild"`` (a heavy job, which also takes a slot). The gate is open only when every
condition holds, and it never opens on what it cannot read:

- **config:** every value from the one configuration file (``gov.resources.config``); each fault is a reason.
- **sessions:** the registry can be read (an unreadable entry shuts it); stale entries are cleared.
- **load (S5):** ``min(load1, load15) < nproc``: a short peak does not shut it; both at or above ``nproc`` do.
- **cpu (S2, S11):** the busy cores over the last minute, with the embedding servers counted at their CPU p95 in
  place of their current use, below ``nproc``. Both the load and the busy cores are shown.
- **memory (S6, S7):** ``MemAvailable`` plus the running sessions' live memory at least the floor, plus each running
  session at what it uses (at least its working size, DEC-961), plus the newcomer: a working size for a session, the
  verification peak for a test run, the rebuild peak for a rebuild. Nothing is set aside for a run not started.
- **disk, inodes (S4):** the shared disk's free space and free inodes at or above their floors.
- **slots (S7, P-2):** the heavy-job slots can be read; a full set never shuts a session start.
- **gpu (S10, S14):** only for a start that declares a need: a GPU whose free memory is at least the need plus the
  margin, and whose room, after the shares of every higher kind not yet held, is too; else the job waits or runs on
  the CPU. A start with no declared need never reads the GPU; the reading reads it once and names a missing GPU.
"""

from __future__ import annotations

import json
import math
import os
import tempfile
import time
from pathlib import Path

from gov.resources import config as configuration
from gov.resources import machine, registry, slots

SERVER_HISTORY = "server-cpu.json"
SERVER_KEEP_S = 7 * 24 * 3600
SERVER_SAMPLES = 500
P95 = 0.95


def _reason(condition: str, reading, threshold, why: str | None = None) -> dict:
    return {"condition": condition, "reading": reading, "threshold": threshold, **({"why": why} if why else {})}


def describe(reason: dict) -> str:
    """A reason in words: ``load 25.0 against the threshold 20``."""
    why = f" ({reason['why']})" if reason.get("why") else ""
    reading = "cannot be read" if reason["reading"] is None else reason["reading"]
    if reason["condition"] == "config":
        return f"config: {reason.get('why')}"
    return f"{reason['condition']} {reading} against the threshold {reason['threshold']}{why}"


# --- the embedding servers' CPU p95 ---------------------------------------------------------------------------------

def _p95(rates: list[float]) -> float:
    ordered = sorted(rates)
    return ordered[max(0, math.ceil(P95 * len(ordered)) - 1)]


def servers(values: dict, table: dict[int, dict]) -> dict:
    """Each embedding server's CPU now and its p95 (cores), from one sample per reading kept for a week in
    ``~/.gov-os/machine/server-cpu.json``. A server that is not listening uses no CPU now."""
    folder = configuration.machine_dir()
    path = folder / SERVER_HISTORY
    try:
        history = json.loads(path.read_text(encoding="utf-8"))
        history = history if isinstance(history, dict) else {}
    except (OSError, ValueError):
        history = {}
    now, out = time.time(), {}
    for name, entry in (values.get(configuration.SERVERS_KEY) or {}).items():
        port = int(entry["host"].rsplit(":", 1)[1])
        pid = machine.listener(port)
        ticks = sum(table[p]["ticks"] for p in machine.tree(table, pid)) if pid in table else None
        kept = history.get(name) if isinstance(history.get(name), dict) else {}
        rates = [r for r in kept.get("rates", []) if isinstance(r, list) and len(r) == 2 and now - r[0] <= SERVER_KEEP_S]
        last, current = kept.get("last"), 0.0 if pid is None else None
        if ticks is not None and isinstance(last, list) and len(last) == 3 and last[1] == pid and now > last[0]:
            current = max(0.0, (ticks - last[2]) / machine.TICKS / (now - last[0]))
        if current is not None:
            rates.append([now, round(current, 3)])
        rates = rates[-SERVER_SAMPLES:]
        history[name] = {"rates": rates, "last": [now, pid, ticks] if ticks is not None else None}
        out[name] = {"host": entry["host"], "pid": pid, "cores_now": None if current is None else round(current, 2),
                     "cores_p95": round(_p95([r[1] for r in rates]), 2) if rates else None,
                     "samples": len(rates), **({"state": "not listening"} if pid is None else {})}
    try:
        folder.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile("w", dir=folder, prefix=".srv-", suffix=".tmp", delete=False) as handle:
            json.dump(history, handle)
        os.replace(handle.name, path)
    except OSError:
        pass
    return out


# --- the GPU --------------------------------------------------------------------------------------------------------

def gpu_room(reading: dict, values: dict, need: int, kind: str) -> dict:
    """For each GPU: its free memory, and its room for ``kind`` after the shares of every higher kind not yet held
    and the headroom; the first GPU on which both hold ``need`` plus the margin, or None."""
    margin = values["gpu_margin"]
    asked = int(math.ceil(need * (1 + margin)))
    order = [share["kind"] for share in values["gpu_shares"]]
    held: dict[str, int] = {}
    for holder in reading.get("holders") or []:
        held[holder["kind"]] = held.get(holder["kind"], 0) + (holder.get("used_bytes") or 0)
    rank = order.index(kind) if kind in order else len(order)
    reserved = sum(max(0, share["bytes"] - held.get(share["kind"], 0)) for i, share in enumerate(values["gpu_shares"])
                   if share["kind"] == "headroom" or (i < rank and share["kind"] != kind))
    gpus = [{"index": g["index"], "free_bytes": g["free_bytes"], "room_bytes": max(0, g["free_bytes"] - reserved)}
            for g in reading["gpus"]]
    fits = next((g for g in gpus if g["free_bytes"] >= asked and g["room_bytes"] >= asked), None)
    return {"need_bytes": need, "asked_bytes": asked, "kind": kind, "reserved_bytes": reserved, "gpus": gpus,
            "fits": fits["index"] if fits else None}


# --- the reading ----------------------------------------------------------------------------------------------------

def read(kind: str | None = None, *, gpu_need_bytes: int | None = None, gpu_kind: str = "other",
         read_gpu: bool | None = None) -> dict:
    """The reading: the machine, the live sessions, the thresholds in force and the gate with its reasons."""
    conf = configuration.load()
    values = conf["values"]
    reasons = [_reason("config", None, None, fault) for fault in conf["faults"]]

    live, cleared, sessions_why = registry.sessions()
    if sessions_why:
        reasons.append(_reason("sessions", None, None, sessions_why))
    table = machine.processes()
    held = registry.live_memory(live, table)
    for entry in live:
        entry["memory_bytes"] = held.get(entry["pid"])

    count, count_why = machine.nproc()
    loads, load_why = machine.load()
    least = None if loads is None else min(loads[0], loads[2])
    if least is None or count is None or not least < count:
        reasons.append(_reason("load", least, count, load_why or count_why))

    busy, busy_why = machine.busy_cores(configuration.machine_dir(), count)
    server_cpu = servers(values, table) if configuration.SERVERS_KEY in values else {}
    demand = None
    if busy is not None:
        demand = busy["cores"]
        for state in server_cpu.values():
            if state["cores_p95"] is not None and state["cores_now"] is not None:
                demand += max(0.0, state["cores_p95"] - state["cores_now"])
        demand = round(demand, 2)
    if demand is None or count is None or not demand < count:
        reasons.append(_reason("cpu", demand, count, busy_why or count_why))

    memory, memory_why = machine.memory()
    need = have = None
    floor, work = values.get("floor_bytes"), values.get("working_size_bytes")
    newcomer = {"test": values.get("verification_peak_bytes"), "rebuild": values.get("rebuild_peak_bytes")}.get(
        kind, work)
    if memory is not None and None not in (floor, work, newcomer) and not sessions_why:
        have = memory["available"] + sum(held.values())
        need = floor + sum(max(work, used) for used in held.values()) + newcomer
        if have < need:
            reasons.append(_reason("memory", have, need, f"{len(live)} running session(s) at what they use (at "
                                   f"least {work} B each), the new {kind or 'session'} {newcomer} B, the floor {floor} B"))
    else:
        reasons.append(_reason("memory", have, need, memory_why or "the memory figures are not configured"))

    disk = None
    if "disk_path" in values:
        disk, disk_why = machine.disk(values["disk_path"])
    else:
        disk_why = "disk_path is not configured"
    free = None if disk is None else disk["free_bytes"]
    inodes = None if disk is None else disk["free_inodes"]
    if free is None or "disk_floor_bytes" not in values or free < values["disk_floor_bytes"]:
        reasons.append(_reason("disk", free, values.get("disk_floor_bytes"), disk_why))
    if inodes is None or "inode_floor" not in values or inodes < values["inode_floor"]:
        reasons.append(_reason("inodes", inodes, values.get("inode_floor"), disk_why))

    jobs, slots_why = slots.holders(values.get("heavy_slots"))
    if slots_why or "heavy_slots" not in values:
        reasons.append(_reason("slots", None, values.get("heavy_slots"), slots_why or "heavy_slots is not configured"))

    gpu = None
    if read_gpu is None:
        read_gpu = kind is None or bool(gpu_need_bytes)
    if read_gpu:
        found, why = machine.gpu()
        gpu = {"read": found is not None, **(found or {}), **({"why": why} if why else {})}
        if gpu_need_bytes:
            if found is None:
                reasons.append(_reason("gpu", None, gpu_need_bytes, why))
            elif "gpu_margin" in values and "gpu_shares" in values:
                room = gpu_room(found, values, gpu_need_bytes, gpu_kind)
                gpu["room"] = room
                if room["fits"] is None:
                    best = max(room["gpus"], key=lambda g: g["room_bytes"])
                    reasons.append(_reason("gpu", min(best["free_bytes"], best["room_bytes"]), room["asked_bytes"],
                                           f"the GPU room it saw: free {best['free_bytes']} B, room "
                                           f"{best['room_bytes']} B after {room['reserved_bytes']} B kept for higher "
                                           f"shares and headroom: the job waits, or runs its model on the CPU"))
            else:
                reasons.append(_reason("gpu", None, gpu_need_bytes, "gpu_margin or gpu_shares is not configured"))

    thresholds = {"nproc": count, "floor_bytes": floor, "working_size_bytes": work, "newcomer_bytes": newcomer,
                  "disk_floor_bytes": values.get("disk_floor_bytes"), "inode_floor": values.get("inode_floor"),
                  "heavy_slots": values.get("heavy_slots")}
    return {
        "registry": str(registry.folder().parent), "kind": kind or "reading",
        "available_memory_bytes": None if memory is None else memory["available"],
        "load_1m": None if loads is None else loads[0], "load_15m": None if loads is None else loads[2],
        "nproc": count, "busy_cores": None if busy is None else busy["cores"],
        "busy_window_s": None if busy is None else busy["window_s"], "cpu_demand_cores": demand,
        "servers": server_cpu, "memory": {"have_bytes": have, "need_bytes": need},
        "disk": disk, "sessions": live, "cleared": cleared,
        "slots": {"count": values.get("heavy_slots"), "held": len(jobs), "holders": jobs,
                  "full": values.get("heavy_slots") is not None and len(jobs) >= values["heavy_slots"]},
        "gpu": gpu, "thresholds": thresholds,
        "config": {"path": conf["path"], "values": values, "dates": conf["dates"], "sources": conf["sources"],
                   "due_for_remeasure": conf["due"]},
        "gate": {"open": not reasons, "reasons": reasons},
    }


def check_disk() -> dict:
    """The disk reading alone, for a close to call before it starts (S4; the call is W2-07's or W2-66's): ``{"open",
    "reasons", "disk"}``, shut below either floor or when the disk or its floors cannot be read."""
    conf = configuration.load()
    values = conf["values"]
    reasons = []
    disk, why = machine.disk(values["disk_path"]) if "disk_path" in values else (None, "disk_path is not configured")
    for condition, key, field in (("disk", "disk_floor_bytes", "free_bytes"), ("inodes", "inode_floor", "free_inodes")):
        reading = None if disk is None else disk[field]
        if reading is None or key not in values or reading < values[key]:
            reasons.append(_reason(condition, reading, values.get(key), why or next(
                (f for f in conf["faults"] if f.startswith(key) or f.startswith("disk_path")), None)))
    return {"open": not reasons, "reasons": reasons, "disk": disk}


def gate_path() -> Path:
    return configuration.path()

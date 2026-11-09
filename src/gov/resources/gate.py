"""The machine-wide resource gate (W2-20; DEC-942, DEC-947, DEC-950, DEC-961, DEC-983, DEC-1010 item 7, DEC-1030).

``read(check=False, gpu_need_mib=None, gpu_kind="other")`` is the reading of the machine, every live session and the
gate with its named reasons; ``check`` makes it the start check of one new session (the GPU read only for a declared
need, S10, P-6). The gate is open only when every condition holds; each broken condition is one reason
``{condition, reading, threshold, ...}``, ``condition`` one of ``memory``, ``load``, ``cpu``, ``disk``, ``inodes``,
``config``, ``gpu``. There is no sessions condition and no ceiling on leads or sessions (DEC-983): heavy jobs wait for
slots instead, and a session takes no slot.

- **memory (S6):** ``available + sessions_live >= floor + working_size * (running sessions + 1)``; equal opens.
  Nothing is reserved for a run that has not started.
- **load (S5):** ``min(load_1m, load_15m) < nproc``; equal shuts.
- **cpu (S2, S12):** ``busy_cores_1m + p95(shared) + p95(query) < nproc``; equal shuts.
- **disk, inodes (S4):** ``free_bytes >= disk_floor_bytes``, ``free_inodes >= inode_floor``; equal opens.
- **config (S8):** one reason per value missing or malformed, naming its key (or the file).
- **gpu (S10, S14), a start check with a declared need only:** some single GPU has room ``>= need * (1 +
  gpu_margin)``; a job's room is that GPU's free memory less the unused part of the shares of the kinds before it.
- **Fail closed (F5):** a reading that cannot be taken is ``null`` and shuts the gate with its condition.
"""

from __future__ import annotations

from gov.resources import config as configuration
from gov.resources import machine, registry, slots

CONDITIONS = ("memory", "load", "cpu", "disk", "inodes", "config", "gpu")
KIND_ORDER = ("embedder", "reranker", "other")


def _reason(condition: str, reading, threshold, why: str | None = None, **more) -> dict:
    return {"condition": condition, "reading": reading, "threshold": threshold, **more, **({"why": why} if why else {})}


def _number(value) -> str:
    return "null" if value is None else str(value)


def describe(reason: dict) -> str:
    """A reason in words: ``memory: reading 1073741824, limit 4294967296``; a configuration fault by its key."""
    if reason["condition"] == "config":
        return f"config: {reason.get('why') or reason.get('key')}"
    why = f" ({reason['why']})" if reason.get("why") and reason["reading"] is None else ""
    return f"{reason['condition']}: reading {_number(reason['reading'])}, limit {_number(reason['threshold'])}{why}"


# --- the GPU --------------------------------------------------------------------------------------------------------

def gpu_room(reading: dict, shares: dict, kind: str) -> list[dict]:
    """Each GPU's room for a job of ``kind``: its free memory less the unused part of the shares of the kinds before
    it (an embedder: none; a reranker: the embedder's; other: both). A share's unused part is the share less what
    that kind's processes use on the GPU; a kind whose processes are there but whose use cannot be read (``[N/A]``)
    holds its share, already within the GPU's used memory: nothing more is kept for it."""
    rank = KIND_ORDER.index(kind) if kind in KIND_ORDER else len(KIND_ORDER) - 1
    kept = 0
    for before in KIND_ORDER[:rank]:
        share = shares.get(f"{before}_mib", 0)
        holders = [p for p in reading.get("processes") or [] if p.get("kind") == before]
        if any(p.get("used_mib") is None for p in holders):
            continue
        kept += max(0, share - sum(p["used_mib"] for p in holders))
    return [{"index": g["index"], "free_mib": g["memory_free_mib"], "kept_mib": kept,
             "room_mib": max(0, g["memory_free_mib"] - kept)} for g in reading["gpus"]]


# --- the reading ----------------------------------------------------------------------------------------------------

def read(check: bool = False, *, gpu_need_mib: int | None = None, gpu_kind: str = "other",
         read_gpu: bool | None = None) -> dict:
    """The reading: the machine, the live sessions, the slots and the gate with its reasons. Clears stale entries."""
    conf = configuration.load()
    values = conf["values"]
    reasons = [_reason("config", fault["reading"], None, fault["why"], key=fault["key"]) for fault in conf["faults"]]

    live, cleared, sessions_why = registry.sessions()
    table = machine.processes()
    held = registry.live_memory(live, table)
    sessions = [{"pid": e["pid"], "repository": e.get("repository"), "ticket": e.get("ticket"), "role": e.get("role"),
                 "live_memory_bytes": held.get(e["pid"])} for e in live]
    cleared = [{"pid": e.get("pid"), "repository": e.get("repository"), "ticket": e.get("ticket"),
                "role": e.get("role"), "live_memory_bytes": None} for e in cleared]
    sessions_live = None if sessions_why else sum(held.values())

    count, count_why = machine.nproc()

    loads, load_why = machine.load()
    least = None if loads is None else min(loads)
    if least is None or count is None or not least < count:
        reasons.append(_reason("load", least, count, load_why or count_why))

    busy, busy_why = machine.busy_cores(configuration.machine_dir(), count)
    p95, p95_why = machine.embedding_cpu(configuration.machine_dir(), values)
    demand = None if busy is None or p95 is None else round(busy + p95["shared"] + p95["query"], 3)
    if demand is None or count is None or not demand < count:
        reasons.append(_reason("cpu", demand, count, busy_why or p95_why or count_why))

    available, memory_why = machine.memory()
    floor, work = values.get("memory_floor_bytes"), values.get("working_size_bytes")
    have = None if available is None or sessions_live is None else available + sessions_live
    need = None if floor is None or work is None else floor + work * (len(live) + 1)
    if have is None or need is None or have < need:
        why = memory_why or sessions_why or (None if need is not None else
                                             "memory_floor_bytes or working_size_bytes is not configured")
        reasons.append(_reason("memory", have, need, why))

    disk, disk_why = machine.disk()
    for condition, key, field in (("disk", "disk_floor_bytes", "free_bytes"), ("inodes", "inode_floor", "free_inodes")):
        value, floor_value = None if disk is None else disk[field], values.get(key)
        if value is None or floor_value is None or value < floor_value:
            reasons.append(_reason(condition, value, floor_value, disk_why or (None if floor_value is not None
                                                                              else f"{key} is not configured")))

    jobs, _ = slots.holders(values.get("heavy_slots"))

    out = {
        "registry": str(registry.folder().parent), "config": conf["path"],
        "available_memory_bytes": available, "sessions_live_memory_bytes": sessions_live,
        "load_1m": None if loads is None else loads[0], "load_15m": None if loads is None else loads[1],
        "busy_cores_1m": busy, "embedding_cpu_p95": p95, "nproc": count, "disk": disk,
        "sessions": sessions, "cleared": cleared,
        "slots": {"total": values.get("heavy_slots"), "held": jobs},
        "due_for_remeasure": conf["due"],
    }

    if read_gpu is None:
        read_gpu = bool(gpu_need_mib) or not check
    if read_gpu:
        found, gpu_why = machine.gpu()
        out["gpu"] = found
        if gpu_need_mib:
            margin, shares = values.get("gpu_margin"), values.get("gpu_shares")
            threshold = None if margin is None else round(gpu_need_mib * (1 + margin), 6)
            if threshold is not None and threshold == int(threshold):
                threshold = int(threshold)
            out["gpu_room_mib"] = None
            if not found["available"]:
                reasons.append(_reason("gpu", None, threshold, gpu_why, kind=gpu_kind))
            elif margin is None or shares is None:
                reasons.append(_reason("gpu", None, threshold, "gpu_margin or gpu_shares is not configured",
                                       kind=gpu_kind))
            else:
                rooms = gpu_room(found, shares, gpu_kind)
                best = max(rooms, key=lambda g: g["room_mib"])
                out["gpu_room_mib"] = best["room_mib"]
                if best["room_mib"] < threshold:
                    reasons.append(_reason("gpu", best["room_mib"], threshold, None, kind=gpu_kind, gpus=rooms))

    out["gate"] = {"open": not reasons, "reasons": reasons}
    return out


def check_disk(env=None) -> dict:
    """The disk reading alone, for a close to call before it starts (S4; the call is W2-07's or W2-66's):
    ``{"open", "reasons", "free_bytes", "free_inodes"}``, shut below either floor or when the disk or its floors cannot
    be read. ``env`` (default ``os.environ``) supplies ``HOME`` and ``GOV_RESOURCES_DISK``."""
    conf = configuration.load(env)
    values = conf["values"]
    disk, why = machine.disk(env)
    reasons = []
    for condition, key, field in (("disk", "disk_floor_bytes", "free_bytes"), ("inodes", "inode_floor", "free_inodes")):
        value, floor_value = None if disk is None else disk[field], values.get(key)
        if value is None or floor_value is None or value < floor_value:
            fault = next((f["why"] for f in conf["faults"] if f["key"] in (key, configuration.FILE)), None)
            reasons.append(_reason(condition, value, floor_value, why or fault))
    return {"open": not reasons, "reasons": reasons, "free_bytes": None if disk is None else disk["free_bytes"],
            "free_inodes": None if disk is None else disk["free_inodes"]}

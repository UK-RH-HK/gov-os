"""The run-time limits from the machine detected at the pass (the run-time tool, slice 1: RT-3; audit 3 D1;
DEC-1037 (4)).

Ratios only: no CPU count, byte or MiB figure of any machine is here or in a configuration. Sources, each plantable:
the CPUs ``gov.resources.machine.nproc`` (``GOV_RESOURCES_NPROC``); the RAM the ``MemTotal:`` line of
``GOV_RESOURCES_MEMINFO`` (else ``/proc/meminfo``); the GPU ``gov.resources.machine.gpu`` (``nvidia-smi`` on PATH);
the measured ``verification_peak_bytes`` and ``working_size_bytes`` of ``~/.gov-os/machine/gate.json`` when there.

The GPU never spills and nothing falls back (the owner's working assumption T3 (a)): a GPU need is admitted only within
the GPU's budget; with no GPU, embedding and reranking jobs are refused and memory is said to be unavailable.
"""

from __future__ import annotations

import datetime
import json
import math
import os
from pathlib import Path

from gov.resources import machine
from gov.resources.config import machine_dir

HEAVY_CPU, HEAVY_RAM = 0.15, 0.5          # heavy_slots: of the CPUs, of the RAM by the verification peak
WORKERS_CPU = 0.9                         # workers_per_slot: of the CPUs, shared by the heavy slots
SESSIONS_CPU, SESSIONS_RAM = 0.5, 0.6     # sessions_max: of the CPUs, of the RAM by the working size
GPU_BUDGET = 0.875                        # gpu_budget_mib: of the GPU's total memory
MEASURED = ("verification_peak_bytes", "working_size_bytes")
RULES = {
    "heavy_slots": f"max(1, min(floor({HEAVY_CPU} x CPUs), floor({HEAVY_RAM} x RAM / verification peak) when "
                   f"gate.json has one))",
    "workers_per_slot": f"max(1, floor({WORKERS_CPU} x CPUs / heavy_slots))",
    "sessions_max": f"max(1, min(floor({SESSIONS_CPU} x CPUs), floor({SESSIONS_RAM} x RAM / working size) when "
                    f"gate.json has one))",
    "gpu_budget_mib": f"floor({GPU_BUDGET} x the GPU's total MiB), 0 with no GPU",
}
NO_GPU_REASONS = ("no nvidia-smi on PATH", "no GPU")  # an absent GPU is a reading, not a problem


def ram_total():
    """``(MemTotal in bytes, None)`` or ``(None, why)``."""
    source = os.environ.get("GOV_RESOURCES_MEMINFO") or "/proc/meminfo"
    try:
        for line in Path(source).read_text().splitlines():
            name, _, rest = line.partition(":")
            if name.strip() == "MemTotal":
                value = int(rest.split()[0]) * 1024
                if value <= 0:
                    raise ValueError("MemTotal is not positive")
                return value, None
    except (OSError, ValueError, IndexError) as error:
        return None, f"{source}: {error}"
    return None, f"{source} has no MemTotal line"


def measured() -> tuple[dict, list[str]]:
    """The measured sizes in gate.json (an object with a value, or a bare number); a file that is there but cannot be
    read is a problem, a missing one is not."""
    path = machine_dir() / "gate.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {}, []
    except (OSError, ValueError, UnicodeDecodeError) as error:
        return {}, [f"gate.json: {path} cannot be read: {error}"]
    out = {}
    for key in MEASURED:
        entry = data.get(key) if isinstance(data, dict) else None
        value = entry.get("value") if isinstance(entry, dict) else entry
        if isinstance(value, int) and not isinstance(value, bool) and value > 0:
            out[key] = value
    return out, []


def derive(cpus: int | None, ram: int | None, gpu_total: int | None, sizes: dict) -> dict:
    """Each limit by its rule; None where its CPU reading is missing."""
    if not cpus:
        heavy = workers = sessions = None
    else:
        heavy = math.floor(HEAVY_CPU * cpus)
        if ram and sizes.get("verification_peak_bytes"):
            heavy = min(heavy, math.floor(HEAVY_RAM * ram / sizes["verification_peak_bytes"]))
        heavy = max(1, heavy)
        workers = max(1, math.floor(WORKERS_CPU * cpus / heavy))
        sessions = math.floor(SESSIONS_CPU * cpus)
        if ram and sizes.get("working_size_bytes"):
            sessions = min(sessions, math.floor(SESSIONS_RAM * ram / sizes["working_size_bytes"]))
        sessions = max(1, sessions)
    budget = math.floor(GPU_BUDGET * gpu_total) if gpu_total else 0
    return {"heavy_slots": heavy, "workers_per_slot": workers, "sessions_max": sessions, "gpu_budget_mib": budget}


def detect() -> dict:
    """``{"machine", "limits", "rules", "gpu", "problems"}``: the machine read now and the limits derived from it.
    Every reading that cannot be taken is named in ``problems``; it is never replaced by a figure."""
    problems = []
    cpus, why = machine.nproc()
    if why:
        problems.append(f"CPUs: {why}")
    ram, why = ram_total()
    if why:
        problems.append(f"RAM: {why}")
    gpu, why = machine.gpu()
    if why and not str(why).startswith(NO_GPU_REASONS):
        problems.append(f"GPU: nvidia-smi: {why}")
    sizes, faults = measured()
    problems += faults
    present = bool(gpu.get("available"))
    total = gpu.get("memory_total_mib") if present else None
    used = gpu.get("memory_used_mib") if present else None
    found = {"cpus": cpus, "ram_bytes": ram, "gpu_total_mib": total if present else 0, "gpu_used_mib": used,
             "detected_at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}
    return {"machine": found, "limits": derive(cpus, ram, total, sizes), "rules": dict(RULES),
            "measured": sizes, "gpu": {"present": present, "reason": gpu.get("reason")}, "problems": problems}


def gpu_answer(detected: dict, need_mib: int) -> tuple[str, str]:
    """``(answer, reason)``: ``admit`` only when a GPU is there and its used MiB plus the need stays within the budget,
    ``wait`` when it would not (or the GPU cannot be read now), ``refuse`` on a machine with no GPU."""
    gpu, found = detected["gpu"], detected["machine"]
    budget = detected["limits"]["gpu_budget_mib"]
    if not gpu["present"]:
        reason = gpu.get("reason") or "no GPU"
        if not str(reason).startswith(NO_GPU_REASONS):
            return "wait", f"the GPU cannot be read now ({reason}); nothing is admitted until it reads"
        return "refuse", (f"no GPU on this machine ({reason}): embedding and reranking jobs are refused here, and "
                          f"memory is unavailable")
    used = found["gpu_used_mib"] or 0
    if used + need_mib <= budget:
        return "admit", f"{used} MiB used + {need_mib} MiB needed = {used + need_mib} MiB, within the GPU budget of " \
                        f"{budget} MiB"
    return "wait", (f"{used} MiB used + {need_mib} MiB needed = {used + need_mib} MiB is over the GPU budget of "
                    f"{budget} MiB: wait until GPU memory frees")

"""Heavy-job slots, their CPU sets and thread budgets, and the out-of-memory trip-wire (W2-20 S7, S10b, S15, S17).

- **Slots (S7):** a test run or a rebuild (``gov resources --slot test|rebuild -- <command>``) waits for one of the
  configuration's ``heavy_slots`` machine-wide slots, then for the gate's memory room for its own measured peak (the
  verification peak, or the rebuild peak, P-7) and the disk floors. A slot is an advisory lock on
  ``~/.gov-os/machine/slots/slot-<i>.lock``, held for the whole run, with its holder in ``slot-<i>.json`` (pid,
  kind, tree, CPU set). Sessions, reviews and single-process runs take no slot. A full set of slots never refuses a
  session (P-2): it is shown in the reading.
- **The CPU set (S17):** the CPUs this process may use, less every CPU the configuration gives the embedding servers,
  divided evenly among the slots; slot ``i`` takes its own contiguous range, and the job and everything it starts
  run on it (``sched_setaffinity`` in the started process, before it runs). A set that cannot be applied refuses the
  run: never an unconfined heavy job.
- **The thread budget (S15):** every common runtime's thread limit (Go, OpenMP, MKL, OpenBLAS, Rayon, numexpr,
  Accelerate) is set to the slot's CPUs divided by the job's workers, at least 1, derived from the machine at start;
  the configuration's ``thread_budget`` replaces it where set. A larger value inherited from the caller never raises
  it. The job's environment also carries ``GOV_HEAVY_THREAD_BUDGET``, ``GOV_HEAVY_CPUS``, ``GOV_HEAVY_SLOT`` and
  ``PYTEST_XDIST_AUTO_NUM_WORKERS`` (its workers).
- **The trip-wire (S10b):** while a slot's job runs, its runner checks memory every few seconds; below the
  configuration's ``trip_floor_bytes`` the largest heavy job on the machine (by its process tree's memory) is named
  and stopped (its process group: SIGTERM, then SIGKILL), and the stop is a finding in
  ``~/.gov-os/machine/findings.jsonl``. Nothing else is ever stopped.
"""

from __future__ import annotations

import datetime
import fcntl
import json
import os
import signal
import subprocess
import sys
import threading
import time
from pathlib import Path

from gov.resources import machine
from gov.resources.config import SERVERS_KEY, cpu_list, machine_dir, parse_cpus

KINDS = ("test", "rebuild")
THREAD_VARIABLES = ("GOMAXPROCS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS", "RAYON_NUM_THREADS",
                    "NUMEXPR_NUM_THREADS", "NUMEXPR_MAX_THREADS", "VECLIB_MAXIMUM_THREADS")
HEAVY_VARIABLES = ("GOV_HEAVY_THREAD_BUDGET", "GOV_HEAVY_CPUS", "GOV_HEAVY_SLOT", "PYTEST_XDIST_AUTO_NUM_WORKERS")
FINDINGS = "findings.jsonl"
TRIP_EVERY_S, STOP_WAIT_S, WAIT_EVERY_S = 5.0, 5.0, 2.0


def folder() -> Path:
    return machine_dir() / "slots"


# --- CPU sets and thread budgets ------------------------------------------------------------------------------------

def server_cpus(values: dict) -> set[int]:
    """Every CPU the configuration gives an embedding server."""
    out: set[int] = set()
    for entry in (values.get(SERVERS_KEY) or {}).values():
        out |= parse_cpus(entry.get("cpus", "")) or set()
    return out


def shares(available, count: int, exclude=()) -> tuple[list[list[int]], str | None]:
    """The ``count`` slots' CPU sets: ``available`` less ``exclude``, divided evenly in contiguous ranges (each at
    least one CPU), and a note where the exclusion left nothing and was not applied."""
    cpus, note = sorted(set(available) - set(exclude)), None
    if not cpus:
        cpus, note = sorted(available), "the embedding servers' CPU sets cover every CPU: not excluded"
    n, out = len(cpus), []
    for i in range(count):
        low, high = i * n // count, (i + 1) * n // count
        out.append(cpus[low:high] if high > low else [cpus[i % n]])
    return out, note


def budget(share: list[int], workers: int, configured: int | None = None) -> int:
    """The slot's thread budget: its CPUs divided by its workers, at least 1; the configuration's where set."""
    if configured:
        return max(1, int(configured))
    return max(1, len(share) // max(1, workers))


def job_env(env: dict, share: list[int], workers: int, threads: int, slot: int) -> dict:
    """The job's environment: the thread budget in every runtime's variable, never raised by an inherited value."""
    out = dict(env)
    for name in THREAD_VARIABLES:
        given = env.get(name, "")
        inherited = int(given) if given.isascii() and given.isdigit() and int(given) >= 1 else None
        out[name] = str(min(threads, inherited) if inherited else threads)
    out.update(GOV_HEAVY_THREAD_BUDGET=str(threads), GOV_HEAVY_CPUS=cpu_list(share), GOV_HEAVY_SLOT=str(slot),
               PYTEST_XDIST_AUTO_NUM_WORKERS=str(workers))
    return out


# --- the slots' state -----------------------------------------------------------------------------------------------

def _held(slot: int) -> bool | None:
    """Whether slot ``slot``'s lock is held by a runner; None where it cannot be told."""
    try:
        fd = os.open(folder() / f"slot-{slot}.lock", os.O_RDONLY | os.O_CLOEXEC)
    except FileNotFoundError:
        return False
    except OSError:
        return None
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        fcntl.flock(fd, fcntl.LOCK_UN)
        return False
    except BlockingIOError:
        return True
    except OSError:
        return None
    finally:
        os.close(fd)


def holders(count: int | None = None) -> tuple[list[dict], str | None]:
    """``(live holders, why)``: each slot's holder record whose slot lock is held (a record left by a runner that
    ended is removed); why the slots cannot be read."""
    place = folder()
    out, unreadable = [], []
    try:
        paths = sorted(place.glob("slot-*.json")) if place.exists() else []
    except OSError as error:
        return [], f"{place}: {error}"
    for path in paths:
        try:
            entry = json.loads(path.read_text(encoding="utf-8"))
            slot, pid = entry["slot"], entry["pid"]
            if any(isinstance(v, bool) or not isinstance(v, int) or v <= 0 for v in (slot, pid)):
                raise ValueError("slot and pid must be positive integers")
        except FileNotFoundError:
            continue
        except (OSError, ValueError, KeyError, TypeError) as error:
            unreadable.append(f"{path}: {error}")
            continue
        held = _held(slot)
        if held is None:
            unreadable.append(f"{path}: its slot lock cannot be read")
        elif held:
            if count is None or slot <= count:
                out.append(entry)
        else:
            try:
                path.unlink()
            except OSError:
                pass
    return out, "; ".join(unreadable) or None


def _take(count: int) -> tuple[int, int] | None:
    """``(slot, fd)`` of a free slot, or None when every slot is held."""
    place = folder()
    place.mkdir(parents=True, exist_ok=True)
    for slot in range(1, count + 1):
        fd = os.open(place / f"slot-{slot}.lock", os.O_RDWR | os.O_CREAT | os.O_CLOEXEC, 0o666)
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            return slot, fd
        except BlockingIOError:
            os.close(fd)
    return None


# --- the trip-wire --------------------------------------------------------------------------------------------------

def _finding(record: dict) -> None:
    path = machine_dir() / FINDINGS
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as out:
        out.write(json.dumps(record) + "\n")


def _stop_group(pgid: int) -> bool:
    for sig in (signal.SIGTERM, signal.SIGKILL):
        try:
            os.killpg(pgid, sig)
        except ProcessLookupError:
            return True
        except OSError:
            return False
        deadline = time.monotonic() + STOP_WAIT_S
        while time.monotonic() < deadline:
            try:
                os.killpg(pgid, 0)
            except ProcessLookupError:
                return True
            except OSError:
                break
            time.sleep(0.1)
    return False


def tripwire(values: dict, available: int | None = None) -> dict | None:
    """Below the trip floor, name and stop the largest heavy job; the finding, or None when nothing tripped.

    ``available`` is the memory reading (None reads it). Only a slot's job is ever stopped, never a session."""
    floor = values.get("trip_floor_bytes")
    if floor is None:
        return None
    if available is None:
        reading, _ = machine.memory()
        if reading is None:
            return None
        available = reading["available"]
    if available >= floor:
        return None
    lock = os.open(machine_dir() / "tripwire.lock", os.O_RDWR | os.O_CREAT | os.O_CLOEXEC, 0o666)
    try:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return None  # another runner is acting on it now
        jobs, _ = holders()
        table = machine.processes()
        sized = [(sum(table[p]["rss"] for p in machine.tree(table, job["pid"])), job) for job in jobs
                 if job.get("pid") in table]
        if not sized:
            return None
        size, job = max(sized, key=lambda item: item[0])
        stopped = _stop_group(job["pid"])
        record = {"time": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
                  "finding": "OOM_TRIPWIRE", "available_bytes": available, "trip_floor_bytes": floor,
                  "stopped": {"pid": job["pid"], "kind": job.get("kind"), "slot": job.get("slot"),
                              "tree": job.get("tree"), "command": job.get("command"), "memory_bytes": size},
                  "stop_succeeded": stopped}
        _finding(record)
        print(f"gov resources: OOM_TRIPWIRE: memory available {available} B below the trip floor {floor} B: the "
              f"largest heavy job (pid {job['pid']}, {job.get('kind')}, {size} B) is stopped; a finding is recorded",
              file=sys.stderr, flush=True)
        return record
    finally:
        os.close(lock)


# --- the run --------------------------------------------------------------------------------------------------------

def run(kind: str, command: list[str], *, workers: int | None = None, tree: str | None = None,
        env: dict | None = None) -> int:
    """Run ``command`` as a heavy job of ``kind`` in a slot; its exit code. Refuses (``GovError``) when the
    configuration cannot be used or the CPU set cannot be applied; waits while the slots are full or the gate has no
    room for the job's peak."""
    from gov.cli.errors import GovError
    from gov.launch.gate import GATE_SHUT, EXIT_GATE_SHUT
    from gov.resources.gate import describe, read

    if kind not in KINDS:
        raise GovError("RESOURCE_SLOT_INVALID", f"a heavy job is one of {', '.join(KINDS)}, not {kind!r}")
    if not command:
        raise GovError("RESOURCE_SLOT_INVALID", "no command to run in the slot")
    env = dict(os.environ if env is None else env)
    said = set()

    def say(key: str, line: str) -> None:
        if key not in said:
            said.add(key)
            print(f"gov resources: {line}", file=sys.stderr, flush=True)

    while True:
        reading = read(kind=kind)
        faults = [r for r in reading["gate"]["reasons"] if r["condition"] in ("config", "slots")]
        if faults:
            named = "; ".join(describe(reason) for reason in faults)
            raise GovError(GATE_SHUT, f"the heavy job cannot take a slot: {named}", reading, exit_code=EXIT_GATE_SHUT)
        values = reading["config"]["values"]
        taken = _take(values["heavy_slots"])
        if taken is None:
            say("slots", f"all {values['heavy_slots']} heavy-job slots are taken; waiting")
            time.sleep(WAIT_EVERY_S)
            continue
        slot, fd = taken
        reading = read(kind=kind)  # with the slot held: the room for this job's own peak
        waiting = [r for r in reading["gate"]["reasons"] if r["condition"] in ("memory", "disk", "inodes")]
        if not waiting:
            break
        os.close(fd)
        say("room", "no room for the job yet (" + "; ".join(describe(reason) for reason in waiting) + "); waiting")
        time.sleep(WAIT_EVERY_S)
    try:
        values = reading["config"]["values"]
        allowed = os.sched_getaffinity(0)
        sets, note = shares(allowed, values["heavy_slots"], server_cpus(values))
        share = sets[slot - 1]
        if note:
            say("note", note)
        given = env.get("PYTEST_XDIST_AUTO_NUM_WORKERS", "")
        workers = workers or (int(given) if given.isascii() and given.isdigit() and int(given) >= 1 else 1)
        threads = budget(share, workers, values.get("thread_budget"))
        job = job_env(env, share, workers, threads, slot)

        def confine():
            os.sched_setaffinity(0, set(share))

        try:
            process = subprocess.Popen(command, env=job, preexec_fn=confine, start_new_session=True)
        except subprocess.SubprocessError as error:
            raise GovError("RESOURCE_SLOT_REFUSED", f"the slot's CPU set {cpu_list(share)} cannot be applied "
                                                    f"({error}): no heavy job runs unconfined") from None
        except OSError as error:
            raise GovError("RESOURCE_SLOT_REFUSED", f"the command cannot be started: {error}") from None
        holder = {"slot": slot, "kind": kind, "pid": process.pid, "runner": os.getpid(),
                  "tree": str(Path(tree).resolve()) if tree else os.getcwd(), "cpus": cpu_list(share),
                  "threads": threads, "workers": workers, "command": " ".join(command)[:200],
                  "started": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")}
        record = folder() / f"slot-{slot}.json"
        record.write_text(json.dumps(holder), encoding="utf-8")
        done = threading.Event()

        def watch():
            while not done.wait(TRIP_EVERY_S):
                try:
                    tripwire(values)
                except Exception as error:  # the watch never fails the job
                    say("trip", f"the trip-wire check failed: {error}")

        watcher = threading.Thread(target=watch, name="gov-resources-tripwire", daemon=True)
        watcher.start()
        try:
            return process.wait()
        except BaseException:
            _stop_group(process.pid)
            raise
        finally:
            done.set()
            try:
                record.unlink()
            except OSError:
                pass
    finally:
        os.close(fd)

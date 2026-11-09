"""Heavy-job slots, their CPU sets and thread budgets, and the out-of-memory trip-wire (W2-20 S7, S11, S15, S17).

- **Slots (S7):** ``gov resources --slot test|rebuild [--tree T] [--workers N] -- CMD...`` waits for one of the
  configuration's ``heavy_slots`` machine-wide slots (a rebuild first for its tree's lock, the real path of ``--tree``:
  a second rebuild of the same tree waits, a rebuild of another tree does not), runs ``CMD`` and gives the slot back
  when it ends. A slot is an advisory lock on ``~/.gov-os/machine/slots/slot-<i>.lock`` held by the runner (the
  ``gov resources`` process) for the whole run, its holder in ``slot-<i>.json``. Sessions take no slot; a full set
  never refuses a session (DEC-983, P-2).
- **The CPU set (S17):** the CPUs this process may use (``os.sched_getaffinity``) less every CPU the
  ``embedding_servers`` section names; each slot has ``max(1, len // heavy_slots)`` of them, slot ``i`` its own range
  (disjoint where there are CPUs enough), applied in the started process before it runs, so everything it starts
  inherits it. A set that cannot be applied refuses the run: never an unconfined heavy job.
- **The thread budget (S15):** ``max(1, len(set) // workers)``, or the file's ``thread_budget``; every program the job
  starts gets it in every common runtime's thread variable and ``GOV_HEAVY_THREAD_BUDGET``, whatever the caller had.
- **The trip-wire (S11):** ``tripwire()`` (``gov resources --trip-wire``) is one pass: below ``oom_floor_bytes`` it
  stops the heavy job (its command's process group, then its runner) whose process tree holds the most memory, and
  appends the stop to ``~/.gov-os/machine/findings.jsonl``. Only slot holders are ever stopped. While a job runs, its
  runner makes that pass every few seconds on the kernel's own memory reading.
"""

from __future__ import annotations

import datetime
import fcntl
import hashlib
import json
import os
import signal
import subprocess
import sys
import threading
import time
from pathlib import Path

from gov.resources import machine
from gov.resources.config import SERVERS, SERVERS_KEY, cpu_list, machine_dir, parse_cpus

KINDS = ("test", "rebuild")
THREAD_VARIABLES = ("GOMAXPROCS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS", "RAYON_NUM_THREADS",
                    "NUMEXPR_NUM_THREADS", "NUMEXPR_MAX_THREADS", "VECLIB_MAXIMUM_THREADS", "GOV_HEAVY_THREAD_BUDGET")
FINDINGS = "findings.jsonl"
TRIP_EVERY_S, STOP_WAIT_S, WAIT_EVERY_S = 5.0, 5.0, 0.2


def folder() -> Path:
    return machine_dir() / "slots"


# --- CPU sets and thread budgets ------------------------------------------------------------------------------------

def server_cpus(values: dict) -> set[int]:
    """Every CPU the configuration gives an embedding server."""
    out: set[int] = set()
    section = values.get(SERVERS_KEY) or {}
    for name in SERVERS:
        entry = section.get(name) if isinstance(section, dict) else None
        if isinstance(entry, dict) and isinstance(entry.get("cpus"), str):
            out |= parse_cpus(entry["cpus"]) or set()
    return out


def cpu_set(available, count: int, slot: int, exclude=()) -> tuple[list[int], str | None]:
    """Slot ``slot``'s CPU set (1-based): ``max(1, n // count)`` of ``available`` less ``exclude``, its own range; and a
    note where the exclusion left nothing and was not applied."""
    cpus, note = sorted(set(available) - set(exclude)), None
    if not cpus:
        cpus, note = sorted(available), "the embedding servers' CPU sets cover every CPU this process may use"
    n = len(cpus)
    size = max(1, n // count)
    return sorted({cpus[((slot - 1) * size + j) % n] for j in range(size)}), note


def budget(share: list[int], workers: int, configured: int | None = None) -> int:
    """The slot's thread budget: its CPUs divided by its workers, at least 1; the configuration's where set."""
    if configured:
        return max(1, int(configured))
    return max(1, len(share) // max(1, workers))


def job_env(env: dict, share: list[int], workers: int, threads: int, slot: int) -> dict:
    """The job's environment: the thread budget in every runtime's variable, whatever the caller had."""
    out = dict(env)
    for name in THREAD_VARIABLES:
        out[name] = str(threads)
    out.update(GOV_HEAVY_CPUS=cpu_list(share), GOV_HEAVY_SLOT=str(slot), PYTEST_XDIST_AUTO_NUM_WORKERS=str(workers))
    return out


# --- the slots' state -----------------------------------------------------------------------------------------------

def _held(path: Path) -> bool | None:
    """Whether the lock at ``path`` is held; None where it cannot be told."""
    try:
        fd = os.open(path, os.O_RDONLY | os.O_CLOEXEC)
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
    """``(holders, why)``: one entry per running heavy job (its slot lock held); a record left by a runner that ended
    is removed; why a record cannot be read."""
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
        held = _held(place / f"slot-{slot}.lock")
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
    return sorted(out, key=lambda e: e["slot"]), "; ".join(unreadable) or None


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


def tree_lock(tree: str) -> Path:
    """A tree's rebuild lock among the slots: 12 hex digits of the tree's real path."""
    digits = hashlib.sha256(os.path.realpath(tree).encode("utf-8", "surrogateescape")).hexdigest()[:12]
    return folder() / f"rebuild-{digits}.lock"


# --- the trip-wire --------------------------------------------------------------------------------------------------

def _finding(record: dict) -> None:
    path = machine_dir() / FINDINGS
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as out:
        out.write(json.dumps(record) + "\n")


def _gone(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return True
    except OSError:
        return False
    try:
        return Path(f"/proc/{pid}/stat").read_text().rsplit(")", 1)[1].split()[0] in ("Z", "X")
    except (OSError, IndexError):
        return True


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
            if _gone(pgid) and not _group_left(pgid):
                return True
            time.sleep(0.05)
    return False


def _group_left(pgid: int) -> bool:
    """Whether any live process other than the leader is still in the group ``pgid``."""
    for name in os.listdir("/proc"):
        if not name.isdigit() or int(name) == pgid:
            continue
        try:
            fields = Path(f"/proc/{name}/stat").read_text().rsplit(")", 1)[1].split()
            if int(fields[2]) == pgid and fields[0] not in ("Z", "X"):
                return True
        except (OSError, IndexError, ValueError):
            continue
    return False


def _stop(job: dict) -> bool:
    """Stop one heavy job: its command's process group, then its runner if it still runs."""
    stopped = _stop_group(job.get("command_pid") or job["pid"])
    runner = job["pid"]
    deadline = time.monotonic() + STOP_WAIT_S
    while not _gone(runner) and time.monotonic() < deadline:
        time.sleep(0.05)
    if not _gone(runner):
        try:
            os.kill(runner, signal.SIGKILL)
        except OSError:
            pass
    return stopped


def tripwire(values: dict, available: int | None = None) -> dict:
    """One pass: below ``oom_floor_bytes``, stop the heavy job whose process tree holds the most memory.
    ``{"stopped": the job and its command or None, "available_memory_bytes", "oom_floor_bytes"}``."""
    floor = values["oom_floor_bytes"]
    why = None
    if available is None:
        available, why = machine.memory()
    out = {"stopped": None, "available_memory_bytes": available, "oom_floor_bytes": floor}
    if available is None:
        return {**out, "why": f"the memory cannot be read ({why}): nothing is stopped"}
    if available >= floor:
        return out
    machine_dir().mkdir(parents=True, exist_ok=True)
    lock = os.open(machine_dir() / "tripwire.lock", os.O_RDWR | os.O_CREAT | os.O_CLOEXEC, 0o666)
    try:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return {**out, "why": "another trip-wire pass is acting now"}
        jobs, _ = holders()
        table = machine.processes()
        sized = [(machine.tree_memory(table, job["pid"]), job) for job in jobs if job["pid"] in table]
        if not sized:
            return {**out, "why": "no heavy job runs"}
        size, job = max(sized, key=lambda item: item[0])
        stopped = {"pid": job["pid"], "command_pid": job.get("command_pid"), "kind": job.get("kind"),
                   "slot": job.get("slot"), "tree": job.get("tree"), "command": job.get("command"),
                   "tree_memory_bytes": size}
        stopped["stop_succeeded"] = _stop(job)
        record = {"time": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
                  "finding": "OOM_TRIPWIRE", "available_memory_bytes": available, "oom_floor_bytes": floor,
                  "stopped": stopped}
        _finding(record)
        print(f"gov resources: OOM_TRIPWIRE: memory available {available} B below the trip floor {floor} B: the "
              f"largest heavy job (pid {job['pid']}, {job.get('kind')}, {size} B: {job.get('command')}) is stopped; "
              f"a finding is recorded", file=sys.stderr, flush=True)
        return {**out, "stopped": stopped}
    finally:
        os.close(lock)


# --- the run --------------------------------------------------------------------------------------------------------

def _lock_tree(tree: str, say) -> int:
    path = tree_lock(tree)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(path, os.O_RDWR | os.O_CREAT | os.O_CLOEXEC, 0o666)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        say(f"another rebuild of {os.path.realpath(tree)} runs; waiting for its lock")
        fcntl.flock(fd, fcntl.LOCK_EX)
    return fd


def run(kind: str, command: list[str], *, workers: int | None = None, tree: str | None = None,
        env: dict | None = None) -> int:
    """Run ``command`` as a heavy job of ``kind`` in a slot; its exit code. Refuses (``GovError``) when the slots
    cannot be read from the configuration or the CPU set cannot be applied; waits while every slot is held."""
    from gov.cli.errors import GovError
    from gov.resources import config as configuration

    if kind not in KINDS:
        raise GovError("RESOURCE_SLOT_INVALID", f"a heavy job is one of {', '.join(KINDS)}, not {kind!r}")
    if not command:
        raise GovError("RESOURCE_SLOT_INVALID", "no command to run in the slot (gov resources --slot KIND -- CMD...)")
    if workers is not None and workers < 1:
        raise GovError("RESOURCE_SLOT_INVALID", f"--workers is a positive count, not {workers}")
    workers = workers or 1
    conf = configuration.load()
    values = conf["values"]
    if "heavy_slots" not in values:
        named = "; ".join(f["why"] for f in conf["faults"] if f["key"] in ("heavy_slots", configuration.FILE))
        raise GovError("RESOURCE_SLOT_REFUSED", f"the heavy job cannot take a slot: {named or 'heavy_slots missing'}",
                       {"faults": conf["faults"]})
    count = values["heavy_slots"]
    env = dict(os.environ if env is None else env)
    tree = os.path.realpath(tree or os.getcwd())

    def say(line: str) -> None:
        print(f"gov resources: {line}", file=sys.stderr, flush=True)

    def ended(signum, frame):
        raise SystemExit(128 + signum)

    previous = {s: signal.signal(s, ended) for s in (signal.SIGTERM, signal.SIGHUP)
                if signal.getsignal(s) is not signal.SIG_IGN}
    tree_fd = fd = None
    try:
        if kind == "rebuild":
            tree_fd = _lock_tree(tree, say)
        waited = False
        while True:
            taken = _take(count)
            if taken is not None:
                break
            if not waited:
                say(f"all {count} heavy-job slots are taken; waiting")
                waited = True
            time.sleep(WAIT_EVERY_S)
        slot, fd = taken
        share, note = cpu_set(os.sched_getaffinity(0), count, slot, server_cpus(values))
        if note:
            say(note)
        threads = budget(share, workers, values.get("thread_budget"))
        holder = {"slot": slot, "kind": kind, "pid": os.getpid(), "command_pid": None, "tree": tree,
                  "cpus": cpu_list(share), "threads": threads, "workers": workers, "command": " ".join(command)[:300],
                  "started": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")}
        record = folder() / f"slot-{slot}.json"
        record.write_text(json.dumps(holder), encoding="utf-8")

        def confine():
            os.sched_setaffinity(0, set(share))

        try:
            process = subprocess.Popen(command, env=job_env(env, share, workers, threads, slot), preexec_fn=confine,
                                       start_new_session=True)
        except subprocess.SubprocessError as error:
            raise GovError("RESOURCE_SLOT_REFUSED", f"the slot's CPU set {cpu_list(share)} cannot be applied "
                                                    f"({error}): no heavy job runs unconfined") from None
        except OSError as error:
            raise GovError("RESOURCE_SLOT_REFUSED", f"the command cannot be started: {error}") from None
        holder["command_pid"] = process.pid
        record.write_text(json.dumps(holder), encoding="utf-8")
        done = threading.Event()

        def watch():  # the kernel's reading only: a planted one is a test's, read by its own passes
            while not done.wait(TRIP_EVERY_S):
                if os.environ.get("GOV_RESOURCES_MEMINFO") or "oom_floor_bytes" not in values:
                    continue
                try:
                    tripwire(values)
                except Exception as error:  # the watch never fails the job
                    say(f"the trip-wire pass failed: {error}")

        threading.Thread(target=watch, name="gov-resources-tripwire", daemon=True).start()
        try:
            code = process.wait()
        except BaseException:
            _stop_group(process.pid)
            raise
        finally:
            done.set()
            try:
                record.unlink()
            except OSError:
                pass
        return code if code >= 0 else 128 - code
    finally:
        for descriptor in (fd, tree_fd):
            if descriptor is not None:
                os.close(descriptor)
        for number, handler in previous.items():
            signal.signal(number, handler or signal.SIG_DFL)

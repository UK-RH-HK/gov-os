"""Heavy-job slots, their CPU sets and thread budgets, and the out-of-memory trip-wire (W2-20 S7, S11, S15, S17).

- **Slots (S7):** ``gov resources --slot test|rebuild|measure|embedder|reranker [--tree T] [--workers N] -- CMD...``
  waits for one of the machine-wide slots (``GOV_HEAVY_SLOTS``, else the configuration's ``heavy_slots``, else the
  count derived from the machine; a rebuild first for its tree's lock, the real path of ``--tree``:
  a second rebuild of the same tree waits, a rebuild of another tree does not), runs ``CMD`` and gives the slot back
  when it ends. A slot is an advisory lock on ``~/.gov-os/machine/slots/slot-<i>.lock`` held by the runner (the
  ``gov resources`` process) for the whole run, its holder in ``slot-<i>.json``. Sessions take no slot; a full set
  never refuses a session (DEC-983, P-2).
- **The load admission (W2-199, RT-3, RT-4, RT-7):** before it takes a slot a run waits until the machine has room
  (``gov.dispatch.admission``: the 1-minute load under ``start_below``, the load plus ``workers x margin`` within the
  limit, a GPU kind within the GPU's budget), logs ``ready``, ``wait``, ``admitted``, ``started`` and ``ended`` to the
  runtime log and measures the load while the job runs. A run inside a run (``GOV_HEAVY_ADMITTED``) is nested: never
  held, no slot, no lock. ``--held 1,2`` runs with those slots' CPUs and their workers and takes no lock (the nightly's
  form). A priority run (``GOV_HEAVY_PRIORITY``, the merge queue and the closes) is served before an ordinary waiter and
  holds at most ``GOV_HEAVY_PRIO_CAP`` (default 2) slots; its registration is the file ``prio-<pid>`` in the slots folder.
- **The CPU set (S17):** the CPUs this process may use (``os.sched_getaffinity``) less every CPU the
  ``embedding_servers`` section names; each slot has ``max(1, len // heavy_slots)`` of them, slot ``i`` its own range
  (disjoint where there are CPUs enough), applied in the started process before it runs, so everything it starts
  inherits it. A set that cannot be applied refuses the run: never an unconfined heavy job.
- **The thread budget (S15):** ``max(1, len(set) // workers)``, or the file's ``thread_budget``; every program the job
  starts gets it in every common runtime's thread variable and ``GOV_HEAVY_THREAD_BUDGET``, whatever the caller had.
- **The trip-wire (S11):** ``tripwire()`` (``gov resources --trip-wire``) is one pass: below ``oom_floor_bytes`` it
  stops the heavy job (its command's process group, then its runner) whose process tree holds the most memory, and
  appends the stop to ``~/.gov-os/machine/findings.jsonl``. Only slot holders are ever stopped. While a job runs, its
  runner makes that pass every few seconds on the kernel's own memory reading. A missing or malformed
  ``oom_floor_bytes`` is named on the job's standard error when it starts (``OOM_TRIPWIRE_OFF``), never skipped
  silently (review F4); the gate itself is shut on it (S8).
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
import uuid
from pathlib import Path

from gov.resources import machine
from gov.resources.config import SERVERS, SERVERS_KEY, cpu_list, machine_dir, parse_cpus

KINDS = ("test", "rebuild", "measure", "embedder", "reranker")
GPU_KINDS = ("embedder", "reranker")
PRIO_PREFIX = "prio-"
PRIO_CAP = 2
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


def job_env(env: dict, share: list[int], workers: int, threads: int, slot) -> dict:
    """The job's environment: the thread budget in every runtime's variable, whatever the caller had, and the mark that
    the job is admitted (a run it starts is nested: never held, no slot)."""
    out = dict(env)
    for name in THREAD_VARIABLES:
        out[name] = str(threads)
    out.update(GOV_HEAVY_CPUS=cpu_list(share) if share else "", GOV_HEAVY_SLOT=str(slot),
               PYTEST_XDIST_AUTO_NUM_WORKERS=str(workers), GOV_HEAVY_ADMITTED="1")
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


def runners(held: list[dict] | None = None) -> dict[int, int]:
    """``{runner pid: slot}`` of the slots held (``holders()``'s entries, or ``held`` when it is already read)."""
    return {entry["pid"]: entry["slot"] for entry in (holders()[0] if held is None else held)}


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


def tripwire_off(conf: dict) -> str | None:
    """Why the trip-wire cannot run, naming ``oom_floor_bytes`` and its fault (S8, review F4); None when it can."""
    from gov.resources.config import FILE

    if "oom_floor_bytes" in conf["values"]:
        return None
    named = "; ".join(f["why"] for f in conf["faults"] if f["key"] in ("oom_floor_bytes", FILE))
    return (f"OOM_TRIPWIRE_OFF: the out-of-memory trip-wire cannot run for this job: "
            f"{named or 'oom_floor_bytes: missing'} (S8, S11)")


def tripwire(values: dict, available: int | None = None) -> dict:
    """One pass: below ``oom_floor_bytes``, stop the heavy job whose process tree holds the most memory.
    ``{"stopped": the job and its command or None, "available_memory_bytes", "oom_floor_bytes"}``; without a usable
    ``oom_floor_bytes``, nothing is stopped and ``why`` names it (review F4)."""
    floor = values.get("oom_floor_bytes")
    if isinstance(floor, bool) or not isinstance(floor, int) or floor < 0:
        return {"stopped": None, "available_memory_bytes": available, "oom_floor_bytes": None,
                "why": f"OOM_TRIPWIRE_OFF: oom_floor_bytes: missing or malformed ({floor!r}): nothing can be judged "
                       f"(S8, S11)"}
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


# --- priority runs --------------------------------------------------------------------------------------------------

def _priority() -> bool:
    return os.environ.get("GOV_HEAVY_PRIORITY", "").strip().lower() not in ("", "0", "false", "no")


def _prio_cap() -> int:
    try:
        return max(1, int(os.environ.get("GOV_HEAVY_PRIO_CAP", "")))
    except ValueError:
        return PRIO_CAP


def _register() -> None:
    path = folder() / f"{PRIO_PREFIX}{os.getpid()}"
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(str(os.getpid()), encoding="utf-8")


def _unregister() -> None:
    try:
        (folder() / f"{PRIO_PREFIX}{os.getpid()}").unlink()
    except OSError:
        pass


def _priority_waiting() -> bool:
    """Whether a live priority run (not this one) is registered; the registration of a dead pid is removed."""
    place = folder()
    try:
        paths = sorted(place.glob(f"{PRIO_PREFIX}*")) if place.exists() else []
    except OSError:
        return False
    for path in paths:
        tail = path.name[len(PRIO_PREFIX):]
        if not tail.isdigit() or int(tail) == os.getpid():
            continue
        if not _gone(int(tail)):
            return True
        try:
            path.unlink()
        except OSError:
            pass
    return False


def _priority_held() -> int:
    """How many slots live priority runs hold."""
    return sum(1 for entry in holders()[0] if entry.get("priority"))


def slot_count(conf: dict, say) -> int:
    """The slot count: ``GOV_HEAVY_SLOTS``, else the configuration's ``heavy_slots``, else the count derived from the
    machine (a file with no ``heavy_slots`` no longer refuses the run), else 1."""
    from gov.dispatch import admission
    given = os.environ.get("GOV_HEAVY_SLOTS", "").strip()
    if given.isdigit() and int(given) >= 1:
        return int(given)
    if "heavy_slots" in conf["values"]:
        return conf["values"]["heavy_slots"]
    named = "; ".join(f["why"] for f in conf["faults"] if f["key"] == "heavy_slots")
    if named:
        say(f"{named}: the slot count is derived from the machine")
    return admission.sized()["heavy_slots"] or 1


def _held_slots(text: str, count: int) -> list[int]:
    seen: list[int] = []
    for part in text.split(","):
        part = part.strip()
        if part.isdigit() and 1 <= int(part) <= count and int(part) not in seen:
            seen.append(int(part))
    return seen


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


def _code(raw: int) -> int:
    return raw if raw >= 0 else 128 - raw


def _say(line: str) -> None:
    print(f"gov resources: {line}", file=sys.stderr, flush=True)


def _nested(kind: str, command: list[str], env: dict, job: str) -> int:
    """A run inside an admitted run: never held, no slot and no lock; the command runs at once in the outer run's CPU set
    and environment (a ``nested`` event), and its code is the run's."""
    from gov.cli.errors import GovError
    from gov.dispatch import admission

    admission.log("nested", job, kind, command=" ".join(command)[:300])
    try:
        process = subprocess.Popen(command, env=env)
    except OSError as error:
        raise GovError("RESOURCE_SLOT_REFUSED", f"the command cannot be started: {error}") from None
    try:
        return _code(process.wait())
    except BaseException:
        process.terminate()
        try:
            process.wait(timeout=STOP_WAIT_S)
        except subprocess.TimeoutExpired:
            process.kill()
        raise


def run(kind: str, command: list[str], *, workers: int | None = None, tree: str | None = None,
        env: dict | None = None, held: str | None = None, gpu_need_mib: int | None = None) -> int:
    """Run ``command`` as a heavy job of ``kind`` in a slot once the machine has room; its exit code. Refuses
    (``GovError``) when the CPU set cannot be applied, or a GPU kind has no GPU; waits while the load, the GPU or every
    slot holds it. A nested run (``GOV_HEAVY_ADMITTED``) runs at once; ``held`` (``"1,2"``) runs with those slots'
    CPUs and takes no lock."""
    from gov.cli.errors import GovError
    from gov.dispatch import admission
    from gov.resources import config as configuration

    if kind not in KINDS:
        raise GovError("RESOURCE_SLOT_INVALID", f"a heavy job is one of {', '.join(KINDS)}, not {kind!r}")
    if not command:
        raise GovError("RESOURCE_SLOT_INVALID", "no command to run in the slot (gov resources --slot KIND -- CMD...)")
    if workers is not None and workers < 1:
        raise GovError("RESOURCE_SLOT_INVALID", f"--workers is a positive count, not {workers}")
    if kind in GPU_KINDS and not gpu_need_mib:
        raise GovError("RESOURCE_ARGUMENTS_INVALID", f"a {kind} job needs --gpu-need-mib <MiB>: its GPU memory")
    env = dict(os.environ if env is None else env)
    job = uuid.uuid4().hex[:12]
    if os.environ.get("GOV_HEAVY_ADMITTED") or env.get("GOV_HEAVY_ADMITTED"):
        return _nested(kind, command, env, job)
    say = _say
    conf = configuration.load()
    values = conf["values"]
    count = slot_count(conf, say)
    sized = admission.sized()
    per_slot = workers
    if per_slot is None:
        given = os.environ.get("GOV_HEAVY_WORKERS", "").strip()
        per_slot = int(given) if given.isdigit() and int(given) >= 1 else (sized["workers_per_slot"] or 1)
    tree = os.path.realpath(tree or os.getcwd())
    named = _held_slots(held, count) if held is not None else None
    if held is not None and not named:
        say(f"--held {held!r} names no slot of {count}: one slot's workers, not confined to CPUs")
    total = per_slot * len(named) if named and workers is None else per_slot  # --workers is the run's whole count
    need = gpu_need_mib if kind in GPU_KINDS else None

    trip_off = tripwire_off(conf)
    if trip_off:  # S8, S11, review F4: named, never a silently skipped trip-wire
        say(trip_off)

    def ended(signum, frame):
        raise SystemExit(128 + signum)

    previous = {s: signal.signal(s, ended) for s in (signal.SIGTERM, signal.SIGHUP)
                if signal.getsignal(s) is not signal.SIG_IGN}
    priority = _priority() and held is None
    mark = {"began": None, "code": 1, "sampler": None, "asked": False}
    tree_fd = fd = None
    try:
        admission.log("ready", job, kind, workers=total, priority=priority, held=held)
        mark["asked"] = True
        if kind == "rebuild":
            tree_fd = _lock_tree(tree, say)

        def gate():
            if not priority:
                return ("priority", "a landing or close waits first; waiting") if _priority_waiting() else None
            if _priority_held() >= _prio_cap():
                _unregister()  # capped: not a waiter, so an ordinary run may take the free slot
                return "priority", f"priority runs hold {_prio_cap()} slots (the cap); waiting"
            _register()
            return None

        taken, readings, waited = admission.wait_for_room(
            job, kind, total, need, say, gate=None if held is not None else gate,
            take=None if held is not None else (lambda: _take(count)),
            slots_note=f"all {count} heavy-job slots are taken; waiting")
        if priority:
            _unregister()
        slot, fd = taken if held is None else (None, None)
        available = os.sched_getaffinity(0)
        excluded = server_cpus(values)
        if held is None:
            share, note = cpu_set(available, count, slot, excluded)
            label = slot
        elif named:
            share, note, label = [], None, "held:" + ",".join(str(i) for i in named)
            for i in named:
                got, note = cpu_set(available, count, i, excluded)
                share = sorted(set(share) | set(got))
        else:
            share, note, label = [], None, "held:"
        if note:
            say(note)
        threads = budget(share or sorted(available), total, values.get("thread_budget"))
        admission.log("admitted", job, kind, binding=readings["binding"], waited_s=waited)
        holder = {"slot": slot, "kind": kind, "pid": os.getpid(), "command_pid": None, "tree": tree, "job": job,
                  "cpus": cpu_list(share), "threads": threads, "workers": total, "priority": priority,
                  "command": " ".join(command)[:300],
                  "started": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")}
        record = folder() / f"slot-{slot}.json" if slot else None
        if record:
            record.write_text(json.dumps(holder), encoding="utf-8")

        def confine():
            os.sched_setaffinity(0, set(share))

        child_env = job_env(env, share, total, threads, label)
        if need:
            child_env["GOV_GPU_NEED_MIB"] = str(need)
        sampler = mark["sampler"] = admission.Sampler(readings.get("load_limit"))
        sampler.seed(readings.get("load_1m"))
        try:
            process = subprocess.Popen(command, env=child_env, preexec_fn=confine if share else None,
                                       start_new_session=True)
        except subprocess.SubprocessError as error:
            raise GovError("RESOURCE_SLOT_REFUSED", f"the slot's CPU set {cpu_list(share)} cannot be applied "
                                                    f"({error}): no heavy job runs unconfined") from None
        except OSError as error:
            raise GovError("RESOURCE_SLOT_REFUSED", f"the command cannot be started: {error}") from None
        holder["command_pid"] = process.pid
        if record:
            record.write_text(json.dumps(holder), encoding="utf-8")
        mark["began"] = time.monotonic()
        sampler.begin()
        admission.log("started", job, kind, slot=slot if slot else label, workers=total, cpus=cpu_list(share),
                      command_pid=process.pid)
        done = threading.Event()

        def watch():  # the kernel's reading only: a planted one is a test's, read by its own passes
            while not done.wait(TRIP_EVERY_S):
                if os.environ.get("GOV_RESOURCES_MEMINFO") or trip_off:  # trip_off was named at the start
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
            if record:
                try:
                    record.unlink()
                except OSError:
                    pass
        mark["code"] = _code(code)
        return mark["code"]
    except SystemExit as stop:
        mark["code"] = stop.code if isinstance(stop.code, int) else 1
        raise
    except GovError as error:
        mark["code"] = error.exit_code
        raise
    finally:
        if priority:
            _unregister()
        if mark["asked"]:
            _finish(job, kind, mark, total)
        for descriptor in (fd, tree_fd):
            if descriptor is not None:
                os.close(descriptor)
        for number, handler in previous.items():
            signal.signal(number, handler or signal.SIG_DFL)


def _finish(job: str, kind: str, mark: dict, workers: int) -> None:
    """The run's ``ended`` event (also for one that never started: killed while it waited, or refused), the peak named
    once on stderr, and the wake message of a job that ran."""
    from gov.dispatch import admission

    code, began, sampler = mark["code"], mark["began"], mark["sampler"]
    if began is None:
        admission.log("ended", job, kind, code=code, ran_s=0, started=False)
        return
    ran = round(time.monotonic() - began, 2)
    fields = sampler.finish(workers)
    admission.log("ended", job, kind, code=code, ran_s=ran, **fields)
    peak, over = fields["load_peak"], fields["over_limit_s"]
    limit = sampler.limit
    if peak is not None and limit is not None and peak > limit:
        _say(f"the load peaked at {peak:g}, over the limit of {limit:g} (for {over:g} s of the run)")
    admission.wake(job, kind, code, ran)

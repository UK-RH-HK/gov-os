"""The load admission of heavy jobs (the run-time tool, slice 2: RT-1, RT-3, RT-4, RT-7; audit 3 D1, D3, D9).

``gov.resources.slots.run`` asks this module before it takes a slot (the imports are lazy, so ``gov.resources`` does not
import ``gov.dispatch`` at load). A run starts only while the machine has room:

- the 1-minute load (``gov.resources.machine.load``, ``GOV_RESOURCES_LOADAVG`` when planted) is under ``start_below``,
  ``START_RATIO`` x the detected CPUs (``GOV_HEAVY_START_BELOW`` sets an absolute load instead);
- the load plus ``workers x margin`` stays within ``load_limit``, the CPUs (the resource gate's own limit): a start
  under ``start_below`` adds at most ``workers x margin``, and the slots and workers are sized so that
  ``start_below + slots x workers x margin <= load_limit``. A run that can never fit (``workers x margin`` over
  ``load_limit - start_below``) is held by the start threshold alone, so an idle machine always admits it; for any other
  run the threshold already keeps the sum within the limit;
- a GPU kind (``embedder``, ``reranker``) is also admitted by ``limits.gpu_answer`` only: never the CPU (RT-4).

``margin`` is what a started job adds to the load per worker, measured: the 90th percentile (nearest rank) of the last
20 ``ended`` events' ``peak_per_worker`` in the runtime log, at least 1.0. A load that cannot be read opens the start
(it cannot be judged), is said, and is a ``problem`` event: the golden rule's fail-open, named.

The runtime log (``~/.gov-os/runtime/log.jsonl``, one JSON object a line, appended whole with ``O_APPEND``): ``ready``,
``wait``, ``admitted``, ``started``, ``ended``, ``nested``, ``problem`` from a run; ``gpu`` from the watch pass; ``end`` (``gov.dispatch.ends``) from a job's wake. Every
event carries ``at``, ``event``, ``job``, ``kind`` and ``pid``. A run writes only to this log; only the watch pass writes
``state.json``.
"""

from __future__ import annotations

import datetime
import json
import math
import os
import sys
import threading
import time

from gov.dispatch.limits import START_RATIO
from gov.resources import machine

LOG = "log.jsonl"
POLL_S, SAMPLE_S, SLOT_POLL_S = 15.0, 5.0, 0.2
WINDOW, PERCENTILE = 20, 0.9
WAIT_REPEAT_S = 60.0       # a wait of one reason is logged again after this long
MAX_READ = 16 * 1024 * 1024
GPU_KINDS = ("embedder", "reranker")
REFUSED = "refused"


def _seconds(name: str, default: float) -> float:
    try:
        value = float(os.environ.get(name, ""))
        return value if math.isfinite(value) and value > 0 else default
    except ValueError:
        return default


def poll_s() -> float:
    return _seconds("GOV_ADMISSION_POLL_S", POLL_S)


def sample_s() -> float:
    return _seconds("GOV_ADMISSION_SAMPLE_S", SAMPLE_S)


def start_below(cpus: int) -> float:
    """The load under which a heavy run may start: the override (an absolute load) or ``START_RATIO`` x the CPUs."""
    given = os.environ.get("GOV_HEAVY_START_BELOW")
    if given:
        try:
            value = float(given)
            if math.isfinite(value) and value > 0:
                return value
        except ValueError:
            pass
    return round(START_RATIO * cpus, 6)


# --- the runtime log ------------------------------------------------------------------------------------------------

def log_path():
    from gov.dispatch import runtime
    return runtime.folder() / LOG


def stamp() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


_said_log = False


def log(event: str, job: str, kind: str, **fields) -> bool:
    """Append one whole JSON line to the runtime log (``O_APPEND``); False, said once, where it cannot be written: a
    log that cannot be written never fails the job."""
    global _said_log
    record = {"at": stamp(), "event": event, "job": job, "kind": kind, "pid": os.getpid(), **fields}
    line = (json.dumps(record) + "\n").encode("utf-8")
    try:
        path = log_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        fd = os.open(path, os.O_WRONLY | os.O_APPEND | os.O_CREAT | os.O_CLOEXEC, 0o644)
        try:
            os.write(fd, line)
        finally:
            os.close(fd)
        return True
    except OSError as error:
        if not _said_log:
            _said_log = True
            print(f"gov resources: the runtime log cannot be written ({error}): the run goes on", file=sys.stderr,
                  flush=True)
        return False


def events(*, newest: int | None = None, want=None) -> list[dict]:
    """The log's events in order: all of them, or the last ``newest`` for which ``want(event)`` is true (read from the
    end of the file, no further than needed). A line that is no JSON object is skipped."""
    try:
        path = log_path()
        size = path.stat().st_size
    except OSError:
        return []

    def parse(data: bytes, whole: bool) -> list[dict]:
        lines = data.split(b"\n")
        if not whole:
            lines = lines[1:]  # the first line may be cut
        out = []
        for line in lines:
            try:
                item = json.loads(line)
            except ValueError:
                continue
            if isinstance(item, dict):
                out.append(item)
        return out

    chunk = 256 * 1024
    while True:
        take = min(size, chunk)
        try:
            with open(path, "rb") as handle:
                handle.seek(size - take)
                found = parse(handle.read(take), take >= size)
        except OSError:
            return []
        picked = [e for e in found if want is None or want(e)]
        if newest is None or take >= size or take >= MAX_READ or len(picked) >= newest:
            return picked if newest is None else picked[-newest:]
        chunk *= 4


def _number(value) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value) and value >= 0


_margin_seen: tuple = (None, 1.0)  # ((path, mtime_ns, size), margin): the log is read again only when it changed


def margin() -> float:
    """The measured per-worker load: ``max(1.0, p90)`` (nearest rank) of the last 20 jobs' ``peak_per_worker``."""
    global _margin_seen
    try:
        path = log_path()
        info = path.stat()
        key = (str(path), info.st_mtime_ns, info.st_size)
    except OSError:
        return 1.0
    if _margin_seen[0] == key:
        return _margin_seen[1]
    found = events(newest=WINDOW, want=lambda e: e.get("event") == "ended" and _number(e.get("peak_per_worker")))
    values = sorted(e["peak_per_worker"] for e in found)
    value = max(1.0, float(values[math.ceil(PERCENTILE * len(values)) - 1])) if values else 1.0
    _margin_seen = (key, value)
    return value


# --- the room -------------------------------------------------------------------------------------------------------

def sized() -> dict:
    """The slots and workers this machine derives now (``limits.derive``, with the measured margin and the start
    threshold); every figure None where the CPU count cannot be read."""
    from gov.dispatch import limits

    cpus, _ = machine.nproc()
    ram, _ = limits.ram_total()
    sizes, _ = limits.measured()
    return limits.derive(cpus, ram, None, sizes, margin(), start_below(cpus) if cpus else None)


def _shown(value: float) -> str:
    return f"{value:g}"


def room(kind: str, workers: int, gpu_need: int | None = None) -> tuple[bool, str | None, dict]:
    """``(ok, reason, readings)``: whether a run of ``workers`` workers may start now; ``reason`` is None when it may,
    else ``load``, ``gpu`` or ``refused`` (a GPU kind on a machine with no GPU). ``readings`` holds ``load_1m``,
    ``start_below``, ``load_limit``, ``margin``, ``binding`` (what holds a start, or ``none``) and, where a reading
    cannot be taken, ``problem``."""
    from gov.dispatch import limits

    readings: dict = {"load_1m": None, "start_below": None, "load_limit": None, "margin": margin()}
    problems = []
    cpus, why = machine.nproc()
    loads, load_why = machine.load()
    if cpus is None:
        problems.append(f"the CPU count cannot be read ({why})")
    else:
        readings["start_below"], readings["load_limit"] = start_below(cpus), cpus
    if loads is None:
        problems.append(f"the load cannot be read ({load_why})")
    else:
        readings["load_1m"] = loads[0]
    if problems:
        readings["problem"] = "; ".join(problems)
    reason, binding = None, "none"
    if not problems:
        load, low = loads[0], readings["start_below"]
        if load >= low:
            reason = "load"
            binding = f"load {_shown(load)} is at or over start_below {_shown(low)}"
            readings["line"] = f"load {_shown(load)}, at or over {_shown(low)}: waiting to start"
    if reason is None and kind in GPU_KINDS:
        if gpu_need is None:
            reason, binding = REFUSED, "a GPU kind needs --gpu-need-mib"
        else:
            found = limits.detect()
            answer, said = limits.gpu_answer(found, gpu_need)
            readings.update(gpu_answer=answer, gpu_reason=said, gpu_need_mib=gpu_need,
                            gpu_used_mib=found["machine"]["gpu_used_mib"],
                            gpu_budget_mib=found["limits"]["gpu_budget_mib"])
            if answer == "refuse":
                reason, binding = REFUSED, said
            elif answer == "wait":
                reason, binding = "gpu", said
                readings["line"] = f"{said}: waiting to start"
    readings["binding"] = binding
    return reason is None, reason, readings


class Waiter:
    """The ``wait`` events of one run: one when the reason changes, and again after a minute of the same reason."""

    def __init__(self, job: str, kind: str):
        self.job, self.kind, self.reason, self.at = job, kind, None, 0.0

    def hold(self, reason: str, has_room: bool, **fields) -> None:
        now = time.monotonic()
        if reason != self.reason or now - self.at >= WAIT_REPEAT_S:
            log("wait", self.job, self.kind, reason=reason, room=has_room, **fields)
            self.reason, self.at = reason, now


def wait_for_room(job: str, kind: str, workers: int, gpu_need: int | None, say, *, gate=None, take=None,
                  slots_note: str = "all heavy-job slots are taken; waiting", sleep=time.sleep):
    """Loop until the run may start: ``(taken, readings, waited_s)``. Each pass, ``gate()`` may hold the run first
    (``(reason, text)``, e.g. a priority waiter ahead); then the load, the limit and (a GPU kind) the GPU are read every
    ``GOV_ADMISSION_POLL_S`` seconds; then ``take()`` (a slot) returns something true, or the run waits for a slot. Every
    hold is said once on stderr and logged as a ``wait``. A GPU kind on a machine with no GPU is refused (``GovError``,
    exit 3) at once."""
    from gov.cli.errors import GovError

    waiter, began, said, opened = Waiter(job, kind), time.monotonic(), set(), False
    while True:
        ok, reason, readings = room(kind, workers, gpu_need)
        if reason == REFUSED:
            raise GovError("RESOURCE_GATE_SHUT", readings.get("gpu_reason") or readings["binding"],
                           {"reason": readings["binding"]}, exit_code=3)
        if readings.get("problem") and not opened:  # cannot be judged: starts without the check, says so
            opened = True
            say(f"{readings['problem']}: starting without the load check")
            log("problem", job, kind, what=readings["problem"])
        held = gate() if gate else None
        fields = {"load_1m": readings["load_1m"], "start_below": readings["start_below"]}
        if held:
            hold, text, has_room, nap = held[0], held[1], True, SLOT_POLL_S  # a priority waiter ahead: room
        elif not ok:
            hold, text, has_room, nap = reason, readings.get("line", reason), False, poll_s()
        else:
            taken = take() if take else True
            if taken:
                return taken, readings, round(time.monotonic() - began, 3)
            hold, text, has_room = "slots", slots_note, False  # the slot count is the machine's capacity
            nap = poll_s() if kind in GPU_KINDS else SLOT_POLL_S
        if hold not in said:
            said.add(hold)
            say(text)
        waiter.hold(hold, has_room, **fields)
        sleep(nap)


# --- the load during a job ------------------------------------------------------------------------------------------

class Sampler:
    """Reads the load every ``GOV_ADMISSION_SAMPLE_S`` seconds while a job runs (and once at its start and its end)."""

    def __init__(self, limit: float | None):
        self.limit, self.start, self.peak, self.over, self.last = limit, None, None, 0.0, None
        self.done, self.thread = threading.Event(), None

    def sample(self) -> None:
        loads, _ = machine.load()
        if loads is None:
            return
        now, load = time.monotonic(), loads[0]
        if self.start is None and self.peak is None:
            self.start = load
        self.peak = load if self.peak is None else max(self.peak, load)
        if self.limit is not None and load > self.limit and self.last is not None:
            self.over += now - self.last
        self.last = now

    def seed(self, load: float | None) -> None:
        """The load read at the admission is the job's start (the command may raise it at once)."""
        if load is not None:
            self.start = self.peak = load
            self.last = time.monotonic()

    def begin(self) -> None:
        if self.start is None:
            self.sample()
        self.thread = threading.Thread(target=self._loop, name="gov-resources-sampler", daemon=True)
        self.thread.start()

    def _loop(self) -> None:
        every = sample_s()
        while not self.done.wait(every):
            self.sample()

    def finish(self, workers: int) -> dict:
        self.done.set()
        self.sample()
        per = None if self.start is None or self.peak is None else max(0, self.peak - self.start) / workers
        return {"load_start": self.start, "load_peak": self.peak, "workers": workers,
                "over_limit_s": round(self.over, 2), "peak_per_worker": per}


def wake(job: str, kind: str, code: int, ran_s: float) -> None:
    """The job-end wake message to ``GOV_MSG_ADDRESS`` (id ``job:<job>``, so a send is idempotent); best effort."""
    address = os.environ.get("GOV_MSG_ADDRESS")
    if not address:
        return
    from gov.dispatch import ends, inbox
    text = f"heavy job {kind} ended with exit code {code} after {ran_s:g} s"
    try:
        ends.record(f"job:{job}", "job", address, ends.stamp(), job=job)  # RT-2: the end event, before the message
        inbox.send(address, "wake", text, sender="runtime", message_id=f"job:{job}",
                   data={"job": job, "kind": kind, "exit_code": code, "ran_s": ran_s})
    except (OSError, inbox.InboxError) as error:
        log("problem", job, kind, what=f"the wake message to {address} cannot be sent: {getattr(error, 'message', error)}")

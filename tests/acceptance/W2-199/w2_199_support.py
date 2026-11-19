"""Support code for the W2-199 acceptance tests: the run-time tool, slice 2 (standard library only).

Every case drives a public interface of ticket DAEO-rt2s as a child process, ``python3 -m gov.cli.main`` on this
worktree's ``src`` (the runner's ``PYTHONPATH`` when it has one): ``gov resources --slot <kind> -- CMD``,
``gov dispatch limits|waits|watch`` and the wrapper ``heavy_slot.sh``; and reads what the ticket's Interface names: the
runtime log ``~/.gov-os/runtime/log.jsonl``, ``state.json``, the inbox file ``messages.jsonl`` and the slots folder
``~/.gov-os/machine/slots/``. Nothing of the implementation is imported.

``Machine`` is slice 1's fixture machine (``w2_121c_support.Box``, imported unchanged: a fixture ``HOME``, a stub folder
first on ``PATH`` with the ``nvidia-smi`` stand-in, ``GOV_RESOURCES_NPROC``, ``GOV_RESOURCES_MEMINFO``) with the
slice-2 plantings: a loadavg file (``GOV_RESOURCES_LOADAVG``, rewritten whole by ``Machine.load``, re-read by the run at
every poll), the admission's poll and sample periods shortened (``GOV_ADMISSION_POLL_S`` and ``GOV_ADMISSION_SAMPLE_S``
0.2), a ``python3`` stand-in on ``PATH`` (the wrapper runs ``python3``), a configuration file ``gate.json`` and the
default profile of 20 CPUs.

``Machine.start`` runs a heavy job: a ``gov resources --slot`` child whose command writes its environment to a marker
file, appends its name to an order file and, when asked, holds until a release file appears (or 20 s pass).
"""

from __future__ import annotations

import fcntl
import json
import os
import re
import signal
import subprocess
import sys
import time
from pathlib import Path

SUITE = Path(__file__).resolve().parent
ACCEPTANCE = SUITE.parent
REPO_ROOT = SUITE.parents[2]
sys.path.insert(0, str(ACCEPTANCE / "W2-121c"))

import w2_121c_support as base  # noqa: E402

GIB = base.GIB
PROFILE_20 = {"cpus": 20, "ram": 64 * GIB, "gpu_total": 24_576}
PROFILE_8 = base.PROFILE_B      # 8 CPUs, 16 GiB, 8,192 MiB GPU
PROFILE_32 = base.PROFILE_A     # 32 CPUs, 64 GiB, 24,576 MiB GPU
HOLD_MAX_S = 20                 # a held command never outlives its test by more than this

poll = base.poll
said = base.said
envelope = base.envelope


def iso(epoch: float) -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(epoch))


def cpu_set(text: str) -> set[int]:
    """The CPUs of a list such as ``0-3,8,10-11``."""
    found: set[int] = set()
    for part in filter(None, (text or "").strip().split(",")):
        low, _, high = part.partition("-")
        found |= set(range(int(low), int(high or low) + 1))
    return found


def numbers(text: str) -> list[float]:
    """The numbers in a line of text, its timestamps (ISO-8601) taken out first."""
    text = re.sub(r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:?\d{2})?", " ", text)
    return [float(item) for item in re.findall(r"(?<![\w.])\d+(?:\.\d+)?", text)]


class Job:
    """One ``gov resources`` child and the files its command writes."""

    def __init__(self, machine, name, proc, mark, release):
        self.machine, self.name, self.proc, self.mark, self.release_file = machine, name, proc, mark, release
        self.result = None

    @property
    def pid(self) -> int:
        return self.proc.pid

    def started(self, seconds: float) -> bool:
        """Whether the command wrote its marker within ``seconds``."""
        return bool(poll(lambda: self.mark.exists(), seconds))

    def must_start(self, seconds: float):
        if not self.started(seconds):
            state = "still running" if self.proc.poll() is None else f"ended (exit {self.proc.returncode})"
            raise AssertionError(f"job {self.name}: its command did not start within {seconds:g} s (the runner is "
                                 f"{state}){self._said()}")

    def held_for(self, seconds: float) -> bool:
        """True when, for ``seconds``, the command has not started and the runner still waits; the reason otherwise."""
        deadline = time.monotonic() + seconds
        while time.monotonic() < deadline:
            if self.mark.exists():
                raise AssertionError(f"job {self.name}: its command started, but it should still be held")
            if self.proc.poll() is not None:
                raise AssertionError(f"job {self.name}: the runner ended (exit {self.proc.returncode}) instead of "
                                     f"waiting{self._said()}")
            time.sleep(0.05)
        return True

    def env(self) -> dict:
        found = {}
        for line in self.mark.read_text(encoding="utf-8", errors="replace").splitlines():
            key, sep, value = line.partition("=")
            if sep:
                found[key] = value
        return found

    def release(self):
        self.release_file.touch()

    def finish(self, timeout: float = 10):
        """``(returncode, stdout, stderr)`` once the runner ends."""
        if self.result is None:
            try:
                out, err = self.proc.communicate(timeout=timeout)
            except subprocess.TimeoutExpired:
                raise AssertionError(f"job {self.name}: the runner did not end within {timeout:g} s"
                                     f"{self._said()}") from None
            self.result = (self.proc.returncode, out, err)
        return self.result

    def release_and_finish(self, timeout: float = 10):
        self.release()
        return self.finish(timeout)

    def _said(self) -> str:
        if self.proc.poll() is None:
            return ""
        out, err = self.proc.communicate()
        return f"\nstdout:\n{out[-1500:]}\nstderr:\n{err[-1500:]}"


class Machine(base.Box):
    """Slice 1's fixture machine with slice 2's plantings."""

    def __init__(self, folder, profile=PROFILE_20, heavy_slots=2):
        super().__init__(folder)
        self.loadavg = self.base / "readings" / "loadavg"
        self.jobs: list[Job] = []
        self.profile(profile)
        self.load(3.0)
        script = base.write(self.bin / "python3", f'#!/bin/sh\nexec "{sys.executable}" "$@"\n')
        script.chmod(0o755)
        self.conf(heavy_slots=heavy_slots)

    # -- the planted readings -------------------------------------------------------------------------------------------

    def env(self, extra=None) -> dict:
        env = super().env()
        env.update(GOV_RESOURCES_LOADAVG=str(self.loadavg), GOV_ADMISSION_POLL_S="0.2", GOV_ADMISSION_SAMPLE_S="0.2")
        env.update(extra or {})
        return {key: value for key, value in env.items() if value is not None}

    def load(self, value: float):
        """The planted 1-minute load (whole file, replaced atomically: the run re-reads it at each poll)."""
        temp = self.loadavg.with_name("loadavg.tmp")
        temp.write_text(f"{value} {value} {value} 1/100 1\n", encoding="utf-8")
        os.replace(temp, self.loadavg)

    def conf(self, heavy_slots=2, peak=1 * GIB):
        """``gate.json`` (the configuration file) with ``heavy_slots`` (None: the file has no such key)."""
        path = self.plant_gate(peak, 1 * GIB)
        data = json.loads(path.read_text(encoding="utf-8"))
        if heavy_slots is None:
            data.pop("heavy_slots", None)
        else:
            data["heavy_slots"]["value"] = heavy_slots
        path.write_text(json.dumps(data, indent=1), encoding="utf-8")

    @property
    def slots_dir(self) -> Path:
        return self.machine / "slots"

    # -- the runtime log ------------------------------------------------------------------------------------------------

    def events(self, event=None, job=None, pid=None) -> list[dict]:
        found = self.log()
        if event is not None:
            found = [e for e in found if e.get("event") == event]
        if job is not None:
            found = [e for e in found if e.get("job") == job]
        if pid is not None:
            found = [e for e in found if e.get("pid") == pid]
        return found

    def job_id(self, pid: int) -> str:
        """The job id the log's ``ready`` event of the run with this pid carries."""
        ready = self.events("ready", pid=pid)
        assert ready, f"no `ready` event of pid {pid} in the runtime log: {self.log()}"
        return ready[-1]["job"]

    def plant_log(self, events: list[dict]):
        self.runtime.mkdir(parents=True, exist_ok=True)
        with self.log_path.open("a", encoding="utf-8") as out:
            for item in events:
                out.write(json.dumps(item) + "\n")

    def plant_ended(self, per_worker: list[float], first_at=None):
        """One ``ended`` event per value of ``per_worker``, oldest first, ending a minute ago."""
        first_at = first_at if first_at is not None else time.time() - 60 - 30 * len(per_worker)
        self.plant_log([{"at": iso(first_at + 30 * n), "event": "ended", "job": f"planted-{n}", "kind": "test",
                         "pid": 999_001 + n, "code": 0, "ran_s": 20, "load_start": 3.0,
                         "load_peak": 3.0 + 4 * value, "workers": 4, "over_limit_s": 0, "peak_per_worker": value}
                        for n, value in enumerate(per_worker)])

    # -- jobs -----------------------------------------------------------------------------------------------------------

    def start(self, name, kind="test", opts=(), code=0, hold=True, pre="", extra_env=None, cmd_args=()) -> Job:
        """``gov resources --slot <kind> <opts> -- sh -c <script>``: the command writes ``<name>.env`` (its environment,
        whole, by a rename), appends ``name`` to ``order``, runs ``pre``, holds until ``<name>.release`` exists (when
        ``hold``) and exits with ``code``."""
        mark, release = self.work / f"{name}.env", self.work / f"{name}.release"
        script = (f"echo {name} >> '{self.work / 'order'}'\n{pre}\n"
                  f"env > '{mark}.tmp' && mv '{mark}.tmp' '{mark}'\n")
        if hold:
            script += (f"n=0; while [ ! -e '{release}' ] && [ $n -lt {HOLD_MAX_S * 10} ]; do sleep 0.1; "
                       f"n=$((n+1)); done\n")
        script += f"exit {code}\n"
        proc = self.popen("resources", "--slot", kind, *opts, "--", "sh", "-c", script, *cmd_args,
                          extra_env=extra_env)
        job = Job(self, name, proc, mark, release)
        self.jobs.append(job)
        return job

    def order(self) -> list[str]:
        path = self.work / "order"
        return path.read_text().split() if path.exists() else []

    def run(self, *args, extra_env=None, timeout=20):
        """``gov resources --slot <args>`` run to its end."""
        return self.gov("resources", "--slot", *args, extra_env=extra_env, timeout=timeout)

    def limits(self, extra_env=None) -> dict:
        return self.ok("dispatch", "limits", extra_env=extra_env)

    def locks_held(self) -> list[str]:
        """The slot locks (and rebuild locks) in the slots folder some process holds now."""
        held = []
        for path in sorted(self.slots_dir.glob("*.lock")) if self.slots_dir.is_dir() else []:
            fd = os.open(path, os.O_RDONLY)
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                fcntl.flock(fd, fcntl.LOCK_UN)
            except BlockingIOError:
                held.append(path.name)
            finally:
                os.close(fd)
        return held

    def prio_files(self) -> list[Path]:
        return sorted(self.slots_dir.glob("prio-*")) if self.slots_dir.is_dir() else []

    def cleanup(self):
        for job in self.jobs:
            try:
                job.release()
            except OSError:
                pass
        super().cleanup()


def value_of(result: dict, key: str):
    """A limit or admission figure of a ``gov dispatch limits --json`` result or of ``state.json``: in ``limits``,
    else at the top, else in ``admission``."""
    for place in (result.get("limits"), result, result.get("admission")):
        if isinstance(place, dict) and key in place:
            return place[key]
    return "<missing>"


def close(value, want, tolerance=1e-9) -> bool:
    """Whether ``value`` is a number within ``tolerance`` of ``want`` (False for anything else, a missing key included)."""
    return isinstance(value, (int, float)) and not isinstance(value, bool) and abs(value - want) <= tolerance


def as_list(value) -> list:
    """A ``jobs`` section's ``running`` / ``waiting``: a list, or an object keyed by job id (its values)."""
    if isinstance(value, dict):
        return list(value.values())
    return list(value or [])


def find_dict_with(data, keys) -> dict | None:
    """The first object anywhere in ``data`` holding every one of ``keys``."""
    if isinstance(data, dict):
        if all(key in data for key in keys):
            return data
        children = data.values()
    elif isinstance(data, list):
        children = data
    else:
        return None
    for child in children:
        found = find_dict_with(child, keys)
        if found is not None:
            return found
    return None


def term(proc, seconds=10):
    """SIGTERM a child and wait for it; its return code."""
    proc.send_signal(signal.SIGTERM)
    try:
        proc.wait(timeout=seconds)
    except subprocess.TimeoutExpired:
        raise AssertionError(f"pid {proc.pid} did not end within {seconds} s of SIGTERM") from None
    return proc.returncode


# Calls gov's own entry point in-process for every (margin, CPUs) pair: one process for the whole sweep.
SWEEP = r"""
import contextlib, io, json, os, sys
log_path, margins, cpus = sys.argv[1], json.loads(sys.argv[2]), json.loads(sys.argv[3])
from gov.cli.main import main
out = []
for margin in margins:
    with open(log_path, "w") as handle:
        for n in range(20):
            handle.write(json.dumps({"at": "2026-11-18T10:%02d:00Z" % n, "event": "ended", "job": "p%d" % n,
                                     "kind": "test", "pid": 999001 + n, "code": 0, "ran_s": 20, "load_start": 3.0,
                                     "load_peak": 3.0 + 4 * margin, "workers": 4, "over_limit_s": 0,
                                     "peak_per_worker": margin}) + "\n")
    for count in cpus:
        os.environ["GOV_RESOURCES_NPROC"] = str(count)
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            try:
                code = main(["dispatch", "limits", "--json"])
            except SystemExit as error:
                code = error.code
        out.append({"margin": margin, "cpus": count, "rc": code, "out": buffer.getvalue()})
json.dump(out, sys.stdout)
"""

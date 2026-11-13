"""Support for the W2-121b acceptance tests (part b of ``gov dispatch``: landing, closes, the nightly hold, heavy steps).

Built on W2-121's planted project (``w2_121_support.Project``: a git root on the branch ``integ``, a worktree and a ticket
per W2, ``governance/project/dispatch.yaml``, a tmp ``HOME``, a planted ``/proc`` through ``GOV_RESOURCES_PROC``), imported
as it is and never edited. This module adds:

- a stub **landing command** (``land.py``): it records its argv, the listing of the state folder as it started, its
  working folder and its pid to ``<records>/land-run-<pid>.json``, prints a line, optionally waits for a release file, and
  exits with the code the test chose;
- helpers to read the landing's files (``land.txt``, ``land-claimed-*.txt``, ``land-done.txt``, ``logs/<land id>``,
  ``logs/<land id>.exit``, the ``*.land.txt`` inbox items) and to tick until a condition holds (bounded);
- planted close processes and planted heavy steps (with a parent pid), and a slot holder that holds
  ``slot-<n>.lock`` with ``flock`` in the test process.

Nothing real is started: no model, no ``claude``, no ``gov close``; the landing command is a stub under ``tmp_path``.
"""

from __future__ import annotations

import datetime
import fcntl
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "W2-121"))

import w2_121_support as base  # noqa: E402
from w2_121_support import (Item, Project, Run, SRC, git, strings, wait_for)  # noqa: E402,F401

HEAD_A, HEAD_B, HEAD_C, HEAD_D = "a1b2c3d4e5f6", "b2c3d4e5f6a1", "c3d4e5f6a1b2", "d4e5f6a1b2c3"
LAND_ID = re.compile(r"^land-.+$")
CLAIMED = re.compile(r"^land-claimed-(land-.+)\.txt$")

LAND_STUB = r'''
import json, os, sys, time
rec, state = sys.argv[1], sys.argv[2]
args = sys.argv[3:]

def read(name, default=""):
    try:
        with open(os.path.join(rec, name)) as handle:
            return handle.read().strip()
    except OSError:
        return default

os.makedirs(rec, exist_ok=True)
doc = {"argv": args, "state_listing": sorted(os.listdir(state)), "cwd": os.getcwd(), "pid": os.getpid(),
       "time": time.time()}
tmp = os.path.join(rec, ".tmp-%d" % os.getpid())
with open(tmp, "w") as handle:
    handle.write(json.dumps(doc))
os.replace(tmp, os.path.join(rec, "land-run-%d.json" % os.getpid()))
open(os.path.join(rec, "pid-%d" % os.getpid()), "w").close()
print("landing stub ran with %d approval argument(s)" % len(args), flush=True)
if os.path.exists(os.path.join(rec, "land-wait")):
    end = time.time() + 15
    while time.time() < end and not os.path.exists(os.path.join(rec, "land-release")):
        time.sleep(0.05)
sys.exit(int(read("land-exit", "0") or 0))
'''


def clock(moment: datetime.datetime) -> str:
    return moment.strftime("%H:%M")


def near_midnight(margin_min: int = 90) -> bool:
    """Whether the local time is within ``margin_min`` minutes after or before midnight (a window's arithmetic is then
    ambiguous; the time-relative cases skip)."""
    now = datetime.datetime.now()
    minutes = now.hour * 60 + now.minute
    return minutes < margin_min or minutes >= 24 * 60 - margin_min


NEAR_MIDNIGHT = "the local time is within 90 minutes of midnight: today's `from` and the window's wrap would be ambiguous"


def window(from_minutes: int, until_minutes: int) -> dict:
    """``{from, until}`` as ``HH:MM`` the given minutes from now (negative: before now)."""
    now = datetime.datetime.now()
    return {"from": clock(now + datetime.timedelta(minutes=from_minutes)),
            "until": clock(now + datetime.timedelta(minutes=until_minutes))}


def today_at(hhmm: str) -> datetime.datetime:
    hour, minute = hhmm.split(":")
    return datetime.datetime.now().replace(hour=int(hour), minute=int(minute), second=0, microsecond=0)


def hold_line(hold: dict) -> str:
    return f"land: held for the nightly until it starts (from {hold['from']}, at the latest {hold['until']})"


class Landing(Project):
    """A planted project with a stub landing command and the close marker ``gov-close-stub`` configured."""

    CLOSE_MARKER = "gov-close-stub"

    def __init__(self, tmp: Path):
        super().__init__(tmp)
        (self.stubs / "land.py").write_text(LAND_STUB, encoding="utf-8")
        self.config["landing_command"] = [sys.executable, str(self.stubs / "land.py"), str(self.rec), str(self.state),
                                          "{approvals}"]
        self.config["job_markers"] = {"close": self.CLOSE_MARKER}
        self.slot_fds: list[int] = []

    # --- the landing command's stub ------------------------------------------------------------------------------

    def land_runs(self) -> list[dict]:
        docs = []
        for f in sorted(self.rec.glob("land-run-*.json"), key=lambda f: f.stat().st_mtime_ns):
            docs.append(json.loads(f.read_text(encoding="utf-8")))
        return docs

    def wait_land_runs(self, count: int, timeout: float = 10.0) -> list[dict]:
        wait_for(lambda: len(self.land_runs()) >= count, timeout, what=f"{count} run(s) of the landing command stub")
        return self.land_runs()

    def wait_exit_file(self, log: str, timeout: float = 10.0) -> str:
        return super().wait_exit_file(log, timeout)

    def stub_waits(self) -> None:
        """The landing stub waits (up to 15 s) for ``release()`` before it exits."""
        (self.rec / "land-wait").write_text("", encoding="utf-8")

    def release(self) -> None:
        (self.rec / "land-release").write_text("", encoding="utf-8")

    def set_land_exit(self, code: int) -> None:
        (self.rec / "land-exit").write_text(str(code), encoding="utf-8")

    def settle_none(self, seconds: float = 0.8) -> None:
        """A short fixed wait for a launch that would have been wrongly made to show itself (the launch is detached)."""
        time.sleep(seconds)

    # --- the landing's files -------------------------------------------------------------------------------------

    def plant_land(self, *pairs: str, extra: str = "") -> None:
        """``land.txt`` with one line per ``<W2>=<head>`` pair (and ``extra`` text verbatim after them)."""
        self.land("".join(f"{pair}\n" for pair in pairs) + extra)

    def plant_done(self, *pairs: str, land_id: str = "land-20261111T000000Z") -> None:
        self.state.mkdir(parents=True, exist_ok=True)
        with open(self.state / "land-done.txt", "a", encoding="utf-8") as handle:
            for pair in pairs:
                handle.write(f"{pair} 2026-11-11T00:00:00Z 0 {land_id}\n")

    @property
    def land_file(self) -> Path:
        return self.state / "land.txt"

    def claimed_files(self) -> list[Path]:
        return sorted(f for f in self.state.glob("land-claimed-*.txt"))

    def done_lines(self) -> list[str]:
        path = self.state / "land-done.txt"
        if not path.is_file():
            return []
        return [l for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]

    def done_for(self, pair: str) -> list[list[str]]:
        return [l.split() for l in self.done_lines() if l.split() and l.split()[0] == pair]

    def land_items(self) -> list[Item]:
        return [i for i in self.all_items() if i.path.name.endswith(".land.txt")]

    def land_id_of(self, run: dict) -> str:
        """The land id the batch ran under, from the claimed file the stub saw in the state folder."""
        found = [m.group(1) for name in run["state_listing"] for m in [CLAIMED.match(name)] if m]
        assert len(found) == 1, f"the state folder held {len(found)} land-claimed-<land id>.txt files when the landing " \
                                f"command started: {run['state_listing']}"
        return found[0]

    def land_lines_in_status(self) -> list[str]:
        return [l.strip() for l in self.status_text().splitlines() if l.strip().startswith("land:")]

    def status_blob(self) -> str:
        """The whole status, as text: ``status.txt`` and ``status.json`` (every string and key)."""
        parts = [self.status_text() if (self.state / "status.txt").is_file() else ""]
        if (self.state / "status.json").is_file():
            parts += strings(self.status_json())
        return "\n".join(parts)

    # --- ticking -------------------------------------------------------------------------------------------------

    def tick_ok(self) -> Run:
        run = self.tick()
        assert run.code == 0, run
        return run

    def tick_until(self, predicate, timeout: float = 12.0, what: str = "the condition") -> Run:
        """Tick (a pass each time, exit 0 asserted) until ``predicate()`` is truthy; the last pass."""
        end = time.monotonic() + timeout
        while True:
            run = self.tick_ok()
            if predicate():
                return run
            if time.monotonic() >= end:
                raise AssertionError(f"timed out after {timeout:.0f}s ticking until {what}\n{base.explain(self, run)}")
            time.sleep(0.2)

    def claim_and_run(self, count: int = 1) -> dict:
        """Tick once and wait for the ``count``-th run of the landing command stub; that run's record."""
        self.tick_ok()
        return self.wait_land_runs(count)[count - 1]

    def finalised(self, pair: str):
        """A predicate: the landing holding ``pair`` has been finalised (its line is in ``land-done.txt``)."""
        return lambda: bool(self.done_for(pair))

    # --- the root's state ----------------------------------------------------------------------------------------

    def dirty_root(self) -> None:
        """A modified tracked file in the root."""
        with open(self.root / "README.md", "a", encoding="utf-8") as handle:
            handle.write("an uncommitted change in the root\n")

    def clean_root(self) -> None:
        (self.root / "README.md").write_text("planted project\n", encoding="utf-8")

    # --- planted processes ---------------------------------------------------------------------------------------

    def plant_proc(self, argv: list[str], ppid: int = 1) -> int:
        """A planted ``/proc`` entry with a chosen parent pid (the 4th field of its ``stat``)."""
        self._pid += 1
        pid = self._pid
        folder = self.proc / str(pid)
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "cmdline").write_bytes(b"\0".join(a.encode() for a in argv) + b"\0")
        (folder / "stat").write_text(
            f"{pid} (sh) S {ppid} {pid} {pid} 0 -1 4194304 100 0 0 0 5 5 0 0 20 0 1 0 100 1000000 0\n", encoding="utf-8")
        (folder / "statm").write_text("100 0 0 0 0 0 0\n", encoding="utf-8")
        return pid

    def plant_close(self, *arguments: str) -> int:
        """A running close: a process whose command line holds the close marker and the given ticket arguments."""
        return self.plant_proc(["python3", self.CLOSE_MARKER, *arguments])

    # --- slots ---------------------------------------------------------------------------------------------------

    @property
    def slots_dir(self) -> Path:
        return self.home / ".gov-os" / "machine" / "slots"

    def hold_slot(self, slot: int, runner_pid: int, held: bool = True) -> None:
        """``slot-<slot>.json`` naming ``runner_pid`` and, when ``held``, ``slot-<slot>.lock`` flock-held by this process
        until ``release_slots``."""
        self.slots_dir.mkdir(parents=True, exist_ok=True)
        (self.slots_dir / f"slot-{slot}.json").write_text(json.dumps({"slot": slot, "pid": runner_pid, "kind": "test"}),
                                                          encoding="utf-8")
        fd = os.open(self.slots_dir / f"slot-{slot}.lock", os.O_RDWR | os.O_CREAT | os.O_CLOEXEC, 0o666)
        if held:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            self.slot_fds.append(fd)
        else:
            os.close(fd)

    def release_slots(self) -> None:
        for fd in self.slot_fds:
            try:
                fcntl.flock(fd, fcntl.LOCK_UN)
                os.close(fd)
            except OSError:
                pass
        self.slot_fds = []

    def cleanup(self) -> None:
        self.release_slots()
        super().cleanup()


def heavy_steps(project: Project) -> list[dict]:
    """``status.json``'s ``heavy_steps``; a failed assertion naming the missing key where there is none."""
    document = project.status_json()
    assert "heavy_steps" in document, f"status.json has no `heavy_steps` key (keys: {sorted(document)})"
    steps = document["heavy_steps"]
    assert isinstance(steps, list), f"`heavy_steps` is not a list: {steps!r}"
    return steps


def has_step(steps: list[dict], kind: str, pid: int, slot) -> bool:
    return any(isinstance(s, dict) and s.get("kind") == kind and s.get("pid") == pid and s.get("slot") == slot
               for s in steps)


def findings(project: Project) -> list[str]:
    document = project.status_json()
    return [s for value in (document.get("findings") or []) for s in strings(value)]

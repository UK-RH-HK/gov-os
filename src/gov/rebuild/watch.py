"""What ``gov rebuild`` keeps around its stages (W2-76, DEC-939 item 2; rows W2-M408, W2-L451).

- **The settings:** ``governance/project/rebuild.yaml`` in the tree rebuilt, optional: ``slow_after_s`` (a positive
  number of seconds, 1800 by default) and ``lock`` (an absolute path, the machine's rebuild lock by default). A file
  that is not valid YAML, not a map, or holds a value of the wrong kind refuses the rebuild.
- **The lock's override:** ``GOV_REBUILD_LOCK``, where set, replaces the machine's default lock (the test harness gives
  each process of a test run one of its own, DEC-956 item 2); a tree's ``lock`` still wins over it. A value that is
  not an absolute path refuses the rebuild: never a fall-back to another lock. The lock's part of the result and the
  record names the path used and its ``source``: ``rebuild.yaml``, ``GOV_REBUILD_LOCK`` or ``default``.
- **The lock:** an advisory whole-file ``flock`` on that path, taken before anything is read or written and held to
  the end; the process ending releases it. A rebuild under its caller's hold (``flock <lock> gov rebuild``) runs at
  once under that hold. One held by another process is waited for, without a time limit, after saying what it waits
  for. A lock that cannot be opened or taken refuses the rebuild: it never runs unlocked (DEC-866).
- **The stages' times:** each stage timed around its call; the secrets filter's wall time apart, nested in the stages
  that run it (its functions are wrapped while they run, never edited).
- **The watchdog:** from the lock taken; past the threshold it flags the rebuild slow and writes the record at once,
  then at least every 30 s (and at least once per threshold when that is shorter). It never stops, signals or fails a
  rebuild: a fault of its own is one line on standard error and an entry of ``watchdog_faults``.
- **The record:** ``.gov-runtime/rebuild/record.json``, replaced whole at every write and at the end of every rebuild; a
  slow rebuild's is also kept as ``slow-<UTC start>.json``. Every run of 13 or more hexadecimal digits in a command
  line is cut to its first 12, and each command line to 200 characters (row W2-L423).
"""

from __future__ import annotations

import fcntl
import functools
import json
import os
import re
import sys
import threading
import time
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path

from gov.cli.errors import GovError

SETTINGS_REL = "governance/project/rebuild.yaml"
SLOW_AFTER_S = 1800
LOCK = "/tmp/gov-os-rebuild.lock"  # the interim wrapper's own path: shared across the launcher's sandbox (W2-76)
ENV_LOCK = "GOV_REBUILD_LOCK"
FROM_SETTINGS, FROM_ENV, FROM_DEFAULT = "rebuild.yaml", ENV_LOCK, "default"  # the lock's ``source``
RECORD_REL = ".gov-runtime/rebuild/record.json"
EVERY_S = 30.0  # the longest gap between two writes of a slow rebuild's record
NOT_KNOWN = "holder not known"
_HEX = re.compile(r"[0-9a-fA-F]{13,}")
_CMDLINE = 200
_FILTERED = ("lexical", "codeintel")  # the stages that run the secrets filter


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds")


def _refused(message: str, details: dict) -> GovError:
    return GovError("REBUILD_FAILED", f"{message}: nothing is rebuilt", details)


def _default_lock() -> tuple[str, str]:
    """The lock a tree without its own uses: ``GOV_REBUILD_LOCK`` where set, else the machine's. A value that is not
    an absolute path refuses (DEC-866)."""
    value = os.environ.get(ENV_LOCK)
    if value is None:
        return LOCK, FROM_DEFAULT
    if not os.path.isabs(value):
        reason = "is empty" if not value else f"is not an absolute path: {value!r}"
        raise _refused(f"the environment variable {ENV_LOCK} {reason}", {"variable": ENV_LOCK, "value": value})
    return value, FROM_ENV


def settings(root: Path) -> tuple[float, str, str]:
    """The threshold in seconds, the lock's path and its source: the tree's ``rebuild.yaml``, else
    ``GOV_REBUILD_LOCK``, else the defaults. A wrong ``GOV_REBUILD_LOCK`` refuses even where the tree names a lock."""
    from gov.config.loader import read_yaml

    default = _default_lock()
    path = Path(root) / SETTINGS_REL
    if not path.is_file():
        return SLOW_AFTER_S, *default
    document = read_yaml(path, "REBUILD_FAILED", SETTINGS_REL)
    if not isinstance(document, dict):
        raise _refused(f"{SETTINGS_REL}: not a map", {"file": SETTINGS_REL, "key": None})
    slow = document.get("slow_after_s", SLOW_AFTER_S)
    if isinstance(slow, bool) or not isinstance(slow, (int, float)) or not slow > 0:
        raise _refused(f"{SETTINGS_REL}: key 'slow_after_s': must be a positive number of seconds, not {slow!r}",
                       {"file": SETTINGS_REL, "key": "slow_after_s"})
    if "lock" not in document:
        return slow, *default
    lock = document["lock"]
    if not isinstance(lock, str) or not os.path.isabs(lock):
        raise _refused(f"{SETTINGS_REL}: key 'lock': must be an absolute path, not {lock!r}",
                       {"file": SETTINGS_REL, "key": "lock"})
    return slow, lock, FROM_SETTINGS


def cut(line: str) -> str:
    """A command line as a record may hold it: hexadecimal runs of 13 digits or more cut to 12, 200 characters."""
    return _HEX.sub(lambda run: run.group()[:12], line)[:_CMDLINE]


def _cmdline(pid: int) -> str:
    raw = Path(f"/proc/{pid}/cmdline").read_bytes()
    return cut(raw.rstrip(b"\0").replace(b"\0", b" ").decode("utf-8", "replace"))


def _stat(pid: int) -> tuple[str, int]:
    """A process's state and its parent's pid."""
    state, parent = Path(f"/proc/{pid}/stat").read_text().rsplit(")", 1)[1].split()[:2]
    return state, int(parent)


def _ancestors() -> set[int]:
    pids, pid = set(), os.getppid()
    while pid > 1 and pid not in pids:
        pids.add(pid)
        try:
            pid = _stat(pid)[1]
        except (OSError, ValueError, IndexError):
            break
    return pids


def _holders(fd: int) -> list[int]:
    """The pids ``/proc/locks`` shows holding a ``flock`` on the file open at ``fd``. A waiter's line (``->``) is no
    holder; in a sandbox only its own pid namespace's locks are shown."""
    status = os.fstat(fd)
    place = (os.major(status.st_dev), os.minor(status.st_dev), status.st_ino)
    try:
        lines = Path("/proc/locks").read_text().splitlines()
    except OSError:
        return []
    pids = []
    for fields in (line.split() for line in lines):
        if len(fields) < 6 or fields[1] != "FLOCK":
            continue
        try:
            major, minor, inode = fields[5].split(":")
            if (int(major, 16), int(minor, 16), int(inode)) == place and int(fields[4]) > 0:
                pids.append(int(fields[4]))
        except ValueError:
            continue
    return pids


def _holder(pids: list[int]) -> dict | str:
    if not pids:
        return NOT_KNOWN
    try:
        cmdline = _cmdline(pids[0])
    except OSError:
        cmdline = None
    return {"pid": pids[0], "cmdline": cmdline}


def _inherited(fd: int) -> bool:
    """Whether a descriptor this process inherited holds the lock open at ``fd`` (``flock <lock> gov rebuild``): the
    lock is held, and only the open file that holds it can take it again."""
    status = os.fstat(fd)
    for name in os.listdir("/proc/self/fd"):
        other = int(name)
        try:
            same = other != fd and os.path.samestat(os.fstat(other), status)
            if same:
                fcntl.flock(other, fcntl.LOCK_EX | fcntl.LOCK_NB)
                return True
        except OSError:
            continue
    return False


def take(path: str, source: str) -> tuple[int | None, dict]:
    """The machine's rebuild lock at ``path``: the descriptor that holds it (None under the caller's hold) and the
    lock's part of the result, ``source`` naming where the path came from. Refuses where it cannot be opened or taken;
    never returns unlocked."""
    try:
        fd = os.open(path, os.O_RDWR | os.O_CREAT | os.O_CLOEXEC, 0o666)
    except OSError as exc:
        try:  # a file that cannot be created here (a sandbox's read-only /tmp) is locked through a read-only open
            fd = os.open(path, os.O_RDONLY | os.O_CLOEXEC)
        except OSError:
            raise _refused(f"the rebuild lock {path} cannot be opened or created: {exc.strerror}",
                           {"lock": path, "error": str(exc)}) from None
    part = {"path": path, "source": source, "wait_s": 0.0, "holder": None, "held_by_caller": False}
    try:
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            holders = _holders(fd)
            part["holder"] = _holder(holders)
            if _inherited(fd) or set(holders) & _ancestors():
                os.close(fd)
                return None, part | {"held_by_caller": True}
            holder = part["holder"]
            said = NOT_KNOWN if holder == NOT_KNOWN else f"held by pid {holder['pid']} ({holder['cmdline']})"
            print(f"rebuild: waiting for the rebuild lock {path}, {said}", file=sys.stderr, flush=True)
            started = time.monotonic()
            fcntl.flock(fd, fcntl.LOCK_EX)
            part["wait_s"] = round(time.monotonic() - started, 1)
    except OSError as exc:
        os.close(fd)
        raise _refused(f"the rebuild lock {path} cannot be taken: {exc.strerror}",
                       {"lock": path, "error": str(exc)}) from None
    return fd, part


class _Spans:
    """The wall time while at least one wrapped call runs: calls in several threads at once count once."""

    def __init__(self) -> None:
        self.lock, self.active, self.since, self.spent = threading.Lock(), 0, None, 0.0

    def wrap(self, function):
        @functools.wraps(function)
        def timed(*args, **kwargs):
            with self.lock:
                if not self.active:
                    self.since = time.monotonic()
                self.active += 1
            try:
                return function(*args, **kwargs)
            finally:
                with self.lock:
                    self.active -= 1
                    if not self.active:
                        self.spent += time.monotonic() - self.since
                        self.since = None
        return timed

    def total(self) -> float:
        since = self.since
        return self.spent + (time.monotonic() - since if since is not None else 0.0)


class Watch:
    """One rebuild's stages, times and watchdog, from the lock taken to ``end()``."""

    def __init__(self, root: Path, slow_after_s: float, lock: dict) -> None:
        self.root, self.slow_after_s, self.lock = Path(root), slow_after_s, lock
        # One reading of the clock, with the lock taken: ``released_at`` is it plus the monotonic time since, so the
        # span is ``total_s`` even where the system clock is stepped during the rebuild.
        self.started, self.started_at = time.monotonic(), datetime.now(timezone.utc)
        self.lock["taken_at"] = self.started_at.isoformat(timespec="microseconds")
        self.done: dict = {}
        self.running: list = []
        self.secrets, self.untimed = _Spans(), None
        self.slow, self.faults, self.total = False, [], None
        self._lock, self._stop = threading.RLock(), threading.Event()
        self._thread = threading.Thread(target=self._watch, name="gov-rebuild-watchdog", daemon=True)
        self._thread.start()

    @contextmanager
    def stage(self, name: str):
        since = time.monotonic()
        self.running.append((name, since))
        try:
            yield
        finally:
            self.running.pop()
            self.done[name] = self.done.get(name, 0.0) + time.monotonic() - since

    def skip(self, name: str) -> None:
        """A stage that did not run: done, in 0 s."""
        self.done.setdefault(name, 0.0)

    @contextmanager
    def filtered(self, module, *names: str):
        """The secrets filter's functions that ``module`` calls, timed while the block runs."""
        saved = {}
        for name in names:
            function = getattr(module, name, None)
            if function is None:
                self.untimed = f"{module.__name__} has no {name}: the secrets filter could not be timed there"
                continue
            saved[name] = function
            setattr(module, name, self.secrets.wrap(function))
        try:
            yield
        finally:
            for name, function in saved.items():
                setattr(module, name, function)

    def timing(self) -> dict:
        done = dict(self.done)
        times = {name: round(done.get(name, 0.0), 1) for name in ("record", "lexical", "semantic", "codeintel",
                                                                    "compaction")}
        # Nested in the stages that ran it, so never more than they are, rounding included.
        secrets = min(round(self.secrets.total(), 1), round(times["lexical"] + times["codeintel"], 1))
        total = self.total if self.total is not None else time.monotonic() - self.started
        timing = {"record_s": times["record"], "lexical_s": times["lexical"],
                  "secrets_s": None if self.untimed else secrets, "semantic_s": times["semantic"],
                  "codeintel_s": times["codeintel"], "compaction_s": times["compaction"],
                  "total_s": max(round(total, 1), round(sum(times.values()), 1))}
        if self.untimed:
            timing["secrets_untimed"] = self.untimed
        return timing

    def _current(self) -> tuple[str | None, float | None]:
        running, since, now = list(self.running), self.secrets.since, time.monotonic()
        if not running:
            return None, None
        if since is not None and running[-1][0] in _FILTERED:
            return "secrets", round(now - since, 1)
        return running[-1][0], round(now - running[-1][1], 1)

    def fault(self, message: str) -> None:
        """A fault of the watchdog itself: said once on standard error and kept; never fatal."""
        with self._lock:
            if message in self.faults:
                return
            self.faults.append(message)
        print(f"rebuild: watchdog fault: {message}", file=sys.stderr, flush=True)

    def _processes(self) -> list[dict]:
        """The rebuild itself and every descendant."""
        children: dict = {}
        for entry in os.listdir("/proc"):
            if entry.isdigit():
                try:
                    children.setdefault(_stat(int(entry))[1], []).append(int(entry))
                except (OSError, ValueError, IndexError):
                    continue  # ended, or another's to read: no descendant of this rebuild is lost by it
        listed, todo = [], [os.getpid()]
        while todo:
            pid = todo.pop(0)
            todo += children.get(pid, [])
            try:
                state, parent = _stat(pid)
                wchan = Path(f"/proc/{pid}/wchan").read_text().strip()
                listed.append({"pid": pid, "ppid": parent, "state": state, "wchan": wchan, "cmdline": _cmdline(pid)})
            except (FileNotFoundError, ProcessLookupError):
                continue  # ended since it was listed
            except (OSError, ValueError, IndexError) as exc:
                self.fault(f"process {pid} could not be read: {exc}")
        return listed

    def _load(self) -> list[float] | None:
        try:
            return [float(value) for value in Path("/proc/loadavg").read_text().split()[:3]]
        except (OSError, ValueError) as exc:
            self.fault(f"the load could not be read: {exc}")
            return None

    def _record(self) -> dict:
        stage, running_s = self._current()
        return {"timing": self.timing(), "lock": dict(self.lock), "slow": self.slow,
                "slow_after_s": self.slow_after_s,
                "stages_done": {name: round(seconds, 1) for name, seconds in dict(self.done).items()},
                "stage_running": stage, "stage_running_s": running_s, "processes": self._processes(),
                "load": self._load(), "written_at": _now(), "watchdog_faults": list(self.faults)}

    def write(self) -> None:
        """The record replaced whole (and a slow rebuild's kept apart); a write that fails is a fault."""
        with self._lock:
            try:
                text = json.dumps(self._record(), indent=2) + "\n"
            except Exception as exc:  # the watchdog never fails a rebuild
                self.fault(f"the record could not be made: {exc}")
                return
            rels = [RECORD_REL] + ([f"{Path(RECORD_REL).parent}/slow-{self.started_at:%Y%m%dT%H%M%SZ}.json"]
                                   if self.slow else [])
            for rel in rels:
                path = self.root / rel
                temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
                try:
                    path.parent.mkdir(parents=True, exist_ok=True)
                    temporary.write_text(text, encoding="utf-8")
                    os.replace(temporary, path)
                except OSError as exc:
                    self.fault(f"{rel} could not be written: {exc}")
                    try:
                        temporary.unlink(missing_ok=True)
                    except OSError:
                        pass

    def _flag(self) -> None:
        with self._lock:
            if self.slow:
                return
            self.slow = True
        print(f"rebuild: slow: past {self.slow_after_s:g} s and still running; it goes on to the end; its record: "
              f"{RECORD_REL}", file=sys.stderr, flush=True)

    def _watch(self) -> None:
        try:
            if self._stop.wait(self.slow_after_s):
                return
            self._flag()
            while True:
                self.write()
                if self._stop.wait(min(EVERY_S, self.slow_after_s)):
                    return
        except Exception as exc:  # the watchdog never fails a rebuild
            self.fault(f"the watchdog stopped: {exc}")

    def end(self) -> dict:
        """The watchdog stopped, the last record written; the result's part of the times, the lock and the record."""
        self._stop.set()
        self._thread.join()
        self.total = time.monotonic() - self.started
        if self.total > self.slow_after_s:
            self._flag()
        self.lock["released_at"] = (self.started_at + timedelta(seconds=self.total)).isoformat(timespec="microseconds")
        self.write()
        return {"timing": self.timing(), "lock": dict(self.lock), "slow": self.slow,
                "slow_after_s": self.slow_after_s, "record": RECORD_REL, "watchdog_faults": list(self.faults)}

"""Support code for the W2-121c acceptance tests: the run-time tool, slice 1 (standard library only).

Every case drives a public interface of ticket DAEO-5rgj (``gov msg send|read|wait|watch``, ``gov dispatch watch``,
``gov dispatch limits``, ``gov launch``) as a child process, ``python3 -m gov.cli.main`` on this worktree's ``src``
(the runner's ``PYTHONPATH`` when it has one), and reads what the ticket's Interface names: the inbox files
``~/.gov-os/inbox/<address>/messages.jsonl`` and ``mark``, the runtime folder ``~/.gov-os/runtime/`` (``state.json``,
``log.jsonl``), exit codes and the ``--json`` envelope. Nothing of the implementation is imported.

``Box`` is one fixture machine under the test's ``tmp_path``: a ``HOME`` (never the real one), a ``TMPDIR``, a folder
of stubs first on ``PATH`` (an ``nvidia-smi`` stand-in answering the two queries ``gov.resources.machine.gpu`` sends,
or none), a planted ``meminfo`` (``MemTotal:`` and ``MemAvailable:``) through ``GOV_RESOURCES_MEMINFO`` and a processor
count through ``GOV_RESOURCES_NPROC``. ``PATH`` holds only the stub folder and ``/usr/local/bin:/usr/bin:/bin``, so the
machine's own ``nvidia-smi`` (``/usr/lib/wsl/lib``) is never reached. Registry entries are planted as the files the
existing registry writes (``~/.gov-os/machine/sessions/<pid>.json``), with the boot and start ticks read from ``/proc``
as ``gov.resources.machine.identity`` reads them; real short-lived ``sleep`` processes stand for sessions.

The two ``gov launch`` lines reuse W2-184's and W2-60a's support modules, imported unchanged (``LaunchKit``).
"""

from __future__ import annotations

import fcntl
import json
import os
import pwd
import re
import shutil
import signal
import stat
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
SUITE = Path(__file__).resolve().parent
ACCEPTANCE = SUITE.parent

KIB, MIB, GIB = 1024, 1024 ** 2, 1024 ** 3
COMMAND_TIMEOUT_S = 60.0

# The two planted machine profiles of RT-3 (EMERGENCY-2 6.3, audit 3 D1): CPUs, RAM bytes, GPU total MiB.
PROFILE_A = {"cpus": 32, "ram": 64 * GIB, "gpu_total": 24_576}
PROFILE_B = {"cpus": 8, "ram": 16 * GIB, "gpu_total": 8_192}


def python_path() -> str:
    """Every child's PYTHONPATH: the runner's own, else this worktree's src (W2-60a's rule)."""
    return os.environ.get("PYTHONPATH") or str(REPO_ROOT / "src")


def user_base() -> str:
    """The real user's ``~/.local`` (the test's own HOME may be an empty folder)."""
    return os.environ.get("PYTHONUSERBASE") or str(Path(pwd.getpwuid(os.getuid()).pw_dir) / ".local")


def write(path, text) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


# --------------------------------------------------------------------------
# /proc readings (as gov.resources.machine.identity reads them)
# --------------------------------------------------------------------------

def boot_id() -> str:
    return Path("/proc/sys/kernel/random/boot_id").read_text().strip()


def start_ticks(pid: int) -> int:
    return int(Path(f"/proc/{pid}/stat").read_text().rsplit(")", 1)[1].split()[19])


def end_id(entry: dict) -> str:
    """The Interface's id of a session's end, from its registry entry."""
    if "boot" in entry and "start_ticks" in entry:
        return f"end:{entry['boot']}:{entry['pid']}:{entry['start_ticks']}"
    return f"end:{entry['pid']}:{entry['started']}"


# --------------------------------------------------------------------------
# The fixture machine
# --------------------------------------------------------------------------

_GPU_STUB = r"""#!/bin/sh
# nvidia-smi stand-in (W2-121c acceptance): answers the GPU query and the compute-apps query from gpu.conf.
. "@CONF@"
if [ "$MODE" = fail ]; then
    echo "NVIDIA-SMI has failed because it couldn't communicate with the NVIDIA driver." >&2
    exit 9
fi
case "$*" in
    *--query-gpu=*) echo "$TOTAL, $USED, $((TOTAL - USED)), 3" ;;
    *--query-compute-apps=*) : ;;
    *) echo "nvidia-smi stand-in" ;;
esac
exit 0
"""

_SUBREAPER = r"""
import ctypes, json, os, subprocess, sys, time
libc = ctypes.CDLL(None, use_errno=True)
if libc.prctl(36, 1, 0, 0, 0) != 0:  # PR_SET_CHILD_SUBREAPER: every orphan of the pass comes here
    sys.exit(97)
with open(sys.argv[1] + ".out", "w+") as out, open(sys.argv[1] + ".err", "w+") as err:
    done = subprocess.run(sys.argv[2:], stdout=out, stderr=err, stdin=subprocess.DEVNULL)  # files: a daemon holding
    out.seek(0)                                                                            # them never delays this
    err.seek(0)
    stdout, stderr = out.read(), err.read()
time.sleep(0.5)
me, kids = os.getpid(), []
for name in os.listdir("/proc"):
    if not name.isdigit():
        continue
    try:
        fields = open(f"/proc/{name}/stat").read().rsplit(")", 1)[1].split()
        line = open(f"/proc/{name}/cmdline", "rb").read().replace(b"\0", b" ").decode("utf-8", "replace")
    except OSError:
        continue
    if int(fields[1]) == me and fields[0] != "Z":
        kids.append({"pid": int(name), "cmdline": line.strip()})
with open(sys.argv[1], "w") as handle:
    json.dump({"rc": done.returncode, "stdout": stdout, "stderr": stderr, "children": kids}, handle)
for kid in kids:
    try:
        os.kill(kid["pid"], 9)
    except OSError:
        pass
"""

# Calls gov's own entry point (gov.cli.main.main) in a loop, after a go file appears: many concurrent senders or
# readers at a few processes' cost. ``reps`` 0: loop until the stop file appears.
_DRIVER = r"""
import contextlib, io, json, os, sys, time
go, out, reps, argv = sys.argv[1], sys.argv[2], int(sys.argv[3]), json.loads(sys.argv[4])
stop = sys.argv[5] if len(sys.argv) > 5 else None
from gov.cli.main import main
deadline = time.time() + 30
while not os.path.exists(go) and time.time() < deadline:
    time.sleep(0.002)
results, i = [], 0
while (i < reps) if reps else not os.path.exists(stop):
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        try:
            code = main([word.replace("{i}", str(i)) for word in argv])
        except SystemExit as error:
            code = error.code
    results.append({"rc": code, "out": buffer.getvalue()})
    i += 1
    if not reps:
        time.sleep(0.01)
with open(out, "w") as handle:
    json.dump(results, handle)
"""


class Box:
    """One fixture machine: HOME, TMPDIR, the stub folder, the planted readings and the processes the test started."""

    def __init__(self, base, home=None):
        self.base = Path(base).resolve()
        self.home = Path(home).resolve() if home is not None else self.base / "home"
        self.tmpdir = self.base / "tmp"
        self.bin = self.base / "bin"
        self.work = self.base / "work"  # a plain folder with no dispatch.yaml: where every gov child runs
        self.meminfo = self.base / "readings" / "meminfo"
        self.gpu_conf = self.base / "readings" / "gpu.conf"
        for folder in (self.home, self.tmpdir, self.bin, self.work, self.meminfo.parent):
            folder.mkdir(parents=True, exist_ok=True)
        self.cpus = None
        self.processes: list[subprocess.Popen] = []
        self.locks: list[int] = []
        self.profile(PROFILE_A)

    # -- the planted machine ------------------------------------------------------------------------------------------

    def profile(self, profile, gpu_used=0, gpu=True):
        """Plant CPUs, RAM (MemTotal; MemAvailable half of it) and the GPU (a stand-in at ``gpu_used`` MiB), or no
        ``nvidia-smi`` at all with ``gpu=False``."""
        self.cpus = profile["cpus"]
        ram_kib = profile["ram"] // KIB
        write(self.meminfo, f"MemTotal:       {ram_kib} kB\nMemFree:        {ram_kib // 2} kB\n"
                            f"MemAvailable:   {ram_kib // 2} kB\n")
        if gpu:
            self.gpu(profile["gpu_total"], gpu_used)
        else:
            self.no_gpu()

    def gpu(self, total, used, mode="ok"):
        write(self.gpu_conf, f"MODE={mode}\nTOTAL={int(total)}\nUSED={int(used)}\n")
        stub = write(self.bin / "nvidia-smi", _GPU_STUB.replace("@CONF@", str(self.gpu_conf)))
        stub.chmod(stub.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

    def gpu_fails(self):
        """An ``nvidia-smi`` that is there but fails (exit 9, the driver message)."""
        self.gpu(1, 0, mode="fail")

    def no_gpu(self):
        try:
            (self.bin / "nvidia-smi").unlink()
        except FileNotFoundError:
            pass
        found = shutil.which("nvidia-smi", path=self.env()["PATH"])
        assert found is None, f"harness: an nvidia-smi is still on the fixture PATH: {found}"

    def plant_gate(self, verification_peak_bytes, working_size_bytes):
        """``~/.gov-os/machine/gate.json`` in W2-20's dated form, with the two measured sizes RT-3 reads."""
        today = time.strftime("%Y-%m-%d")

        def dated(value):
            return {"value": value, "date": today, "source": "planted for the W2-121c acceptance tests"}

        values = {
            "memory_floor_bytes": dated(1 * GIB), "verification_peak_bytes": dated(int(verification_peak_bytes)),
            "working_size_bytes": dated(int(working_size_bytes)), "rebuild_peak_bytes": dated(2 * GIB),
            "disk_floor_bytes": dated(1 * GIB), "inode_floor": dated(1000),
            "verification_lock": dated(str(self.base / "verification.lock")), "gpu_margin": dated(0.10),
            "oom_floor_bytes": dated(1 * GIB), "heavy_slots": dated(2),
            "gpu_shares": dated({"embedder_mib": 0, "reranker_mib": 0}),
            "embedding_servers": {name: {"cpus": "0", "nice": 10, "date": today, "source": "planted"}
                                  for name in ("shared", "query")},
        }
        return write(self.machine / "gate.json", json.dumps(values, indent=1))

    # -- places -------------------------------------------------------------------------------------------------------

    @property
    def gov_os(self) -> Path:
        return self.home / ".gov-os"

    @property
    def machine(self) -> Path:
        return self.gov_os / "machine"

    @property
    def sessions(self) -> Path:
        return self.machine / "sessions"

    @property
    def inbox_root(self) -> Path:
        return self.gov_os / "inbox"

    @property
    def runtime(self) -> Path:
        return self.gov_os / "runtime"

    @property
    def state_path(self) -> Path:
        return self.runtime / "state.json"

    @property
    def log_path(self) -> Path:
        return self.runtime / "log.jsonl"

    def home_files(self) -> dict:
        """Every file under HOME and its bytes: what a refused command must leave unchanged."""
        found = {}
        for path in sorted(self.home.rglob("*")):
            if path.is_file():
                found[str(path.relative_to(self.home))] = path.read_bytes()
        return found

    # -- running gov --------------------------------------------------------------------------------------------------

    def env(self, extra=None) -> dict:
        env = {
            "PATH": f"{self.bin}:/usr/local/bin:/usr/bin:/bin",
            "HOME": str(self.home),
            "TMPDIR": str(self.tmpdir),
            "LANG": "C.UTF-8", "LC_ALL": "C.UTF-8", "TZ": "UTC",
            "PYTHONPATH": python_path(),
            "PYTHONUSERBASE": user_base(),
            "PYTHONDONTWRITEBYTECODE": "1",
            "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_SYSTEM": os.devnull,
            "GOV_RESOURCES_NPROC": str(self.cpus),
            "GOV_RESOURCES_MEMINFO": str(self.meminfo),
        }
        env.update(extra or {})
        return {key: value for key, value in env.items() if value is not None}

    def argv(self, *args) -> list[str]:
        return [sys.executable, "-m", "gov.cli.main", *map(str, args)]

    def gov(self, *args, cwd=None, extra_env=None, timeout=COMMAND_TIMEOUT_S) -> subprocess.CompletedProcess:
        try:
            return subprocess.run(self.argv(*args), cwd=str(cwd or self.work), env=self.env(extra_env),
                                  capture_output=True, text=True, timeout=timeout, stdin=subprocess.DEVNULL)
        except subprocess.TimeoutExpired:
            raise AssertionError(f"gov {' '.join(map(str, args))} did not end within {timeout:.0f} s") from None

    def popen(self, *args, cwd=None, extra_env=None) -> subprocess.Popen:
        proc = subprocess.Popen(self.argv(*args), cwd=str(cwd or self.work), env=self.env(extra_env),
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, stdin=subprocess.DEVNULL)
        self.processes.append(proc)
        return proc

    def ok(self, *args, cwd=None, extra_env=None) -> dict:
        """``gov <args> --json`` that must succeed: its envelope's ``result``."""
        done = self.gov(*args, "--json", cwd=cwd, extra_env=extra_env)
        assert done.returncode == 0, f"gov {' '.join(map(str, args))} --json: exit {done.returncode}\n{said(done)}"
        return envelope(done)["result"]

    # -- the inbox ----------------------------------------------------------------------------------------------------

    def send(self, to, kind, text, *more, extra_env=None) -> dict:
        return self.ok("msg", "send", to, kind, text, *more, extra_env=extra_env)

    def inbox_file(self, address) -> Path:
        return self.inbox_root / address / "messages.jsonl"

    def messages(self, address) -> list[dict]:
        """Every message in the address's inbox file, read straight from the file (no mark moved); a line that is
        not a whole JSON object fails the case."""
        path = self.inbox_file(address)
        if not path.is_file():
            return []
        data = path.read_bytes()
        assert not data or data.endswith(b"\n"), f"{path} ends in a partial line: {data[-200:]!r}"
        found = []
        for number, line in enumerate(data.decode("utf-8").splitlines(), 1):
            try:
                item = json.loads(line)
            except ValueError:
                raise AssertionError(f"{path} line {number} is not whole JSON: {line[:200]!r}") from None
            assert isinstance(item, dict), f"{path} line {number} is not a JSON object: {line[:200]!r}"
            found.append(item)
        return found

    def wakes(self, address) -> list[dict]:
        return [item for item in self.messages(address) if item.get("kind") == "wake"]

    def mark_bytes(self, address):
        path = self.inbox_root / address / "mark"
        return path.read_bytes() if path.is_file() else None

    def watch(self, to, name, *form) -> str:
        """``gov msg watch --to <to> --name <name> <form>``: the request's id."""
        result = self.ok("msg", "watch", "--to", to, "--name", name, *form)
        assert isinstance(result, dict) and isinstance(result.get("id"), str) and result["id"], (
            f"gov msg watch gave no request id: {result}")
        return result["id"]

    # -- the watch pass -----------------------------------------------------------------------------------------------

    def run_pass(self, check=True, extra_env=None) -> subprocess.CompletedProcess:
        done = self.gov("dispatch", "watch", "--json", extra_env=extra_env)
        if check:
            assert done.returncode == 0, f"gov dispatch watch: exit {done.returncode}\n{said(done)}"
        return done

    def passes(self, count):
        for _ in range(count):
            self.run_pass()

    def state(self) -> dict:
        assert self.state_path.is_file(), f"no {self.state_path} after the pass"
        try:
            data = json.loads(self.state_path.read_text(encoding="utf-8"))
        except ValueError as error:
            raise AssertionError(f"state.json does not parse: {error}") from None
        assert isinstance(data, dict), "state.json is not a JSON object"
        return data

    def log(self) -> list[dict]:
        if not self.log_path.is_file():
            return []
        lines = []
        for number, line in enumerate(self.log_path.read_text(encoding="utf-8").splitlines(), 1):
            try:
                lines.append(json.loads(line))
            except ValueError:
                raise AssertionError(f"log.jsonl line {number} is not whole JSON: {line[:200]!r}") from None
        return lines

    def hold_runtime_lock(self) -> int:
        """The test holds the watch pass's lock: an exclusive flock on the runtime folder itself."""
        self.runtime.mkdir(parents=True, exist_ok=True)
        fd = os.open(self.runtime, os.O_RDONLY)
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        self.locks.append(fd)
        return fd

    def release_locks(self):
        while self.locks:
            fd = self.locks.pop()
            try:
                fcntl.flock(fd, fcntl.LOCK_UN)
            finally:
                os.close(fd)

    def pass_under_subreaper(self) -> dict:
        """One pass run by a wrapper that is a child subreaper: what the pass left running is the wrapper's children
        half a second after the pass returned (``children``), killed afterwards."""
        out = self.base / f"subreaper-{time.monotonic_ns()}.json"
        done = subprocess.run([sys.executable, "-c", _SUBREAPER, str(out), *self.argv("dispatch", "watch", "--json")],
                              cwd=str(self.work), env=self.env(), capture_output=True, text=True,
                              timeout=COMMAND_TIMEOUT_S)
        assert done.returncode != 97, "harness: PR_SET_CHILD_SUBREAPER is refused on this machine"
        assert out.is_file(), f"harness: the subreaper wrapper wrote nothing\n{done.stderr[-2000:]}"
        return json.loads(out.read_text())

    # -- sessions and processes ---------------------------------------------------------------------------------------

    def sleeper(self, seconds=120) -> subprocess.Popen:
        proc = subprocess.Popen(["sleep", str(seconds)], stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL)
        self.processes.append(proc)
        return proc

    @staticmethod
    def end(proc: subprocess.Popen):
        """End a process and reap it, so its pid is gone (not a zombie)."""
        if proc.poll() is None:
            proc.kill()
        proc.wait(timeout=10)

    def dead_pid(self) -> tuple[int, int]:
        """A pid whose process ran and is gone, with its start ticks taken while it ran."""
        proc = self.sleeper()
        ticks = start_ticks(proc.pid)
        self.end(proc)
        return proc.pid, ticks

    def register(self, pid, ticks, ticket="DAEO-x121", role="engineer", notify=None, address=None,
                 identity=True) -> dict:
        """A registry entry as the registry writes it (``<pid>.json``, whole), with ``notify`` / ``address`` when
        given."""
        entry = {"pid": pid, "repository": str(self.work), "ticket": ticket, "role": role,
                 "started": time.strftime("%Y-%m-%dT%H:%M:%S+00:00", time.gmtime())}
        if identity:
            entry.update({"boot": boot_id(), "start_ticks": ticks})
        if notify is not None:
            entry["notify"] = notify
        if address is not None:
            entry["address"] = address
        self.sessions.mkdir(parents=True, exist_ok=True)
        temp = self.sessions / f".entry-{pid}.tmp"
        temp.write_text(json.dumps(entry), encoding="utf-8")
        os.replace(temp, self.sessions / f"{pid}.json")
        return entry

    # -- many senders or readers at once --------------------------------------------------------------------------------

    def drivers(self, count, reps, argv, stop=None) -> tuple[Path, list[tuple[subprocess.Popen, Path]]]:
        """``count`` processes calling gov's entry point ``reps`` times each with ``argv`` (``{i}`` the call's number),
        all waiting on one go file (returned); ``reps`` 0 loops until ``stop`` exists."""
        go = self.base / f"go-{time.monotonic_ns()}"
        started = []
        for n in range(count):
            out = self.base / f"driver-{time.monotonic_ns()}-{n}.json"
            words = [word.replace("{n}", str(n)) for word in argv]
            proc = subprocess.Popen([sys.executable, "-c", _DRIVER, str(go), str(out), str(reps), json.dumps(words),
                                     *([str(stop)] if stop else [])], cwd=str(self.work), env=self.env(),
                                    stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
                                    text=True)
            self.processes.append(proc)
            started.append((proc, out))
        return go, started

    @staticmethod
    def driver_results(started, timeout=90) -> list[list[dict]]:
        found = []
        for proc, out in started:
            try:
                _, err = proc.communicate(timeout=timeout)
            except subprocess.TimeoutExpired:
                proc.kill()
                raise AssertionError("harness: a driver did not end in time") from None
            assert out.is_file(), f"harness: a driver wrote no result (exit {proc.returncode})\n{err[-2000:]}"
            found.append(json.loads(out.read_text()))
        return found

    def cleanup(self):
        self.release_locks()
        for proc in self.processes:
            if proc.poll() is None:
                try:
                    proc.send_signal(signal.SIGKILL)
                    proc.wait(timeout=10)
                except (OSError, subprocess.TimeoutExpired):
                    pass


# --------------------------------------------------------------------------
# Reading what gov printed
# --------------------------------------------------------------------------

def said(done) -> str:
    return f"stdout:\n{done.stdout[-3000:]}\nstderr:\n{done.stderr[-3000:]}"


def envelope(done) -> dict:
    try:
        data = json.loads(done.stdout)
    except ValueError:
        raise AssertionError(f"the --json output is not one JSON envelope\n{said(done)}") from None
    assert isinstance(data, dict) and "result" in data, f"no envelope with a result\n{said(done)}"
    return data


def mentions(item, token: str) -> bool:
    """Whether ``token`` appears (case-insensitive) anywhere in ``item`` written as JSON."""
    return token.lower() in json.dumps(item, ensure_ascii=False).lower()


def message_words(message: dict) -> str:
    """A message's text and data, as one string to search."""
    return json.dumps({"text": message.get("text"), "data": message.get("data")}, ensure_ascii=False)


# The GPU never spills: an answer that offers the CPU as a place to run (run/use/fall back ... CPU), unless the phrase
# refuses it ("not run on the CPU"). Mentioning the machine's CPU count is no offer.
OFFER = re.compile(r"\b(run|runs|running|use|using|try|fall(?:s|ing)?[\s-]*back|fallback|instead|spill\w*)\b"
                   r"[^.\n;]{0,24}?\bcpus?\b", re.I)
NEGATION = re.compile(r"\b(not|never|no|nor|won't|cannot|isn't)\b", re.I)


def cpu_offers(text: str) -> list[str]:
    offers = []
    for found in OFFER.finditer(text):
        before = text[max(0, found.start() - 30):found.start()] + " " + found.group(0)
        if not NEGATION.search(before):
            offers.append(found.group(0))
    return offers


# --------------------------------------------------------------------------
# gov launch: W2-184's and W2-60a's harness, imported unchanged
# --------------------------------------------------------------------------

def launch_support():
    """W2-184's support module (which imports W2-60a's as ``b``), never edited."""
    for name in ("W2-184", "W2-60a"):
        folder = str(ACCEPTANCE / name)
        if folder not in sys.path:
            sys.path.insert(0, folder)
    import w2_184_support  # noqa: E402

    return w2_184_support


_WRAPPER = r'''#!@PYTHON@
"""W2-121c: in front of W2-60a's recording stand-in. A session start (not --version) waits for its own registry entry,
logs it, waits for a release file while a hold file exists, then becomes the recording stand-in (same pid)."""
import json, os, sys, time
args = sys.argv[1:]
real = @REAL@
if "--version" not in args:
    entry_path = os.path.join(@SESSIONS@, f"{os.getpid()}.json")
    seen, deadline = None, time.time() + 10
    while time.time() < deadline:
        try:
            with open(entry_path, encoding="utf-8") as handle:
                seen = json.load(handle)
            break
        except (OSError, ValueError):
            time.sleep(0.05)
    with open(@REGISTRY_LOG@, "a", encoding="utf-8") as handle:
        handle.write(json.dumps({"pid": os.getpid(), "entry": seen}) + "\n")
    if os.path.exists(@HOLD@):
        deadline = time.time() + 30
        while not os.path.exists(@RELEASE@) and time.time() < deadline:
            time.sleep(0.05)
os.execv(real, [real] + args)
'''


class LaunchKit:
    """A W2-60a sandbox with the recording stand-in CLI behind a wrapper that captures the session's registry entry
    and can hold the session until released."""

    def __init__(self, base, rubric: bool):
        self.s = launch_support()
        self.b = self.s.b
        self.sandbox = self.b.make_sandbox(Path(base) / "launch")
        self.project = self.s.make_project(self.sandbox, criticality=rubric)
        self.cli = self.b.install_stand_in_cli(self.sandbox)
        real = self.cli.path.with_name("claude-recording")
        os.replace(self.cli.path, real)
        self.registry_log = self.sandbox.elsewhere / "registry-at-start.jsonl"
        self.hold = self.sandbox.elsewhere / "hold"
        self.release = self.sandbox.elsewhere / "release"
        sessions = self.sandbox.home / ".gov-os" / "machine" / "sessions"
        text = (_WRAPPER.replace("@PYTHON@", sys.executable).replace("@REAL@", repr(str(real)))
                .replace("@SESSIONS@", repr(str(sessions))).replace("@REGISTRY_LOG@", repr(str(self.registry_log)))
                .replace("@HOLD@", repr(str(self.hold))).replace("@RELEASE@", repr(str(self.release))))
        write(self.cli.path, text)
        self.cli.path.chmod(0o755)
        self.ticket = self.s.ticket(self.project, self.s.ENGINEER, "C2")

    @property
    def home(self) -> Path:
        return self.sandbox.home

    def exit_with(self, code: int):
        write(self.cli.exit_file, f"{code}\n")

    def launch(self, extra_env=None):
        """``gov launch engineer <ticket>`` through the entry point; W2-60a's ``Launch``."""
        records = Path(self.sandbox.records)
        before_calls, before = len(self.b.calls(self.cli)), self.b._listing(records)
        started = time.time()
        run = self.b.run_gov(self.sandbox, self.project, "launch", self.s.ENGINEER, self.ticket, extra_env=extra_env)
        return self.b.Launch(run, tuple(self.b.calls(self.cli)[before_calls:]), records, before,
                             self.b._listing(records), started, time.time(), ())

    def popen_launch(self, extra_env=None) -> subprocess.Popen:
        return subprocess.Popen(self.b.gov_argv("launch", self.s.ENGINEER, self.ticket), cwd=str(self.project),
                                env=self.b.base_environment(self.sandbox, extra_env), stdin=subprocess.DEVNULL,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    def registry_entries(self) -> list[dict]:
        if not self.registry_log.is_file():
            return []
        return [json.loads(line) for line in self.registry_log.read_text().splitlines() if line.strip()]

    def messages(self, address) -> list[dict]:
        path = self.home / ".gov-os" / "inbox" / address / "messages.jsonl"
        if not path.is_file():
            return []
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def poll(predicate, seconds, step=0.1):
    """``predicate()``'s first true value within ``seconds``, else its last value."""
    deadline = time.monotonic() + seconds
    value = predicate()
    while not value and time.monotonic() < deadline:
        time.sleep(step)
        value = predicate()
    return value

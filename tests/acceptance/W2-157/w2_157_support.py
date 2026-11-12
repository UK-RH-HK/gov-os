"""Support code for the W2-157 acceptance tests (standard library only).

W2-157 delivers the GPU backstop in the product: ``gov resources --backstop <pgid> [<pgid> ...]`` watches the named
process groups of a GPU job and pauses them (SIGSTOP) when GPU memory passes a configured limit, spills into shared
memory (used within 64 MiB of the card's total), or an embedding server is not wholly on the GPU. The tests use only the
public interface the brief states (the command line, the gate's configuration file, the backstop's log, the inbox item,
the envelope's ``result``); nothing here imports ``gov``.

How the code under test is chosen (DEC-732): every command runs in a child process with ``PYTHONPATH`` set to the
``src/`` folder of the working tree this file is in, so in a ticket worktree it runs that worktree's own code; the
first run of a session checks that ``gov`` imports from there.

What is never touched: the real GPU, the real HOME, the real embedding servers (ports 11434 and 11435), the reranker
and every process the test did not start. Every command runs with ``HOME`` set to a folder under pytest's
``tmp_path``, an environment built from scratch, and ``PATH`` set to this test's stand-in folder first (the stand-in
``nvidia-smi``). The stand-in embedding servers are small HTTP servers started by the test on free ports. The "job"
and the "unrelated process" are child processes the test starts, each with ``start_new_session=True`` so each is its own
process group; every teardown sends SIGCONT then SIGKILL to each group it started and waits for them. Nothing is
matched by name.
"""

from __future__ import annotations

import datetime
import json
import os
import re
import signal
import socket
import subprocess
import sys
import threading
import time
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "src"

WAIT_S = 30.0            # how long a test waits for a child to reach a step (a bound, never a promise of the ticket)
COMMAND_TIMEOUT_S = 40.0

GIB = 1024 ** 3
LIMIT_MIB = 15872        # this machine's value (DEC-1067 (GPU safety), DEC-1068 (4)); the file's value is what counts
TOTAL_MIB = 24576        # a card total that is no spill for any reading below the limit
SAFE_PATH = "/usr/local/bin:/usr/bin:/bin"

SMI_ARGV = ["--query-gpu=memory.used,memory.total", "--format=csv,noheader,nounits"]  # L3, exactly

KEYS = ("gpu_backstop_limit_mib", "gpu_backstop_every_s", "gpu_backstop_embedders")
RESULT_KEYS = {"tripped", "reason", "reading", "paused", "skipped", "log", "inbox_item"}
STOPPED = ("T", "t")
RUNNING = ("R", "S", "D")

# The log's lines (L6): each begins with a timestamp.
TS = r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}"
START_RE = re.compile(rf"^{TS} start: limit (\d+) MiB; every ([0-9.]+) s; groups ([0-9 ]+); "
                      rf"skipped \(ended\) ([0-9 ]+|none); embedders ([0-9 ]+|none)$")
TRIP_RE = re.compile(rf"^{TS} TRIP: (.+); reading (\d+)/(\d+) MiB; paused groups ([0-9 ]+)$")
TRIP_NO_READING_RE = re.compile(rf"^{TS} TRIP: (.+); reading none; paused groups ([0-9 ]+)$")
END_RE = re.compile(rf"^{TS} end: every watched group has ended \(([0-9 ]+)\)$")
NO_READING_RE = re.compile(rf"^{TS} no GPU reading: .+$")
INBOX_NAME_RE = re.compile(r"^gpu-backstop-\d{8}-\d{6}\.txt$")


def today() -> str:
    return datetime.date.today().isoformat()


def dated(value, *, date: str | None = None, source: str = "planted for the W2-157 acceptance tests") -> dict:
    """One configuration value in the gate file's usual form."""
    return {"value": value, "date": date or today(), "source": source}


def free_port() -> int:
    """A local port nothing listens on (never 11434 or 11435)."""
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("127.0.0.1", 0))
            port = s.getsockname()[1]
        if port not in (11434, 11435):
            return port


def state_of(pid: int) -> str | None:
    """The process state letter from ``/proc/<pid>/stat`` (``T`` is stopped), or None when there is no such process."""
    try:
        return Path(f"/proc/{pid}/stat").read_text().rsplit(")", 1)[1].split()[0]
    except (OSError, IndexError):
        return None


def wait_for(predicate, what: str, timeout: float = WAIT_S, step: float = 0.02, watch: "Watch | None" = None,
             exit_ok: bool = False):
    """Poll ``predicate`` until it gives a true value, with a deadline. If ``watch`` (the command under test) ends first
    the wait is over: None when ``exit_ok``, otherwise a failure that shows what the command printed."""
    deadline = time.monotonic() + timeout
    while True:
        value = predicate()
        if value:
            return value
        if watch is not None and watch.proc.poll() is not None:
            value = predicate()
            if value:
                return value
            if exit_ok:
                return None
            raise AssertionError(f"the command ended before {what}\n{watch.describe()}")
        if time.monotonic() >= deadline:
            raise AssertionError(f"timed out after {timeout:.0f} s waiting for {what}"
                                 + (f"\n{watch.describe()}" if watch is not None else ""))
        time.sleep(step)


# --- the scripts the children run -----------------------------------------------------------------------------------

# The job and the unrelated process: the same script, the same command line. It installs a handler for every catchable
# signal that records the signal it gets in ``<pid>.signals`` (SIGSTOP cannot be caught: the state in /proc shows it),
# writes ``<pid>.ready``, and then runs until ``end-<pid>`` appears. Modes: ``run``; ``child`` (also starts a child that
# stays in the same group); ``orphan`` (starts that child and the leader exits at once, so the group lives on through
# the child alone).
JOB_SCRIPT = r'''
import os, signal, subprocess, sys, time
folder, mode = sys.argv[1], sys.argv[2]
pid = os.getpid()
def note(signum, frame):
    with open(os.path.join(folder, "%d.signals" % pid), "a") as handle:
        handle.write("%d\n" % signum)
for name in ("SIGTERM", "SIGINT", "SIGHUP", "SIGUSR1", "SIGUSR2", "SIGQUIT", "SIGCONT", "SIGALRM", "SIGTSTP",
             "SIGTTIN", "SIGTTOU"):
    signal.signal(getattr(signal, name), note)
if mode in ("child", "orphan"):
    child = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(300)"], stdin=subprocess.DEVNULL,
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    with open(os.path.join(folder, "%d.child" % pid), "w") as handle:
        handle.write(str(child.pid))
with open(os.path.join(folder, "%d.ready" % pid), "w") as handle:
    handle.write("ready")
if mode == "orphan":
    sys.exit(0)
end = os.path.join(folder, "end-%d" % pid)
deadline = time.monotonic() + 300
while not os.path.exists(end) and time.monotonic() < deadline:
    time.sleep(0.02)
'''

# The stand-in nvidia-smi. It records every call (arguments and time). Asked exactly L3's form
# (``--query-gpu=memory.used,memory.total --format=csv,noheader,nounits``) it answers from the planted sequence, one
# entry per call, the last entry repeating; asked anything else it prints nothing and exits 0. An entry is
# ``{"used", "total"}`` (printed ``<used>, <total>``), ``{"exit": N}`` (stderr text, exit N) or ``{"text": "..."}``;
# an entry marked ``gate`` waits until the test creates ``gates/<index>`` before it answers.
NVIDIA_SMI = r'''#!@PYTHON@
import fcntl, json, os, sys, time
STATE, CALLS, COUNT, GATES = @STATE@, @CALLS@, @COUNT@, @GATES@
EXPECT = ["--query-gpu=memory.used,memory.total", "--format=csv,noheader,nounits"]
args = sys.argv[1:]
fd = os.open(COUNT, os.O_RDWR | os.O_CREAT, 0o644)
fcntl.flock(fd, fcntl.LOCK_EX)
raw = os.read(fd, 32).decode() or "0"
index = int(raw)
with open(CALLS, "a") as handle:
    handle.write(json.dumps({"args": args, "t": time.time()}) + "\n")
if args == EXPECT:
    os.lseek(fd, 0, os.SEEK_SET)
    os.ftruncate(fd, 0)
    os.write(fd, str(index + 1).encode())
os.close(fd)
if args != EXPECT:
    sys.exit(0)
entries = json.load(open(STATE))
entry = entries[min(index, len(entries) - 1)]
if entry.get("gate") and index < len(entries):   # only the call of that number waits, not the repeats after it
    gate = os.path.join(GATES, str(index))
    deadline = time.monotonic() + 60
    while not os.path.exists(gate) and time.monotonic() < deadline:
        time.sleep(0.01)
if "exit" in entry:
    print("NVIDIA-SMI has failed because it couldn't communicate with the NVIDIA driver.", file=sys.stderr)
    sys.exit(entry["exit"])
if "text" in entry:
    print(entry["text"])
    sys.exit(0)
print("%d, %d" % (entry["used"], entry["total"]))
'''


# --- the stand-in embedding server ----------------------------------------------------------------------------------

def model(name: str = "nomic-embed-text:latest", size: int = 700_000_000, size_vram: int | None = None) -> dict:
    return {"name": name, "size": size, "size_vram": size if size_vram is None else size_vram, "digest": "planted"}


class Embedder:
    """A stand-in embedding server: ``GET /api/ps`` answers a planted body; every request is recorded. It also owns its
    planted log file (``<home>/.ollama/serve-<port>.log``)."""

    def __init__(self, home: Path, *, listen: bool = True, models: list | None = None):
        self.requests: list[tuple[str, str]] = []
        self.status = 200
        self.body = json.dumps({"models": [model()] if models is None else models}).encode()
        self.server = None
        embedder = self

        class Handler(BaseHTTPRequestHandler):
            def _answer(self):
                embedder.requests.append((self.command, self.path))
                if self.command == "GET" and self.path == "/api/ps":
                    body, status = embedder.body, embedder.status
                else:
                    body, status = b"{}", 404
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            do_GET = do_POST = do_PUT = do_DELETE = do_HEAD = do_PATCH = _answer

            def log_message(self, *args):
                pass

        if listen:
            self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
            self.port = self.server.server_address[1]
            assert self.port not in (11434, 11435)
            threading.Thread(target=self.server.serve_forever, daemon=True).start()
        else:
            self.port = free_port()  # nothing listens here
        self.log = home / ".ollama" / f"serve-{self.port}.log"

    def entry(self) -> dict:
        return {"port": self.port, "log": str(self.log)}

    def answer(self, models: list) -> None:
        self.body, self.status = json.dumps({"models": models}).encode(), 200

    def answer_raw(self, body: str | bytes, status: int = 200) -> None:
        self.body, self.status = (body.encode() if isinstance(body, str) else body), status

    def plant_log(self, text: str) -> None:
        self.log.parent.mkdir(parents=True, exist_ok=True)
        self.log.write_text(text)

    def append_log(self, text: str) -> None:
        self.log.parent.mkdir(parents=True, exist_ok=True)
        with open(self.log, "a") as handle:
            handle.write(text)

    def close(self) -> None:
        if self.server is not None:
            self.server.shutdown()
            self.server.server_close()


# --- processes ------------------------------------------------------------------------------------------------------

class Job:
    """A child process in its own process group (``pgid`` is its pid), started by the test."""

    def __init__(self, machine: "Machine", proc: subprocess.Popen):
        self.machine, self.proc = machine, proc

    @property
    def pgid(self) -> int:
        return self.proc.pid

    def state(self) -> str | None:
        return state_of(self.proc.pid)

    def stopped(self) -> bool:
        return self.state() in STOPPED

    def running(self) -> bool:
        return self.state() in RUNNING

    def signals(self) -> list[int]:
        path = self.machine.jobs_dir / f"{self.proc.pid}.signals"
        return [int(line) for line in path.read_text().split()] if path.exists() else []

    def child_pid(self) -> int:
        return int((self.machine.jobs_dir / f"{self.proc.pid}.child").read_text())

    def end(self) -> None:
        """Let the job end on its own and reap it, so its group no longer exists."""
        (self.machine.jobs_dir / f"end-{self.proc.pid}").write_text("end")
        self.proc.wait(timeout=WAIT_S)


class Watch:
    """The command under test, running (``gov resources --backstop ...`` in a child process)."""

    def __init__(self, proc: subprocess.Popen, argv: list[str], out_path: Path, err_path: Path):
        self.proc, self.argv, self.out_path, self.err_path = proc, argv, out_path, err_path

    def texts(self) -> tuple[str, str]:
        return (self.out_path.read_text() if self.out_path.exists() else "",
                self.err_path.read_text() if self.err_path.exists() else "")

    def describe(self) -> str:
        out, err = self.texts()
        return f"command: {' '.join(self.argv)}\nexit: {self.proc.poll()}\nstdout: {out}\nstderr: {err}"


@dataclass
class Outcome:
    code: int
    envelope: dict | None
    out: str
    err: str

    def text(self) -> str:
        return f"exit: {self.code}\nenvelope: {self.envelope}\nstdout: {self.out}\nstderr: {self.err}"

    def result(self) -> dict:
        """The ``result`` of a command that succeeded (exit 0, ``ok``), checked against L8's shape."""
        assert self.envelope is not None, f"the command printed no JSON envelope\n{self.text()}"
        assert self.code == 0 and self.envelope.get("ok") is True, f"the command did not succeed\n{self.text()}"
        assert "resources" in str(self.envelope.get("command")), f"the envelope names another command\n{self.text()}"
        result = self.envelope.get("result")
        assert isinstance(result, dict) and set(result) == RESULT_KEYS, (
            f"the result is not L8's object (keys {sorted(RESULT_KEYS)})\n{self.text()}")
        assert isinstance(result["tripped"], bool), self.text()
        assert isinstance(result["paused"], list) and isinstance(result["skipped"], list), self.text()
        assert result["reason"] is None or isinstance(result["reason"], str), self.text()
        assert result["reading"] is None or (isinstance(result["reading"], dict)
                                             and set(result["reading"]) == {"used_mib", "total_mib"}), self.text()
        return result

    def refusal(self, code: int = 1) -> dict:
        """The error of a refused start: ``ok: false`` and the exit ``code``; returns the envelope's ``error``."""
        assert self.code == code, f"expected exit {code}\n{self.text()}"
        assert self.envelope is not None and self.envelope.get("ok") is False, f"expected ok: false\n{self.text()}"
        error = self.envelope.get("error")
        assert isinstance(error, dict), f"the envelope has no error\n{self.text()}"
        return error


_SOURCE_CHECKED = False


class Machine:
    """One test's world: a planted HOME and project, the stand-in ``nvidia-smi``, stand-in servers, child processes."""

    def __init__(self, base: Path):
        self.base = base
        self.home = base / "home"
        self.project = base / "project"
        self.bin = base / "bin"              # the stand-in nvidia-smi's folder, first on PATH
        self.scripts = base / "scripts"
        self.jobs_dir = base / "jobs"        # the jobs' own marks (outside the planted HOME and project)
        self.work = base / "work"            # the stand-in's state, calls and the commands' output
        self.tmp = base / "tmp"
        for folder in (self.home, self.project, self.bin, self.scripts, self.jobs_dir, self.work, self.tmp):
            folder.mkdir()
        (self.scripts / "job.py").write_text(JOB_SCRIPT)
        self.smi_state, self.smi_calls_file = self.work / "smi.json", self.work / "smi-calls.jsonl"
        self.smi_count, self.smi_gates = self.work / "smi-count", self.work / "smi-gates"
        self.smi_gates.mkdir()
        self.procs: list[subprocess.Popen] = []
        self.embedders: list[Embedder] = []
        self._runs = 0
        self.gate = self.base_gate()
        self.gate_text: str | None = None     # raw bytes to plant instead of ``gate`` (a malformed file)
        self.gate_missing = False

    # ------------------------------------------------------------------ places

    @property
    def machine_dir(self) -> Path:
        return self.home / ".gov-os" / "machine"

    @property
    def gate_file(self) -> Path:
        return self.machine_dir / "gate.json"

    @property
    def log_file(self) -> Path:
        return self.machine_dir / "gpu-backstop.log"

    @property
    def inbox(self) -> Path:
        return self.project / ".gov-runtime" / "dispatch" / "inbox"

    # ------------------------------------------------------------------ the gate's configuration file

    def base_gate(self) -> dict:
        """A whole, valid gate file: W2-20's eleven dated values and the embedding servers' section (the backstop
        reads none of them), and the three W2-157 values, with a poll period of 0.1 s so each case takes seconds."""
        cpus = sorted(os.sched_getaffinity(0))
        shared, query = str(cpus[-1]), str(cpus[-2] if len(cpus) > 1 else cpus[-1])
        return {
            "memory_floor_bytes": dated(3 * GIB, source="DEC-942 item 2 (planted)"),
            "verification_peak_bytes": dated(4 * GIB, source="measured (planted)"),
            "working_size_bytes": dated(1 * GIB, source="measured (planted)"),
            "rebuild_peak_bytes": dated(2 * GIB, source="measured (planted)"),
            "disk_floor_bytes": dated(100 * GIB, source="DEC-898 item 1 (planted)"),
            "inode_floor": dated(10_000_000, source="DEC-898 item 1 (planted)"),
            "verification_lock": dated(str(self.base / "verification.lock"), source="planted"),
            "gpu_margin": dated(0.10, source="DEC-950 item 2 (planted)"),
            "oom_floor_bytes": dated(1 * GIB, source="planted"),
            "heavy_slots": dated(2, source="planted"),
            "gpu_shares": dated({"embedder_mib": 0, "reranker_mib": 0}, source="planted"),
            "embedding_servers": {
                "shared": {"cpus": shared, "nice": 10},
                "query": {"cpus": query, "nice": 10},
                "date": today(), "source": "planted",
            },
            "gpu_backstop_limit_mib": dated(LIMIT_MIB, source="DEC-1067 (GPU safety), DEC-1068 (4) (planted)"),
            "gpu_backstop_every_s": dated(0.1, source="planted: a short period for the tests"),
            "gpu_backstop_embedders": dated([], source="planted"),
        }

    def write_gate(self) -> None:
        if self.gate_missing:
            self.gate_file.unlink(missing_ok=True)
            return
        self.machine_dir.mkdir(parents=True, exist_ok=True)
        self.gate_file.write_text(self.gate_text if self.gate_text is not None else json.dumps(self.gate, indent=1))

    def set_limit(self, mib) -> None:
        self.gate["gpu_backstop_limit_mib"] = dated(mib)

    def set_every(self, seconds) -> None:
        self.gate["gpu_backstop_every_s"] = dated(seconds)

    def add_embedder(self, *, listen: bool = True, models: list | None = None, log_text: str | None = None) -> Embedder:
        """A stand-in embedding server entered in the file's ``gpu_backstop_embedders``. ``log_text``: plant its log with
        that text now (None: the log does not exist); ``listen=False``: the port has nothing listening."""
        embedder = Embedder(self.home, listen=listen, models=models)
        if log_text is not None:
            embedder.plant_log(log_text)
        self.gate["gpu_backstop_embedders"]["value"].append(embedder.entry())
        self.embedders.append(embedder)
        return embedder

    # ------------------------------------------------------------------ the stand-in nvidia-smi

    def plant_smi(self, readings, *, gated=()) -> None:
        """Put the stand-in ``nvidia-smi`` first on PATH. ``readings``: one entry per call (the last repeats): a pair
        ``(used, total)`` in MiB or a dict (``{"exit": 9}``, ``{"text": "garbage"}``). ``gated``: the 0-based call
        numbers that wait for ``release(n)`` before answering."""
        entries = []
        for i, reading in enumerate(readings):
            entry = dict(reading) if isinstance(reading, dict) else {"used": reading[0], "total": reading[1]}
            if i in gated:
                entry["gate"] = True
            entries.append(entry)
        self.smi_state.write_text(json.dumps(entries))
        script = self.bin / "nvidia-smi"
        text = NVIDIA_SMI
        for name, value in (("@PYTHON@", sys.executable), ("@STATE@", repr(str(self.smi_state))),
                            ("@CALLS@", repr(str(self.smi_calls_file))), ("@COUNT@", repr(str(self.smi_count))),
                            ("@GATES@", repr(str(self.smi_gates)))):
            text = text.replace(name, value)
        script.write_text(text)
        script.chmod(0o755)

    def smi_calls(self) -> list[dict]:
        if not self.smi_calls_file.exists():
            return []
        return [json.loads(line) for line in self.smi_calls_file.read_text().splitlines() if line.strip()]

    def smi_argvs(self) -> list[list[str]]:
        return [call["args"] for call in self.smi_calls()]

    def release(self, index: int) -> None:
        (self.smi_gates / str(index)).write_text("go")

    def wait_calls(self, count: int, watch: Watch | None = None, exit_ok: bool = False):
        return wait_for(lambda: len(self.smi_calls()) >= count, f"{count} calls of nvidia-smi", watch=watch,
                        exit_ok=exit_ok)

    # ------------------------------------------------------------------ processes

    def start_job(self, mode: str = "run") -> Job:
        """A job in its own process group; returns once its handlers are installed. Every job has the same command
        line, so two jobs are told apart by nothing but their group."""
        proc = subprocess.Popen([sys.executable, str(self.scripts / "job.py"), str(self.jobs_dir), mode],
                                stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                start_new_session=True, env={"PATH": SAFE_PATH})
        self.procs.append(proc)
        ready = self.jobs_dir / f"{proc.pid}.ready"
        wait_for(ready.exists, "a job to be ready")
        return Job(self, proc)

    def ended_group(self) -> int:
        """The id of a process group that has ended (a job that ended on its own and was reaped)."""
        job = self.start_job()
        job.end()
        return job.pgid

    def env(self, path: str | None = None, **extra) -> dict:
        env = {
            "PATH": path if path is not None else f"{self.bin}:{SAFE_PATH}",
            "HOME": str(self.home),
            "TMPDIR": str(self.tmp),
            "LC_ALL": "C",
            "PYTHONPATH": str(SRC),
            "PYTHONDONTWRITEBYTECODE": "1",
            "GIT_CONFIG_NOSYSTEM": "1",
        }
        if os.environ.get("PYTHONUSERBASE"):  # where this interpreter's own packages are, not a configuration
            env["PYTHONUSERBASE"] = os.environ["PYTHONUSERBASE"]
        env.update({key: value for key, value in extra.items() if value is not None})
        return env

    def _check_source(self) -> None:
        global _SOURCE_CHECKED
        if _SOURCE_CHECKED:
            return
        done = subprocess.run([sys.executable, "-c", "import gov, sys; sys.stdout.write(gov.__file__)"],
                              env=self.env(), capture_output=True, text=True, timeout=COMMAND_TIMEOUT_S)
        assert done.returncode == 0, f"gov cannot be imported with PYTHONPATH={SRC}: {done.stderr}"
        where = os.path.realpath(done.stdout)
        assert where.startswith(os.path.realpath(SRC) + os.sep), f"gov would import from {where}, not from {SRC}"
        _SOURCE_CHECKED = True

    def argv(self, groups, *extra: str, root: Path | None = None, json_output: bool = True) -> list[str]:
        argv = [sys.executable, "-m", "gov.cli.main", "resources", "--backstop", *[str(g) for g in groups], *extra,
                "--root", str(root or self.project)]
        if json_output:
            argv.append("--json")
        return argv

    def start_watch(self, groups, *extra: str, path: str | None = None, env_extra: dict | None = None,
                    plant: bool = True) -> Watch:
        """``gov resources --backstop <groups> [extra] --root <project> --json`` in a child process of its own group
        (never one of the named groups). The gate file is planted first (``plant=False`` leaves it as it is)."""
        self._check_source()
        if plant:
            self.write_gate()
        self._runs += 1
        out_path, err_path = self.work / f"out-{self._runs}.txt", self.work / f"err-{self._runs}.txt"
        argv = self.argv(groups, *extra)
        proc = subprocess.Popen(argv, cwd=str(self.project), env=self.env(path, **(env_extra or {})),
                                stdin=subprocess.DEVNULL, stdout=open(out_path, "w"), stderr=open(err_path, "w"),
                                start_new_session=True)
        self.procs.append(proc)
        return Watch(proc, argv, out_path, err_path)

    def finish(self, watch: Watch, timeout: float = COMMAND_TIMEOUT_S) -> Outcome:
        """Wait for the command to end (killing it and failing at the bound) and return what it did."""
        try:
            watch.proc.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            self._kill_group(watch.proc)
            raise AssertionError(f"the command did not end within {timeout:.0f} s\n{watch.describe()}") from None
        out, err = watch.texts()
        try:
            envelope = json.loads(out)
        except ValueError:
            envelope = None
        return Outcome(watch.proc.returncode, envelope, out, err)

    def run(self, groups, *extra: str, path: str | None = None, env_extra: dict | None = None,
            timeout: float = COMMAND_TIMEOUT_S) -> Outcome:
        return self.finish(self.start_watch(groups, *extra, path=path, env_extra=env_extra), timeout)

    def watch_quietly(self, watch: Watch, job: Job, polls: int = 4) -> Outcome:
        """No trip is expected: wait until nvidia-smi has been asked ``polls`` times (so ``polls - 1`` readings were
        judged), check the job still runs and received nothing, end the job, and return the command's outcome."""
        self.wait_calls(polls, watch=watch)
        assert job.running(), f"the job was paused or ended (state {job.state()})\n{watch.describe()}"
        assert job.signals() == [], f"the job received signals {job.signals()}"
        job.end()
        return self.finish(watch)

    @staticmethod
    def _kill_group(proc: subprocess.Popen) -> None:
        for sig in (signal.SIGCONT, signal.SIGKILL):
            try:
                os.killpg(proc.pid, sig)
            except OSError:
                pass

    def cleanup(self) -> None:
        for proc in self.procs:
            self._kill_group(proc)
        for proc in self.procs:
            try:
                proc.wait(timeout=WAIT_S)
            except subprocess.TimeoutExpired:
                pass
        for embedder in self.embedders:
            embedder.close()

    # ------------------------------------------------------------------ what the command wrote

    def log_lines(self) -> list[str]:
        return self.log_file.read_text().splitlines() if self.log_file.exists() else []

    def trips(self) -> list[re.Match]:
        found = []
        for line in self.log_lines():
            match = TRIP_RE.match(line) or TRIP_NO_READING_RE.match(line)
            if match:
                found.append(match)
            else:
                assert " TRIP:" not in line, f"a TRIP line not in L6's form: {line!r}"
        return found

    def inbox_items(self) -> list[Path]:
        return sorted(self.inbox.iterdir()) if self.inbox.is_dir() else []

    def snapshot(self, *roots: Path) -> dict:
        """Every file under the roots: path -> (size, mtime_ns, bytes)."""
        files = {}
        for root in roots:
            for folder, _, names in os.walk(root):
                for name in names:
                    path = Path(folder) / name
                    stat = path.stat()
                    files[str(path)] = (stat.st_size, stat.st_mtime_ns, path.read_bytes())
        return files

    def folders(self, *roots: Path) -> set[str]:
        return {str(Path(folder)) for root in roots for folder, _, _ in os.walk(root)}

    def nothing_started(self, why: str) -> None:
        """Nothing was read, written or signalled: no log, no inbox, no call of nvidia-smi, no request to a server."""
        assert not self.log_file.exists(), f"{why}: the log was written: {self.log_file.read_text()}"
        assert not self.inbox.exists(), f"{why}: the inbox folder was made"
        assert self.smi_calls() == [], f"{why}: nvidia-smi was asked: {self.smi_calls()}"
        assert all(e.requests == [] for e in self.embedders), f"{why}: a server was asked"


def names_group(text: str, pgid: int) -> bool:
    """True when ``text`` holds the number ``pgid`` as a whole number (not inside a longer one)."""
    return re.search(rf"(?<!\d){pgid}(?!\d)", text) is not None


def same_path(a, b) -> bool:
    return os.path.realpath(str(a)) == os.path.realpath(str(b))


def assert_untouched(job: Job, what: str = "the job") -> None:
    """A job that was never named: running, and no signal reached it."""
    assert job.state() not in STOPPED, f"{what} was stopped (state {job.state()})"
    assert job.running(), f"{what} is not running (state {job.state()})"
    assert job.signals() == [], f"{what} received signals {job.signals()}"


def assert_inbox_item(path: Path, *, reason: str, paused: list[int], skipped: list[int]) -> None:
    """L7: the item's first three lines, then the paused and skipped lines, then a resume line and a stop line for
    each paused group."""
    assert INBOX_NAME_RE.match(path.name), f"the item's name is not gpu-backstop-<YYYYmmdd-HHMMSS>.txt: {path.name}"
    lines = [line for line in path.read_text().splitlines() if line.strip()]
    assert lines[:3] == ["log: gpu-backstop.log", "W2: none", f"status: GPU backstop tripped: {reason}"], lines[:3]
    assert lines[3] == "paused: " + " ".join(str(g) for g in paused), lines
    assert lines[4] == "skipped (already ended): " + (" ".join(str(g) for g in skipped) or "none"), lines
    expected = ([f"resume: kill -CONT -- -{g}" for g in paused]
                + [f"stop: kill -TERM -- -{g} && kill -CONT -- -{g}" for g in paused])
    assert sorted(lines[5:]) == sorted(expected), f"the resume and stop lines are not L7's:\n{lines[5:]}"

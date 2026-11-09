"""Support code for the W2-20 acceptance tests (standard library only).

W2-20 delivers the machine-wide resource gate: ``gov resources`` (a reading of the machine and of every live Gov OS
session in a registry under ``~/.gov-os/machine/``), its start check, its heavy-job slots, its re-measure and its
trip-wire; a disk reading ``gov close`` can call; the launch refusal of DEC-1088 (5)(b); and the query embedder's
automatic start of DEC-1037. The tests use it only through the public interface stated in ``README.md``.

How the code under test is chosen (DEC-732): every command runs with ``PYTHONPATH`` set to the ``src/`` folder of the
working tree this file is in, so in a ticket worktree it runs that worktree's own code.

What is never touched: the real ``~/.gov-os/``, the real GPU, the real embedding servers (ports 11434 and 11435) and
``~/.local/bin`` (the interim wrapper). Every command runs with ``HOME`` set to a temporary folder, an environment
built from scratch, and ``PATH`` set to this test's stand-in folder and ``/usr/local/bin:/usr/bin:/bin`` only, so no
real ``nvidia-smi`` and no wrapper is found. Every machine reading comes from a file the test writes. "Live" and
"dead" sessions and heavy jobs are child processes the test starts and stops itself, each in its own process group.
"""

from __future__ import annotations

import datetime
import json
import os
import signal
import socket
import subprocess
import sys
import time
from pathlib import Path

SRC = Path(__file__).resolve().parents[3] / "src"

COMMAND_TIMEOUT_S = 120.0  # a wait under parallel load, not a time the ticket promises
WAIT_S = 60.0              # how long a test waits for a child to reach a step

GIB = 1024 ** 3
MIB = 1024 ** 2
KIB = 1024

SAFE_PATH = "/usr/local/bin:/usr/bin:/bin"  # no ~/.local/bin (the wrapper), no /usr/lib/wsl/lib (the real nvidia-smi)

GATE_SHUT_ERROR = "RESOURCE_GATE_SHUT"
CONDITIONS = ("memory", "load", "cpu", "disk", "inodes", "config", "gpu")

# The common runtimes' thread limits a heavy slot sets (Go, OpenMP, MKL, OpenBLAS, Rayon, numexpr, Accelerate), and
# the slot's own budget variable that the product's pools read (gov.secrets).
RUNTIME_THREAD_VARS = ("GOMAXPROCS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS",
                       "RAYON_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS")
BUDGET_VAR = "GOV_HEAVY_THREAD_BUDGET"
THREAD_VARS = RUNTIME_THREAD_VARS + (BUDGET_VAR,)

# The configuration file's keys (README, "The configuration file"); each value is {"value", "date", "source"}.
GATE_KEYS = ("memory_floor_bytes", "verification_peak_bytes", "working_size_bytes", "disk_floor_bytes",
             "inode_floor", "verification_lock", "gpu_margin", "oom_floor_bytes", "heavy_slots", "gpu_shares")
MEASURED_KEYS = ("verification_peak_bytes", "working_size_bytes")
REBUILD_PEAK_KEY = "rebuild_peak_bytes"  # P-5 (a): the re-measure's third figure, from rebuild slot holders' samples


def today() -> str:
    return datetime.date.today().isoformat()


def days_ago(n: int) -> str:
    return (datetime.date.today() - datetime.timedelta(days=n)).isoformat()


def dated(value, *, date: str | None = None, source: str = "planted for the W2-20 acceptance tests") -> dict:
    """One configuration value with its date and source."""
    return {"value": value, "date": date or today(), "source": source}


def allowed_cpus() -> list[int]:
    """The CPUs this process may run on; every CPU set the tests plant is taken from these."""
    return sorted(os.sched_getaffinity(0))


def cpu_list(cpus) -> str:
    return ",".join(str(c) for c in sorted(cpus))


def parse_cpu_list(text: str) -> set[int]:
    cpus: set[int] = set()
    for part in text.split(","):
        low, _, high = part.strip().partition("-")
        cpus.update(range(int(low), int(high or low) + 1))
    return cpus


def free_port() -> int:
    """A local port nothing listens on (never 11434 or 11435)."""
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("127.0.0.1", 0))
            port = s.getsockname()[1]
        if port not in (11434, 11435):
            return port


def wait_for(predicate, what: str, timeout: float = WAIT_S, step: float = 0.05):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        value = predicate()
        if value:
            return value
        time.sleep(step)
    raise AssertionError(f"timed out after {timeout:.0f} s waiting for {what}")


def alive(pid: int) -> bool:
    """True while ``pid`` names a process that is not a zombie."""
    try:
        state = Path(f"/proc/{pid}/stat").read_text().rsplit(")", 1)[1].split()[0]
    except (OSError, IndexError):
        return False
    return state not in ("Z", "X")


# --- the scripts the children run ------------------------------------------------------------------------------------

# A session process: optionally holds memory (written, so it is resident), optionally takes an exclusive flock on a
# path when a "go" file appears; writes "ready" (and "held") files so the test knows when it is in place.
SESSION_SCRIPT = r'''
import fcntl, os, sys, time
mib, ready, go, lock, more = int(sys.argv[1]), sys.argv[2], sys.argv[3], sys.argv[4], int(sys.argv[5])
held = bytearray(b"\x01") * (mib * 1024 * 1024) if mib else b""
open(ready, "w").write(str(os.getpid()))
if go != "-":
    while not os.path.exists(go):
        time.sleep(0.05)
    fd = os.open(lock, os.O_RDWR | os.O_CREAT, 0o644)
    fcntl.flock(fd, fcntl.LOCK_EX)
    extra = bytearray(b"\x01") * (more * 1024 * 1024)
    open(ready + ".held", "w").write(str(os.getpid()))
time.sleep(600)
'''

# A lead that starts one worker (a child holding memory) and writes the worker's pid.
LEAD_SCRIPT = r'''
import subprocess, sys, time
mib, worker_ready, session_script = sys.argv[1], sys.argv[2], sys.argv[3]
worker = subprocess.Popen([sys.executable, session_script, mib, worker_ready, "-", "-", "0"])
time.sleep(600)
'''

# A heavy job's command: records its pid, environment (thread variables), CPU affinity and niceness, optionally
# starts a child that records the same, holds memory, and waits for its release file.
JOB_SCRIPT = r'''
import json, os, subprocess, sys, time
tag, folder, mib, hold, child = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4] == "hold", sys.argv[5]
VARS = %(vars)r
def record(path):
    data = {"pid": os.getpid(), "ppid": os.getppid(), "env": {v: os.environ.get(v) for v in VARS},
            "affinity": sorted(os.sched_getaffinity(0)), "nice": os.getpriority(os.PRIO_PROCESS, 0)}
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(data, f)
    os.replace(tmp, path)
if child == "record-only":
    record(os.path.join(folder, tag + ".json"))
    sys.exit(0)
held = bytearray(b"\x01") * (mib * 1024 * 1024) if mib else b""
record(os.path.join(folder, tag + ".json"))
if child == "child":
    subprocess.run([sys.executable, __file__, tag + ".child", folder, "0", "nohold", "record-only"], check=True)
open(os.path.join(folder, tag + ".started"), "w").write(str(os.getpid()))
if hold:
    release = os.path.join(folder, tag + ".release")
    deadline = time.monotonic() + 300
    while not os.path.exists(release) and time.monotonic() < deadline:
        time.sleep(0.05)
open(os.path.join(folder, tag + ".done"), "w").write("done")
''' % {"vars": THREAD_VARS}

# The stand-in nvidia-smi: answers --query-gpu= and --query-compute-apps= from a planted JSON state, in the fields
# and format asked; "-L" lists the GPUs; records every call.
NVIDIA_SMI = r'''#!%(python)s
import json, sys
STATE, CALLS = %(state)r, %(calls)r
with open(CALLS, "a") as f:
    f.write(json.dumps(sys.argv[1:]) + "\n")
state = json.load(open(STATE))
if state.get("fail") == "no-gpu":
    print("No devices were found")
    sys.exit(6)
if state.get("fail") == "error":
    print("NVIDIA-SMI has failed because it couldn't communicate with the NVIDIA driver.", file=sys.stderr)
    sys.exit(9)
args = sys.argv[1:]
fmt = next((a.split("=", 1)[1] for a in args if a.startswith("--format=")), "csv")
if "--format" in args:
    fmt = args[args.index("--format") + 1]
def fields_of(flag):
    for i, a in enumerate(args):
        if a.startswith(flag + "="):
            return a.split("=", 1)[1].split(",")
        if a == flag and i + 1 < len(args):
            return args[i + 1].split(",")
    return None
UNITS = {"memory.total": " MiB", "memory.used": " MiB", "memory.free": " MiB", "utilization.gpu": " %%",
         "used_memory": " MiB", "used_gpu_memory": " MiB"}
ALIASES = {"used_gpu_memory": "used_memory", "name": "process_name"}
def emit(fields, rows, apps):
    if "noheader" not in fmt:
        print(", ".join(fields))
    for row in rows:
        out = []
        for name in fields:
            name = name.strip()
            key = ALIASES.get(name, name) if apps else name
            value = row.get(key, "[N/A]")
            unit = "" if "nounits" in fmt or value == "[N/A]" else UNITS.get(name, "")
            out.append(f"{value}{unit}")
        print(", ".join(out))
gpu_fields, app_fields = fields_of("--query-gpu"), fields_of("--query-compute-apps")
if "-L" in args:
    for g in state["gpus"]:
        print(f"GPU {g['index']}: {g['name']} (UUID: {g['uuid']})")
elif gpu_fields:
    emit(gpu_fields, state["gpus"], False)
elif app_fields:
    emit(app_fields, state["apps"], True)
else:
    print("stand-in nvidia-smi: only --query-gpu=, --query-compute-apps= and -L are answered", file=sys.stderr)
    sys.exit(2)
'''

# The stand-in ``ollama``: records its argv, environment, CPU affinity and niceness (one JSON line per start), and
# writes one line to its standard output and one to its standard error; then ends.
OLLAMA = r'''#!%(python)s
import json, os, sys
print("W2-20 STAND-IN OUT", flush=True)
print("W2-20 STAND-IN ERR", file=sys.stderr, flush=True)
data = {"argv": sys.argv[1:], "pid": os.getpid(), "env": dict(os.environ),
        "affinity": sorted(os.sched_getaffinity(0)), "nice": os.getpriority(os.PRIO_PROCESS, 0)}
with open(%(record)r, "a") as f:
    f.write(json.dumps(data) + "\n")
'''


class Machine:
    """One test's machine: a temporary home, reading files, stand-ins and child processes."""

    def __init__(self, base: Path):
        self.base = base
        self.home = base / "home"
        self.home.mkdir()
        self.readings = base / "readings"
        self.readings.mkdir()
        self.bin = base / "bin"  # the stand-ins' folder, first on PATH
        self.bin.mkdir()
        self.scripts = base / "scripts"
        self.scripts.mkdir()
        self.marks = base / "marks"
        self.marks.mkdir()
        self.meminfo = self.readings / "meminfo"
        self.loadavg = self.readings / "loadavg"
        self.busy = self.readings / "busy_cores"
        self.embedding_cpu = self.readings / "embedding_cpu.json"
        self.disk = self.readings / "disk.json"
        self.gpu_state = self.readings / "gpu.json"
        self.gpu_calls = self.readings / "nvidia-smi-calls.jsonl"
        self.verification_lock = base / "verification.lock"
        self.nproc = 4
        self.groups: list[subprocess.Popen] = []
        self._location_checked = False
        self._counter = 0
        for name, text in (("session.py", SESSION_SCRIPT), ("lead.py", LEAD_SCRIPT), ("job.py", JOB_SCRIPT)):
            (self.scripts / name).write_text(text)
        # Generous readings by default; each test sets what it needs.
        self.set_readings(available_bytes=64 * GIB, load=0.10, load_15=0.10, nproc=4, busy_cores=0.5,
                          embedding_p95=(0.25, 0.25), free_bytes=500 * GIB, free_inodes=50_000_000)
        self.open_config()

    # ------------------------------------------------------------------ places

    @property
    def registry(self) -> Path:
        return self.home / ".gov-os" / "machine"

    @property
    def config_file(self) -> Path:
        return self.registry / "gate.json"

    @property
    def launch_log(self) -> Path:
        return self.registry / "launch.log"

    @property
    def findings(self) -> Path:
        return self.registry / "findings.jsonl"

    def repo(self, name: str) -> Path:
        """A git repository built from scratch, with one commit."""
        path = self.base / name
        path.mkdir()
        self._git(path, "init", "-q")
        (path / "README.md").write_text(f"{name}: a W2-20 test repository\n")
        self._git(path, "add", "README.md")
        self._git(path, "commit", "-q", "-m", "initial")
        return path.resolve()

    def _git(self, path: Path, *args: str) -> None:
        env = {
            "PATH": SAFE_PATH, "HOME": str(self.home), "LC_ALL": "C", "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_AUTHOR_NAME": "W2-20 tests", "GIT_AUTHOR_EMAIL": "w2-20@example.invalid",
            "GIT_COMMITTER_NAME": "W2-20 tests", "GIT_COMMITTER_EMAIL": "w2-20@example.invalid",
        }
        subprocess.run(["git", "-C", str(path), *args], env=env, check=True, capture_output=True,
                       timeout=COMMAND_TIMEOUT_S)

    # ---------------------------------------------------------------- readings

    def set_readings(self, *, available_bytes=None, load=None, load_15=None, nproc=None, busy_cores=None,
                     embedding_p95=None, free_bytes=None, free_inodes=None) -> None:
        """Write the reading files. ``available_bytes`` must be a whole number of KiB (meminfo counts in kB).
        ``load`` alone sets the 1-, 5- and 15-minute loads alike; ``load_15`` sets the 15-minute load."""
        if available_bytes is not None:
            assert available_bytes % KIB == 0
            kib = available_bytes // KIB
            self.meminfo.write_text(
                f"MemTotal:       {kib + 8 * 1024 * 1024} kB\n"
                f"MemFree:        {max(kib // 2, 1)} kB\n"
                f"MemAvailable:   {kib} kB\n"
                f"Buffers:        1024 kB\n"
                f"Cached:         2048 kB\n"
            )
        if load is not None or load_15 is not None:
            one, _, fifteen = self._loads()
            one = one if load is None else load
            fifteen = (one if load is not None else fifteen) if load_15 is None else load_15
            self.loadavg.write_text(f"{one:.2f} {one:.2f} {fifteen:.2f} 1/321 54321\n")
        if nproc is not None:
            self.nproc = nproc
        if busy_cores is not None:
            self.busy.write_text(f"{busy_cores}\n")
        if embedding_p95 is not None:
            self.embedding_cpu.write_text(json.dumps({"shared": embedding_p95[0], "query": embedding_p95[1]}))
        if free_bytes is not None or free_inodes is not None:
            current = json.loads(self.disk.read_text()) if self.disk.exists() else {}
            if free_bytes is not None:
                current["free_bytes"] = free_bytes
            if free_inodes is not None:
                current["free_inodes"] = free_inodes
            self.disk.write_text(json.dumps(current))

    def _loads(self):
        try:
            fields = self.loadavg.read_text().split()
            return float(fields[0]), float(fields[1]), float(fields[2])
        except (OSError, ValueError, IndexError):
            return 0.1, 0.1, 0.1

    # ---------------------------------------------------------------- the configuration file

    def embedding_cpus(self) -> tuple[str, str]:
        """The embedding servers' planted CPU sets: the highest allowed CPU for each (one CPU when only one)."""
        cpus = allowed_cpus()
        shared = cpus[-1]
        query = cpus[-2] if len(cpus) > 1 else cpus[-1]
        return str(shared), str(query)

    def config_values(self, **overrides) -> dict:
        """A whole, valid configuration with values the default readings pass with room to spare. An override is a
        bare value (dated today), a full ``dated(...)`` object, or ``None`` to leave the key out."""
        shared, query = self.embedding_cpus()
        values = {
            "memory_floor_bytes": dated(3 * GIB, source="DEC-942 item 2 (planted)"),
            "verification_peak_bytes": dated(4 * GIB, source="measured (planted)"),
            "working_size_bytes": dated(1 * GIB, source="measured (planted)"),
            # P-5 (a), settled (DEC-1097 (8)): the re-measure's third figure. Planted, so a gate that requires it
            # and one that does not both read a whole file; whether it is required is not tested (README, P-5).
            "rebuild_peak_bytes": dated(2 * GIB, source="measured (planted)"),
            "disk_floor_bytes": dated(100 * GIB, source="DEC-898 item 1 (planted)"),
            "inode_floor": dated(10_000_000, source="DEC-898 item 1 (planted)"),
            "verification_lock": dated(str(self.verification_lock), source="planted"),
            "gpu_margin": dated(0.10, source="DEC-950 item 2 (planted)"),
            "oom_floor_bytes": dated(1 * GIB, source="planted"),
            "heavy_slots": dated(2, source="planted"),
            "gpu_shares": dated({"embedder_mib": 0, "reranker_mib": 0}, source="planted"),
            "embedding_servers": {
                "shared": {"cpus": shared, "nice": 10, "date": today(), "source": "planted"},
                "query": {"cpus": query, "nice": 10, "date": today(), "source": "planted"},
            },
        }
        for key, value in overrides.items():
            if value is None:
                values.pop(key, None)
            elif isinstance(value, dict) and ("value" in value or key == "embedding_servers"):
                values[key] = value
            else:
                values[key] = dated(value)
        return values

    def open_config(self, **overrides) -> dict:
        values = self.config_values(**overrides)
        self.write_config(values)
        return values

    def write_config(self, values) -> None:
        self.registry.mkdir(parents=True, exist_ok=True)
        self.config_file.write_text(values if isinstance(values, str) else json.dumps(values, indent=1))

    def read_config(self) -> dict:
        return json.loads(self.config_file.read_text())

    # ---------------------------------------------------------------- stand-ins

    def plant_gpu(self, *, gpus=None, apps=(), fail=None) -> None:
        """Put the stand-in ``nvidia-smi`` on PATH with this state. ``gpus``: a list of dicts with
        ``memory.total``, ``memory.used`` and ``utilization.gpu`` (``memory.free`` is derived)."""
        rows = []
        for i, g in enumerate(gpus if gpus is not None else [{"memory.total": 8192, "memory.used": 0,
                                                               "utilization.gpu": 3}]):
            row = {"index": i, "name": f"W2-20 stand-in GPU {i}", "uuid": f"GPU-w2-20-{i:04d}",
                   "pci.bus_id": f"00000000:0{i}:00.0", **g}
            row.setdefault("memory.free", row["memory.total"] - row["memory.used"])
            rows.append(row)
        self.gpu_state.write_text(json.dumps({"gpus": rows, "apps": list(apps), "fail": fail}))
        script = self.bin / "nvidia-smi"
        script.write_text(NVIDIA_SMI % {"python": sys.executable, "state": str(self.gpu_state),
                                        "calls": str(self.gpu_calls)})
        script.chmod(0o755)

    def gpu_call_list(self) -> list[list[str]]:
        if not self.gpu_calls.exists():
            return []
        return [json.loads(line) for line in self.gpu_calls.read_text().splitlines() if line.strip()]

    def plant_ollama(self, folder: Path | None = None) -> tuple[Path, Path]:
        """The stand-in ``ollama`` in ``folder`` (default: a folder of its own); returns (folder, record file)."""
        folder = folder or (self.base / "ollama-bin")
        folder.mkdir(exist_ok=True)
        record = self.base / "ollama-record.jsonl"
        script = folder / "ollama"
        script.write_text(OLLAMA % {"python": sys.executable, "record": str(record)})
        script.chmod(0o755)
        return folder, record

    # ---------------------------------------------------------------- processes

    def _spawn(self, argv, **kw) -> subprocess.Popen:
        proc = subprocess.Popen(argv, stdin=subprocess.DEVNULL, start_new_session=True, **kw)
        self.groups.append(proc)
        return proc

    def _mark(self, stem: str) -> Path:
        self._counter += 1
        return self.marks / f"{stem}-{self._counter}"

    def live_process(self, *, memory_mib: int = 0, light: bool = False, tag: str | None = None) -> subprocess.Popen:
        """A child process that stays alive until the test ends; with ``memory_mib``, it holds that much memory
        (written, so resident) before this returns. ``light``: ``sleep 600``, the smallest process. ``tag`` is a
        word added to its command line."""
        if light:
            return self._spawn(["sleep", "600"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        ready = self._mark("ready")
        argv = [sys.executable, str(self.scripts / "session.py"), str(memory_mib), str(ready), "-", "-", "0"]
        if tag:
            argv.append(tag)
        proc = self._spawn(argv, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        wait_for(ready.exists, f"a session process holding {memory_mib} MiB")
        return proc

    def verification_session(self, *, memory_mib: int = 0, more_mib: int = 0):
        """A session process that, once ``go()`` is called, takes the configured verification lock and holds
        ``more_mib`` more memory. Returns (process, go)."""
        ready, go = self._mark("ready"), self._mark("go")
        proc = self._spawn([sys.executable, str(self.scripts / "session.py"), str(memory_mib), str(ready), str(go),
                            str(self.verification_lock), str(more_mib)],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        wait_for(ready.exists, "the verification session's start")

        def start_verification():
            go.write_text("go")
            wait_for(Path(str(ready) + ".held").exists, "the verification lock taken")
        return proc, start_verification

    def lead_with_worker(self, worker_mib: int) -> tuple[subprocess.Popen, int]:
        """A lead process that started one worker holding ``worker_mib`` MiB; returns (lead, worker pid)."""
        ready = self._mark("worker-ready")
        lead = self._spawn([sys.executable, str(self.scripts / "lead.py"), str(worker_mib), str(ready),
                            str(self.scripts / "session.py")], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        wait_for(ready.exists, "the lead's worker")
        return lead, int(ready.read_text())

    @staticmethod
    def stop(proc: subprocess.Popen) -> None:
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except OSError:
            proc.kill()
        proc.wait(timeout=COMMAND_TIMEOUT_S)

    def cleanup(self) -> None:
        for proc in self.groups:
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except OSError:
                pass
            try:
                proc.wait(timeout=COMMAND_TIMEOUT_S)
            except subprocess.TimeoutExpired:
                pass

    # ---------------------------------------------------------------- the command

    def env(self, **extra) -> dict:
        env = {
            "PATH": f"{self.bin}:{SAFE_PATH}",
            "HOME": str(self.home),
            "TMPDIR": str(self.base),
            "LC_ALL": "C",
            "PYTHONPATH": str(SRC),
            "PYTHONDONTWRITEBYTECODE": "1",
            "GIT_CONFIG_NOSYSTEM": "1",
            "GOV_RESOURCES_MEMINFO": str(self.meminfo),
            "GOV_RESOURCES_LOADAVG": str(self.loadavg),
            "GOV_RESOURCES_NPROC": str(self.nproc),
            "GOV_RESOURCES_BUSY_CORES": str(self.busy),
            "GOV_RESOURCES_EMBEDDING_CPU": str(self.embedding_cpu),
            "GOV_RESOURCES_DISK": str(self.disk),
        }
        env.update({k: v for k, v in extra.items() if v is not None})
        for key in [k for k, v in extra.items() if v is None]:
            env.pop(key, None)
        return env

    def argv(self, repo: Path, *args: str, json_output: bool = True, passthrough=None) -> list[str]:
        argv = [sys.executable, "-m", "gov.cli.main", "resources", *args, "--root", str(repo)]
        if json_output:
            argv.append("--json")
        if passthrough is not None:
            argv += ["--", *passthrough]
        return argv

    def gov(self, repo: Path, *args: str, json_output: bool = True, env_extra: dict | None = None):
        """Run ``gov resources <args>`` in ``repo``; return ``(exit code, envelope or None, stdout, stderr)``."""
        if not self._location_checked:
            self._location_checked = True
            self._check_location(repo)
        return self._run(repo, *args, json_output=json_output, env_extra=env_extra)

    def _run(self, repo: Path, *args: str, json_output: bool = True, env_extra: dict | None = None):
        proc = subprocess.run(self.argv(repo, *args, json_output=json_output), cwd=str(repo),
                              env=self.env(**(env_extra or {})), capture_output=True, text=True,
                              timeout=COMMAND_TIMEOUT_S)
        envelope = None
        if json_output:
            try:
                envelope = json.loads(proc.stdout)
            except ValueError:
                envelope = None
        return proc.returncode, envelope, proc.stdout, proc.stderr

    def _check_location(self, repo: Path) -> None:
        """Before a test enters anything, the reading must name a registry inside this test's temporary home."""
        code, envelope, out, err = self._run(repo)
        result = reading_of(code, envelope, out, err)
        assert "registry" in result, f"the reading names no registry folder: {result}"
        registry = os.path.realpath(result["registry"])
        expected = os.path.realpath(self.registry)
        assert registry == expected or registry.startswith(expected + os.sep), (
            f"the registry is {registry}, not under $HOME/.gov-os/machine/ ({expected})")

    def register(self, repo: Path, pid: int, *, ticket: str, role: str = "engineer"):
        code, envelope, out, err = self.gov(repo, "--register", str(pid), "--ticket", ticket, "--session-role", role)
        assert code == 0 and envelope is not None and envelope.get("ok") is True, (
            f"registering pid {pid} failed: exit {code}\nstdout: {out}\nstderr: {err}")
        return envelope

    def read(self, repo: Path, **kw) -> dict:
        code, envelope, out, err = self.gov(repo, **kw)
        return reading_of(code, envelope, out, err)

    def check(self, repo: Path, *, gpu_need_mib: int | None = None, gpu_kind: str | None = None, **kw):
        """The start check; ``gpu_need_mib`` declares a GPU need, ``gpu_kind`` its kind."""
        args = ["--check"]
        if gpu_need_mib is not None:
            args += ["--gpu-need-mib", str(gpu_need_mib)]
        if gpu_kind is not None:
            args += ["--gpu-kind", gpu_kind]
        return self.gov(repo, *args, **kw)

    # ---------------------------------------------------------------- heavy jobs

    def slot_job(self, repo: Path, kind: str, tag: str, *, tree: Path | None = None, workers: int | None = None,
                 hold: bool = True, memory_mib: int = 0, child: bool = False,
                 env_extra: dict | None = None) -> subprocess.Popen:
        """``gov resources --slot <kind> [--tree T] [--workers N] -- python3 job.py <tag> ...`` in the background.
        The job writes ``<tag>.json`` (its record) and ``<tag>.started``, then waits for ``<tag>.release``."""
        if not self._location_checked:
            self._location_checked = True
            self._check_location(repo)
        args = ["--slot", kind]
        if tree is not None:
            args += ["--tree", str(tree)]
        if workers is not None:
            args += ["--workers", str(workers)]
        command = [sys.executable, str(self.scripts / "job.py"), tag, str(self.marks), str(memory_mib),
                   "hold" if hold else "nohold", "child" if child else "none"]
        log = open(self.base / f"slot-{tag}.log", "w")
        return self._spawn(self.argv(repo, *args, json_output=False, passthrough=command), cwd=str(repo),
                           env=self.env(**(env_extra or {})), stdout=log, stderr=subprocess.STDOUT)

    def started(self, tag: str) -> Path:
        return self.marks / f"{tag}.started"

    def wait_started(self, tag: str, timeout: float = WAIT_S) -> int:
        wait_for(self.started(tag).exists, f"heavy job {tag} to start its command", timeout)
        return int(self.started(tag).read_text())

    def release(self, tag: str) -> None:
        (self.marks / f"{tag}.release").write_text("go")

    def job_record(self, tag: str) -> dict:
        path = self.marks / f"{tag}.json"
        wait_for(path.exists, f"the record of {tag}")
        return json.loads(path.read_text())

    def slot_log(self, tag: str) -> str:
        path = self.base / f"slot-{tag}.log"
        return path.read_text() if path.exists() else ""


def reading_of(code, envelope, out, err) -> dict:
    """The ``result`` of a successful ``gov resources --json``."""
    assert envelope is not None, f"gov resources printed no JSON envelope (exit {code})\nstdout: {out}\nstderr: {err}"
    assert code == 0 and envelope.get("ok") is True, (
        f"gov resources did not succeed: exit {code}\nenvelope: {envelope}\nstderr: {err}")
    assert "resources" in str(envelope.get("command")), f"the envelope names another command: {envelope}"
    result = envelope.get("result")
    assert isinstance(result, dict), f"the envelope's result is not an object: {envelope}"
    return result


def refusal_of(code, envelope, out, err) -> dict:
    """The reading a refused start check carries: ``ok: false``, error ``RESOURCE_GATE_SHUT``, reading in details."""
    assert envelope is not None, f"gov resources --check printed no JSON envelope (exit {code})\nstdout: {out}\nstderr: {err}"
    assert code not in (0, 2), f"a start check with the gate shut ended with exit {code}, not a refusal\n{envelope}"
    assert envelope.get("ok") is False, f"a refused start check has ok: {envelope.get('ok')}\n{envelope}"
    error = envelope.get("error")
    assert isinstance(error, dict) and error.get("code") == GATE_SHUT_ERROR, (
        f"the refusal is not the named error {GATE_SHUT_ERROR}: {error}")
    details = error.get("details")
    assert isinstance(details, dict), f"the refusal carries no reading in error.details: {error}"
    return details


def opened_of(code, envelope, out, err) -> dict:
    """The reading of a start check that opened."""
    reading = reading_of(code, envelope, out, err)
    gate = gate_of(reading)
    assert gate["open"] is True and gate["reasons"] == [], f"the start check did not open: {reading}"
    return reading


def gate_of(reading: dict) -> dict:
    gate = reading.get("gate")
    assert isinstance(gate, dict) and isinstance(gate.get("open"), bool) and isinstance(gate.get("reasons"), list), (
        f"the reading has no gate {{open, reasons}}: {reading}")
    return gate


def reasons_list(reading: dict) -> list[dict]:
    out = []
    for reason in gate_of(reading)["reasons"]:
        assert isinstance(reason, dict) and {"condition", "reading", "threshold"} <= set(reason), (
            f"a reason without condition, reading and threshold: {reason}")
        assert reason["condition"] in CONDITIONS, f"a reason with an unknown condition: {reason}"
        out.append(reason)
    return out


def reasons_by_condition(reading: dict) -> dict:
    """``{condition: reason}`` of a reading's gate (the last reason of a condition named twice)."""
    return {reason["condition"]: reason for reason in reasons_list(reading)}


def config_reasons(reading: dict) -> list[dict]:
    return [r for r in reasons_list(reading) if r["condition"] == "config"]


def names_key(reason: dict, key: str) -> bool:
    return key in json.dumps(reason)


def session_pids(reading: dict) -> list[int]:
    sessions = reading.get("sessions")
    assert isinstance(sessions, list), f"the reading has no sessions list: {reading}"
    return sorted(int(s["pid"]) for s in sessions)


def same_path(a, b) -> bool:
    return os.path.realpath(str(a)) == os.path.realpath(str(b))


def close_to(a, b, tol=1e-6) -> bool:
    return a is not None and b is not None and abs(float(a) - float(b)) <= tol

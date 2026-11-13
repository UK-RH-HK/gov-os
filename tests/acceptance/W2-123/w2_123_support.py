"""Support code for the W2-123 acceptance tests (DAEO-qzrq; standard library only).

W2-123 (DEC-1014, DEC-1015 item 2, DEC-1017): both embedding servers the Gov OS starts are started under a CPU cap,
a lower priority and a number of parallel requests read from the gate's configuration file; a health probe and a
safe restart; a determinism check for parallel requests. The tests use it only through the lead's public interface
(README, "The interface"), every name in ``gov.retrieval.ollama``.

How the tests run (README, "How the suite runs the code under test"):

- **The code under test is whatever ``gov`` the pytest process imports** (DEC-732). The probe and the determinism
  check are called in the pytest process; the start and the safe restart are called in a child ``sys.executable``
  whose ``PYTHONPATH`` is the pytest process's own (or, unset, the folder the pytest process imported ``gov`` from).
- **Nothing real is touched.** Every call is given ``HOME`` (a temporary one, holding the planted
  ``.gov-os/machine/gate.json``), ``OLLAMA_HOST`` and ``GOV_QUERY_OLLAMA_HOST`` (free loopback ports this suite
  picks) and ``GOV_OLLAMA_BIN`` (a planted executable under ``tmp_path``). Nothing is sent to 127.0.0.1:11434 or
  :11435 and the real ``ollama`` is never run.
- **The planted executable** is a bash script that ``exec -a``'s Python on a stand-in daemon, so its command line
  reads exactly ``<executable> serve`` (S4 compares command lines). The daemon records, from inside, its
  ``Cpus_allowed_list``, its niceness and its environment; starts one child (its "runner", as ``ollama serve``
  starts ``llama-server``) that records the same; and answers Ollama's ``/api/version`` and ``/api/embed`` in the
  mode the stage names (healthy, slow or hung).
- **Every process a test or the code under test starts is ended at teardown**, after checking its command line
  names this test's folder; a stand-in also ends by itself.
- **CPU lists are picked at run time** from ``os.sched_getaffinity(0)``: nothing of this machine is in the tests.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import signal
import socket
import struct
import subprocess
import sys
import threading
import time
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
EVIDENCE_REL = "docs/changes/W2-123-evidence.md"

MODEL = "qwen3-embedding:0.6b"                 # the semantic store's embedder (src/gov/retrieval/semantic.py)
GATE_REL = ".gov-os/machine/gate.json"         # S1: the gate's one configuration file (W2-20), under HOME
RESTARTS_REL = ".gov-os/machine/embedding-restarts.jsonl"   # S4: the restart record, under HOME
SECTION = "embedding_servers"
CONFIG_INVALID = "CONFIG_INVALID"

RESULT_KEYS = ("available", "started", "facet", "state", "warning", "settings")
SETTINGS_KEYS = ("parallel", "cpus", "nice", "source")
PROBE_KEYS = ("server", "host", "state", "seconds")
RESTART_KEYS = ("server", "host", "restarted", "reason", "probe", "settings", "old_pid", "new_pid")
RECORD_KEYS = ("time", "server", "host", "probe_state", "old_pid", "new_pid", "restarted", "settings")
WATCHED_ENV = ("OLLAMA_HOST", "OLLAMA_NUM_PARALLEL", "CUDA_VISIBLE_DEVICES")

HANG_LIMIT_S = 90.0          # a child call that has not returned by then is killed and the test fails
STAND_IN_LIFETIME_S = 120    # a stand-in daemon, runner or foreign holder ends by itself after this long
START_TIMEOUT_S = 10.0       # the timeout_s the starting cases pass
PROBE_SLOW_S = 1.5           # the probe times every case configures (S3)
PROBE_HUNG_S = 4.0
SLOW_DELAY_S = 2.5           # a "slow" stand-in answers after this long: between the two
WAIT_S = 15.0                # how long a test waits for a stand-in's record or for a process to end


# --------------------------------------------------------------------------
# CPU lists and niceness, picked at run time
# --------------------------------------------------------------------------

def parse_cpus(text):
    """The set of CPUs in a CPU list (``"2-5,8"``)."""
    cpus = set()
    for part in str(text).strip().split(","):
        part = part.strip()
        if not part:
            continue
        low, dash, high = part.partition("-")
        cpus.update(range(int(low), int(high) + 1) if dash else (int(low),))
    return cpus


def cpu_list(cpus):
    """A set of CPUs in the CPU-list form of ``taskset -c``."""
    ordered, parts, i = sorted(cpus), [], 0
    while i < len(ordered):
        j = i
        while j + 1 < len(ordered) and ordered[j + 1] == ordered[j] + 1:
            j += 1
        parts.append(str(ordered[i]) if i == j else f"{ordered[i]}-{ordered[j]}")
        i = j + 1
    return ",".join(parts)


def allowed_cpus():
    """The CPUs this process may run on, in order."""
    return sorted(os.sched_getaffinity(0))


def lower_cpus():
    """The lower half of the CPUs this process may run on (at least one): never the highest-numbered default."""
    cpus = allowed_cpus()
    return set(cpus[:max(1, len(cpus) // 2)])


def upper_cpus():
    """The upper half (at least one): differs from ``lower_cpus`` whenever this process may run on two or more."""
    cpus = allowed_cpus()
    return set(cpus[len(cpus) // 2:]) if len(cpus) > 1 else set(cpus)


def no_allowed_cpu():
    """A CPU number this process may not run on."""
    return max(allowed_cpus()) + 1


def own_nice():
    return os.getpriority(os.PRIO_PROCESS, 0)


def a_nice(step=5):
    """A niceness above this process's own (19 at most), so a cap that is not applied shows."""
    return min(19, own_nice() + step)


def code_path():
    """The ``PYTHONPATH`` of every child: the pytest process's own, else the folder it imported ``gov`` from."""
    given = os.environ.get("PYTHONPATH")
    if given:
        return given
    import gov
    return str(Path(gov.__file__).resolve().parents[1])


def free_port(taken=()):
    """A loopback port nothing listens on (and not in ``taken``)."""
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
            probe.bind(("127.0.0.1", 0))
            port = probe.getsockname()[1]
        if port not in taken:
            return port


# --------------------------------------------------------------------------
# vectors
# --------------------------------------------------------------------------

DIMENSIONS = 16


def vector_of(text):
    """The stand-in embedder's vector for ``text``: exact float32 values of magnitude 0.1 to 1."""
    digest = hashlib.sha256(text.encode("utf-8")).digest()
    raw = [(0.1 + 0.9 * digest[i] / 255.0) * (1 if digest[i + DIMENSIONS] % 2 else -1) for i in range(DIMENSIONS)]
    return list(struct.unpack(f"{DIMENSIONS}f", struct.pack(f"{DIMENSIONS}f", *raw)))


def stored(vector):
    """A vector as the semantic store keeps it: float32, native byte order."""
    return struct.pack(f"{len(vector)}f", *vector)


# --------------------------------------------------------------------------
# an Ollama stand-in served from a thread of the pytest process
# --------------------------------------------------------------------------

class _Server(ThreadingHTTPServer):
    daemon_threads = True
    block_on_close = False   # a handler that never answers must not hold the teardown


class Embedder:
    """A loopback Ollama endpoint in a thread: ``/api/version``, ``/api/tags`` and ``/api/embed``.

    - ``delay``: seconds before an embedding is answered; ``never``: an embedding request is never answered;
      ``no_vector``: it is answered 200 without a vector.
    - ``perturb_parallel``: a vector computed while another embedding request is in flight differs (1e-3 on one
      value); ``differ``: the texts whose vector always differs; ``missing``: the texts answered with no vector;
      ``below_precision``: every value is moved by 1e-12, below float32's precision.
    - ``in_flight_max`` is the most embedding requests it held at once. Every request is recorded.
    """

    def __init__(self, port=0, delay=0.0, never=False, no_vector=False, perturb_parallel=False, differ=(),
                 missing=(), below_precision=False):
        self.delay, self.never, self.no_vector = delay, never, no_vector
        self.perturb_parallel, self.differ, self.missing = perturb_parallel, set(differ), set(missing)
        self.below_precision = below_precision
        self.requests, self.in_flight, self.in_flight_max = [], 0, 0
        self._lock, self._stop = threading.Lock(), threading.Event()
        stand_in = self

        class Handler(BaseHTTPRequestHandler):
            def answer(self):
                length = int(self.headers.get("Content-Length") or 0)
                body = self.rfile.read(length).decode("utf-8", "replace") if length else ""
                try:
                    asked = json.loads(body) if body else {}
                except ValueError:
                    asked = {}
                reply = stand_in.reply(self.command, self.path.split("?")[0].rstrip("/"), asked)
                if reply is None:
                    return
                status, payload = reply
                data = json.dumps(payload).encode()
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)

            do_GET = do_POST = do_HEAD = do_DELETE = answer

            def log_message(self, *args):
                pass

        self.server = _Server(("127.0.0.1", port), Handler)
        self.host = f"127.0.0.1:{self.server.server_address[1]}"
        threading.Thread(target=self.server.serve_forever, kwargs={"poll_interval": 0.05}, daemon=True).start()

    def reply(self, method, route, asked):
        with self._lock:
            self.requests.append({"method": method, "route": route, "body": asked})
        if route == "/api/version":
            return 200, {"version": "0.35.0"}
        if route == "/api/tags":
            return 200, {"models": [{"name": MODEL, "model": MODEL, "digest": "0" * 64}]}
        if route not in ("/api/embed", "/api/embeddings"):
            return 404, {}
        with self._lock:
            self.in_flight += 1
            self.in_flight_max = max(self.in_flight_max, self.in_flight)
        try:
            if self.never:
                self._stop.wait(STAND_IN_LIFETIME_S)
                return None
            if self.delay:
                self._stop.wait(self.delay)
            given = asked.get("input", asked.get("prompt", ""))
            texts = [given] if isinstance(given, str) else [str(text) for text in given]
            with self._lock:
                crowded = self.in_flight > 1
            if self.no_vector:
                return 200, {"model": MODEL, "embeddings": []}
            vectors = []
            for text in texts:
                if text in self.missing:
                    continue
                vector = vector_of(text)
                if text in self.differ or (self.perturb_parallel and crowded):
                    vector[0] += 1e-3
                if self.below_precision:
                    vector = [value + 1e-12 for value in vector]
                vectors.append(vector)
            return 200, {"model": MODEL, "embeddings": vectors}
        finally:
            with self._lock:
                self.in_flight -= 1

    def embed_requests(self):
        return [request for request in self.requests if request["route"] in ("/api/embed", "/api/embeddings")]

    def close(self):
        self._stop.set()
        self.server.shutdown()
        self.server.server_close()


# --------------------------------------------------------------------------
# the planted executable
# --------------------------------------------------------------------------

# GOV_OLLAMA_BIN. Run as ``<it> serve`` it becomes the stand-in daemon with its command line kept as
# ``<it> serve`` (``exec -a``); run any other way it ends at once.
WRAPPER = """\
#!/bin/bash
if [ "$1" != "serve" ]; then
  exit 0
fi
cd {folder} || exit 1
exec -a "$0" {python} serve
"""

# The stand-in daemon (the file ``serve`` beside the wrapper, run as ``<wrapper> serve``).
DAEMON = """\
import json, os, subprocess, sys, threading, time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

LOG, MODE_FILE, RUNNER, PYTHON = {log!r}, {mode_file!r}, {runner!r}, {python!r}
LIFETIME_S, SLOW_DELAY_S, WATCHED, MODEL = {lifetime}, {slow}, {watched!r}, {model!r}


def record(entry):
    with open(LOG, "a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry) + "\\n")


def seen():
    cpus = None
    with open("/proc/self/status", encoding="utf-8") as handle:
        for line in handle:
            if line.startswith("Cpus_allowed_list:"):
                cpus = line.split(":", 1)[1].strip()
    with open("/proc/self/cmdline", "rb") as handle:
        cmdline = [part.decode("utf-8", "replace") for part in handle.read().split(b"\\0") if part]
    return {{"pid": os.getpid(), "ppid": os.getppid(), "cpus": cpus, "nice": os.getpriority(os.PRIO_PROCESS, 0),
            "env": {{name: os.environ.get(name) for name in WATCHED}}, "cmdline": cmdline}}


try:
    with open(MODE_FILE, encoding="utf-8") as handle:
        mode = handle.read().strip() or "healthy"
except OSError:
    mode = "healthy"
host = os.environ.get("OLLAMA_HOST") or "127.0.0.1:11434"
record({{"kind": "serve", "mode": mode, "host": host, **seen()}})
runner = subprocess.Popen([PYTHON, RUNNER], stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                          stderr=subprocess.DEVNULL)


class Handler(BaseHTTPRequestHandler):
    def answer(self):
        length = int(self.headers.get("Content-Length") or 0)
        body = self.rfile.read(length).decode("utf-8", "replace") if length else ""
        route = self.path.split("?")[0].rstrip("/")
        record({{"kind": "request", "pid": os.getpid(), "route": route, "body": body}})
        if route == "/api/version":
            status, payload = 200, {{"version": "0.35.0"}}
        elif route == "/api/tags":
            status, payload = 200, {{"models": [{{"name": MODEL, "model": MODEL, "digest": "0" * 64}}]}}
        elif route in ("/api/embed", "/api/embeddings"):
            if mode == "hung":
                time.sleep(LIFETIME_S)
                return
            if mode == "slow":
                time.sleep(SLOW_DELAY_S)
            status, payload = 200, {{"model": MODEL, "embeddings": [[0.25, -0.5, 0.75, 0.125]]}}
        else:
            status, payload = 404, {{}}
        data = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    do_GET = do_POST = do_HEAD = do_DELETE = answer

    def log_message(self, *args):
        pass


class Server(ThreadingHTTPServer):
    daemon_threads = True
    block_on_close = False


name, _, port = host.split("//")[-1].rstrip("/").rpartition(":")
try:
    server = Server((name or "127.0.0.1", int(port)), Handler)
except OSError as error:
    record({{"kind": "bind-failed", "pid": os.getpid(), "error": str(error)}})
    sys.exit(1)
threading.Thread(target=server.serve_forever, kwargs={{"poll_interval": 0.05}}, daemon=True).start()
record({{"kind": "listening", "pid": os.getpid(), "host": host}})
time.sleep(LIFETIME_S)
os._exit(0)
"""

# The child the daemon starts, as ``ollama serve`` starts its runner: it records what it inherited and waits.
RUNNER = """\
import json, os, time
LOG, LIFETIME_S, WATCHED = {log!r}, {lifetime}, {watched!r}
cpus = None
with open("/proc/self/status", encoding="utf-8") as handle:
    for line in handle:
        if line.startswith("Cpus_allowed_list:"):
            cpus = line.split(":", 1)[1].strip()
with open(LOG, "a", encoding="utf-8") as handle:
    handle.write(json.dumps({{"kind": "runner", "pid": os.getpid(), "ppid": os.getppid(), "cpus": cpus,
                             "nice": os.getpriority(os.PRIO_PROCESS, 0),
                             "env": {{name: os.environ.get(name) for name in WATCHED}}}}) + "\\n")
time.sleep(LIFETIME_S)
"""

# A process that is not the Gov OS's server: it holds a port, accepts connections and never answers.
FOREIGN = """\
import socket, sys, time
listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
listener.bind(("127.0.0.1", int(sys.argv[1])))
listener.listen(64)
listener.settimeout(0.2)
held, end = [], time.monotonic() + float(sys.argv[2])
while time.monotonic() < end:
    try:
        held.append(listener.accept()[0])
    except OSError:
        pass
"""

# Calls one public function of gov.retrieval.ollama with env= its own environment and prints the result as the
# last line. With "affinity", the calling process first narrows the CPUs it may run on.
DRIVER = """\
import json, os, sys
spec = json.loads(sys.argv[1])
if spec.get("affinity"):
    os.sched_setaffinity(0, spec["affinity"])
from gov.retrieval import ollama
function = getattr(ollama, spec["call"])
result = function(*spec.get("args", []), **spec.get("kwargs", {}), env=dict(os.environ))
sys.stdout.write("\\n" + json.dumps({"result": result}, default=repr) + "\\n")
"""


@dataclass(frozen=True)
class Call:
    """One call of a public function in a child process."""

    result: dict
    stderr: str
    wall_s: float


class Stage:
    """One test's HOME, gate file, planted executable, endpoints and child calls, under one temporary folder."""

    def __init__(self, root):
        self.root = Path(root)
        self.home, self.work, self.tmp = self.root / "home", self.root / "work", self.root / "tmp"
        self.bin, self.out, self.stand_in = self.root / "bin", self.root / "out", self.root / "stand-in"
        for folder in (self.home, self.work, self.tmp, self.bin, self.out, self.stand_in):
            folder.mkdir(parents=True)
        self.log = self.root / "stand-in.jsonl"
        self.mode_file = self.stand_in / "mode"
        self.executable = self.stand_in / "ollama"
        python = sys.executable
        values = dict(log=str(self.log), lifetime=STAND_IN_LIFETIME_S, watched=WATCHED_ENV)
        (self.stand_in / "runner.py").write_text(RUNNER.format(**values), encoding="utf-8")
        (self.stand_in / "serve").write_text(DAEMON.format(
            mode_file=str(self.mode_file), runner=str(self.stand_in / "runner.py"), python=python,
            slow=SLOW_DELAY_S, model=MODEL, **values), encoding="utf-8")
        self.executable.write_text(WRAPPER.format(folder=_quoted(self.stand_in), python=_quoted(python)),
                                   encoding="utf-8")
        self.executable.chmod(0o755)
        self.set_mode("healthy")
        self.port = free_port()
        self.query_port = free_port({self.port})
        self.host, self.query_host = f"127.0.0.1:{self.port}", f"127.0.0.1:{self.query_port}"
        self._endpoints, self._processes, self._calls = [], [], 0

    # ---- the configuration -------------------------------------------------

    @property
    def gate_path(self):
        return self.home / GATE_REL

    @property
    def restarts_path(self):
        return self.home / RESTARTS_REL

    def configure(self, servers=None, raw=None):
        """Plant the gate file: ``raw`` text as given, else ``{"slots": 4, "embedding_servers": servers}`` (the
        other key is W2-20's and is not read here)."""
        self.gate_path.parent.mkdir(parents=True, exist_ok=True)
        text = raw if raw is not None else json.dumps({"slots": 4, SECTION: servers}, indent=2)
        self.gate_path.write_text(text, encoding="utf-8")
        return self.gate_path

    def set_mode(self, mode):
        """How the next stand-in daemon started answers embeddings: ``healthy``, ``slow`` or ``hung``."""
        self.mode_file.write_text(mode, encoding="utf-8")

    def environment(self, **extra):
        """The whole environment of a child call, also given to the function as ``env=``."""
        env = {
            "PATH": f"{self.bin}:/usr/bin:/bin",
            "HOME": str(self.home),
            "TMPDIR": str(self.tmp),
            "LANG": "C.UTF-8",
            "LC_ALL": "C.UTF-8",
            "PYTHONPATH": code_path(),
            "PYTHONDONTWRITEBYTECODE": "1",
            "OLLAMA_HOST": self.host,
            "GOV_QUERY_OLLAMA_HOST": self.query_host,
            "GOV_OLLAMA_BIN": str(self.executable),
        }
        env.update(extra)
        return env

    # ---- endpoints the test stands up --------------------------------------

    def embedder(self, query=False, **behaviour):
        """An in-thread stand-in at the shared (or the query) server's address."""
        endpoint = Embedder(port=self.query_port if query else self.port, **behaviour)
        self._endpoints.append(endpoint)
        return endpoint

    def start_server(self, mode, query=False):
        """The planted executable started by the test itself as ``<executable> serve`` at the shared (or query)
        address, answering embeddings in ``mode``; waits until it listens. The next start is healthy again."""
        self.set_mode(mode)
        env = self.environment(OLLAMA_HOST=self.query_host if query else self.host)
        process = subprocess.Popen([str(self.executable), "serve"], env=env, cwd=self.work,
                                   stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                   start_new_session=True)
        self._processes.append(process)
        self.wait_for(lambda: any(r["pid"] == process.pid for r in self.records("listening")),
                      f"the stand-in daemon {process.pid} the test started did not listen")
        self.set_mode("healthy")
        return process

    def start_foreign(self, query=False):
        """Another program (not the Gov OS's executable) holding the server's port and never answering."""
        port = self.query_port if query else self.port
        process = subprocess.Popen([sys.executable, "-c", FOREIGN, str(port), str(STAND_IN_LIFETIME_S)],
                                   cwd=self.work, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                                   stderr=subprocess.DEVNULL, start_new_session=True)
        self._processes.append(process)

        def listens():
            try:
                with socket.create_connection(("127.0.0.1", port), timeout=0.5):
                    return True
            except OSError:
                return False

        self.wait_for(listens, "the foreign process did not listen")
        return process

    # ---- calling the function in a child -----------------------------------

    def call(self, name, *args, affinity=None, env_extra=None, **kwargs):
        """``gov.retrieval.ollama.<name>(*args, **kwargs, env=<the child's environment>)`` in a child process."""
        self._calls += 1
        out_path, err_path = self.out / f"call-{self._calls}.stdout", self.out / f"call-{self._calls}.stderr"
        spec = {"call": name, "args": list(args), "kwargs": kwargs, "affinity": sorted(affinity or ())}
        began = time.monotonic()
        with open(out_path, "wb") as out, open(err_path, "wb") as err:
            child = subprocess.Popen([sys.executable, "-c", DRIVER, json.dumps(spec)], cwd=self.work,
                                     env=self.environment(**(env_extra or {})), stdin=subprocess.DEVNULL,
                                     stdout=out, stderr=err)
            try:
                code = child.wait(timeout=HANG_LIMIT_S)
            except subprocess.TimeoutExpired:
                child.kill()
                child.wait()
                raise AssertionError(f"{name} had not returned after {HANG_LIMIT_S:.0f} s and was killed") from None
        wall_s = time.monotonic() - began
        stdout = out_path.read_text(encoding="utf-8", errors="replace")
        stderr = err_path.read_text(encoding="utf-8", errors="replace")
        assert code == 0, f"the child that calls gov.retrieval.ollama.{name} ended with exit code {code}:\n" \
                          f"{stderr[-3000:]}"
        lines = [line for line in stdout.splitlines() if line.strip()]
        assert lines, f"the child that calls {name} printed no result"
        result = json.loads(lines[-1])["result"]
        assert isinstance(result, dict), f"{name} returned {result!r}, not an object"
        return Call(result=result, stderr=stderr, wall_s=wall_s)

    # ---- what the stand-ins saw --------------------------------------------

    def records(self, kind):
        if not self.log.is_file():
            return []
        entries = []
        for line in self.log.read_text(encoding="utf-8").splitlines():
            try:
                entries.append(json.loads(line))
            except ValueError:
                continue
        return [entry for entry in entries if entry.get("kind") == kind]

    def serves(self):
        """Every run of the planted executable as ``serve``: what it saw from inside."""
        return self.records("serve")

    def serve_of(self, pid):
        found = [entry for entry in self.serves() if entry["pid"] == pid]
        assert found, f"no stand-in daemon ran with pid {pid}; the daemons that ran: {self.serves()}"
        return found[0]

    def runner_of(self, pid):
        """The record of the runner the daemon ``pid`` started (waited for)."""
        self.wait_for(lambda: any(r["ppid"] == pid for r in self.records("runner")),
                      f"the stand-in daemon {pid} started no runner that recorded itself")
        return [r for r in self.records("runner") if r["ppid"] == pid][0]

    def restarts(self):
        """The lines of the restart record (S4)."""
        if not self.restarts_path.is_file():
            return []
        return [json.loads(line) for line in self.restarts_path.read_text(encoding="utf-8").splitlines()
                if line.strip()]

    @staticmethod
    def wait_for(predicate, message, timeout=WAIT_S):
        end = time.monotonic() + timeout
        while time.monotonic() < end:
            if predicate():
                return
            time.sleep(0.05)
        raise AssertionError(message)

    # ---- teardown ----------------------------------------------------------

    def close(self):
        """End every stand-in: the in-thread endpoints, the processes the test started, and every daemon and
        runner that recorded itself (the code under test may have started them)."""
        for endpoint in self._endpoints:
            endpoint.close()
        for process in self._processes:
            if process.poll() is None:
                process.kill()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                pass
        for entry in self.records("serve") + self.records("runner"):
            end_if_ours(entry["pid"], self.root)


def _quoted(path):
    return "'" + str(path).replace("'", "'\"'\"'") + "'"


def end_if_ours(pid, root):
    """Kill ``pid`` only if its command line names ``root`` (a stand-in of this test)."""
    try:
        cmdline = Path(f"/proc/{pid}/cmdline").read_bytes()
    except OSError:
        return
    if str(root).encode() not in cmdline:
        return
    try:
        os.kill(pid, signal.SIGKILL)
    except (ProcessLookupError, PermissionError):
        pass


def gone(pid):
    """True when ``pid`` no longer runs (absent, or a zombie waiting to be reaped)."""
    try:
        text = Path(f"/proc/{pid}/status").read_text(encoding="utf-8")
    except OSError:
        return True
    match = re.search(r"^State:\s+(\S)", text, re.MULTILINE)
    return bool(match) and match.group(1) in ("Z", "X")


# --------------------------------------------------------------------------
# reading results
# --------------------------------------------------------------------------

def assert_keys(result, keys, what):
    missing = [key for key in keys if key not in result]
    assert not missing, f"{what} lacks {missing} (the interface names {list(keys)}): {result}"


def assert_settings(settings, *, parallel=None, cpus=None, nice=None, source=None):
    """``settings`` is S2's object, with the values given (``source`` a path compared resolved, or "default")."""
    assert isinstance(settings, dict), f"settings is {settings!r}, not S2's object"
    assert_keys(settings, SETTINGS_KEYS, "settings")
    assert isinstance(settings["parallel"], int) and settings["parallel"] >= 1, settings
    assert isinstance(settings["nice"], int) and 0 <= settings["nice"] <= 19, settings
    assert isinstance(settings["cpus"], str) and parse_cpus(settings["cpus"]), settings
    if parallel is not None:
        assert settings["parallel"] == parallel, f"settings.parallel is {settings['parallel']}, not {parallel}"
    if cpus is not None:
        assert parse_cpus(settings["cpus"]) == set(cpus), \
            f"settings.cpus is {settings['cpus']!r}, not {cpu_list(cpus)!r}"
    if nice is not None:
        assert settings["nice"] == nice, f"settings.nice is {settings['nice']}, not {nice}"
    if source == "default":
        assert settings["source"] == "default", f"settings.source is {settings['source']!r}, not 'default'"
    elif source is not None:
        assert settings["source"] != "default" and Path(str(settings["source"])).resolve() == Path(source).resolve(), \
            f"settings.source is {settings['source']!r}, not the configuration file {source}"


def assert_capped(seen, *, cpus, nice, parallel, what):
    """What a stand-in process saw from inside: its CPUs, a niceness of at least ``nice``, its parallel requests."""
    assert parse_cpus(seen["cpus"]) == set(cpus), \
        f"{what} runs on CPUs {seen['cpus']}, not the cap {cpu_list(cpus)}"
    assert seen["nice"] >= nice, f"{what} runs at niceness {seen['nice']}, below the cap's {nice}"
    assert seen["env"].get("OLLAMA_NUM_PARALLEL") == str(parallel), \
        f"{what} has OLLAMA_NUM_PARALLEL={seen['env'].get('OLLAMA_NUM_PARALLEL')!r}, not {parallel!r}"


def probe_section(**more):
    """An entry of ``embedding_servers`` with this suite's probe times and ``more``."""
    return {"probe_slow_s": PROBE_SLOW_S, "probe_hung_s": PROBE_HUNG_S, **more}

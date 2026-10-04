"""Support code for the W1-18 acceptance tests (standard library only).

W1-18 builds the on-demand lifecycle of the stack's only daemon (Ollama) and the
lexical fallback. The tests use it only through its public interface (DEC-260):
``gov.retrieval.ollama.ensure_available(*, timeout_s, env=None)``, the three
environment variables it reads, and what it writes to standard error.

- **Where the module lives.** The ticket's ``allowed_paths`` give
  ``src/gov/retrieval/ollama*``. Until something matches, every test stops there.
- **Unit files.** The repository is asked, through ``git ls-files`` with three
  pathspecs, for service, socket and timer units, tracked or untracked and not
  ignored. No other file is listed or read.
- **Nothing is installed and Ollama is not needed.** A :class:`Stage` holds one
  test's stand-ins in a temporary directory: a stand-in ``ollama`` executable, a
  stand-in endpoint on a free loopback port, and recording stand-ins for
  ``systemctl``, ``systemd-run`` and ``loginctl``.
- **The function runs in a child ``python3`` process** the test starts, so a hang
  is killed and standard error is captured. The child's environment is built from
  scratch: ``PATH`` holds only the stage's own directory and ``HOME`` is the
  stage's own, so no real ``ollama`` can be found.
- **Every stand-in process is ended at teardown,** including one the module
  started. A stand-in daemon also ends by itself after a minute.
"""

from __future__ import annotations

import hashlib
import json
import os
import signal
import socket
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
MODULE_DIR_REL = "src/gov/retrieval"
MODULE_GLOB = "ollama*"
# An always-on daemon on this stack would be a systemd unit (the registry row: "run on demand, no systemd unit").
UNIT_PATHSPECS = ("*.service", "*.socket", "*.timer")
# The commands that would set up or start a unit; the stage puts a recording stand-in for each on PATH.
UNIT_COMMANDS = ("systemctl", "systemd-run", "loginctl")

# The KPI's bound: a call that has not returned after 30 s is a hang, and the child is killed.
HANG_LIMIT_S = 30.0
# The default total deadline (DEC-260).
DEFAULT_DEADLINE_S = 20.0
# The deadline the degraded cases pass, so the suite stays fast.
SHORT_DEADLINE_S = 2.0
# The deadline the starting cases pass; a healthy stand-in answers long before it.
START_DEADLINE_S = 10.0
# Allowance for scheduling when a test says "within the deadline".
DEADLINE_SLACK_S = 2.0
# A stand-in daemon ends by itself after this long, whatever happens to the test.
STAND_IN_LIFETIME_S = 60

HEALTH_PATH = "/api/version"
FACET = "semantic"
FACET_UNAVAILABLE = "FACET_UNAVAILABLE"
RESULT_KEYS = ("available", "started", "facet", "state", "warning")

# Where the executable may be found (DEC-260), in the order the decision gives.
EXECUTABLE_PLACES = ("GOV_OLLAMA_BIN", "PATH", "HOME")
HOME_EXECUTABLE_REL = ".local/ollama/bin/ollama"


class ModuleMissing(AssertionError):
    """The Ollama lifecycle module does not exist yet."""


def module_paths(root=REPO_ROOT):
    """What the ticket's ``allowed_paths`` pattern matches in the source tree, bytecode left out."""
    found = sorted(path for path in (Path(root) / MODULE_DIR_REL).glob(MODULE_GLOB) if path.name != "__pycache__")
    if not found:
        raise ModuleMissing(
            f"the Ollama lifecycle module does not exist: nothing matches {MODULE_DIR_REL}/{MODULE_GLOB}")
    return found


def unit_files(root=REPO_ROOT):
    """Service, socket and timer units in the working tree (tracked, or untracked and not ignored)."""
    listing = subprocess.run(
        ["git", "-C", str(root), "ls-files", "-z", "--cached", "--others", "--exclude-standard", "--",
         *UNIT_PATHSPECS],
        capture_output=True, text=True, check=True,
    ).stdout
    return sorted(Path(root) / rel for rel in listing.split("\0") if rel)


def mentions_ollama(path):
    """True when the unit's name or its text names Ollama."""
    if "ollama" in path.name.lower():
        return True
    if not path.is_file():
        return False
    return "ollama" in path.read_text(encoding="utf-8", errors="replace").lower()


# --------------------------------------------------------------------------
# the child process that calls the function
# --------------------------------------------------------------------------

# Calls the function with the deadline given as the first argument and prints the outcome as the last line.
CALL_DRIVER = """\
import json, sys, time
from gov.retrieval.ollama import ensure_available
began = time.monotonic()
result = ensure_available(timeout_s=float(sys.argv[1]))
elapsed_s = time.monotonic() - began
sys.stdout.write("\\n" + json.dumps({"result": dict(result), "elapsed_s": elapsed_s}, default=repr) + "\\n")
"""

# Prints the default of ``timeout_s``, read from the function's signature.
DEFAULT_DRIVER = """\
import inspect, json
from gov.retrieval.ollama import ensure_available
parameter = inspect.signature(ensure_available).parameters["timeout_s"]
default = None if parameter.default is inspect.Parameter.empty else parameter.default
print(json.dumps({"default": default}, default=repr))
"""


@dataclass(frozen=True)
class Call:
    """One call of ``ensure_available`` in a child process."""

    result: dict
    elapsed_s: float  # around the call itself, measured in the child
    wall_s: float  # the whole child process, measured by the test
    stderr: str

    @property
    def warning(self):
        return self.result.get("warning")


# --------------------------------------------------------------------------
# the stand-ins
# --------------------------------------------------------------------------

# The stand-in ``ollama``. It records how it was run. ``serve`` then either answers the health request on the
# endpoint of its own OLLAMA_HOST ("healthy") or only sleeps ("never"). It writes nothing to its output streams.
OLLAMA_STAND_IN = """\
#!{python}
import json, os, sys, time

LOG = {log!r}
MODE = {mode!r}
LIFETIME_S = {lifetime}


def record(entry):
    with open(LOG, "a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry) + "\\n")


host = os.environ.get("OLLAMA_HOST")
record({{"kind": "exec", "argv": sys.argv[1:], "pid": os.getpid(), "host": host,
        "keep_alive_env": {{k: v for k, v in os.environ.items() if "KEEP_ALIVE" in k.upper()}}}})
if sys.argv[1:2] != ["serve"]:
    sys.exit(0)
end = time.monotonic() + LIFETIME_S
if MODE != "healthy" or not host:
    while time.monotonic() < end:
        time.sleep(0.2)
    sys.exit(0)

from http.server import BaseHTTPRequestHandler, HTTPServer


class Handler(BaseHTTPRequestHandler):
    def answer(self):
        length = int(self.headers.get("Content-Length") or 0)
        body = self.rfile.read(length).decode("utf-8", "replace") if length else ""
        record({{"kind": "request", "method": self.command, "path": self.path, "body": body}})
        ok = self.command == "GET" and self.path == {health!r}
        payload = b'{{"version":"0.35.0"}}' if ok else b"{{}}"
        self.send_response(200 if ok else 404)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    do_GET = do_POST = do_DELETE = do_HEAD = answer

    def log_message(self, *args):
        pass


name, _, port = host.split("//")[-1].rstrip("/").rpartition(":")
server = HTTPServer((name, int(port)), Handler)
server.timeout = 0.2
while time.monotonic() < end:
    server.handle_request()
"""

# The stand-in for a unit command: it records the call and does nothing.
UNIT_STAND_IN = """\
#!{python}
import json, os, sys

with open({log!r}, "a", encoding="utf-8") as handle:
    handle.write(json.dumps({{"kind": "unit", "name": os.path.basename(sys.argv[0]), "argv": sys.argv[1:]}}) + "\\n")
"""


def free_port():
    """A loopback port nothing listens on."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.bind(("127.0.0.1", 0))
        return probe.getsockname()[1]


def _write_executable(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    path.chmod(0o755)
    return path


class Stage:
    """One test's stand-ins, environment and child calls, all under one temporary directory."""

    def __init__(self, root):
        self.root = Path(root)
        self.home = self.root / "home"
        self.work = self.root / "work"
        self.tmp = self.root / "tmp"
        self.bin = self.root / "bin"
        self.out = self.root / "out"
        self.log = self.root / "log" / "calls.jsonl"
        for folder in (self.home, self.work, self.tmp, self.bin, self.out, self.log.parent):
            folder.mkdir(parents=True)
        self.port = free_port()
        self.host = f"127.0.0.1:{self.port}"
        self.gov_ollama_bin = None
        self.endpoint_requests = []
        self._servers = []
        self._sockets = []
        self._calls = 0
        for name in UNIT_COMMANDS:
            _write_executable(self.bin / name, UNIT_STAND_IN.format(python=sys.executable, log=str(self.log)))

    # ---- setting the stage ------------------------------------------------

    def install_executable(self, mode, place="GOV_OLLAMA_BIN"):
        """Put the stand-in ``ollama`` where DEC-260 looks: ``mode`` is ``"healthy"`` or ``"never"``."""
        text = OLLAMA_STAND_IN.format(python=sys.executable, log=str(self.log), mode=mode,
                                      lifetime=STAND_IN_LIFETIME_S, health=HEALTH_PATH)
        if place == "GOV_OLLAMA_BIN":
            self.gov_ollama_bin = _write_executable(self.root / "stand-in" / "ollama", text)
            return self.gov_ollama_bin
        if place == "PATH":
            return _write_executable(self.bin / "ollama", text)
        if place == "HOME":
            return _write_executable(self.home / HOME_EXECUTABLE_REL, text)
        raise ValueError(place)

    def endpoint_up(self):
        """A healthy endpoint already listening before the call: ``GET /api/version`` answers 200."""
        requests = self.endpoint_requests

        class Handler(BaseHTTPRequestHandler):
            def answer(self):
                length = int(self.headers.get("Content-Length") or 0)
                body = self.rfile.read(length).decode("utf-8", "replace") if length else ""
                requests.append({"method": self.command, "path": self.path, "body": body})
                ok = self.command == "GET" and self.path == HEALTH_PATH
                payload = b'{"version":"0.35.0"}' if ok else b"{}"
                self.send_response(200 if ok else 404)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)

            do_GET = do_POST = do_DELETE = do_HEAD = answer

            def log_message(self, *args):
                pass

        server = ThreadingHTTPServer(("127.0.0.1", self.port), Handler)
        server.daemon_threads = True
        threading.Thread(target=server.serve_forever, kwargs={"poll_interval": 0.05}, daemon=True).start()
        self._servers.append(server)

    def endpoint_silent(self):
        """An endpoint that accepts a connection and never answers it."""
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listener.bind(("127.0.0.1", self.port))
        listener.listen(64)
        self._sockets.append(listener)

    # ---- calling the function --------------------------------------------

    def environment(self):
        """The child's whole environment. ``PATH`` and ``HOME`` hold only what the stage put there."""
        env = {
            "PATH": str(self.bin),
            "HOME": str(self.home),
            "TMPDIR": str(self.tmp),
            "LANG": "C.UTF-8",
            "LC_ALL": "C.UTF-8",
            "PYTHONPATH": str(REPO_ROOT / "src"),
            "PYTHONDONTWRITEBYTECODE": "1",
            "OLLAMA_HOST": self.host,
        }
        if self.gov_ollama_bin is not None:
            env["GOV_OLLAMA_BIN"] = str(self.gov_ollama_bin)
        return env

    def _child(self, code, *args):
        """Run ``python3 -c code`` and return (standard output, standard error, wall seconds).

        The streams go to files, not pipes: a daemon the module starts may inherit them, and a pipe would then
        stay open after the child has ended.
        """
        self._calls += 1
        out_path = self.out / f"call-{self._calls}.stdout"
        err_path = self.out / f"call-{self._calls}.stderr"
        began = time.monotonic()
        with open(out_path, "wb") as out, open(err_path, "wb") as err:
            child = subprocess.Popen([sys.executable, "-c", code, *args], cwd=self.work, env=self.environment(),
                                     stdin=subprocess.DEVNULL, stdout=out, stderr=err)
            try:
                code_out = child.wait(timeout=HANG_LIMIT_S)
            except subprocess.TimeoutExpired:
                child.kill()
                child.wait()
                raise AssertionError(
                    f"the call hung: it had not returned after {HANG_LIMIT_S:.0f} s and was killed") from None
        wall_s = time.monotonic() - began
        stdout = out_path.read_text(encoding="utf-8", errors="replace")
        stderr = err_path.read_text(encoding="utf-8", errors="replace")
        assert code_out == 0, (
            f"the child that calls ensure_available ended with exit code {code_out} "
            f"(the function never raises when the daemon is unavailable, DEC-260):\n{stderr[-2000:]}")
        return stdout, stderr, wall_s

    def call(self, timeout_s=SHORT_DEADLINE_S):
        """Call ``ensure_available(timeout_s=...)`` in a child process."""
        stdout, stderr, wall_s = self._child(CALL_DRIVER, repr(float(timeout_s)))
        lines = [line for line in stdout.splitlines() if line.strip()]
        assert lines, "the child printed no outcome"
        outcome = json.loads(lines[-1])
        result = outcome["result"]
        missing = [key for key in RESULT_KEYS if key not in result]
        assert not missing, f"the result lacks {missing} (DEC-260 names {list(RESULT_KEYS)}): {result}"
        return Call(result=result, elapsed_s=outcome["elapsed_s"], wall_s=wall_s, stderr=stderr)

    def default_deadline(self):
        """The default of ``timeout_s``, read from the function's signature in a child process."""
        stdout, _, _ = self._child(DEFAULT_DRIVER)
        return json.loads(stdout.strip().splitlines()[-1])["default"]

    # ---- what happened ----------------------------------------------------

    def _records(self, kind):
        if not self.log.is_file():
            return []
        entries = [json.loads(line) for line in self.log.read_text(encoding="utf-8").splitlines() if line.strip()]
        return [entry for entry in entries if entry["kind"] == kind]

    def runs(self):
        """Every run of the stand-in ``ollama``: its arguments, its pid and its keep-alive environment."""
        return self._records("exec")

    def serve_runs(self):
        return [run for run in self.runs() if run["argv"][:1] == ["serve"]]

    def unit_calls(self):
        """Every call of ``systemctl``, ``systemd-run`` or ``loginctl``."""
        return self._records("unit")

    def requests(self):
        """Every request the stand-in endpoint received, whoever served it."""
        return list(self.endpoint_requests) + self._records("request")

    def endpoint_answers(self):
        """True when ``GET /api/version`` answers 200 now (asked by the test, with no proxy)."""
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        try:
            with opener.open(f"http://{self.host}{HEALTH_PATH}", timeout=2.0) as reply:
                return reply.status == 200
        except (urllib.error.URLError, OSError):
            return False

    def files(self, *bases):
        """Every path under the child's HOME, working directory and TMPDIR (or ``bases``), with each file's hash."""
        seen = {}
        for base in bases or (self.home, self.work, self.tmp):
            for path in sorted(base.rglob("*")):
                rel = f"{base.name}/{path.relative_to(base)}"
                if path.is_file() and not path.is_symlink():
                    seen[rel] = hashlib.sha256(path.read_bytes()).hexdigest()
                else:
                    seen[rel] = "-"
        return seen

    # ---- teardown ---------------------------------------------------------

    def close(self):
        """End every stand-in: the in-test endpoints, and each ``serve`` the module started."""
        for server in self._servers:
            server.shutdown()
            server.server_close()
        for listener in self._sockets:
            listener.close()
        for run in self.serve_runs():
            _end_stand_in(run["pid"])


def _end_stand_in(pid):
    """Kill a stand-in daemon by the pid it recorded, after checking the pid is still that stand-in."""
    cmdline = Path(f"/proc/{pid}/cmdline")
    try:
        if cmdline.parent.parent.is_dir() and b"ollama" not in cmdline.read_bytes():
            return
    except OSError:
        return
    try:
        os.kill(pid, signal.SIGKILL)
    except (ProcessLookupError, PermissionError):
        pass

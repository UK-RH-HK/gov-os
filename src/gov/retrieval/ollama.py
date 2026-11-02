"""Start Ollama on demand, or say that retrieval is FTS-only (DEC-260, DEC-261, DEC-257).

``gov`` starts ``ollama serve`` when the endpoint is down and never stops it:
Ollama's own 5-minute idle unload frees the model's memory. There is no unit and
no keep-alive override. When the daemon cannot be reached within the deadline,
the result names the facet state and the warning is written once to standard error.

Two daemons are started so (DEC-261 as DEC-798 amends it): the shared one at
``OLLAMA_HOST``, which builds the index, and a CPU-only one at
``GOV_QUERY_OLLAMA_HOST``, which embeds the questions and nothing else. The second
is started with its own ``OLLAMA_HOST`` and the GPU hidden (``NO_GPU``).

Every start of either daemon is capped (DEC-1014, DEC-1017): its parallel requests, its logical CPUs and its
niceness come from the ``embedding_servers`` section of the resource gate's configuration file (W2-20), else from
the defaults below. The CPUs and the niceness are set in the started process itself, so every runner it starts
inherits them; an unreadable value refuses the start, never an uncapped one. ``probe`` states a daemon healthy,
slow, hung or down, ``safe_restart`` restarts a hung or down one under the same cap (DEC-1015 item 2), and
``check_determinism`` refuses a parallel setting that changes a vector.
"""

from __future__ import annotations

import concurrent.futures
import datetime
import http.client
import json
import os
import shutil
import signal
import struct
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

DEFAULT_HOST = "127.0.0.1:11434"
HEALTH_PATH = "/api/version"
FACET = "semantic"
WARNING = "Ollama is unavailable: semantic retrieval is skipped and results are FTS-only."
QUERY_HOST_SETTING = "GOV_QUERY_OLLAMA_HOST"  # the CPU-only embedder's address, in OLLAMA_HOST's form (DEC-798)
QUERY_DEFAULT_HOST = "127.0.0.1:11435"
NO_GPU = {"CUDA_VISIBLE_DEVICES": "-1"}  # an id that names no device: Ollama's documented way to use no GPU

GATE_REL = ".gov-os/machine/gate.json"  # the resource gate's one configuration file, under HOME (W2-20)
RESTARTS_REL = ".gov-os/machine/embedding-restarts.jsonl"  # one line per stop or start by ``safe_restart``
SECTION = "embedding_servers"
SERVERS = ("shared", "query")
PARALLEL_SETTING = "OLLAMA_NUM_PARALLEL"  # Ollama's own setting for the requests a runner answers at once
# The measured defaults, the same on every machine (W2-123 KPI 3: docs/changes/W2-123-evidence.md, §4):
# one request at a time: Ollama starts the embedding runner with -np 1 whatever the setting (evidence, figure 1)
DEFAULT_PARALLEL = {"shared": 1, "query": 1}
# ACT-OLLAMA-CAP-1's cap as a count, the highest-numbered 8 CPUs this process may run on; not the limit (figure 2)
DEFAULT_CPU_COUNT = 8
DEFAULT_NICE = 10  # ACT-OLLAMA-CAP-1 and -2's lower priority (evidence, figure 2)
DEFAULT_PROBE_SLOW_S = 10.0  # above a cold model load to the first vector (evidence, figure 5)
DEFAULT_PROBE_HUNG_S = 120.0  # semantic.TIMEOUT_S: past it a rebuild's own request gives up on the server
PROBE_TEXT = "Gov OS embedding server health probe"
STOP_WAIT_S = 10.0  # how long a stopped server's port is waited for before its processes are killed

_OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}))  # the endpoint is local: no proxy


def _healthy(url: str, deadline: float) -> bool:
    """True when ``GET /api/version`` answers 200 before the deadline."""
    try:
        with _OPENER.open(url, timeout=max(0.05, min(1.0, deadline - time.monotonic()))) as reply:
            return reply.status == 200
    except (OSError, http.client.HTTPException):
        return False


def _executable(env) -> str | None:
    """``GOV_OLLAMA_BIN``, then ``ollama`` on ``PATH``, then ``~/.local/ollama/bin/ollama``."""
    home = Path(env.get("HOME") or Path.home()) / ".local/ollama/bin/ollama"
    return (env.get("GOV_OLLAMA_BIN") or shutil.which("ollama", path=env.get("PATH"))
            or (str(home) if home.is_file() else None))


def _home(env) -> Path:
    return Path(env.get("HOME") or Path.home())


def _url(host: str, path: str = "") -> str:
    return (host if "://" in host else f"http://{host}").rstrip("/") + path


def _cpu_list(cpus) -> str:
    """``{12, 13, 14, 19}`` as ``"12-14,19"``, the CPU-list form of ``taskset -c``."""
    ranges: list[list[int]] = []
    for cpu in sorted(cpus):
        if ranges and cpu == ranges[-1][1] + 1:
            ranges[-1][1] = cpu
        else:
            ranges.append([cpu, cpu])
    return ",".join(str(a) if a == b else f"{a}-{b}" for a, b in ranges)


def _parse_cpus(text: str) -> set[int] | None:
    """The CPUs a CPU list names, or None when it cannot be parsed."""
    cpus: set[int] = set()
    for part in text.split(","):
        low, _, high = part.strip().partition("-")
        if not low.isdigit() or (high and not high.isdigit()) or int(high or low) < int(low):
            return None
        cpus.update(range(int(low), int(high or low) + 1))
    return cpus


def _number(value, low, integer: bool) -> bool:
    kinds = (int,) if integer else (int, float)
    return isinstance(value, kinds) and not isinstance(value, bool) and value >= low


def _config(server: str, env) -> tuple[dict | None, dict | None, str | None]:
    """``(settings, probe limits, None)`` for ``server`` from the gate's file and the defaults, or
    ``(None, None, warning)`` naming the file and the key of the first unreadable value."""
    path = _home(env) / GATE_REL
    entry: dict = {}

    def bad(key: str, why: str):
        return None, None, f"{path}: {key} is unreadable ({why}); the {server} embedding server is not started"
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as error:
            return bad(SECTION, f"the file is not JSON: {error}")
        if not isinstance(data, dict):
            return bad(SECTION, "the file is not a JSON object")
        section = data.get(SECTION, {})
        if not isinstance(section, dict):
            return bad(SECTION, "not an object")
        entry = section.get(server, {})
        if not isinstance(entry, dict):
            return bad(f"{SECTION}.{server}", "not an object")
    key = f"{SECTION}.{server}."
    parallel = entry.get("parallel", DEFAULT_PARALLEL[server])
    if not _number(parallel, 1, True):
        return bad(key + "parallel", "an integer of at least 1 is needed")
    nice = entry.get("nice", DEFAULT_NICE)
    if not _number(nice, 0, True) or nice > 19:
        return bad(key + "nice", "an integer from 0 to 19 is needed")
    allowed = os.sched_getaffinity(0)
    if "cpus" in entry:
        named = _parse_cpus(entry["cpus"]) if isinstance(entry["cpus"], str) else None
        if named is None:
            return bad(key + "cpus", "a CPU list such as \"2-5,8\" is needed")
        cpus = named & allowed
        if not cpus:
            return bad(key + "cpus", f"it names no CPU this process may run on ({_cpu_list(allowed)})")
    else:
        cpus = set(sorted(allowed)[-DEFAULT_CPU_COUNT:])
    limits = {"probe_slow_s": entry.get("probe_slow_s", DEFAULT_PROBE_SLOW_S),
              "probe_hung_s": entry.get("probe_hung_s", DEFAULT_PROBE_HUNG_S)}
    for name, value in limits.items():
        if not _number(value, 0, False) or value <= 0:
            return bad(key + name, "a positive number of seconds is needed")
    if limits["probe_slow_s"] >= limits["probe_hung_s"]:
        return bad(key + "probe_slow_s", "it must be below probe_hung_s")
    source = str(path) if any(name in entry for name in ("parallel", "cpus", "nice")) else "default"
    return {"parallel": parallel, "cpus": _cpu_list(cpus), "nice": nice, "source": source}, limits, None


def _server(env) -> str:
    """``"query"`` when ``OLLAMA_HOST`` is the query embedder's address (``ensure_query_available`` sets it so),
    else ``"shared"``."""
    return "query" if (env.get("OLLAMA_HOST") or DEFAULT_HOST) == query_host(env) else "shared"


def _host(server: str, env) -> str:
    return query_host(env) if server == "query" else env.get("OLLAMA_HOST") or DEFAULT_HOST


def _capped(settings: dict):
    """The function the started daemon runs before ``serve``: its CPUs and its niceness, which every process it
    starts inherits. Niceness is only ever raised."""
    cpus = _parse_cpus(settings["cpus"])

    def cap():
        os.sched_setaffinity(0, cpus)
        os.setpriority(os.PRIO_PROCESS, 0, max(settings["nice"], os.getpriority(os.PRIO_PROCESS, 0)))
    return cap


def ensure_available(*, timeout_s: float = 20.0, env=None) -> dict:
    """Make the Ollama endpoint answer within ``timeout_s``, starting ``ollama serve`` if needed, capped; never raises
    when it cannot. ``env`` (default: the process environment) is read for the three variables and given to
    the daemon."""
    env = os.environ if env is None else env
    server = _server(env)
    settings, _, invalid = _config(server, env)
    deadline = time.monotonic() + timeout_s
    url = _url(env.get("OLLAMA_HOST") or DEFAULT_HOST, HEALTH_PATH)
    available = _healthy(url, deadline)
    started = False
    if invalid:
        print(invalid, file=sys.stderr)
        if available:
            return {"available": True, "started": False, "facet": FACET, "state": "AVAILABLE", "warning": invalid,
                    "settings": None}
        return {"available": False, "started": False, "facet": FACET, "state": "CONFIG_INVALID", "warning": invalid,
                "settings": None}
    executable = None if available else _executable(env)
    if executable:
        daemon_env = {**env, PARALLEL_SETTING: str(settings["parallel"]), **(NO_GPU if server == "query" else {})}
        try:
            # Its own session and no inherited streams: the daemon outlives this call and is never stopped.
            subprocess.Popen([executable, "serve"], env=daemon_env, stdin=subprocess.DEVNULL,
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True,
                             preexec_fn=_capped(settings))
            started = True
        except FileNotFoundError:  # the executable named is not there: it is not found
            executable = None
        except (OSError, subprocess.SubprocessError):  # a cap that cannot be set is no start
            pass
        while started and not available and time.monotonic() < deadline:
            time.sleep(0.1)
            available = _healthy(url, deadline)
    if available:
        return {"available": True, "started": started, "facet": FACET, "state": "AVAILABLE", "warning": None,
                "settings": settings}
    print(WARNING, file=sys.stderr)
    result = {"available": False, "started": started, "facet": FACET, "state": "FACET_UNAVAILABLE",
              "warning": WARNING}
    # No executable found, so nothing could start and there are no settings of a start to state (W1-18's result).
    return {**result, "settings": settings} if executable else result


def query_host(env=None) -> str:
    """The CPU-only embedder's address: ``GOV_QUERY_OLLAMA_HOST``, else ``QUERY_DEFAULT_HOST``."""
    env = os.environ if env is None else env
    return env.get(QUERY_HOST_SETTING) or QUERY_DEFAULT_HOST


def ensure_query_available(*, timeout_s: float = 20.0, env=None) -> dict:
    """Make the CPU-only embedder answer at ``query_host``, as ``ensure_available`` does, starting ``ollama serve``
    with ``OLLAMA_HOST`` set to that address and ``NO_GPU`` in its environment; never stopped."""
    env = os.environ if env is None else env
    return ensure_available(timeout_s=timeout_s, env={**env, "OLLAMA_HOST": query_host(env), **NO_GPU})


def _embed_one(host: str, text: str, timeout_s: float) -> bytes | None:
    """The float32 BLOB of ``text`` embedded alone at ``host``, packed as the semantic store packs it; None when the
    answer holds no single vector. A failed connection or a timeout raises."""
    from gov.retrieval.semantic import MODEL  # semantic imports this module
    request = urllib.request.Request(_url(host, "/api/embed"), headers={"Content-Type": "application/json"},
                                     data=json.dumps({"model": MODEL, "input": [text]}).encode())
    with _OPENER.open(request, timeout=timeout_s) as reply:
        vectors = json.load(reply).get("embeddings") or []
    return struct.pack(f"{len(vectors[0])}f", *vectors[0]) if len(vectors) == 1 else None


def probe(server: str, *, env=None) -> dict:
    """One fixed text embedded at ``server``'s address: ``healthy`` within ``probe_slow_s``, ``slow`` within
    ``probe_hung_s``, ``hung`` with no vector by then, ``down`` when nothing listens. Never starts or stops anything."""
    env = os.environ if env is None else env
    host = _host(server, env)
    _, limits, invalid = _config(server, env)
    result = {"server": server, "host": host, "state": "CONFIG_INVALID", "seconds": None, "warning": invalid}
    if invalid:
        return result
    began = time.monotonic()
    try:
        vector = _embed_one(host, PROBE_TEXT, limits["probe_hung_s"])
        seconds = time.monotonic() - began
    except urllib.error.URLError as error:
        down = isinstance(error.reason, ConnectionRefusedError)
        return {**result, "state": "down" if down else "hung"}
    except (OSError, http.client.HTTPException, ValueError, AttributeError, TypeError, struct.error):
        return {**result, "state": "hung"}
    if vector is None or seconds > limits["probe_hung_s"]:
        state = "hung"
    else:
        state = "healthy" if seconds <= limits["probe_slow_s"] else "slow"
    return {**result, "state": state, "seconds": seconds}


def _port(host: str) -> int:
    return urllib.parse.urlsplit(_url(host)).port or int(DEFAULT_HOST.rsplit(":", 1)[1])


def _stat(pid: int) -> tuple[str, int] | None:
    """A live process's state letter and parent pid; None when it is gone or a zombie."""
    try:
        fields = Path(f"/proc/{pid}/stat").read_text().rsplit(")", 1)[1].split()
    except (OSError, IndexError):
        return None
    return None if fields[0] in "ZX" else (fields[0], int(fields[1]))


def _listener(port: int) -> int | None:
    """The pid that listens on ``port`` (the eldest, when its children share the socket), or None."""
    sockets = set()
    for table in ("/proc/net/tcp", "/proc/net/tcp6"):
        try:
            rows = Path(table).read_text().splitlines()[1:]
        except OSError:
            continue
        sockets.update(f"socket:[{row.split()[9]}]" for row in rows
                       if row.split()[3] == "0A" and int(row.split()[1].rsplit(":", 1)[1], 16) == port)
    holders = set()
    for proc in Path("/proc").iterdir():
        try:
            if proc.name.isdigit() and any(os.readlink(fd) in sockets for fd in (proc / "fd").iterdir()):
                holders.add(int(proc.name))
        except OSError:
            continue
    eldest = [pid for pid in holders if (_stat(pid) or ("", 0))[1] not in holders]
    return min(eldest) if eldest else None


def _cmdline(pid: int) -> list[str]:
    try:
        return Path(f"/proc/{pid}/cmdline").read_bytes().decode(errors="replace").rstrip("\0").split("\0")
    except OSError:
        return []


def _is_serve(pid: int, executable: str | None) -> bool:
    """True when ``pid`` runs ``<executable> serve`` (paths resolved; a script's interpreter may come first)."""
    args = _cmdline(pid)
    if not executable or len(args) < 2 or args[-1] != "serve":
        return False
    try:
        cwd = os.readlink(f"/proc/{pid}/cwd")
    except OSError:
        return False
    return os.path.realpath(os.path.join(cwd, args[-2])) == os.path.realpath(executable)


def _stop(pid: int, port: int) -> bool:
    """Stop ``pid`` and every process it started, politely then by force; True once all are gone and the port free."""
    victims, parents = [pid], {}
    for proc in Path("/proc").iterdir():
        if proc.name.isdigit() and (stat := _stat(int(proc.name))):
            parents.setdefault(stat[1], []).append(int(proc.name))
    for victim in victims:
        victims.extend(parents.get(victim, []))
    for sig in (signal.SIGTERM, signal.SIGKILL):
        for victim in victims:
            try:
                os.kill(victim, sig)
            except OSError:
                pass
        deadline = time.monotonic() + STOP_WAIT_S
        while time.monotonic() < deadline and (any(map(_stat, victims)) or _listener(port)):
            time.sleep(0.1)
        if not any(map(_stat, victims)) and not _listener(port):
            return True
    return False


def safe_restart(server: str, *, env=None) -> dict:
    """Restart ``server`` when it is hung or down, under the cap its start applies, and record it; never while it
    answers, and never a process on its port that is not the Gov OS's own ``<executable> serve``."""
    env = os.environ if env is None else env
    host, port = _host(server, env), _port(_host(server, env))
    settings, _, invalid = _config(server, env)
    checked = probe(server, env=env)
    result = {"server": server, "host": host, "restarted": False, "reason": invalid, "probe": checked,
              "settings": settings, "old_pid": None, "new_pid": None}
    if invalid:
        return result
    if checked["state"] == "hung":
        checked = result["probe"] = probe(server, env=env)  # re-checked immediately before any stop
    if checked["state"] in ("healthy", "slow"):
        return {**result, "reason": f"the server is answering ({checked['state']}): nothing is restarted"}
    if checked["state"] == "hung":
        old = _listener(port)
        if old is None:
            return {**result, "reason": f"no process this session can see listens on port {port}: nothing is stopped"}
        if not _is_serve(old, _executable(env)):
            return {**result, "reason": f"port {port} is held by process {old} ({' '.join(_cmdline(old))}), not the "
                                        f"Gov OS's `{_executable(env)} serve`: it is not stopped"}
        result["old_pid"] = old
        if not _stop(old, port):
            _record(env, result, checked)
            return {**result, "reason": f"process {old} or a process it started did not stop; nothing is started"}
    start = (ensure_query_available if server == "query" else ensure_available)(env=env)
    result.update(restarted=start["started"], new_pid=_listener(port) if start["started"] else None,
                  reason=f"the server was {checked['state']}: " + (
                      "started again under its cap" if start["started"] and start["available"] else
                      "started again, not answering yet" if start["started"] else f"not started ({start['state']})"))
    if start["started"] or result["old_pid"]:
        _record(env, result, checked)
    return result


def _record(env, result: dict, checked: dict) -> None:
    path = _home(env) / RESTARTS_REL
    path.parent.mkdir(parents=True, exist_ok=True)
    line = {"time": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
            "probe_state": checked["state"], "reason": result["reason"],
            **{key: result[key] for key in ("server", "host", "old_pid", "new_pid", "restarted", "settings")}}
    with path.open("a", encoding="utf-8") as record:
        record.write(json.dumps(line) + "\n")


def check_determinism(host: str, references, parallel: int) -> dict:
    """Embed every ``(text, expected)`` alone at ``host``, ``parallel`` requests in flight at once, and compare each
    float32 BLOB with ``expected`` byte for byte: ``accepted`` only when every vector came back equal."""
    from gov.retrieval.semantic import TIMEOUT_S
    references = list(references)

    def one(text):
        try:
            return _embed_one(host, text, TIMEOUT_S)
        except (OSError, http.client.HTTPException, ValueError, AttributeError, TypeError, struct.error):
            return None
    with concurrent.futures.ThreadPoolExecutor(max_workers=parallel) as pool:
        answers = list(pool.map(one, [text for text, _ in references]))
    differing = [index for index, (answer, (_, expected)) in enumerate(zip(answers, references))
                 if answer is None or answer != bytes(expected)]
    # Nothing checked is no measure: it refuses too.
    verdict = "accepted" if references and not differing else "refused"
    return {"parallel": parallel, "checked": len(references), "differing": differing, "verdict": verdict}

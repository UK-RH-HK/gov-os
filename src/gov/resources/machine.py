"""The gate's readings of the machine (W2-20 S1, S2, S4, S5, S12, S13).

Each reader returns ``(value, why)``: the value, or None with why it cannot be read. A reading that cannot be taken
is never a default: the gate shuts on it, naming it (F5).

Sources, each replaceable for a planted machine:

- memory ``/proc/meminfo`` (``GOV_RESOURCES_MEMINFO``: ``MemAvailable:`` in kB); load ``/proc/loadavg``
  (``GOV_RESOURCES_LOADAVG``: fields 1 and 3); the processor count (``GOV_RESOURCES_NPROC``, else the machine's);
  busy cores over the last minute (``GOV_RESOURCES_BUSY_CORES``, one number, else the gate's own sampling of
  ``/proc/stat``, ``GOV_RESOURCES_STAT``); the embedding servers' CPU p95 (``GOV_RESOURCES_EMBEDDING_CPU``, JSON
  ``{"shared": cores, "query": cores}``, else the gate's own sampling of the two servers) and their use over the
  same last minute (``GOV_RESOURCES_EMBEDDING_CPU_NOW``, the same form; round 7, review F2); the shared disk
  (``GOV_RESOURCES_DISK``, JSON ``{"free_bytes", "free_inodes"}``, else ``statvfs`` of HOME's disk); the processes
  ``/proc/<pid>`` (``GOV_RESOURCES_PROC``); the GPU ``nvidia-smi`` on ``PATH``.
- The own busy-cores sampling: two readings of the CPU counters; the earlier one is the newest sample at least a
  minute old in ``~/.gov-os/machine/cpu-stat.json`` (each reading adds one), else the oldest at least a quarter of a
  second old, else a reading a quarter of a second before.
"""

from __future__ import annotations

import datetime
import json
import math
import os
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

PAGE = os.sysconf("SC_PAGE_SIZE") if hasattr(os, "sysconf") else 4096
TICKS = os.sysconf("SC_CLK_TCK") if hasattr(os, "sysconf") else 100
CPU_HISTORY = "cpu-stat.json"
SERVER_HISTORY = "embedding-cpu.jsonl"  # the servers' CPU samples, one JSON line per server per sample (review R2-F1)
OLD_SERVER_HISTORY = "server-cpu.json"  # round 3's history: dropped at the next reading, never read
SERVER_LINES = 600  # the lines kept of each server
WINDOW_S, KEEP_S, SHORT_S = 60.0, 600.0, 0.25  # the last minute; the history kept; the window with no history
SERVER_KEEP_S, SERVER_SAMPLES, P95 = 7 * 24 * 3600, 500, 0.95
SMI_TIMEOUT_S = 10.0
MIB = 1024 ** 2


def _source(env: str, default: str) -> str:
    return os.environ.get(env) or default


def proc_root() -> Path:
    return Path(_source("GOV_RESOURCES_PROC", "/proc"))


def memory():
    """``(MemAvailable in bytes, None)``."""
    source = _source("GOV_RESOURCES_MEMINFO", "/proc/meminfo")
    try:
        for line in Path(source).read_text().splitlines():
            name, _, rest = line.partition(":")
            if name.strip() == "MemAvailable":
                value = int(rest.split()[0]) * 1024
                if value < 0:
                    raise ValueError("a negative MemAvailable")
                return value, None
    except (OSError, ValueError, IndexError) as error:
        return None, f"{source}: {error}"
    return None, f"{source} has no MemAvailable line"


def load():
    """``((load1, load15), None)``: fields 1 and 3 of the load file."""
    source = _source("GOV_RESOURCES_LOADAVG", "/proc/loadavg")
    try:
        parts = Path(source).read_text().split()
        one, fifteen = float(parts[0]), float(parts[2])
        if not (math.isfinite(one) and math.isfinite(fifteen)) or one < 0 or fifteen < 0:
            raise ValueError("non-negative load figures are needed")
        return (one, fifteen), None
    except (OSError, ValueError, IndexError) as error:
        return None, f"{source}: {error}"


def nproc():
    """``(count, None)``: the machine's processors (``GOV_RESOURCES_NPROC`` where set), never the caller's CPU set."""
    given = os.environ.get("GOV_RESOURCES_NPROC")
    if given is None:
        count = os.cpu_count()
        return (count, None) if count else (None, "the processor count cannot be read")
    try:
        if int(given) > 0:
            return int(given), None
    except ValueError:
        pass
    return None, f"GOV_RESOURCES_NPROC={given!r} is not a positive count"


def _planted_text(name: str, env=None):
    """``(text, None)`` of a planted reading: the file the variable names (as ``GOV_RESOURCES_MEMINFO`` names one),
    or the value itself when it is no path; ``(None, why)`` when the file cannot be read."""
    given = (os.environ if env is None else env).get(name)
    if given is None:
        return None, f"{name} is not set"
    if os.sep in given and not given.lstrip().startswith(("{", "[")):
        try:
            return Path(given).read_text(encoding="utf-8"), None
        except (OSError, UnicodeDecodeError) as error:
            return None, f"{name}: {given}: {error}"
    return given, None


def _planted_number(name: str):
    text, why = _planted_text(name)
    if why:
        return None, why
    try:
        value = float(text.split()[0])
        if not math.isfinite(value) or value < 0:
            raise ValueError
    except (IndexError, ValueError):
        return None, f"{name}: {text.strip()[:80]!r} is not a non-negative number"
    return value, None


# --- busy cores ------------------------------------------------------------------------------------------------------

def cpu_counters():
    """``((busy_ticks, total_ticks), None)`` from the ``cpu`` line of ``/proc/stat`` (idle and iowait are not busy)."""
    source = _source("GOV_RESOURCES_STAT", "/proc/stat")
    try:
        for line in Path(source).read_text().splitlines():
            parts = line.split()
            if parts and parts[0] == "cpu":
                ticks = [int(part) for part in parts[1:9]]
                if len(ticks) < 4:
                    break
                idle = ticks[3] + (ticks[4] if len(ticks) > 4 else 0)
                return (sum(ticks) - idle, sum(ticks)), None
    except (OSError, ValueError) as error:
        return None, f"{source}: {error}"
    return None, f"{source} has no cpu line"


def _read_json(path: Path, kind):
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, kind) else kind()
    except (OSError, ValueError):
        return kind()


def _write_json(path: Path, data) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile("w", dir=path.parent, prefix=".hist-", suffix=".tmp", delete=False) as out:
            json.dump(data, out)
        os.replace(out.name, path)
    except OSError:
        pass  # a history only lengthens the window


def boot_id() -> str | None:
    """This boot's id (``/proc/sys/kernel/random/boot_id``), or None where it cannot be read."""
    try:
        return Path("/proc/sys/kernel/random/boot_id").read_text().strip() or None
    except OSError:
        return None


def _this_boot(item: dict, boot: str | None) -> bool:
    """Whether a kept sample may be of this boot: one that names another boot is not (review F6)."""
    return not (boot and isinstance(item.get("boot"), str) and item["boot"] != boot)


def busy_cores(folder: Path, processors: int | None):
    """``(busy cores over the last minute, None)``: ``GOV_RESOURCES_BUSY_CORES`` where set, else the own sampling.

    A kept sample from before a restart (another boot, or counters above today's) is dropped at once, so the reading
    after a restart is a short window, never null (review F6)."""
    if "GOV_RESOURCES_BUSY_CORES" in os.environ:
        return _planted_number("GOV_RESOURCES_BUSY_CORES")
    now_counters, why = cpu_counters()
    if why:
        return None, why
    if not processors:
        return None, "the processor count is unknown, so busy cores cannot be counted"
    path, now, boot = folder / CPU_HISTORY, time.time(), boot_id()
    history = [item for item in _read_json(path, list) if isinstance(item, dict) and {"t", "busy", "total"} <= set(item)
               and all(isinstance(item[k], (int, float)) and not isinstance(item[k], bool) for k in ("t", "busy", "total"))
               and 0 <= now - item["t"] <= KEEP_S and _this_boot(item, boot)
               and item["busy"] <= now_counters[0] and item["total"] <= now_counters[1]]
    older = [item for item in history if now - item["t"] >= WINDOW_S]
    recent = [item for item in history if SHORT_S <= now - item["t"] < WINDOW_S]
    base = max(older, key=lambda i: i["t"]) if older else (min(recent, key=lambda i: i["t"]) if recent else None)
    if base is None:
        time.sleep(SHORT_S)
        later, why = cpu_counters()
        if why:
            return None, why
        base = {"t": now, "busy": now_counters[0], "total": now_counters[1]}
        now, now_counters = time.time(), later
    history.append({"t": now, "busy": now_counters[0], "total": now_counters[1], **({"boot": boot} if boot else {})})
    _write_json(path, history[-64:])
    busy, total = now_counters[0] - base["busy"], now_counters[1] - base["total"]
    if total > 0 and busy >= 0:
        return round(processors * busy / total, 2), None
    if total == 0 and busy == 0 and now_counters[1] > 0:  # a still, planted snapshot: its own share since its start
        return round(processors * now_counters[0] / now_counters[1], 2), None
    return None, "the CPU counters went back or hold no time, so busy cores cannot be counted"


# --- the embedding servers' CPU p95 ---------------------------------------------------------------------------------

def _p95(rates: list[float]) -> float:
    ordered = sorted(rates)
    return ordered[max(0, math.ceil(P95 * len(ordered)) - 1)]


def _server_ports(values: dict) -> dict[str, int] | None:
    from gov.retrieval import ollama

    if values.get("embedding_servers") is None:
        return None
    hosts = {"shared": os.environ.get("OLLAMA_HOST") or ollama.DEFAULT_HOST, "query": ollama.query_host()}
    out = {}
    for name, host in hosts.items():
        entry = values["embedding_servers"].get(name) or {}
        host = entry.get("host") if isinstance(entry.get("host"), str) else host
        try:
            out[name] = int(host.rsplit(":", 1)[1].split("/")[0])
        except (IndexError, ValueError):
            return None
    return out


def _planted_servers(name: str):
    """``({"shared": cores, "query": cores}, None)`` of a planted servers' reading, or ``(None, why)``."""
    given, why = _planted_text(name)
    if why:
        return None, why
    try:
        data = json.loads(given)
        out = {server: float(data[server]) for server in ("shared", "query")}
        if any(not math.isfinite(v) or v < 0 for v in out.values()) or any(
                isinstance(data[server], bool) for server in out):
            raise ValueError
        return out, None
    except (ValueError, TypeError, KeyError):
        return None, f"{name}={given!r} is not {{\"shared\": cores, \"query\": cores}}"


def embedding_cpu(folder: Path, values: dict):
    """``({"shared": p95 cores, "query": p95 cores}, None)``: the servers' CPU p95 (``servers_cpu``'s first half)."""
    return servers_cpu(folder, values)[0]


def servers_cpu(folder: Path, values: dict):
    """``((p95, why), (now, why))``, each ``{"shared": cores, "query": cores}`` or None (round 7, review F2).

    - p95: ``GOV_RESOURCES_EMBEDDING_CPU`` where set, else the p95 of each server's rates between its consecutive
      samples of one process over the last week (one sample of each server's process tree per reading, in
      ``embedding-cpu.jsonl``: ``{"time", "server", "pid", "cpu_seconds"}``).
    - now: ``GOV_RESOURCES_EMBEDDING_CPU_NOW`` where set, else each server's CPU use over the busy cores' last minute
      from its kept samples, those of its current pid at most ``KEEP_S`` old (the same window rule: the newest kept
      sample at least a minute old, else the oldest). It is the servers' part of the busy cores.

    A listening server with no kept sample (a new process, or every sample expired) is sampled afresh first, a quarter
    of a second apart, so stale samples never shut the gate (review R2-F1, DEC-1105). A server that is not listening
    uses no CPU now."""
    planted = {}
    for key, name in (("p95", "GOV_RESOURCES_EMBEDDING_CPU"), ("now", "GOV_RESOURCES_EMBEDDING_CPU_NOW")):
        if os.environ.get(name) is not None:
            planted[key] = _planted_servers(name)
    if len(planted) < 2:
        sampled = _sample_servers(folder, values)
        planted.setdefault("p95", sampled[0])
        planted.setdefault("now", sampled[1])
    return planted["p95"], planted["now"]


def _number(value) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def _read_samples(path: Path) -> list[dict]:
    """The servers' kept samples, oldest first; a line that is not ``{"time", "server", "pid", "cpu_seconds"}`` is
    skipped (a sample only lengthens the window)."""
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return []
    out = []
    for line in text.splitlines():
        try:
            item = json.loads(line)
        except ValueError:
            continue
        if isinstance(item, dict) and item.get("server") in ("shared", "query") and _number(item.get("time")) \
                and isinstance(item.get("pid"), int) and not isinstance(item["pid"], bool) \
                and _number(item.get("cpu_seconds")) and item["cpu_seconds"] >= 0:
            out.append({key: item[key] for key in ("time", "server", "pid", "cpu_seconds")})
    return sorted(out, key=lambda s: s["time"])


def _write_samples(path: Path, samples: list[dict]) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile("w", dir=path.parent, prefix=".hist-", suffix=".tmp", delete=False) as out:
            out.writelines(json.dumps(sample) + "\n" for sample in samples)
        os.replace(out.name, path)
    except OSError:
        pass  # a history only lengthens the window


def _window_rate(kept: list[dict], at: float, cpu: float) -> float | None:
    """A server's cores over the last minute from its kept samples (its current pid, at most ``KEEP_S`` old)."""
    same = [s for s in kept if s["cpu_seconds"] <= cpu and at > s["time"]]
    older = [s for s in same if at - s["time"] >= WINDOW_S]
    base = max(older, key=lambda s: s["time"]) if older else (min(same, key=lambda s: s["time"]) if same else None)
    if base is None:
        return None
    return round(max(0.0, (cpu - base["cpu_seconds"]) / (at - base["time"])), 2)


def _rates(samples: list[dict]) -> list[float]:
    """The rates between one server's consecutive samples of one process (oldest first)."""
    return [(b["cpu_seconds"] - a["cpu_seconds"]) / (b["time"] - a["time"]) for a, b in zip(samples, samples[1:])
            if a["pid"] == b["pid"] and b["time"] > a["time"] and b["cpu_seconds"] >= a["cpu_seconds"]]


def _sample_servers(folder: Path, values: dict):
    """The servers' own sampling: ``((p95, why), (now, why))``."""
    ports = _server_ports(values)
    if ports is None:
        why = "the embedding servers' section cannot be read, so their CPU cannot be measured"
        return (None, why), (None, why)
    path, samples = folder / SERVER_HISTORY, _read_samples(folder / SERVER_HISTORY)
    try:
        (folder / OLD_SERVER_HISTORY).unlink(missing_ok=True)  # round 3's history is never read
    except OSError:
        pass

    def cpu_now():
        table = processes()
        pids = {name: listener(port, table) for name, port in ports.items()}
        return {name: (pid, round(sum(table[p]["ticks"] for p in tree(table, pid)) / TICKS, 3)
                       if pid in table else None) for name, pid in pids.items()}, time.time()

    def kept(name, pid, at) -> list[dict]:
        """The server's kept samples: of its current pid, earlier than ``at`` and at most ``KEEP_S`` old."""
        return [s for s in samples if s["server"] == name and s["pid"] == pid and 0 < at - s["time"] <= KEEP_S]

    first, at = cpu_now()
    pending = [n for n, (pid, cpu) in first.items() if pid is not None and cpu is not None and not kept(n, pid, at)]
    if pending:  # no kept sample of this server's process (new, or every one expired): a short fresh one first
        time.sleep(SHORT_S)
        second, later = cpu_now()
        samples += [{"time": at, "server": n, "pid": first[n][0], "cpu_seconds": first[n][1]} for n in pending]
        first, at = second, later
    out, now = {}, {}
    for name, (pid, cpu) in first.items():
        mine = [s for s in samples if s["server"] == name and 0 <= at - s["time"] <= SERVER_KEEP_S]
        if cpu is not None:
            mine.append({"time": at, "server": name, "pid": pid, "cpu_seconds": cpu})
        rates = _rates(mine)[-SERVER_SAMPLES:] + ([0.0] if pid is None else [])
        out[name] = round(_p95(rates), 2) if rates else None
        now[name] = 0.0 if pid is None else (None if cpu is None else _window_rate(kept(name, pid, at), at, cpu))
        samples = [s for s in samples if s["server"] != name] + mine[-SERVER_LINES:]
    _write_samples(path, sorted(samples, key=lambda s: s["time"]))
    p95 = (None, "an embedding server's CPU could not be sampled") if None in out.values() else (out, None)
    current = (None, "an embedding server's CPU use over the last minute could not be sampled") \
        if None in now.values() else (now, None)
    return p95, current


# --- the disk ---------------------------------------------------------------------------------------------------------

def disk(env=None):
    """``({"free_bytes", "free_inodes"}, None)`` of the shared disk (HOME's): ``GOV_RESOURCES_DISK`` where set."""
    env = os.environ if env is None else env
    if env.get("GOV_RESOURCES_DISK") is not None:
        given, why = _planted_text("GOV_RESOURCES_DISK", env)
        if why:
            return None, why
        try:
            data = json.loads(given)
            out = {key: data[key] for key in ("free_bytes", "free_inodes")}
            if any(isinstance(v, bool) or not isinstance(v, int) or v < 0 for v in out.values()):
                raise ValueError
            return out, None
        except (ValueError, TypeError, KeyError):
            return None, f"GOV_RESOURCES_DISK={given!r} is not {{\"free_bytes\": N, \"free_inodes\": N}}"
    place = env.get("HOME") or str(Path.home())
    try:
        stat = os.statvfs(place)
    except OSError as error:
        return None, f"{place}: {error}"
    return {"free_bytes": stat.f_bavail * stat.f_frsize, "free_inodes": stat.f_favail}, None


# --- processes --------------------------------------------------------------------------------------------------------

def processes() -> dict[int, dict]:
    """Every readable process: ``{pid: {"ppid", "rss", "ticks", "cmdline"}}`` (rss in bytes, ticks of CPU time)."""
    root, table = proc_root(), {}
    try:
        names = os.listdir(root)
    except OSError:
        return table
    for name in names:
        if not name.isdigit():
            continue
        try:
            fields = (root / name / "stat").read_text().rsplit(")", 1)[1].split()
            statm = (root / name / "statm").read_text().split()
            try:
                cmdline = (root / name / "cmdline").read_bytes().rstrip(b"\0").replace(b"\0", b" ").decode(
                    "utf-8", "replace")
            except OSError:
                cmdline = ""
            table[int(name)] = {"ppid": int(fields[1]), "rss": int(statm[1]) * PAGE,
                                "ticks": int(fields[11]) + int(fields[12]), "cmdline": cmdline}
        except (OSError, ValueError, IndexError):
            continue  # ended meanwhile, or another's: never counted as anything
    return table


def children(table: dict[int, dict]) -> dict[int, list[int]]:
    kids: dict[int, list[int]] = {}
    for pid, info in table.items():
        kids.setdefault(info["ppid"], []).append(pid)
    return kids


def tree(table: dict[int, dict], pid, stop=frozenset()) -> list[int]:
    """``pid`` and every descendant, a subtree rooted at a pid in ``stop`` left out (another session's own)."""
    kids, out, seen, todo = children(table), [], set(), [pid]
    while todo:
        current = todo.pop()
        if current in table and current not in seen:
            seen.add(current)
            out.append(current)
            todo += [child for child in kids.get(current, []) if child not in stop]
    return out


def tree_memory(table: dict[int, dict], pid, stop=frozenset()) -> int:
    return sum(table[p]["rss"] for p in tree(table, pid, stop))


def alive(pid: int) -> bool:
    """Whether ``pid`` runs (a zombie does not); on a planted process table, whether the table holds it."""
    if proc_root() != Path("/proc"):
        return (proc_root() / str(pid)).is_dir()
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:  # another user's process: alive
        return True
    except OSError:
        return False
    try:
        state = Path(f"/proc/{pid}/stat").read_text().rsplit(")", 1)[1].split()[0]
        return state not in ("Z", "X")
    except (OSError, IndexError):
        return True


START_GRACE_S = 5.0  # a process may have started this long after its entry's ``started`` and still be its own


def _boot_time() -> float | None:
    try:
        for line in Path("/proc/stat").read_text().splitlines():
            if line.startswith("btime "):
                return float(line.split()[1])
    except (OSError, ValueError, IndexError):
        pass
    return None


def identity(pid: int) -> dict | None:
    """Who ``pid`` is on the real ``/proc``: ``{"boot", "start_ticks", "start_time"}`` (the boot's id, its start in
    clock ticks since boot, and in epoch seconds where the boot time reads); None on a planted process table or where
    it cannot be read."""
    if proc_root() != Path("/proc"):
        return None
    try:
        ticks = int(Path(f"/proc/{pid}/stat").read_text().rsplit(")", 1)[1].split()[19])
    except (OSError, ValueError, IndexError):
        return None
    boot = _boot_time()
    return {"boot": boot_id(), "start_ticks": ticks,
            "start_time": None if boot is None else round(boot + ticks / TICKS, 2)}


def same_process(pid: int, entry: dict) -> bool:
    """Whether the live ``pid`` is still the process the registry entry names (review F6): False when the entry's
    recorded boot or start differs from the process's, or, for an entry that records neither, when the process started
    after the entry's ``started`` (a pid reused, e.g. after a WSL restart). True where it cannot be told: a live pid
    the gate cannot place is counted, never dropped."""
    found = identity(pid)
    if found is None:
        return True
    boot, ticks = entry.get("boot"), entry.get("start_ticks")
    if isinstance(ticks, int) and not isinstance(ticks, bool):
        if isinstance(boot, str) and found["boot"] and boot != found["boot"]:
            return False
        return ticks == found["start_ticks"]
    started = entry.get("started")
    if not isinstance(started, str) or found["start_time"] is None:
        return True
    try:
        when = datetime.datetime.fromisoformat(started.replace("Z", "+00:00"))
        if when.tzinfo is None:
            when = when.replace(tzinfo=datetime.timezone.utc)
    except ValueError:
        return True
    return found["start_time"] <= when.timestamp() + START_GRACE_S


def listener(port: int, table: dict[int, dict] | None = None) -> int | None:
    """The eldest pid listening on TCP ``port`` (its children may share the socket), or None."""
    root, sockets = proc_root(), set()
    for name in ("net/tcp", "net/tcp6"):
        try:
            rows = (root / name).read_text().splitlines()[1:]
        except OSError:
            continue
        for row in rows:
            parts = row.split()
            try:
                if parts[3] == "0A" and int(parts[1].rsplit(":", 1)[1], 16) == port:
                    sockets.add(f"socket:[{parts[9]}]")
            except (IndexError, ValueError):
                continue
    if not sockets:
        return None
    holders, table = set(), processes() if table is None else table
    for pid in table:
        try:
            if any(os.readlink(fd) in sockets for fd in (root / str(pid) / "fd").iterdir()):
                holders.add(pid)
        except OSError:
            continue
    eldest = [pid for pid in holders if table[pid]["ppid"] not in holders]
    return min(eldest) if eldest else None


# --- the GPU ------------------------------------------------------------------------------------------------------------

GPU_FIELDS = ("memory.total", "memory.used", "memory.free", "utilization.gpu")
APP_FIELDS = ("pid", "process_name", "used_memory")


def _figure(text: str) -> float | None:
    """A CSV figure (``1024``, ``1024 MiB``, ``37 %``); None for ``[N/A]`` or anything not a number."""
    words = text.strip().split()
    try:
        value = float(words[0]) if words else None
    except ValueError:
        return None
    return value if value is not None and math.isfinite(value) and value >= 0 else None


def _rows(stdout: str, fields: tuple) -> list[list[str]]:
    rows = []
    for line in stdout.splitlines():
        if not line.strip():
            continue
        parts = [part.strip() for part in line.split(",")]
        if parts and parts[0].split(" ")[0] in fields:  # a header, though none was asked for
            continue
        rows.append(parts)
    return rows


def gpu_kind(cmdline: str) -> str:
    """A process's GPU work: ``reranker`` (``rerank`` anywhere), ``embedder`` (a word whose file name begins with
    ``ollama``) or ``other``."""
    if "rerank" in cmdline.lower():
        return "reranker"
    if any(os.path.basename(word).lower().startswith("ollama") for word in cmdline.split()):
        return "embedder"
    return "other"


def gpu():
    """``({"available": true, "memory_used_mib", "memory_total_mib", "memory_free_mib", "utilisation_pct",
    "gpus": [...], "processes": [{pid, kind, used_mib}]}, None)``, or ``({"available": false, "reason"}, why)``
    where there is no ``nvidia-smi``, no GPU (exit 6) or an unreadable answer: never an error. One check: two calls of
    ``nvidia-smi``, the GPUs and their processes. A process's memory ``[N/A]`` (WSL) is ``used_mib: null``."""
    program = shutil.which("nvidia-smi")
    if not program:
        return _no_gpu("no nvidia-smi on PATH")
    query = [program, f"--query-gpu={','.join(GPU_FIELDS)}", "--format=csv,noheader,nounits"]
    try:
        answer = subprocess.run(query, capture_output=True, text=True, timeout=SMI_TIMEOUT_S)
    except (OSError, subprocess.SubprocessError) as error:
        return _no_gpu(f"nvidia-smi cannot be run: {error}")
    said = " ".join((answer.stderr + " " + answer.stdout).split())[:200]
    if answer.returncode == 6 or "No devices were found" in said:
        return _no_gpu(f"no GPU: nvidia-smi exit {answer.returncode}: {said}")
    if answer.returncode != 0:
        return _no_gpu(f"the GPU cannot be read: nvidia-smi exit {answer.returncode}: {said}")
    gpus = []
    for index, parts in enumerate(_rows(answer.stdout, GPU_FIELDS)):
        figures = [_figure(part) for part in parts] if len(parts) == len(GPU_FIELDS) else []
        total, used, free, util = figures if figures else (None,) * 4
        if total is None or (used is None and free is None):
            return _no_gpu(f"the GPU cannot be read: an unreadable line {','.join(parts)[:80]!r}")
        used = used if used is not None else max(0.0, total - free)
        free = free if free is not None else max(0.0, total - used)
        gpus.append({"index": index, "memory_total_mib": int(total), "memory_used_mib": int(used),
                     "memory_free_mib": int(free), "utilisation_pct": util})
    if not gpus:
        return _no_gpu("no GPU: nvidia-smi names none")
    found, why = _processes(program)
    utils = [g["utilisation_pct"] for g in gpus if g["utilisation_pct"] is not None]
    out = {"available": True,
           "memory_used_mib": sum(g["memory_used_mib"] for g in gpus),
           "memory_total_mib": sum(g["memory_total_mib"] for g in gpus),
           "memory_free_mib": sum(g["memory_free_mib"] for g in gpus),
           "utilisation_pct": round(sum(utils) / len(utils), 1) if utils else None,
           "gpus": gpus, "processes": found}
    if why:
        out["processes_unreadable"] = why
    return out, None


def _no_gpu(reason: str):
    return {"available": False, "reason": reason}, reason


def _processes(program: str):
    query = [program, f"--query-compute-apps={','.join(APP_FIELDS)}", "--format=csv,noheader,nounits"]
    try:
        answer = subprocess.run(query, capture_output=True, text=True, timeout=SMI_TIMEOUT_S)
    except (OSError, subprocess.SubprocessError) as error:
        return [], f"the GPU's processes cannot be read: {error}"
    if answer.returncode != 0:
        return [], f"the GPU's processes cannot be read (nvidia-smi exit {answer.returncode})"
    out, root = [], proc_root()
    for parts in _rows(answer.stdout, APP_FIELDS):
        if len(parts) < 3 or not parts[0].isdigit():
            return out, f"the GPU's processes: an unreadable line {','.join(parts)[:80]!r}"
        pid, name, used = int(parts[0]), ",".join(parts[1:-1]), _figure(parts[-1])
        try:
            cmdline = (root / str(pid) / "cmdline").read_bytes().replace(b"\0", b" ").decode("utf-8", "replace")
        except OSError:
            cmdline = ""
        out.append({"pid": pid, "kind": gpu_kind(cmdline.strip() or name), "used_mib": None if used is None
                    else int(used)})
    return out, None

"""The gate's readings of the machine (W2-20 S1, S2, S4, S5, S11, S13).

Each reader returns ``(value, why)``: the value, or None with why it cannot be read. A reading that cannot be taken
is never a default: the gate shuts on it, naming it.

Sources, each replaceable for a planted machine:

- memory ``/proc/meminfo`` (``GOV_RESOURCES_MEMINFO``), load ``/proc/loadavg`` (``GOV_RESOURCES_LOADAVG``), the CPU
  counters ``/proc/stat`` (``GOV_RESOURCES_STAT``), the processes ``/proc/<pid>`` (``GOV_RESOURCES_PROC``, a folder
  laid out as ``/proc``), the processor count (``GOV_RESOURCES_NPROC``, else the machine's online CPUs), the GPU
  ``nvidia-smi`` on ``PATH`` (``GOV_RESOURCES_NVIDIA_SMI`` names another).
- Busy cores over the last minute: two readings of the CPU counters; the earlier one is the newest sample at least a
  minute old in ``~/.gov-os/machine/cpu-stat.json`` (each reading adds one), else the oldest at least a second old,
  else a reading one second before. Counters that do not advance cannot be read.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

PAGE = os.sysconf("SC_PAGE_SIZE") if hasattr(os, "sysconf") else 4096
TICKS = os.sysconf("SC_CLK_TCK") if hasattr(os, "sysconf") else 100
CPU_HISTORY = "cpu-stat.json"
WINDOW_S, KEEP_S, SHORT_S = 60.0, 600.0, 1.0
SMI_TIMEOUT_S = 10.0


def _source(env: str, default: str) -> str:
    return os.environ.get(env) or default


def proc_root() -> Path:
    return Path(_source("GOV_RESOURCES_PROC", "/proc"))


def memory():
    """``({"available": bytes, "total": bytes}, None)`` from MemAvailable and MemTotal."""
    source = _source("GOV_RESOURCES_MEMINFO", "/proc/meminfo")
    try:
        fields = {}
        for line in Path(source).read_text().splitlines():
            name, _, rest = line.partition(":")
            if name in ("MemAvailable", "MemTotal"):
                fields[name] = int(rest.split()[0]) * 1024
    except (OSError, ValueError, IndexError) as error:
        return None, f"{source}: {error}"
    if "MemAvailable" not in fields:
        return None, f"{source} has no MemAvailable line"
    return {"available": fields["MemAvailable"], "total": fields.get("MemTotal")}, None


def load():
    """``((load1, load5, load15), None)``."""
    source = _source("GOV_RESOURCES_LOADAVG", "/proc/loadavg")
    try:
        parts = Path(source).read_text().split()
        values = tuple(float(part) for part in parts[:3])
        if len(values) != 3 or any(value < 0 for value in values):
            raise ValueError("three non-negative load figures are needed")
        return values, None
    except (OSError, ValueError) as error:
        return None, f"{source}: {error}"


def nproc():
    """``(count, None)``: the machine's processors, never the caller's CPU set (a gate read inside a slot still
    judges the whole machine)."""
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


def _history_path(folder: Path) -> Path:
    return folder / CPU_HISTORY


def _read_history(folder: Path) -> list[dict]:
    try:
        data = json.loads(_history_path(folder).read_text(encoding="utf-8"))
        return [item for item in data if isinstance(item, dict) and {"t", "busy", "total"} <= set(item)]
    except (OSError, ValueError, TypeError):
        return []


def _write_history(folder: Path, items: list[dict]) -> None:
    try:
        folder.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile("w", dir=folder, prefix=".cpu-", suffix=".tmp", delete=False) as handle:
            json.dump(items, handle)
        os.replace(handle.name, _history_path(folder))
    except OSError:
        pass  # the history only lengthens the window; without it the window is one second


def busy_cores(folder: Path, processors: int | None):
    """``({"cores": busy cores, "window_s": seconds}, None)`` over the last minute where the history allows."""
    now_counters, why = cpu_counters()
    if why:
        return None, why
    if not processors:
        return None, "the processor count is unknown, so busy cores cannot be counted"
    now = time.time()
    history = [item for item in _read_history(folder) if 0 <= now - item["t"] <= KEEP_S]
    older = [item for item in history if now - item["t"] >= WINDOW_S]
    recent = [item for item in history if SHORT_S <= now - item["t"] < WINDOW_S]
    base = max(older, key=lambda item: item["t"]) if older else (min(recent, key=lambda item: item["t"])
                                                                    if recent else None)
    if base is None:
        time.sleep(SHORT_S)
        later, why = cpu_counters()
        if why:
            return None, why
        base = {"t": now, "busy": now_counters[0], "total": now_counters[1]}
        now, now_counters = time.time(), later
    history.append({"t": now, "busy": now_counters[0], "total": now_counters[1]})
    _write_history(folder, history[-64:])
    busy, total = now_counters[0] - base["busy"], now_counters[1] - base["total"]
    if total <= 0 or busy < 0:
        return None, "the CPU counters did not advance, so busy cores cannot be counted"
    return {"cores": round(processors * busy / total, 2), "window_s": round(now - base["t"], 1)}, None


def disk(place: str):
    """``({"free_bytes", "free_inodes", "path"}, None)`` of the file system holding ``place``."""
    try:
        stat = os.statvfs(place)
    except OSError as error:
        return None, f"{place}: {error}"
    return {"path": place, "free_bytes": stat.f_bavail * stat.f_frsize, "free_inodes": stat.f_favail}, None


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


def tree(table: dict[int, dict], pid: int, stop: set[int] = frozenset()) -> list[int]:
    """``pid`` and every descendant, a subtree rooted at a pid in ``stop`` left out (another session's own)."""
    kids, out, todo = children(table), [], [pid]
    while todo:
        current = todo.pop()
        if current in table and current not in out:
            out.append(current)
            todo += [child for child in kids.get(current, []) if child not in stop]
    return out


def alive(pid: int) -> bool:
    """Whether ``pid`` runs; on a planted process table, whether the table holds it (no real process is asked)."""
    if proc_root() != Path("/proc"):
        return (proc_root() / str(pid)).is_dir()
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:  # another user's process: alive
        pass
    except OSError:
        return False
    return True


def listener(port: int) -> int | None:
    """The eldest pid listening on TCP ``port`` (its children may share the socket), or None."""
    root, sockets = proc_root(), set()
    for table in ("net/tcp", "net/tcp6"):
        try:
            rows = (root / table).read_text().splitlines()[1:]
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
    holders, table = set(), processes()
    for pid in table:
        try:
            if any(os.readlink(fd) in sockets for fd in (root / str(pid) / "fd").iterdir()):
                holders.add(pid)
        except OSError:
            continue
    eldest = [pid for pid in holders if table[pid]["ppid"] not in holders]
    return min(eldest) if eldest else None


def gpu(smi: str | None = None):
    """``({"gpus": [{"index", "used_bytes", "total_bytes", "free_bytes", "utilization"}], "holders": [...]}, None)``
    from ``nvidia-smi``; ``(None, why)`` where there is no ``nvidia-smi``, no GPU, or its answer cannot be read.
    The holders (``{"pid", "used_bytes", "kind"}``: ``embedder``, ``reranker`` or ``other``) are read in the same
    check; holders that cannot be read are named, never an error."""
    program = smi or os.environ.get("GOV_RESOURCES_NVIDIA_SMI") or shutil.which("nvidia-smi")
    if not program or not os.path.exists(program):
        return None, "no nvidia-smi on this machine"
    query = [program, "--query-gpu=index,memory.used,memory.total,utilization.gpu", "--format=csv,noheader,nounits"]
    try:
        answer = subprocess.run(query, capture_output=True, text=True, timeout=SMI_TIMEOUT_S)
    except (OSError, subprocess.SubprocessError) as error:
        return None, f"nvidia-smi cannot be run: {error}"
    if answer.returncode != 0:
        return None, f"nvidia-smi exit {answer.returncode}: {' '.join((answer.stderr or answer.stdout).split())[:160]}"
    gpus = []
    for line in answer.stdout.splitlines():
        if not line.strip():
            continue
        try:
            index, used, total, util = (part.strip() for part in line.split(","))
            used_b, total_b = int(float(used)) * 1024 ** 2, int(float(total)) * 1024 ** 2
            gpus.append({"index": int(index), "used_bytes": used_b, "total_bytes": total_b,
                         "free_bytes": max(0, total_b - used_b),
                         "utilization": None if util in ("[N/A]", "N/A") else float(util)})
        except ValueError:
            return None, f"nvidia-smi: an unreadable line {line[:80]!r}"
    if not gpus:
        return None, "nvidia-smi names no GPU"
    holders, holders_why = _holders(program)
    return {"gpus": gpus, "holders": holders, "holders_why": holders_why}, None


def _kind(cmdline: str) -> str:
    low = cmdline.lower()
    if "rerank" in low:
        return "reranker"
    if "ollama" in low or "embed" in low:
        return "embedder"
    return "other"


def _holders(program: str):
    query = [program, "--query-compute-apps=pid,used_memory", "--format=csv,noheader,nounits"]
    try:
        answer = subprocess.run(query, capture_output=True, text=True, timeout=SMI_TIMEOUT_S)
    except (OSError, subprocess.SubprocessError) as error:
        return [], f"the GPU's holders cannot be read: {error}"
    if answer.returncode != 0:
        return [], f"the GPU's holders cannot be read (nvidia-smi exit {answer.returncode})"
    holders, root = [], proc_root()
    for line in answer.stdout.splitlines():
        parts = [part.strip() for part in line.split(",")]
        if len(parts) != 2 or not parts[0].isdigit():
            if line.strip():
                return holders, f"the GPU's holders: an unreadable line {line[:80]!r}"
            continue
        try:
            cmdline = (root / parts[0] / "cmdline").read_bytes().replace(b"\0", b" ").decode("utf-8", "replace")
        except OSError:
            cmdline = ""  # a pid of the host, or ended: other
        try:
            used = int(float(parts[1])) * 1024 ** 2
        except ValueError:
            used = None
        holders.append({"pid": int(parts[0]), "used_bytes": used, "kind": _kind(cmdline)})
    return holders, None

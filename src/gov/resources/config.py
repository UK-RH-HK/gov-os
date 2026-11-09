"""The resource gate's one configuration file (W2-20 S8; DEC-947 item 3, DEC-950 item 2, P-3, P-7).

``~/.gov-os/machine/gate.json`` holds every value the gate uses. Each value is an object with its ``value``, its
``date`` (``YYYY-MM-DD``) and its ``source`` (the decision or measure it comes from)::

    {"floor_bytes": {"value": 3221225472, "date": "2026-10-29", "source": "DEC-947 item 5"}, ...}

The embedding servers' section (``embedding_servers``, read by ``gov.retrieval.ollama`` for their starts, W2-123)
keeps its own shape: one object per server holding ``host``, ``cpus`` and ``nice`` (and the query server's
``device``), each server dated and sourced by its own ``date`` and ``source`` keys.

Nothing is defaulted: a value missing or malformed is a fault, and every fault shuts the gate, naming it. A measured
figure (the verification peak, the working size, the rebuild peak) dated more than seven days ago is named as due for
re-measure; it still counts. ``template()`` is this machine's file from the decisions (``gov resources
--init-config``), written only where no file is.
"""

from __future__ import annotations

import datetime
import json
import os
import tempfile
from pathlib import Path

FILE = "gate.json"
SERVERS_KEY = "embedding_servers"
SERVERS = ("shared", "query")
DEVICES = ("gpu", "cpu")
MEASURED = ("verification_peak_bytes", "working_size_bytes", "rebuild_peak_bytes")
DUE_AFTER_DAYS = 7
GIB = 1024 ** 3


def machine_dir() -> Path:
    """The machine-wide folder: ``~/.gov-os/machine`` (HOME's, so every repository on the machine shares it)."""
    return Path(os.environ.get("HOME") or Path.home()) / ".gov-os" / "machine"


def path() -> Path:
    return machine_dir() / FILE


def _int(low: int = 0):
    def check(value):
        if isinstance(value, bool) or not isinstance(value, int) or value < low:
            return f"an integer of at least {low} is needed"
        return None
    return check


def _fraction(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not 0 <= value < 1:
        return "a number from 0 up to (not including) 1 is needed, e.g. 0.1 for 10 %"
    return None


def _abs_path(value):
    if not isinstance(value, str) or not os.path.isabs(value):
        return "an absolute path is needed"
    return None


def _shares(value):
    """The GPU shares, in priority order: a list of ``{"kind": <name>, "bytes": <int>}``, each kind once."""
    if not isinstance(value, list) or not value:
        return "a non-empty list of {\"kind\": <name>, \"bytes\": <integer>} in priority order is needed"
    seen = set()
    for item in value:
        if (not isinstance(item, dict) or set(item) != {"kind", "bytes"} or not isinstance(item["kind"], str)
                or not item["kind"] or _int(0)(item["bytes"]) or item["kind"] in seen):
            return "each share is {\"kind\": <name>, \"bytes\": <integer>}, each kind once"
        seen.add(item["kind"])
    return None


# Every value the gate's opening uses (S8's list, the slots of S7 and the rebuild peak of P-7), with its check.
VALUES = {
    "floor_bytes": _int(0),                 # S6: the memory floor
    "working_size_bytes": _int(1),          # S6, S9: a running session's working size (measured)
    "verification_peak_bytes": _int(1),     # S9: a verification run's peak (measured)
    "rebuild_peak_bytes": _int(1),          # S7, S9, P-7: a rebuild's peak (measured)
    "disk_floor_bytes": _int(0),            # S4: 100 GiB
    "inode_floor": _int(0),                 # S4: 10,000,000
    "verification_lock": _abs_path,         # S9: the lock a verification run holds
    "gpu_margin": _fraction,                # S10: 10 %
    "heavy_slots": _int(1),                 # S7: the machine-wide heavy-job slots
    "trip_floor_bytes": _int(0),            # S11: the out-of-memory trip-wire's lower floor ("in the file")
}
# Values the file may set, each dated and sourced when set, malformed a fault like any other. Absent: the GPU shares
# are DEC-1032's default (S14 states it); the disk is the one holding HOME (the shared disk, S4). The embedding
# servers' section (S12, "the file holds each one's") is required too, below.
OPTIONAL = {
    "gpu_shares": _shares,                  # S14: the embedder first, then one reranker, then the rest
    "disk_path": _abs_path,                 # S4: a path on the shared disk
    "thread_budget": _int(1),               # S15: the slot's thread budget, when the file sets it
}


def default_shares() -> list[dict]:
    """DEC-1032 item 1's GPU budget: the embedder first, the shared reranker second, at least 2 GB headroom."""
    return [{"kind": "embedder", "bytes": int(3.5 * GIB)}, {"kind": "reranker", "bytes": int(3.5 * GIB)},
            {"kind": "headroom", "bytes": 2 * GIB}]


def _date(value) -> datetime.date | None:
    if not isinstance(value, str):
        return None
    try:
        return datetime.date.fromisoformat(value)
    except ValueError:
        return None


def _dated(entry, key: str) -> str | None:
    """Why ``entry`` is not dated and sourced, or None."""
    if _date(entry.get("date")) is None:
        return f"{key}: no date (a YYYY-MM-DD 'date' is needed)"
    if not isinstance(entry.get("source"), str) or not entry["source"].strip():
        return f"{key}: no source (a non-empty 'source' is needed)"
    return None


def _server_faults(section) -> list[str]:
    if not isinstance(section, dict):
        return [f"{SERVERS_KEY}: missing or not an object"]
    faults = []
    for server in SERVERS:
        key, entry = f"{SERVERS_KEY}.{server}", section.get(server)
        if not isinstance(entry, dict):
            faults.append(f"{key}: missing or not an object")
            continue
        if not isinstance(entry.get("host"), str) or not entry["host"].rsplit(":", 1)[-1].isdigit():
            faults.append(f"{key}.host: a host:port is needed")
        if not isinstance(entry.get("cpus"), str) or parse_cpus(entry["cpus"]) is None:
            faults.append(f"{key}.cpus: a CPU list such as \"8-11\" is needed")
        nice = entry.get("nice")
        if isinstance(nice, bool) or not isinstance(nice, int) or not 0 <= nice <= 19:
            faults.append(f"{key}.nice: an integer from 0 to 19 is needed")
        if "device" in entry and entry["device"] not in DEVICES:
            faults.append(f"{key}.device: one of {', '.join(DEVICES)} is needed")
        undated = _dated(entry, key)
        if undated:
            faults.append(undated)
    return faults


def load(today: datetime.date | None = None) -> dict:
    """``{"path", "values", "dates", "sources", "faults", "due"}``: the values (bare), their dates and sources, every
    fault (a value missing or malformed, the file missing or unreadable) and the measured figures due for re-measure.
    Never raises: a fault is named, and the gate shuts on it."""
    today = today or datetime.date.today()
    file = path()
    out = {"path": str(file), "values": {}, "dates": {}, "sources": {}, "faults": [], "due": []}
    try:
        data = json.loads(file.read_text(encoding="utf-8"))
    except FileNotFoundError:
        out["faults"].append(f"{file} is missing (gov resources --init-config writes this machine's)")
        return out
    except (OSError, ValueError, UnicodeDecodeError) as error:
        out["faults"].append(f"{file} cannot be read as JSON: {error}")
        return out
    if not isinstance(data, dict):
        out["faults"].append(f"{file} is not a JSON object")
        return out
    for key, check in {**VALUES, **OPTIONAL}.items():
        entry = data.get(key)
        if entry is None and key in OPTIONAL:
            continue
        if not isinstance(entry, dict) or "value" not in entry:
            out["faults"].append(f"{key}: missing (an object with its value, date and source is needed)")
            continue
        why = check(entry["value"]) or _dated(entry, key)
        if why:
            out["faults"].append(why if why.startswith(key) else f"{key}: {why}")
            continue
        out["values"][key], out["dates"][key], out["sources"][key] = entry["value"], entry["date"], entry["source"]
        if key in MEASURED and (today - _date(entry["date"])).days > DUE_AFTER_DAYS:
            out["due"].append(f"{key} measured {entry['date']}, more than {DUE_AFTER_DAYS} days ago: due for re-measure")
    values = out["values"]
    if "trip_floor_bytes" in values and "floor_bytes" in values and values["trip_floor_bytes"] >= values["floor_bytes"]:
        out["faults"].append("trip_floor_bytes: must be below floor_bytes")
        del values["trip_floor_bytes"]
    if "gpu_shares" not in values and "gpu_shares" not in data:
        values["gpu_shares"] = default_shares()
        out["sources"]["gpu_shares"] = "default: DEC-1032 item 1"
    if "disk_path" not in values and "disk_path" not in data:
        values["disk_path"] = os.environ.get("HOME") or str(Path.home())
        out["sources"]["disk_path"] = "default: the disk holding HOME"
    servers = data.get(SERVERS_KEY)
    faults = _server_faults(servers)
    out["faults"] += faults
    if not faults:
        values[SERVERS_KEY] = servers
    return out


def parse_cpus(text: str) -> set[int] | None:
    """The CPUs a CPU list (``"0-5,8"``) names, or None when it cannot be parsed."""
    cpus: set[int] = set()
    for part in str(text).split(","):
        low, _, high = part.strip().partition("-")
        if not low.isdigit() or (high and not high.isdigit()) or int(high or low) < int(low):
            return None
        cpus.update(range(int(low), int(high or low) + 1))
    return cpus or None


def cpu_list(cpus) -> str:
    """``{0, 1, 2, 5}`` as ``"0-2,5"``."""
    ranges: list[list[int]] = []
    for cpu in sorted(cpus):
        if ranges and cpu == ranges[-1][1] + 1:
            ranges[-1][1] = cpu
        else:
            ranges.append([cpu, cpu])
    return ",".join(str(a) if a == b else f"{a}-{b}" for a, b in ranges)


def _entry(value, date: str, source: str) -> dict:
    return {"value": value, "date": date, "source": source}


def template(cpus: list[int] | None = None, home: str | None = None) -> dict:
    """This machine's configuration from the decisions (P-3): every value dated and sourced.

    The embedding servers' CPU sets are the decided ones (the shared server on 12-19, the query server on 8-11) where
    the machine has those CPUs; otherwise derived from the machine's own CPUs (the highest 8 and the 4 below them,
    DEC-1037 (4)). ``rebuild_peak_bytes`` has no measure yet: it is the verification peak, dated with DEC-1001 (d), so
    the reading names it due for re-measure at once (P-7)."""
    cpus = sorted(cpus if cpus is not None else os.sched_getaffinity(0))
    home = home or os.environ.get("HOME") or str(Path.home())
    decided = {"shared": set(range(12, 20)), "query": set(range(8, 12))}
    if decided["shared"] | decided["query"] <= set(cpus):
        shared, query = decided["shared"], decided["query"]
        cpu_source = "ACT-OLLAMA-CAP-1 (shared 12-19, nice 10), ACT-QUERY-CPUS-1 (query 8-11, nice 0)"
    else:
        shared, query = set(cpus[-8:]), set(cpus[-12:-8] or cpus[-8:])
        cpu_source = "derived from this machine's CPUs (DEC-1037 (4)): the highest 8, and the 4 below them"
    return {
        "floor_bytes": _entry(3 * GIB, "2026-10-29", "DEC-947 item 5: the floor 3 GiB"),
        "trip_floor_bytes": _entry(2 * GIB, "2026-10-29", "DEC-947 item 5: the trip-wire below 2 GiB available"),
        "working_size_bytes": _entry(2140236 * 1024, "2026-10-29",
                                     "DEC-947 item 2: a lead's working size outside verification, 2,140,236 kB"),
        "verification_peak_bytes": _entry(7404492 * 1024, "2026-10-29",
                                          "DEC-947 item 1: a verification run's peak, 7,404,492 kB"),
        "rebuild_peak_bytes": _entry(7404492 * 1024, "2026-11-01",
                                     "DEC-1001 (d), P-7: not yet measured; the verification peak until the re-measure"),
        "disk_path": _entry(home, "2026-10-28", "DEC-898 item 1: the shared disk (HOME's)"),
        "disk_floor_bytes": _entry(100 * GIB, "2026-10-28", "DEC-898 item 1: 100 GiB free"),
        "inode_floor": _entry(10_000_000, "2026-10-28", "DEC-898 item 1: 10,000,000 free inodes"),
        "verification_lock": _entry("/tmp/gov-os-verify.lock", "2026-10-29",
                                    "DEC-947 item 1: the verification lock"),
        "gpu_margin": _entry(0.10, "2026-10-29", "DEC-950 item 2: the declared need plus 10 %"),
        "gpu_shares": _entry([{"kind": "embedder", "bytes": int(3.5 * GIB)},
                              {"kind": "reranker", "bytes": int(3.5 * GIB)},
                              {"kind": "headroom", "bytes": 2 * GIB}], "2026-11-02",
                             "DEC-1032 item 1: the embedder first (about 3.5 GB), the shared reranker second (2.5 to "
                             "3.5 GB), at least 2 GB headroom, nothing else by default"),
        "heavy_slots": _entry(3, "2026-10-31", "DEC-979 item 1 D1: 3 slots (heavy_slots.conf), re-sized at the "
                                               "re-measure"),
        SERVERS_KEY: {
            "shared": {"host": "127.0.0.1:11434", "cpus": cpu_list(shared), "nice": 10, "date": "2026-11-01",
                       "source": cpu_source},
            "query": {"host": "127.0.0.1:11435", "cpus": cpu_list(query), "nice": 0, "device": "gpu",
                      "date": "2026-11-02", "source": cpu_source + "; ACT-QUERY-GPU-2 (the query server on the GPU)"},
        },
    }


def write(data: dict) -> Path:
    """Replace the file whole (a reader never sees half a file)."""
    file = path()
    file.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", dir=file.parent, prefix=".gate-", suffix=".tmp", delete=False,
                                     encoding="utf-8") as handle:
        json.dump(data, handle, indent=2)
        handle.write("\n")
    os.replace(handle.name, file)
    return file


def init() -> dict:
    """``gov resources --init-config``: write this machine's file, never over an existing one (P-3)."""
    from gov.cli.errors import GovError

    file = path()
    if os.path.lexists(file):
        raise GovError("RESOURCE_CONFIG_EXISTS", f"{file} already exists: it is never overwritten", {"config": str(file)})
    written = write(template())
    return {"written": str(written), "config": json.loads(written.read_text(encoding="utf-8"))}


def raw() -> dict:
    """The file as written, for the re-measure's update (which keeps everything else as it is)."""
    return json.loads(path().read_text(encoding="utf-8"))

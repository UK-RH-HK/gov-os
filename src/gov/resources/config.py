"""The resource gate's one configuration file (W2-20 S8; DEC-947 item 3, DEC-950 item 2, P-3, P-7).

``$HOME/.gov-os/machine/gate.json`` holds every value the gate uses. Each value is an object with its ``value``, its
``date`` (``YYYY-MM-DD``) and its ``source`` (the decision or measure it comes from)::

    {"memory_floor_bytes": {"value": 3221225472, "date": "2026-10-29", "source": "DEC-942 item 2"}, ...}

The embedding servers' section (``embedding_servers``, read by ``gov.retrieval.ollama`` for their starts, W2-123)
keeps its own shape: ``shared`` and ``query``, each with ``cpus`` and ``nice`` (and ``parallel``, ``probe_*``), the
query server also ``device`` (``gpu`` or ``cpu``).

Nothing is defaulted: a value missing or malformed is a fault naming its key (or the file, when it is missing or not
JSON), and every fault shuts the gate. A measured figure (the verification peak, the working size, the rebuild peak,
P-7) dated more than seven days ago is named as due for re-measure; it still counts. ``template()`` is this
machine's file from the decisions (``gov resources --init-config``), written only where no file is.
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


def _env(env=None):
    return os.environ if env is None else env


def machine_dir(env=None) -> Path:
    """The machine-wide folder: ``$HOME/.gov-os/machine`` (so every repository on the machine shares it)."""
    return Path(_env(env).get("HOME") or Path.home()) / ".gov-os" / "machine"


def path(env=None) -> Path:
    return machine_dir(env) / FILE


def _int(low: int = 0):
    def check(value):
        if isinstance(value, bool) or not isinstance(value, int) or value < low:
            return f"an integer of at least {low} is needed"
        return None
    return check


def _number(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0 or value != value:
        return "a number of at least 0 is needed, e.g. 0.1 for 10 %"
    return None


def _text_path(value):
    if not isinstance(value, str) or not value.strip():
        return "a path is needed"
    return None


def _shares(value):
    """The GPU shares by kind: ``{"embedder_mib": int, "reranker_mib": int}``."""
    if (not isinstance(value, dict) or set(value) != {"embedder_mib", "reranker_mib"}
            or any(_int(0)(item) for item in value.values())):
        return "{\"embedder_mib\": <integer>, \"reranker_mib\": <integer>} is needed"
    return None


# Every value the gate uses, with its check (S4, S6, S7, S8, S9, S10, S11, S14, P-7).
VALUES = {
    "memory_floor_bytes": _int(0),          # S6: the memory floor
    "verification_peak_bytes": _int(0),     # S9: a verification run's peak (measured)
    "working_size_bytes": _int(0),          # S6, S9: a session's working size (measured)
    "rebuild_peak_bytes": _int(0),          # S7, S9, P-7: a rebuild's peak (measured)
    "disk_floor_bytes": _int(0),            # S4: 100 GiB
    "inode_floor": _int(0),                 # S4: 10,000,000
    "verification_lock": _text_path,        # S9: the lock a verification run holds
    "gpu_margin": _number,                  # S10: 0.10
    "oom_floor_bytes": _int(0),             # S11: the out-of-memory trip-wire's floor
    "heavy_slots": _int(1),                 # S7: the machine-wide heavy-job slots
    "gpu_shares": _shares,                  # S14: the GPU shares by kind
}
OPTIONAL = {
    "thread_budget": _int(1),               # S15: the slot's thread budget, when the file sets it
}


def _date(value) -> datetime.date | None:
    if not isinstance(value, str) or len(value) != 10:
        return None
    try:
        return datetime.date.fromisoformat(value)
    except ValueError:
        return None


def _fault(key: str, reading, why: str) -> dict:
    return {"key": key, "reading": reading, "why": f"{key}: {why}"}


def _server_faults(section) -> list[dict]:
    if not isinstance(section, dict):
        return [_fault(SERVERS_KEY, section, "missing or not an object (shared and query, each cpus and nice)")]
    faults = []
    for server in SERVERS:
        key, entry = f"{SERVERS_KEY}.{server}", section.get(server)
        if not isinstance(entry, dict):
            faults.append(_fault(key, entry, "missing or not an object"))
            continue
        if "cpus" in entry and (not isinstance(entry["cpus"], str) or parse_cpus(entry["cpus"]) is None):
            faults.append(_fault(f"{key}.cpus", entry["cpus"], "a CPU list such as \"8-11\" is needed"))
        if "nice" in entry:
            nice = entry["nice"]
            if isinstance(nice, bool) or not isinstance(nice, int) or not 0 <= nice <= 19:
                faults.append(_fault(f"{key}.nice", nice, "an integer from 0 to 19 is needed"))
        if server == "query" and "device" in entry and entry["device"] not in DEVICES:
            faults.append(_fault(f"{key}.device", entry["device"], f"one of {', '.join(DEVICES)} is needed"))
    return faults


def load(env=None, today: datetime.date | None = None) -> dict:
    """``{"path", "values", "dates", "sources", "faults", "due"}``: the values (bare), their dates and sources, every
    fault (``{"key", "reading", "why"}``: a value missing or malformed, the file missing or not JSON) and the
    measured keys due for re-measure. Never raises: a fault is named, and the gate shuts on it."""
    today = today or datetime.date.today()
    file = path(env)
    out = {"path": str(file), "values": {}, "dates": {}, "sources": {}, "faults": [], "due": []}
    try:
        data = json.loads(file.read_text(encoding="utf-8"))
    except FileNotFoundError:
        out["faults"].append({"key": FILE, "reading": None,
                              "why": f"{FILE}: {file} is missing (gov resources --init-config writes this machine's)"})
        return out
    except (OSError, ValueError, UnicodeDecodeError) as error:
        out["faults"].append({"key": FILE, "reading": None, "why": f"{FILE}: {file} cannot be read as JSON: {error}"})
        return out
    if not isinstance(data, dict):
        out["faults"].append({"key": FILE, "reading": None, "why": f"{FILE}: {file} is not a JSON object"})
        return out
    for key, check in {**VALUES, **OPTIONAL}.items():
        if key not in data and key in OPTIONAL:
            continue
        entry = data.get(key)
        if not isinstance(entry, dict) or "value" not in entry:
            reading = entry if key in data else None
            why = ("missing (an object with its value, date and source is needed)" if key not in data else
                   "malformed: an object {\"value\", \"date\", \"source\"} is needed")
            out["faults"].append(_fault(key, reading, why))
            continue
        why = check(entry["value"])
        if why is None and _date(entry.get("date")) is None:
            why = f"no date (a YYYY-MM-DD 'date' is needed, not {entry.get('date')!r})"
        if why is None and (not isinstance(entry.get("source"), str) or not entry["source"].strip()):
            why = "no source (a non-empty 'source' is needed)"
        if why:
            out["faults"].append(_fault(key, entry.get("value"), why))
            continue
        out["values"][key], out["dates"][key], out["sources"][key] = entry["value"], entry["date"], entry["source"]
        if key in MEASURED and (today - _date(entry["date"])).days > DUE_AFTER_DAYS:
            out["due"].append(key)
    servers = data.get(SERVERS_KEY)
    faults = _server_faults(servers)
    out["faults"] += faults
    if not faults:
        out["values"][SERVERS_KEY] = servers
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


def template(cpus: list[int] | None = None) -> dict:
    """This machine's configuration from the decisions (P-3): every value dated and sourced.

    The embedding servers' CPU sets are the decided ones (the shared server on 12-19, the query server on 8-11) where
    the machine has those CPUs; otherwise derived from the machine's own CPUs (the highest 8 and the 4 below them,
    DEC-1037 (4)). ``rebuild_peak_bytes`` has no measure yet: it is the verification peak, dated with DEC-1001 (d), so
    the reading names it due for re-measure at once (P-7)."""
    cpus = sorted(cpus if cpus is not None else os.sched_getaffinity(0))
    decided = {"shared": set(range(12, 20)), "query": set(range(8, 12))}
    if decided["shared"] | decided["query"] <= set(cpus):
        shared, query = decided["shared"], decided["query"]
        cpu_source = "ACT-OLLAMA-CAP-1 (shared 12-19, nice 10), ACT-QUERY-CPUS-1 (query 8-11, nice 0)"
    else:
        shared, query = set(cpus[-8:]), set(cpus[-12:-8] or cpus[-8:])
        cpu_source = "derived from this machine's CPUs (DEC-1037 (4)): the highest 8, and the 4 below them"
    return {
        "memory_floor_bytes": _entry(3 * GIB, "2026-10-29", "DEC-942 item 2: the memory floor 3 GiB"),
        "oom_floor_bytes": _entry(2 * GIB, "2026-10-29", "DEC-947 item 5: the trip-wire below 2 GiB available"),
        "working_size_bytes": _entry(805_306_368, "2026-11-12",
                                     "DEC-1149 (1), (2): 0.75 GiB per live session, from the lead-memory ledger "
                                     "(ACT-P95-1)"),
        "verification_peak_bytes": _entry(7404492 * 1024, "2026-10-29",
                                          "DEC-947 item 1: a verification run's peak, 7,404,492 kB"),
        "rebuild_peak_bytes": _entry(7404492 * 1024, "2026-11-01",
                                     "DEC-1001 (d), P-7: not yet measured; the verification peak until the re-measure"),
        "disk_floor_bytes": _entry(100 * GIB, "2026-10-28", "DEC-898 item 1: 100 GiB free on the shared disk"),
        "inode_floor": _entry(10_000_000, "2026-10-28", "DEC-898 item 1: 10,000,000 free inodes"),
        "verification_lock": _entry("/tmp/gov-os-verify.lock", "2026-10-29",
                                    "DEC-947 item 1: the verification lock"),
        "gpu_margin": _entry(0.10, "2026-10-29", "DEC-950 item 2: the declared need plus 10 %"),
        "gpu_shares": _entry({"embedder_mib": 3584, "reranker_mib": 3584}, "2026-11-02",
                             "DEC-1032 item 1: the embedder first (about 3.5 GB), then the shared reranker (2.5 to "
                             "3.5 GB)"),
        "heavy_slots": _entry(3, "2026-10-31", "DEC-979 item 1 D1: 3 slots (heavy_slots.conf), re-sized at the "
                                               "re-measure"),
        SERVERS_KEY: {
            "shared": {"cpus": cpu_list(shared), "nice": 10},
            "query": {"cpus": cpu_list(query), "nice": 0, "device": "gpu"},
            "date": "2026-11-02",
            "source": cpu_source + "; ACT-QUERY-GPU-2 (the query server on the GPU)",
        },
    }


# The GPU backstop's three values (W2-157, Interface L2): read and checked only by ``gov resources --backstop``. They are
# in neither VALUES nor OPTIONAL nor template(), so a file without them (or with a malformed one) opens the gate as before
# and --init-config writes W2-20's frozen key set. This machine's entries are held here for the operator's step (the
# evidence): never a fallback. ``$HOME`` stands for this machine's home; ``backstop_entries()`` gives it resolved.
BACKSTOP_KEYS = ("gpu_backstop_limit_mib", "gpu_backstop_every_s", "gpu_backstop_embedders")
BACKSTOP_ENTRIES = {
    "gpu_backstop_limit_mib": _entry(15872, "2026-11-04", "DEC-1067 (GPU safety), DEC-1068 (4): 15.5 GiB, 15,872 MiB"),
    "gpu_backstop_every_s": _entry(5, "2026-11-04", "DEC-1067 (GPU safety), DEC-1068 (4): the poll every 5 seconds"),
    "gpu_backstop_embedders": _entry(
        [{"port": 11434, "log": "$HOME/.ollama/serve-11434.log"}, {"port": 11435, "log": "$HOME/.ollama/serve-11435.log"}],
        "2026-11-04", "DEC-1067 (GPU safety), DEC-1068 (4), DEC-1030: the two shared embedding servers and their logs"),
}


def backstop_entries(env=None) -> dict:
    """This machine's three entries with ``$HOME`` resolved, as the operator adds them to ``gate.json``."""
    home = str(Path(_env(env).get("HOME") or Path.home()))
    entries = json.loads(json.dumps(BACKSTOP_ENTRIES).replace("$HOME", home))
    return entries


def _embedders(value):
    if not isinstance(value, list):
        return "a list of {\"port\": <1-65535>, \"log\": <absolute path>} is needed (possibly empty)"
    for item in value:
        if (not isinstance(item, dict) or set(item) != {"port", "log"} or _int(1)(item["port"]) or item["port"] > 65535
                or not isinstance(item["log"], str) or not os.path.isabs(item["log"])):
            return f"{item!r}: {{\"port\": <1-65535>, \"log\": <absolute path>}} is needed"
    return None


def _every(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not value > 0 or value == float("inf"):
        return "a number above 0 is needed"
    return None


BACKSTOP_CHECKS = {"gpu_backstop_limit_mib": _int(1), "gpu_backstop_every_s": _every, "gpu_backstop_embedders": _embedders}


def backstop_values(env=None) -> tuple[dict, list[dict]]:
    """``({"limit_mib", "every_s", "embedders"}, faults)``: the backstop's three values from the gate's file, each with its
    date and source checked; a fault (``{"key", "reading", "why"}``) names each key missing or malformed, or ``gate.json``
    when the file is missing or not JSON. Nothing is defaulted; the values are empty when any fault is."""
    file = path(env)
    try:
        data = json.loads(file.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {}, [{"key": FILE, "reading": None, "why": f"{FILE}: {file} is missing"}]
    except (OSError, ValueError, UnicodeDecodeError) as error:
        return {}, [{"key": FILE, "reading": None, "why": f"{FILE}: {file} cannot be read as JSON: {error}"}]
    if not isinstance(data, dict):
        return {}, [{"key": FILE, "reading": None, "why": f"{FILE}: {file} is not a JSON object"}]
    found, faults = {}, []
    for key, check in BACKSTOP_CHECKS.items():
        entry = data.get(key)
        if not isinstance(entry, dict) or "value" not in entry:
            faults.append(_fault(key, entry, "missing (an object with its value, date and source is needed)"
                                 if key not in data else "malformed: an object {\"value\", \"date\", \"source\"} is needed"))
            continue
        why = check(entry["value"])
        if why is None and _date(entry.get("date")) is None:
            why = f"no date (a YYYY-MM-DD 'date' is needed, not {entry.get('date')!r})"
        if why is None and (not isinstance(entry.get("source"), str) or not entry["source"].strip()):
            why = "no source (a non-empty 'source' is needed)"
        if why:
            faults.append(_fault(key, entry.get("value"), why))
        else:
            found[key] = entry["value"]
    if faults:
        return {}, faults
    return {"limit_mib": found["gpu_backstop_limit_mib"], "every_s": found["gpu_backstop_every_s"],
            "embedders": found["gpu_backstop_embedders"]}, []


def write(data: dict, env=None) -> Path:
    """Replace the file whole (a reader never sees half a file); mode 0600."""
    file = path(env)
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
        raise GovError("RESOURCE_CONFIG_EXISTS", f"{FILE} already exists at {file}: it is never overwritten",
                       {"config": str(file)})
    written = write(template())
    return {"written": str(written), "config": json.loads(written.read_text(encoding="utf-8"))}


def raw() -> dict:
    """The file as written, for the re-measure's update (which keeps everything else as it is)."""
    return json.loads(path().read_text(encoding="utf-8"))

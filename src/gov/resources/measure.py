"""The re-measure (W2-20 S9; DEC-947 items 2 and 3, DEC-950 item 2, P-5, P-7).

``sample()`` (``gov resources --sample``) takes one sample of every live session's process-tree memory (other
sessions' subtrees left out), noting whether a verification run holds the configured ``verification_lock``, and one
of every heavy-job slot holder's process tree with its ``kind`` (P-5 (a)); it returns them as ``samples``
(``[{pid, tree_memory_bytes, verification}]``, a slot holder's also ``kind``) and appends them, as one line, to
``~/.gov-os/machine/samples.jsonl``.

``remeasure()`` (``gov resources --remeasure``) writes three figures into the configuration file, each dated today
with a source naming the samples, and returns ``{"old": {key: value}, "new": {key: value}}`` (and the entries
written, ``written``):

- ``verification_peak_bytes``: the largest session sample;
- ``working_size_bytes``: the largest session sample taken while no verification run held the lock;
- ``rebuild_peak_bytes``: the largest sample of a slot holder of kind ``rebuild`` (a rebuild holds no verification
  lock, P-5). A slot holder is no session: its sample is never a working size.

A figure with no sample to measure it is kept as it is.
"""

from __future__ import annotations

import datetime
import fcntl
import json
import os
from pathlib import Path

from gov.resources import config as configuration
from gov.resources import machine, registry, slots

SAMPLES = "samples.jsonl"


def samples_path() -> Path:
    return configuration.machine_dir() / SAMPLES


def lock_held(path: str) -> bool | None:
    """Whether a process holds the advisory lock at ``path``; False where no such file is; None where it cannot be
    told."""
    try:
        fd = os.open(path, os.O_RDONLY | os.O_CLOEXEC)
    except FileNotFoundError:
        return False
    except OSError:
        return None
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        fcntl.flock(fd, fcntl.LOCK_UN)
        return False
    except BlockingIOError:
        return True
    except OSError:
        return None
    finally:
        os.close(fd)


def sample() -> dict:
    """Take and record one sample of every live session and every slot holder."""
    from gov.cli.errors import GovError

    conf = configuration.load()
    if "verification_lock" not in conf["values"]:
        named = "; ".join(f["why"] for f in conf["faults"] if f["key"] in ("verification_lock", configuration.FILE))
        raise GovError("RESOURCE_CONFIG_INVALID", f"the sample needs the configured verification_lock: {named}",
                       {"faults": conf["faults"]})
    live, _, why = registry.sessions()
    if why:
        raise GovError("RESOURCE_REGISTRY_UNREADABLE", f"the registry cannot be read: {why}")
    table = machine.processes()
    memory = registry.live_memory(live, table)
    verification = lock_held(conf["values"]["verification_lock"])
    taken = [{"pid": e["pid"], "tree_memory_bytes": memory[e["pid"]], "verification": verification,
              "ticket": e.get("ticket"), "role": e.get("role")} for e in live]
    jobs, _ = slots.holders()
    taken += [{"pid": j["pid"], "tree_memory_bytes": machine.tree_memory(table, j["pid"]),
               "verification": verification, "kind": j.get("kind"), "slot": j.get("slot")}
              for j in jobs if j["pid"] in table]
    stamp = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
    path = samples_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as out:
        out.write(json.dumps({"time": stamp, "samples": taken}) + "\n")
    return {"time": stamp, "samples": taken, "file": str(path)}


def figures(lines: list[dict]) -> dict:
    """The three figures from the recorded samples: ``{key: (bytes or None, count of samples behind it)}``."""
    every, outside, rebuilds = [], [], []
    for line in lines:
        for item in line.get("samples", []) if isinstance(line, dict) else []:
            size = item.get("tree_memory_bytes") if isinstance(item, dict) else None
            if isinstance(size, bool) or not isinstance(size, int):
                continue
            if "kind" in item:  # a slot holder: no session
                if item["kind"] == "rebuild":
                    rebuilds.append(size)
                continue
            every.append(size)
            if item.get("verification") is False:
                outside.append(size)
    return {"verification_peak_bytes": (max(every) if every else None, len(every)),
            "working_size_bytes": (max(outside) if outside else None, len(outside)),
            "rebuild_peak_bytes": (max(rebuilds) if rebuilds else None, len(rebuilds))}


def remeasure(today: datetime.date | None = None) -> dict:
    """Write the measured figures, dated today, into the configuration file; old and new side by side."""
    from gov.cli.errors import GovError

    today = today or datetime.date.today()
    try:
        lines = [json.loads(line) for line in samples_path().read_text(encoding="utf-8").splitlines() if line.strip()]
    except FileNotFoundError:
        lines = []
    except (OSError, ValueError) as error:
        raise GovError("RESOURCE_SAMPLES_UNREADABLE", f"{samples_path()} cannot be read: {error}") from None
    try:
        data = configuration.raw()
        if not isinstance(data, dict):
            raise ValueError("not a JSON object")
    except (OSError, ValueError) as error:
        raise GovError("RESOURCE_CONFIG_INVALID", f"{configuration.path()} cannot be read: {error}") from None
    span = f"{lines[0].get('time')} to {lines[-1].get('time')}" if lines else "none"
    old, new, entries = {}, {}, {}
    for key, (value, count) in figures(lines).items():
        before = data.get(key)
        old[key] = before.get("value") if isinstance(before, dict) else before
        if value is None:  # no sample measures it: kept as it is
            new[key] = old[key]
            continue
        data[key] = entries[key] = {"value": value, "date": today.isoformat(),
                                    "source": f"gov resources --remeasure: the largest of {count} sample(s), {span} "
                                              f"({samples_path()})"}
        new[key] = value
    configuration.write(data)
    return {"config": str(configuration.path()), "samples": len(lines), "old": old, "new": new, "written": entries}

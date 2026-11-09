"""The re-measure (W2-20 S9; DEC-947 items 2 and 3, DEC-950 item 2, P-5, P-7).

``sample()`` (``gov resources --sample``) appends one line to ``~/.gov-os/machine/samples.jsonl``: each live
session's process-tree memory (other sessions' subtrees left out), whether a verification run holds the configured
``verification_lock``, and each heavy-job slot holder's process-tree memory with its kind.

``remeasure()`` (``gov resources --remeasure``) writes three figures into the configuration file, each with today's
date and a source naming the samples, and shows old and new side by side:

- ``verification_peak_bytes``: the largest session sample;
- ``working_size_bytes``: the largest session sample taken while no verification run held the lock;
- ``rebuild_peak_bytes``: the largest sample of a slot holder of kind ``rebuild`` (a rebuild does not hold the
  verification lock, P-5).

A figure with no sample to measure it is kept as it is, and said so.
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
    """Whether another process holds the advisory lock at ``path``; False where no such file is; None where it
    cannot be told."""
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
    """Record one sample; it names the verification lock's state as ``null`` where it cannot be told."""
    from gov.cli.errors import GovError

    conf = configuration.load()
    if "verification_lock" not in conf["values"]:
        raise GovError("RESOURCE_CONFIG_INVALID", "the sample needs the configured verification_lock: "
                       + "; ".join(conf["faults"]), {"faults": conf["faults"]})
    live, _, why = registry.sessions()
    if why:
        raise GovError("RESOURCE_REGISTRY_UNREADABLE", f"the registry cannot be read: {why}")
    table = machine.processes()
    memory = registry.live_memory(live, table)
    jobs, _ = slots.holders()
    record = {
        "time": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "verification": lock_held(conf["values"]["verification_lock"]),
        "sessions": [{"pid": e["pid"], "ticket": e.get("ticket"), "role": e.get("role"),
                      "repository": e.get("repository"), "bytes": memory[e["pid"]]} for e in live],
        "jobs": [{"pid": j["pid"], "kind": j.get("kind"), "tree": j.get("tree"),
                  "bytes": sum(table[p]["rss"] for p in machine.tree(table, j["pid"]))} for j in jobs
                 if j.get("pid") in table],
    }
    path = samples_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as out:
        out.write(json.dumps(record) + "\n")
    return record


def figures(lines: list[dict]) -> dict:
    """The three figures from the samples: ``{name: (bytes or None, count of samples behind it)}``."""
    every, outside, rebuilds = [], [], []
    for line in lines:
        values = [s["bytes"] for s in line.get("sessions", []) if isinstance(s.get("bytes"), int)]
        every += values
        if line.get("verification") is False:
            outside += values
        rebuilds += [j["bytes"] for j in line.get("jobs", []) if j.get("kind") == "rebuild"
                     and isinstance(j.get("bytes"), int)]
    return {"verification_peak_bytes": (max(every) if every else None, len(every)),
            "working_size_bytes": (max(outside) if outside else None, len(outside)),
            "rebuild_peak_bytes": (max(rebuilds) if rebuilds else None, len(rebuilds))}


def remeasure(today: datetime.date | None = None) -> dict:
    """Write the measured figures with the date into the configuration file; old and new side by side."""
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
    except (OSError, ValueError) as error:
        raise GovError("RESOURCE_CONFIG_INVALID", f"{configuration.path()} cannot be read: {error}") from None
    span = f"{lines[0].get('time')} to {lines[-1].get('time')}" if lines else "none"
    changes = {}
    for key, (value, count) in figures(lines).items():
        old = data.get(key) if isinstance(data.get(key), dict) else None
        if value is None:
            changes[key] = {"old": old, "new": None, "kept": "no sample measures it"}
            continue
        new = {"value": value, "date": today.isoformat(),
               "source": f"gov resources --remeasure: the largest of {count} sample(s), {span} ({samples_path()})"}
        data[key] = new
        changes[key] = {"old": old, "new": new}
    configuration.write(data)
    return {"config": str(configuration.path()), "samples": len(lines), "figures": changes}

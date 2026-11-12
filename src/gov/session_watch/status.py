"""The dispatcher's status (``.gov-runtime/dispatch/status.json``), used only when at most 5 minutes old by mtime.

A shut gate, a full machine and running work are read from it; an older or unreadable status is not used and is named.
"""

from __future__ import annotations

import json
from pathlib import Path

from gov.session_watch.state import now

FILE = Path(".gov-runtime") / "dispatch" / "status.json"
MAX_AGE_S = 300


def read(root: Path, notes: list) -> dict | None:
    file = Path(root) / FILE
    try:
        age = now() - file.stat().st_mtime
        data = json.loads(file.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None
    except (OSError, ValueError) as error:
        notes.append(f"dispatcher status unusable ({type(error).__name__})")
        return None
    if not isinstance(data, dict):
        notes.append("dispatcher status unusable (not an object)")
        return None
    if age > MAX_AGE_S:
        notes.append(f"dispatcher status not used (written {int(age)} s ago, over {MAX_AGE_S} s)")
        return None
    return data


def _mapping(value) -> dict:
    return value if isinstance(value, dict) else {}


def legitimate_wait(status: dict | None) -> str | None:
    """Which wait the status shows: the gate shut (the gate or the disk gate) or the machine full; else None."""
    if status is None:
        return None
    gate = _mapping(status.get("gate"))
    if gate.get("open") is False:
        return f"the resource gate is shut ({'; '.join(map(str, gate.get('reasons') or []))[:160] or 'no reason given'})"
    if _mapping(gate.get("disk")).get("open") is False:
        return "the resource gate is shut (the disk gate)"
    if status.get("outcome") == "refused":
        return "the machine is full (the dispatcher refused a start)"
    return None


def running(status: dict | None) -> list:
    """What the status shows running: leads, jobs and starts pending."""
    if status is None:
        return []
    out = [f"dispatcher lead {_mapping(r).get('ticket', '?')}" for r in status.get("running") or []]
    out += [f"dispatcher job {_mapping(j).get('kind', '?')}" for j in status.get("running_jobs") or []]
    out += [f"dispatcher start pending for {_mapping(s).get('ticket', '?')}" for s in status.get("pending_starts") or []]
    return out


def running_tickets(status: dict | None) -> set:
    if status is None:
        return set()
    entries = [*(status.get("running") or []), *(status.get("pending_starts") or [])]
    return {str(_mapping(e).get("ticket")) for e in entries}

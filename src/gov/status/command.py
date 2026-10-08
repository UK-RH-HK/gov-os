"""``gov status`` as a command module (W1-32, CAP-27.a, CAP-28.a). The convention is in ``gov.cli.main``.

Six parts, each read from the module that owns its rule: ``tickets`` (``gov.tasks``: the READY rule and the claim
lock), ``decision_packages`` (the record store), ``readiness`` (``gov.readiness``), ``governance_share``
(``gov.telemetry.counter``), ``pause`` (the guard's reading of the freeze flag and its mirror) and ``doctor``
(``gov doctor``). It only reads: no store is loaded and nothing is cached.

A result is measured or it is refused (DEC-449, DEC-454). A part, a list or an entry that was not read is
``{"read": false, "reason": ...}`` in its place, never an empty list, a zero or "not paused", and ``not_read``
names every such place with its reason. The command itself still succeeds (W1-07 holds it to exit code 0 on a
project without a store): a caller reads ``not_read``, not the exit code, to know whether the answer is whole.
"""

from __future__ import annotations

import os
import stat
import subprocess
from pathlib import Path


def _unread(reason: str) -> dict:
    return {"read": False, "reason": reason}


def _part(read, *args):
    """What ``read`` gives; whatever stopped it is the reason the part was not read, never a default answer."""
    try:
        return read(*args)
    except Exception as error:
        return _unread(f"{type(error).__name__}: {error}")


def _listable(folder: Path) -> None:
    """Raise when ``folder`` is there and cannot be listed: its readers would then answer "none". A project
    without the folder holds none of what it would hold, and that is read."""
    if os.path.lexists(folder):
        os.listdir(folder)


def _store_fault(root: Path) -> str | None:
    """Why the record store cannot answer for ``HEAD``; None when it was loaded from a history that holds it and
    its records and edges, which the READY rule and the packages are read from, answer too."""
    from gov import records
    from gov.store import STORE_REL

    try:
        head = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"], capture_output=True, text=True,
                              check=True).stdout.strip()
        loaded = {commit["commit"] for commit in records.commits(root)}
        records.records(root), records.edges(root)  # the READY rule answers "none ready" for a store without them
    except Exception as error:
        return f"the record store ({STORE_REL}) was not read: {type(error).__name__}: {error}"
    return None if head in loaded else (f"the record store ({STORE_REL}) is older than HEAD ({head[:12]}): what was "
                                        "committed since its last load is not in it")


def _tickets(root: Path, fault: str | None) -> dict:
    from gov import tasks
    from gov.tasks.tickets import TICKETS_REL, frontmatter

    _listable(root / TICKETS_REL)
    ready, held, blocked, claimed = tasks.ready(root), tasks.blocked(root), [], []
    for ticket, reasons in held.items():
        if frontmatter(root / TICKETS_REL / f"{ticket}.md") is None:
            blocked.append({"id": ticket, **_unread(f"{TICKETS_REL}/{ticket}.md cannot be read as a ticket")})
        else:
            blocked.append({"id": ticket, "reasons": reasons})
        if "CLAIMED" in reasons:  # in progress, or locked: the lock alone names a holder (DEC-292)
            claimed.append({"id": ticket, "holder": _part(tasks.holder, root, ticket)})
    stale = _unread(fault) if fault else None  # the READY rule reads the store: without it neither list is its answer
    return {"ready": stale or ready, "blocked": stale or blocked, "claimed": claimed}


def _packages(root: Path, fault: str | None):
    """The open decision packages (PROPOSED, DEC-308), each with the tickets it constrains. A file of ``HEAD`` that
    the store's load could not take as a record (DEC-239) may be one: it is listed by its path, not read. The load
    keeps no list of them, so they are read again from ``HEAD``, which the store holds, by the load's own rule."""
    from gov import records
    from gov.store.loader import _read_records

    if fault:
        return _unread(fault)
    return [{"id": record["id"],
             "tickets": [edge["target"] for edge in records.edges(root, type="CONSTRAINS", source=record["id"])]}
            for record in records.records(root, type="decision-package", status="PROPOSED")] + [
        {"name": entry["path"], **_unread(f"{entry['path']} could not be loaded as a record ({entry['reason']}): "
                                          "it may be an open decision package")}
        for entry in _read_records(root)[2]]


def _readiness(root: Path) -> list:
    """The checker's report of every specification; one it could not judge is not read, with the checker's reason."""
    from gov.cli.errors import GovError
    from gov.readiness import check, check_all
    from gov.readiness.checker import CHANGES_REL

    _listable(root / CHANGES_REL)
    try:
        answers = check_all(root)["specifications"]
    except GovError as error:
        answers = error.details["specifications"]
    entries = []
    for answer in answers:
        if "open" in answer:
            entries.append(answer)
        elif "specification" in answer:
            reason = _part(check, root, answer["specification"])
            entries.append({"specification": answer["specification"],
                            **(reason if reason.get("read") is False else _unread("the checker gave no report"))})
        else:
            entries.append({"change": answer["change"], **_unread("the change holds no specification record")})
    return entries


def _share(root: Path, tickets) -> dict:
    """W1-31's counter, asked for each claimed ticket. No session of a ticket is recorded anywhere (DEC-491), so
    none is named, and the counter's own refusal is the reason."""
    from gov.cli.errors import GovError
    from gov.telemetry.counter import NOT_MEASURED, measure

    if "claimed" not in tickets:
        raise LookupError(f"the claimed tickets were not read ({tickets['reason']}), so the counter was not asked")
    entries = []
    for ticket in [entry["id"] for entry in tickets["claimed"]]:
        try:
            entries.append({"ticket": ticket, "share": measure(root, ticket, [])["governance_share"]})
        except GovError as error:
            entries.append({"ticket": ticket, "share": NOT_MEASURED, "reason": error.message})
    return {"share": NOT_MEASURED, "reason": "no session of a ticket is recorded (DEC-491), so the counter is asked "
            "with none named, ticket by ticket; no figure across tickets exists", "tickets": entries}


def _pause(root: Path) -> dict:
    """What the guard will do: frozen by the marked flag (DEC-402) or by its mirror (DEC-429)."""
    from gov.guard.decide import FREEZE_FLAG, _mirror_frozen, freeze_state

    flag, mirror = freeze_state(str(root)), _mirror_frozen(str(root))
    if flag == "unmarked" and stat.S_ISCHR(os.stat(root / FREEZE_FLAG).st_mode):
        # A session's sandbox puts a device at the path whether or not a flag exists (DEC-402): the flag was not
        # read. The mirror alone can still say paused (DEC-429); it cannot say not paused.
        hidden = _unread(f"{FREEZE_FLAG} is a character device, what a session's sandbox puts at the path whether "
                         "or not a flag exists: the flag was not read")
        return {"paused": True, "flag": hidden, "mirror": True} if mirror else {**hidden, "mirror": False}
    part = {"paused": flag == "frozen" or mirror, "flag": flag, "mirror": mirror}
    if flag == "frozen":  # the marker line is ``FROZEN <who> <when>`` (DEC-404)
        words = _part(lambda: (root / FREEZE_FLAG).read_text(encoding="utf-8", errors="replace").split("\n")[0].split())
        marked = isinstance(words, list) and len(words) == 3
        part["by"], part["since"] = words[1:] if marked else [_unread(f"{FREEZE_FLAG} holds no marker line that "
                                                                      "can be read: the guard holds the tree")] * 2
    return part


def _doctor(root: Path, args, config: dict) -> dict:
    """Doctor's verdict and the state of each of its parts: "unmeasured" is not "pass"."""
    from gov.cli.errors import GovError
    from gov.doctor.command import run as doctor

    try:
        report = doctor(root, args, config)
    except GovError as error:
        if "healthy" not in error.details:
            raise
        report = error.details
    return {"healthy": report["healthy"],
            "parts": {name: section["status"] for name, section in report.items() if name != "healthy"}}


def _unread_in(value, where: str = "") -> list[str]:
    """``<where>: <reason>`` of everything in the answer that says it was not read."""
    if isinstance(value, dict) and value.get("read") is False:
        return [f"{where}: {value['reason']}"]
    items = value.items() if isinstance(value, dict) else enumerate(value) if isinstance(value, list) else ()
    return [found for key, item in items for found in _unread_in(item, f"{where}.{key}" if where else str(key))]


def run(root: Path, args, config: dict) -> dict:
    root, fault = Path(root), _store_fault(Path(root))
    tickets = _part(_tickets, root, fault)
    answer = {
        "tickets": tickets,
        "decision_packages": _part(_packages, root, fault),
        "readiness": _part(_readiness, root),
        "governance_share": _part(_share, root, tickets),
        "pause": _part(_pause, root),
        "doctor": _part(_doctor, root, args, config),
    }
    # ``root`` and ``config_files`` are W1-07's answer, kept: a builder test of the command line reads them.
    return {"root": str(root), "config_files": sorted(config), **answer, "not_read": _unread_in(answer)}

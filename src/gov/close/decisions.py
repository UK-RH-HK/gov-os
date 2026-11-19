"""The decisions a close records, from the ticket's own sources (W2-200; DEC-1214 M1 (c)).

``decisions_of(root, ticket, front)`` takes the ``DEC-<n>`` ids the ticket's frontmatter names in its ``sources``, in
its optional ``decisions`` list and in its KPI lines (success and failure), each once, and resolves each by id in the
register ``HEAD`` holds (``gov.util.register.read``). No store, no retrieval, no size ceiling.

- A decision **stands** unless its entry's status is SUPERSEDED, RETIRED or REJECTED, or its id is a key of the
  register's ``superseded`` map (superseded by a successor's ``Supersedes`` line); a done-tagged entry stands.
- ``applied``: the ids that stand, sorted by number. ``inputs``: ``{id, hash}`` for each of them, in that order, the
  hash the sha256 of the UTF-8 bytes of the entry's span of the register.
- ``not_standing``: ``{id, status}`` for each cited decision that no longer stands, sorted by number; never applied.
- ``unresolved``: the cited ids neither the register nor the archive holds, sorted by number, and every cited id
  where the project's path map names no register.
- An id only the archived register holds (the path map's ``decision_register_archive``) is ``not_standing`` with the
  state ``ARCHIVED``: history, never applied, never a refusal.
- Nothing here refuses (W2-200 S6 as amended at the land): an id neither the register nor the archive holds, wherever
  the ticket names it, is ``unresolved``, and the close goes on. The close records; it does not prevent.

Ids of other forms (CAP-, W2-, MR-, paths, document names) are not decisions and are left alone.
"""

from __future__ import annotations

import hashlib
from pathlib import Path


ARCHIVED = "ARCHIVED"  # the state of a decision only the archived register holds
NO_LONGER_STANDS = ("SUPERSEDED", "RETIRED", "REJECTED")
TICKETS_REL = ".tickets"


def _number(decision: str) -> int:
    return int(decision.split("-", 1)[1])


def _items(value) -> list[str]:
    """A frontmatter field read as a list of texts: a list's items, a single value as one, nothing for none."""
    if value is None:
        return []
    return [str(item) for item in value] if isinstance(value, (list, tuple)) else [str(value)]


def _kpi_lines(front: dict) -> list[str]:
    """The ticket's KPI lines, success then failure, as its frontmatter states them (a plain list is read whole)."""
    kpis = front.get("kpis")
    if isinstance(kpis, dict):
        return [line for kind in ("success", "failure") for line in _items(kpis.get(kind))]
    return _items(kpis) if isinstance(kpis, list) else []


def cited(front: dict) -> tuple[list[str], list[str]]:
    """``(declared, in_kpis)``: the decision ids of ``sources`` and ``decisions``, and those of the KPI lines alone,
    each once."""
    from gov.util.register import ids

    declared = ids("\n".join(_items(front.get("sources")) + _items(front.get("decisions"))))
    return declared, [found for found in ids("\n".join(_kpi_lines(front))) if found not in declared]


def decisions_of(root: Path, ticket: str, front: dict) -> dict:
    """``{"applied", "not_standing", "unresolved", "inputs"}`` of the decisions ``ticket`` cites (the module's text).
    It never refuses."""
    from gov.util import register as _register

    declared, in_kpis = cited(front or {})
    every = sorted(declared + in_kpis, key=_number)
    result = {"applied": [], "not_standing": [], "unresolved": [], "inputs": []}
    if not every:
        return result
    register = _register.read(Path(root))
    if register is None:  # no register to resolve in: nothing is applied, nothing refuses
        result["unresolved"] = every
        return result
    entries: dict[str, dict] = {}
    for entry in register["entries"]:
        entries.setdefault(entry["id"], entry)
    # A decision the register no longer holds because it is in the archive (EMERGENCY-2 11.3; W2-203) is history: it
    # is no missing decision. It is listed as no longer standing (ARCHIVED) and never applied.
    from gov.util import archive as _archive
    archived = _archive.read(Path(root)) or {}
    for found in every:
        entry = entries.get(found)
        if entry is None and found in archived:
            result["not_standing"].append({"id": found, "status": ARCHIVED})
        elif entry is None:
            result["unresolved"].append(found)
        elif entry["status"] in NO_LONGER_STANDS or found in register["superseded"]:
            status = entry["status"] if entry["status"] in NO_LONGER_STANDS else "SUPERSEDED"
            result["not_standing"].append({"id": found, "status": status})
        else:
            result["applied"].append(found)
            result["inputs"].append({"id": found, "hash":
                                     "sha256:" + hashlib.sha256(entry["span"].encode("utf-8")).hexdigest()})
    return result


def record_fields(root: Path, ticket: str, front: dict) -> dict:
    """What every close record states of the ticket's decisions: ``inputs`` (the ticket's own entry, then each applied
    decision's), ``decisions_applied``, ``decisions_not_standing`` and ``decisions_unresolved``."""
    found = decisions_of(root, ticket, front)
    own = {"id": ticket, "hash": "sha256:" + hashlib.sha256(
        (Path(root) / TICKETS_REL / f"{ticket}.md").read_bytes()).hexdigest()}
    return {"inputs": [own] + found["inputs"], "decisions_applied": found["applied"],
            "decisions_not_standing": found["not_standing"], "decisions_unresolved": found["unresolved"]}

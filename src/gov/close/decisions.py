"""The decisions a close records, from the ticket's own sources (W2-200; DEC-1214 M1 (c)).

``decisions_of(root, ticket, front)`` takes the ``DEC-<n>`` ids the ticket's frontmatter names in its ``sources``, in
its optional ``decisions`` list and in its KPI lines (success and failure), each once, and resolves each by id in the
register ``HEAD`` holds (``gov.util.register.read``). No store, no retrieval, no size ceiling.

- A decision **stands** unless its entry's status is SUPERSEDED, RETIRED or REJECTED, or its id is a key of the
  register's ``superseded`` map (superseded by a successor's ``Supersedes`` line); a done-tagged entry stands.
- ``applied``: the ids that stand, sorted by number. ``inputs``: ``{id, hash}`` for each of them, in that order, the
  hash the sha256 of the UTF-8 bytes of the entry's span of the register.
- ``not_standing``: ``{id, status}`` for each cited decision that no longer stands, sorted by number; never applied.
- ``unresolved``: the ids the register does not hold that the ticket names only in a KPI line, and every cited id
  where the project's path map names no register.
- An id named in ``sources`` or ``decisions`` that the register does not hold refuses: ``DECISION_NOT_FOUND``, naming
  the ticket and every such id. The caller asks before any gate runs, so nothing is written.

Ids of other forms (CAP-, W2-, MR-, paths, document names) are not decisions and are left alone.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

from gov.cli.errors import GovError

NOT_FOUND = "DECISION_NOT_FOUND"
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
    """``{"applied", "not_standing", "unresolved", "inputs"}`` of the decisions ``ticket`` cites (the module's text);
    ``GovError`` ``DECISION_NOT_FOUND`` where ``sources`` or ``decisions`` name one the register does not hold."""
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
    missing = sorted((found for found in declared if found not in entries), key=_number)
    if missing:
        raise GovError(NOT_FOUND, f"{ticket} names {', '.join(missing)} in its sources or decisions, and the decision "
                                  f"register {register['path']} of HEAD does not hold "
                                  f"{'it' if len(missing) == 1 else 'them'}; nothing is closed or recorded",
                       {"ticket": ticket, "missing": missing, "register": register["path"]})
    for found in every:
        entry = entries.get(found)
        if entry is None:
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

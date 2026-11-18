"""The project's coordination ticket (W2-113, DEC-971 item 4): the top-level key ``coordination_ticket`` of
``governance/project/roster.yaml``, which ``gov adopt --lite --stage A0`` writes when ``tk`` is vendored.

Moved from ``gov.guard.install`` unchanged when the guard was retired (EMERGENCY-2 6.1); its install rule, the key's
first reader, went with the guard.
"""

from __future__ import annotations

import os

from gov.util.tickets import _parse_frontmatter

ROSTER = "governance/project/roster.yaml"
COORDINATION_KEY = "coordination_ticket"


def _ticket_file(project_root, name):
    """The real path of the ticket *name* names in ``.tickets/``, or None.

    Resolved as ``gov.util.tickets._load_ticket`` resolves a ticket:
    the file ``<name>.md``, else the ticket whose ``wbs_id`` is *name*.
    """
    if not name or "/" in name or os.sep in name:
        return None
    folder = os.path.join(project_root, ".tickets")
    if not os.path.isdir(folder):
        return None

    def _front(path):
        try:
            with open(path, encoding="utf-8") as f:
                return _parse_frontmatter(f.read())
        except (OSError, UnicodeDecodeError):
            return None

    path = os.path.join(folder, name + ".md")
    if os.path.isfile(path):
        return os.path.realpath(path) if _front(path) is not None else None
    for entry in sorted(os.listdir(folder)):
        path = os.path.join(folder, entry)
        if not entry.endswith(".md") or not os.path.isfile(path):
            continue
        fm = _front(path)
        wbs = (fm or {}).get("wbs_id", "")
        if len(wbs) >= 2 and wbs[0] == wbs[-1] and wbs[0] in ("'", '"'):
            wbs = wbs[1:-1]
        if wbs == name:
            return os.path.realpath(path)
    return None


def coordination_ticket(project_root):
    """``(ticket file, "")`` for the project's coordination ticket, or
    ``(None, why)`` when the key does not name one: the top-level key
    ``coordination_ticket`` of ``governance/project/roster.yaml``, written
    by ``gov adopt --lite --stage A0`` when ``tk`` is vendored, else set by
    hand (DEC-971 item 4).  Never raises."""
    path = os.path.join(project_root, ROSTER)
    try:
        if not os.path.isfile(path):
            return None, f"{ROSTER} does not exist"
        import yaml
        with open(path, encoding="utf-8") as f:
            roster = yaml.safe_load(f)
        value = roster.get(COORDINATION_KEY) if isinstance(roster, dict) \
            else None
        if not isinstance(value, str) or not value.strip():
            return None, (f"{ROSTER} has no text value for the top-level key "
                          f"'{COORDINATION_KEY}'")
        found = _ticket_file(project_root, value.strip())
        if found is None:
            return None, (f"'{COORDINATION_KEY}: {value.strip()}' in {ROSTER} "
                          f"names no ticket in .tickets/")
        return found, ""
    except Exception as exc:
        return None, f"{ROSTER} cannot be read: {type(exc).__name__}: {exc}"

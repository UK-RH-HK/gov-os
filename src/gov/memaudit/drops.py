"""The drop and void rule, after the checker's last pass (Interface section 5, ``void``; S2, F4).

Every question whose line in the highest ``XCHECK-r<n>.md`` is not exactly ``accept`` is moved into
``hidden/dropped/`` (never deleted); the kept count and the scales are recomputed from the kept files. A kept count
under 36 or a domain under its scaled minimum makes the audit void: no ``USED`` and no ``DECLARATION.json`` follow.
"""

from __future__ import annotations

import os
import re

from gov.memaudit import layout, ledger, tables
from gov.memaudit.common import set_digest, utc_iso, write_whole
from gov.memaudit.preflight import MIN_FILES, _load, first_path

SECTION = "## Questions"
HEADING = re.compile(r"#{1,6}(\s|$)")
LEAD_ID = re.compile(r"(q[0-9]{2})(?![0-9A-Za-z_-])")
VERDICTS = ("accept", "revise", "reject")
NOLINE, UNFIT = "NOLINE", "UNFIT"


def read_notes(text: str) -> dict[str, list[str]] | None:
    """``{id: [its lines' fields]}`` from the ``## Questions`` section, or None when the section is absent. A line is
    split on `` | `` into at most five fields; a line not led by an id is not counted for any id."""
    lines = text.splitlines()
    at = next((i for i, line in enumerate(lines) if line.strip() == SECTION), None)
    if at is None:
        return None
    out: dict[str, list] = {}
    for line in lines[at + 1:]:
        if HEADING.match(line):
            break
        line = line.rstrip()
        if not line.strip():
            continue
        m = LEAD_ID.match(line)
        if m:  # a line led by an id counts for it, fitting or not
            out.setdefault(m[1], []).append(line.split(" | ", 4))
    return out


def _codes(field: str) -> list[str]:
    return [c for c in re.split(r"[,;\s]+", field.strip()) if c and c != "-"]


def verdict(rows: list | None) -> tuple[bool, list[str]]:
    """``(kept, drop codes)`` for one question's lines: kept only for exactly one fitting line whose verdict is exactly
    ``accept``; a missing line is ``NOLINE``; a line that does not fit the checker brief's form (or two lines) is
    ``UNFIT``; any other is counted by its codes."""
    if not rows:
        return False, [NOLINE]
    if len(rows) != 1:
        return False, [UNFIT]
    f = rows[0]
    if len(f) != 5 or f[0] != f[0].strip() or f[1] not in VERDICTS or not f[3].startswith("also:"):
        return False, [UNFIT]
    if f[1] == "accept":
        return True, []
    codes = _codes(f[2])
    return (False, codes) if codes else (False, [UNFIT])


def apply(sets_root, audit) -> tuple[str, dict]:
    """The rule for ``audit``. Returns the exit word (``ok``, ``void``, ``refused`` with ``DR-NOTES`` or ``DR-DONE``,
    or ``used``) and the counts the subcommand prints."""
    p = layout.paths(sets_root, audit)
    if os.path.lexists(p["used"]):
        return "used", {"used": True}
    if os.path.lexists(p["drops"]):
        return "refused", {"code": "DR-DONE"}
    notes, rnd = layout.notes(p)
    if notes is None:
        return "refused", {"code": "DR-NOTES"}
    with open(notes, encoding="utf-8", errors="replace") as f:
        rows = read_notes(f.read())
    if rows is None:
        return "refused", {"code": "DR-NOTES"}

    files, _ = layout.entries(p["hidden"])
    drop, by_code = [], {}
    for f in files:
        kept, codes = verdict(rows.get(f.stem))
        if not kept:
            drop.append(f)
            for code in dict.fromkeys(codes):
                by_code[code] = by_code.get(code, 0) + 1
    for f in drop:  # never overwrite a dropped question: a clash stops before anything moves
        if os.path.lexists(p["dropped"] / f.name):
            raise FileExistsError("dropped")
    if drop and not p["dropped"].is_dir():
        os.mkdir(p["dropped"], 0o700)
    for f in drop:
        os.rename(f, p["dropped"] / f.name)

    kept_files, _ = layout.entries(p["hidden"])
    kept = len(kept_files)
    domains, subsystems = tables.spread([first_path(_load(f)) for f in kept_files])
    thin = tables.thin_domains(domains, kept)
    over = tables.heavy_subsystems(subsystems, kept)
    cause = "VOID-COUNT" if kept < MIN_FILES else ("VOID-DOMAIN" if thin else None)
    counts = {"kept": kept, "dropped": len(drop), "by_code": dict(sorted(by_code.items())), "domains": domains,
              "subsystems": subsystems, "subsystem_over": over, "void": cause, "set_digest": set_digest(p["hidden"]),
              "notes_round": rnd, "domain_min": tables.domain_min(kept), "subsystem_max": tables.subsystem_max(kept),
              "thin_domains": thin, "at": utc_iso()}
    run_dir = layout.make_run(p)
    write_whole(run_dir, "DROPS.json", counts)
    ledger.append(run_dir, "drop", kept=kept, dropped=len(drop), void=cause, notes_round=rnd)
    if cause:
        ledger.append(run_dir, "void", cause=cause, kept=kept)
        return "void", counts
    return "ok", counts


def lines(word: str, counts: dict) -> list[str]:
    if word == "used":
        return ["USED"]
    if word == "refused":
        return [counts["code"]]
    out = [f"subsystem {name} {counts['subsystems'][name]} over {counts['subsystem_max']}"
           for name in counts["subsystem_over"]]
    if word == "void":
        out += [f"domain {name} {counts['domains'][name]} under {counts['domain_min']}"
                for name in counts["thin_domains"]]
        out.append(f"VOID {counts['void']} kept {counts['kept']} dropped {counts['dropped']}")
    else:
        out.append(f"DROPS: kept {counts['kept']} dropped {counts['dropped']}")
    return out

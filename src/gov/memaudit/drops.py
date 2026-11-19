"""The drop and void rule, after the checker's last pass (Interface section 5, ``void``; S2, F4).

Every question whose line in the highest ``XCHECK-r<n>.md`` is not exactly ``accept`` is moved into
``hidden/dropped/`` (never deleted); the kept count and the scales are recomputed from the kept files. A kept count
under 36 or a domain under its scaled minimum makes the audit void: no ``USED`` and no ``DECLARATION.json`` follow.
"""

from __future__ import annotations

import os
import re

from pathlib import Path

from gov.memaudit import config as _config
from gov.memaudit import layout, ledger, tables
from gov.memaudit.common import UsageError, read_json, set_digest, toplevel, utc_iso, write_whole
from gov.memaudit.preflight import _load, first_path

SECTION = "## Questions"
HEADING = re.compile(r"#{1,6}(\s|$)")
LEAD_ID = re.compile(r"(q[0-9]{2})(?![0-9A-Za-z_-])")
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
    ``accept``; a missing line is ``NOLINE``; a line that does not fit the checker brief's form
    ``<id> | <verdict> | <codes> | also: <...> | <sentence>`` (or two lines) is ``UNFIT``; any other is counted by its
    codes (none when its codes field is ``-``)."""
    if not rows:
        return False, [NOLINE]
    if len(rows) != 1:
        return False, [UNFIT]
    f = rows[0]
    if len(f) != 5 or not LEAD_ID.fullmatch(f[0]) or not f[3].startswith("also:"):
        return False, [UNFIT]
    if f[1] == "accept":
        return True, []
    return False, _codes(f[2])


def _repo(repo):
    """``--repo``, else the top level the process stands in, else None (the configuration may still be named by
    ``MEMAUDIT_CONFIG``)."""
    if repo is not None:
        return Path(repo)
    try:
        return toplevel()
    except UsageError:
        return None


def apply(sets_root, audit, repo=None) -> tuple[str, dict]:
    """The rule for ``audit``. Returns the exit word (``ok``, ``void``, ``refused`` with ``DR-NOTES`` or ``DR-DONE``,
    or ``used``) and the counts the subcommand prints. The tables are the configuration of ``repo`` at the audit commit
    ``PREFLIGHT.json`` records (the working tree's file when it records none the repository holds); a record-key
    subsystem is read from the question's first source file there."""
    p = layout.paths(sets_root, audit)
    repo = _repo(repo)
    if repo is not None and layout.inside(repo, p["root"]):
        raise UsageError("flag inside the sets root")
    pre = read_json(p["preflight"])
    commit = _config.recorded(repo, pre.get("audit_commit") if isinstance(pre, dict) else None)
    cfg = _config.load(repo, commit)
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
    at = tables.reader(repo, commit) if repo is not None else None
    domains, subsystems = tables.spread([first_path(_load(f)) for f in kept_files], cfg, at)
    thin = tables.thin_domains(domains, kept, cfg)
    over = tables.heavy_subsystems(subsystems, kept, cfg)
    cause = "VOID-COUNT" if kept < cfg.min_kept else ("VOID-DOMAIN" if thin else None)
    counts = {"kept": kept, "dropped": len(drop), "by_code": dict(sorted(by_code.items())), "domains": domains,
              "subsystems": subsystems, "subsystem_over": over, "void": cause, "set_digest": set_digest(p["hidden"]),
              "notes_round": rnd, "domain_min": cfg.domain_min(kept), "subsystem_max": cfg.subsystem_max(kept),
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
